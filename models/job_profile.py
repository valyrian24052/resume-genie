"""Data models for job profile and requirements."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class JobProfile:
    """Job profile data for AI customization."""
    title: str
    company: str
    description: str
    requirements: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    industry: str = ""
    experience_level: str = ""
    
    def validate(self) -> List[str]:
        """Validate the job profile data and return list of validation errors."""
        errors = []
        
        if not self.title.strip():
            errors.append("Job title is required")
        
        if not self.company.strip():
            errors.append("Company name is required")
        
        if not self.description.strip():
            errors.append("Job description is required")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if the job profile data is valid."""
        return len(self.validate()) == 0