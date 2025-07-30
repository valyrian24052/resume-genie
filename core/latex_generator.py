"""LaTeX document generation from resume data."""

from typing import Dict, Any, Optional
import re
import yaml
from pathlib import Path

from models.resume_data import ResumeData
from core.template_manager import TemplateManager


class LaTeXGenerationError(Exception):
    """Exception raised during LaTeX generation."""
    pass


class LaTeXGenerator:
    """Generates LaTeX documents from resume data using simple variable replacement."""
    
    def __init__(self, template_directory: str = "templates"):
        """Initialize LaTeX generator.
        
        Args:
            template_directory: Path to directory containing LaTeX templates
        """
        self.template_manager = TemplateManager(template_directory)
        self.template_directory = Path(template_directory)
    
    def _load_yaml_data(self, yaml_file: str = "data/resume.yaml") -> Dict[str, Any]:
        """Load resume data from YAML file.
        
        Args:
            yaml_file: Path to YAML file
            
        Returns:
            Dictionary containing resume data
        """
        yaml_path = Path(yaml_file)
        if not yaml_path.exists():
            raise LaTeXGenerationError(f"YAML file not found: {yaml_file}")
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _latex_escape(self, text: str) -> str:
        """Escape special LaTeX characters in text.
        
        Args:
            text: Text to escape
            
        Returns:
            LaTeX-escaped text
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Simple character-by-character replacement
        result = ""
        for char in text:
            if char == '\\':
                result += '\\textbackslash{}'
            elif char == '&':
                result += '\\&'
            elif char == '%':
                result += '\\%'
            elif char == '$':
                result += '\\$'
            elif char == '#':
                result += '\\#'
            elif char == '^':
                result += '\\textasciicircum{}'
            elif char == '_':
                result += '\\_'
            elif char == '{':
                result += '\\{'
            elif char == '}':
                result += '\\}'
            elif char == '~':
                result += '\\textasciitilde{}'
            else:
                result += char
        
        return result    
 
    def _format_date_range(self, start_date: str, end_date: str) -> str:
        """Format date range for LaTeX output.
        
        Args:
            start_date: Start date string
            end_date: End date string
            
        Returns:
            Formatted date range
        """
        if end_date.lower() in ['present', 'current', 'now']:
            end_date = 'Present'
        
        return f"{start_date} - {end_date}"
    
    def _join_with_bullets(self, items: list, bullet: str = r'\textbullet') -> str:
        """Join list items with LaTeX bullets.
        
        Args:
            items: List of items to join
            bullet: LaTeX bullet character
            
        Returns:
            Joined string with bullets
        """
        if not items:
            return ""
        
        escaped_items = [self._latex_escape(str(item)) for item in items]
        return f" {bullet} ".join(escaped_items)
    
    def generate_latex(self, resume_data: ResumeData, template_name: str = "resume") -> str:
        """Generate LaTeX document from resume data.
        
        Args:
            resume_data: Resume data object
            template_name: Name of template to use (without .tex extension)
            
        Returns:
            Generated LaTeX document as string
            
        Raises:
            LaTeXGenerationError: If generation fails
        """
        try:
            # Use the template manager to render the resume
            latex_content = self.template_manager.render_resume(template_name, resume_data)
            
            return latex_content
            
        except Exception as e:
            raise LaTeXGenerationError(f"Failed to generate LaTeX: {e}")
    
    def render_template(self, template_name: str, yaml_data: Dict[str, Any]) -> str:
        """Render template with YAML data using simple variable replacement.
        
        Args:
            template_name: Name of template to render
            yaml_data: YAML data for variable replacement
            
        Returns:
            Rendered template content
            
        Raises:
            LaTeXGenerationError: If template rendering fails
        """
        try:
            # Ensure .tex extension
            if not template_name.endswith('.tex'):
                template_name += '.tex'
            
            # Load template content
            template_path = self.template_directory / template_name
            if not template_path.exists():
                raise LaTeXGenerationError(f"Template '{template_name}' not found at {template_path}")
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Replace variables using simple string replacement
            rendered = self._replace_variables(template_content, yaml_data)
            
            return rendered
            
        except Exception as e:
            raise LaTeXGenerationError(f"Unexpected error rendering template: {e}")
    
    def _replace_variables(self, template_content: str, yaml_data: Dict[str, Any]) -> str:
        """Replace variables in template content with YAML data.
        
        Args:
            template_content: Template content with {{VARIABLE}} placeholders
            yaml_data: YAML data containing variable values
            
        Returns:
            Template content with variables replaced
        """
        # Create a flattened dictionary for easy variable replacement
        variables = self._flatten_yaml_data(yaml_data)
        
        # Replace all {{VARIABLE}} patterns
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            template_content = template_content.replace(placeholder, str(value))
        
        return template_content
    
    def _flatten_yaml_data(self, yaml_data: Dict[str, Any]) -> Dict[str, str]:
        """Flatten YAML data into simple key-value pairs for variable replacement.
        
        Args:
            yaml_data: YAML data dictionary
            
        Returns:
            Flattened dictionary with uppercase keys
        """
        variables = {}
        
        # Basic information
        variables['NAME'] = yaml_data.get('name', '')
        variables['EMAIL'] = yaml_data.get('email', '')
        variables['PHONE'] = yaml_data.get('phone', '')
        
        # Links
        variables['PORTFOLIO_URL'] = yaml_data.get('portfolio_url', '')
        variables['LINKEDIN_URL'] = yaml_data.get('linkedin_url', '')
        variables['LINKEDIN_TEXT'] = yaml_data.get('linkedin_text', '')
        variables['GITHUB_URL'] = yaml_data.get('github_url', '')
        variables['GITHUB_TEXT'] = yaml_data.get('github_text', '')
        
        # Education
        variables['EDUCATION_SCHOOL'] = yaml_data.get('education_school', '')
        variables['EDUCATION_LOCATION'] = yaml_data.get('education_location', '')
        variables['EDUCATION_DEGREE'] = yaml_data.get('education_degree', '')
        variables['EDUCATION_GPA'] = yaml_data.get('education_gpa', '')
        variables['EDUCATION_DATES'] = yaml_data.get('education_dates', '')
        variables['EDUCATION_COURSEWORK'] = yaml_data.get('education_coursework', '')
        
        # Skills
        variables['SKILLS_LANGUAGES'] = yaml_data.get('skills_languages', '')
        variables['SKILLS_FRAMEWORKS'] = yaml_data.get('skills_frameworks', '')
        variables['SKILLS_TOOLS'] = yaml_data.get('skills_tools', '')
        variables['SKILLS_PROFICIENCY'] = yaml_data.get('skills_proficiency', '')
        
        return variables
    
    def validate_template(self, template_name: str) -> bool:
        """Validate template exists and is readable.
        
        Args:
            template_name: Name of template to validate
            
        Returns:
            True if template is valid
        """
        try:
            # Ensure .tex extension
            if not template_name.endswith('.tex'):
                template_name += '.tex'
            
            # Check if template exists
            template_path = self.template_directory / template_name
            return template_path.exists() and template_path.is_file()
                
        except Exception:
            return False