"""YAML processing module for resume data validation and management."""

import yaml
import jsonschema
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from models.resume_data import (
    ResumeData, BasicInfo, ContactInfo, Website, Experience, 
    JobTitle, Education, Degree, SkillCategory, ProjectData, ResearchData
)


class YAMLProcessingError(Exception):
    """Exception raised for YAML processing errors."""
    pass


class ResumeValidator:
    """Validates resume data against YAML schema."""
    
    def __init__(self, schema_path: Optional[str] = None):
        """Initialize validator with schema file.
        
        Args:
            schema_path: Path to YAML schema file. If None, uses default schema.
        """
        if schema_path is None:
            schema_path = Path(__file__).parent.parent / "config" / "schema.yaml"
        
        self.schema_path = Path(schema_path)
        self._schema = None
        self._load_schema()
    
    def _load_schema(self) -> None:
        """Load the YAML schema from file."""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                self._schema = yaml.safe_load(f)
        except FileNotFoundError:
            raise YAMLProcessingError(f"Schema file not found: {self.schema_path}")
        except yaml.YAMLError as e:
            raise YAMLProcessingError(f"Invalid schema YAML: {e}")
    
    def validate_schema(self, data: Dict[str, Any]) -> bool:
        """Validate data against the schema.
        
        Args:
            data: Dictionary containing resume data to validate
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            YAMLProcessingError: If validation fails with detailed errors
        """
        try:
            jsonschema.validate(data, self._schema)
            return True
        except jsonschema.ValidationError as e:
            error_msg = f"Schema validation failed: {e.message}"
            if e.absolute_path:
                error_msg += f" at path: {'.'.join(str(p) for p in e.absolute_path)}"
            raise YAMLProcessingError(error_msg)
        except jsonschema.SchemaError as e:
            raise YAMLProcessingError(f"Invalid schema: {e.message}")
    
    def get_validation_errors(self, data: Dict[str, Any]) -> List[str]:
        """Get list of validation errors without raising exceptions.
        
        Args:
            data: Dictionary containing resume data to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        try:
            jsonschema.validate(data, self._schema)
        except jsonschema.ValidationError as e:
            # Collect all validation errors
            validator = jsonschema.Draft7Validator(self._schema)
            for error in validator.iter_errors(data):
                error_msg = f"{error.message}"
                if error.absolute_path:
                    error_msg += f" at path: {'.'.join(str(p) for p in error.absolute_path)}"
                errors.append(error_msg)
        except jsonschema.SchemaError as e:
            errors.append(f"Invalid schema: {e.message}")
        
        return errors


class YAMLProcessor:
    """Processes YAML resume files with validation and data conversion."""
    
    def __init__(self, schema_path: Optional[str] = None):
        """Initialize processor with optional schema path.
        
        Args:
            schema_path: Path to YAML schema file for validation
        """
        self.validator = ResumeValidator(schema_path)
    
    def load_resume(self, file_path: str) -> ResumeData:
        """Load and validate resume data from YAML file.
        
        Args:
            file_path: Path to YAML resume file
            
        Returns:
            ResumeData object with validated data
            
        Raises:
            YAMLProcessingError: If file cannot be loaded or data is invalid
        """
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            raise YAMLProcessingError(f"Resume file not found: {file_path}")
        
        # Load YAML content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise YAMLProcessingError(f"Invalid YAML format: {e}")
        except Exception as e:
            raise YAMLProcessingError(f"Error reading file {file_path}: {e}")
        
        if data is None:
            raise YAMLProcessingError("YAML file is empty")
        
        # Validate against schema
        self.validator.validate_schema(data)
        
        # Convert to ResumeData object
        try:
            resume_data = self._dict_to_resume_data(data)
        except Exception as e:
            raise YAMLProcessingError(f"Error converting data to ResumeData: {e}")
        
        # Perform additional validation using ResumeData's validate method
        validation_errors = resume_data.validate()
        if validation_errors:
            error_msg = "Resume data validation failed:\n" + "\n".join(f"- {error}" for error in validation_errors)
            raise YAMLProcessingError(error_msg)
        
        return resume_data
    
    def save_resume(self, resume_data: ResumeData, file_path: str) -> None:
        """Save ResumeData object to YAML file.
        
        Args:
            resume_data: ResumeData object to save
            file_path: Path where to save the YAML file
            
        Raises:
            YAMLProcessingError: If data cannot be saved
        """
        file_path = Path(file_path)
        
        # Convert ResumeData to dictionary
        try:
            data_dict = asdict(resume_data)
        except Exception as e:
            raise YAMLProcessingError(f"Error converting ResumeData to dictionary: {e}")
        
        # Validate the data before saving
        self.validator.validate_schema(data_dict)
        
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to YAML file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data_dict, f, default_flow_style=False, allow_unicode=True, indent=2)
        except Exception as e:
            raise YAMLProcessingError(f"Error writing to file {file_path}: {e}")
    
    def validate_schema(self, data: Dict[str, Any]) -> bool:
        """Validate data dictionary against schema.
        
        Args:
            data: Dictionary to validate
            
        Returns:
            True if valid
            
        Raises:
            YAMLProcessingError: If validation fails
        """
        return self.validator.validate_schema(data)
    
    def get_validation_errors(self, data: Dict[str, Any]) -> List[str]:
        """Get validation errors for data dictionary.
        
        Args:
            data: Dictionary to validate
            
        Returns:
            List of validation error messages
        """
        return self.validator.get_validation_errors(data)
    
    def _dict_to_resume_data(self, data: Dict[str, Any]) -> ResumeData:
        """Convert dictionary to ResumeData object.
        
        Args:
            data: Dictionary containing resume data
            
        Returns:
            ResumeData object
        """
        # Convert basic info
        basic_data = data['basic']
        contact_data = basic_data['contact']
        
        contact = ContactInfo(
            email=contact_data['email'],
            phone=contact_data['phone']
        )
        
        websites = []
        for website_data in basic_data.get('websites', []):
            websites.append(Website(
                text=website_data['text'],
                url=website_data['url'],
                icon=website_data.get('icon')
            ))
        
        basic = BasicInfo(
            name=basic_data['name'],
            address=basic_data['address'],
            contact=contact,
            websites=websites
        )
        
        # Convert experiences
        experiences = []
        for exp_data in data.get('experiences', []):
            titles = []
            for title_data in exp_data['titles']:
                titles.append(JobTitle(
                    name=title_data['name'],
                    startdate=title_data['startdate'],
                    enddate=title_data['enddate']
                ))
            
            experiences.append(Experience(
                company=exp_data['company'],
                titles=titles,
                highlights=exp_data.get('highlights', []),
                unedited=exp_data.get('unedited', [])
            ))
        
        # Convert education
        education = []
        for edu_data in data.get('education', []):
            degrees = []
            for degree_data in edu_data['degrees']:
                degrees.append(Degree(
                    names=degree_data['names'],
                    startdate=degree_data['startdate'],
                    enddate=degree_data['enddate'],
                    gpa=degree_data.get('gpa')
                ))
            
            education.append(Education(
                school=edu_data['school'],
                degrees=degrees,
                achievements=edu_data.get('achievements', [])
            ))
        
        # Convert projects
        projects = []
        for project_data in data.get('projects', []):
            projects.append(ProjectData(
                name=project_data['name'],
                description=project_data['description'],
                subtitle=project_data.get('subtitle'),
                url=project_data.get('url'),
                technologies=project_data.get('technologies', []),
                highlights=project_data.get('highlights', [])
            ))
        
        # Convert research
        research = []
        for research_data in data.get('research', []):
            research.append(ResearchData(
                title=research_data['title'],
                description=research_data['description'],
                publication_date=research_data.get('publication_date'),
                collaborators=research_data.get('collaborators', []),
                keywords=research_data.get('keywords', [])
            ))
        
        # Convert skills
        skills = []
        for skill_data in data.get('skills', []):
            skills.append(SkillCategory(
                category=skill_data['category'],
                skills=skill_data['skills']
            ))
        
        return ResumeData(
            basic=basic,
            summary=data.get('summary'),
            experiences=experiences,
            education=education,
            projects=projects,
            research=research,
            skills=skills
        )