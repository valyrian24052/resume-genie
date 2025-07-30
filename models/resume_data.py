"""Data models for resume structure and validation."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class ContactInfo:
    """Contact information for the resume."""
    email: str
    phone: str


@dataclass
class Website:
    """Website information with optional icon."""
    text: str
    url: str
    icon: Optional[str] = None


@dataclass
class BasicInfo:
    """Basic personal information section."""
    name: str
    address: List[str]
    contact: ContactInfo
    websites: List[Website] = field(default_factory=list)


@dataclass
class Degree:
    """Educational degree information."""
    names: List[str]
    startdate: str
    enddate: str
    gpa: Optional[float] = None


@dataclass
class Education:
    """Education section with school and degree information."""
    school: str
    degrees: List[Degree]
    achievements: List[str] = field(default_factory=list)


@dataclass
class JobTitle:
    """Job title with date range."""
    name: str
    startdate: str
    enddate: str


@dataclass
class Experience:
    """Work experience section."""
    company: str
    titles: List[JobTitle]
    highlights: List[str] = field(default_factory=list)
    unedited: List[str] = field(default_factory=list)  # For AI processing


@dataclass
class SkillCategory:
    """Skills grouped by category."""
    category: str
    skills: List[str]


@dataclass
class ProjectData:
    """Project information with details and technologies."""
    name: str
    description: str
    subtitle: Optional[str] = None
    url: Optional[str] = None
    technologies: List[str] = field(default_factory=list)
    highlights: List[str] = field(default_factory=list)


@dataclass
class ResearchData:
    """Research project information."""
    title: str
    description: str
    publication_date: Optional[str] = None
    collaborators: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


@dataclass
class ResumeData:
    """Complete resume data structure."""
    basic: BasicInfo
    summary: Optional[str] = None
    experiences: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    projects: List[ProjectData] = field(default_factory=list)
    research: List[ResearchData] = field(default_factory=list)
    skills: List[SkillCategory] = field(default_factory=list)

    def validate(self) -> List[str]:
        """Validate the resume data and return list of validation errors."""
        errors = []
        
        # Validate basic info
        if not self.basic.name.strip():
            errors.append("Name is required")
        
        if not self.basic.contact.email.strip():
            errors.append("Email is required")
        
        if not self.basic.contact.phone.strip():
            errors.append("Phone is required")
        
        if not self.basic.address:
            errors.append("Address is required")
        
        # Validate experiences
        for i, exp in enumerate(self.experiences):
            if not exp.company.strip():
                errors.append(f"Experience {i+1}: Company name is required")
            
            if not exp.titles:
                errors.append(f"Experience {i+1}: At least one job title is required")
            
            for j, title in enumerate(exp.titles):
                if not title.name.strip():
                    errors.append(f"Experience {i+1}, Title {j+1}: Job title name is required")
                if not title.startdate.strip():
                    errors.append(f"Experience {i+1}, Title {j+1}: Start date is required")
                if not title.enddate.strip():
                    errors.append(f"Experience {i+1}, Title {j+1}: End date is required")
        
        # Validate education
        for i, edu in enumerate(self.education):
            if not edu.school.strip():
                errors.append(f"Education {i+1}: School name is required")
            
            if not edu.degrees:
                errors.append(f"Education {i+1}: At least one degree is required")
            
            for j, degree in enumerate(edu.degrees):
                if not degree.names:
                    errors.append(f"Education {i+1}, Degree {j+1}: Degree name is required")
                if not degree.startdate.strip():
                    errors.append(f"Education {i+1}, Degree {j+1}: Start date is required")
                if not degree.enddate.strip():
                    errors.append(f"Education {i+1}, Degree {j+1}: End date is required")
        
        # Validate skills
        for i, skill_cat in enumerate(self.skills):
            if not skill_cat.category.strip():
                errors.append(f"Skill category {i+1}: Category name is required")
            if not skill_cat.skills:
                errors.append(f"Skill category {i+1}: At least one skill is required")
        
        # Validate projects
        for i, project in enumerate(self.projects):
            if not project.name.strip():
                errors.append(f"Project {i+1}: Project name is required")
            if not project.description.strip():
                errors.append(f"Project {i+1}: Project description is required")
        
        # Validate research
        for i, research in enumerate(self.research):
            if not research.title.strip():
                errors.append(f"Research {i+1}: Research title is required")
            if not research.description.strip():
                errors.append(f"Research {i+1}: Research description is required")
        
        return errors

    def is_valid(self) -> bool:
        """Check if the resume data is valid."""
        return len(self.validate()) == 0