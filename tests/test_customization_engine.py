"""Tests for AI customization engine functionality."""

import pytest
from unittest.mock import Mock, patch
from copy import deepcopy

from ai.customization_engine import CustomizationEngine
from ai.ai_client import AIClient, AIResponse
from models.resume_data import (
    ResumeData, BasicInfo, ContactInfo, Experience, JobTitle, 
    SkillCategory, Website
)
from models.job_profile import JobProfile


class TestCustomizationEngine:
    """Test cases for CustomizationEngine class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create mock AI client
        self.mock_ai_client = Mock(spec=AIClient)
        
        # Mock the prompt loader to avoid file dependencies in tests
        with patch('ai.customization_engine.PromptLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader.load.return_value = True
            mock_loader_class.return_value = mock_loader
            self.engine = CustomizationEngine(self.mock_ai_client)
        
        # Create sample resume data
        self.sample_resume = ResumeData(
            basic=BasicInfo(
                name="John Doe",
                address=["123 Main St", "City, State 12345"],
                contact=ContactInfo(email="john@example.com", phone="555-0123"),
                websites=[Website(text="LinkedIn", url="https://linkedin.com/in/johndoe")]
            ),
            summary="Experienced software developer with 5 years of experience",
            experiences=[
                Experience(
                    company="Tech Corp",
                    titles=[JobTitle(name="Software Engineer", startdate="2020", enddate="2023")],
                    highlights=["Developed web applications", "Led team of 3 developers"],
                    unedited=["Built scalable web apps", "Managed development team"]
                )
            ],
            skills=[
                SkillCategory(category="Programming", skills=["Python", "JavaScript", "Java"]),
                SkillCategory(category="Frameworks", skills=["Django", "React", "Spring"])
            ]
        )
        
        # Create sample job profile
        self.sample_job = JobProfile(
            title="Senior Python Developer",
            company="Python Corp",
            description="Looking for experienced Python developer",
            requirements=["Python", "Django", "REST APIs"],
            preferred_skills=["PostgreSQL", "Docker"],
            industry="Technology",
            experience_level="Senior"
        )
    
    def test_init(self):
        """Test engine initialization."""
        assert self.engine.ai_client == self.mock_ai_client
        assert hasattr(self.engine, 'prompt_loader')
        assert hasattr(self.engine, '_fallback_prompts')
        assert 'summary' in self.engine._fallback_prompts
        assert 'experience' in self.engine._fallback_prompts
        assert 'skills' in self.engine._fallback_prompts
    
    def test_customize_for_job_ai_unavailable(self):
        """Test customization when AI is unavailable."""
        self.mock_ai_client.is_available.return_value = False
        
        result = self.engine.customize_for_job(self.sample_resume, self.sample_job)
        
        # Should return original resume without modification
        assert result.basic.name == self.sample_resume.basic.name
        assert result.summary == self.sample_resume.summary
        assert len(result.experiences) == len(self.sample_resume.experiences)
        assert len(result.skills) == len(self.sample_resume.skills)
        
        # Verify AI client was checked for availability
        self.mock_ai_client.is_available.assert_called_once()
    
    def test_customize_for_job_success(self):
        """Test successful full resume customization."""
        self.mock_ai_client.is_available.return_value = True
        
        # Mock successful AI responses
        self.mock_ai_client.customize_content_with_params.side_effect = [
            AIResponse(success=True, content="Enhanced summary for Python role"),
            AIResponse(success=True, content="- Built Python web applications\n- Led Python development team"),
            AIResponse(success=True, content="Programming:\n  - Python\n  - JavaScript\n  - Java\n\nFrameworks:\n  - Django\n  - React\n  - Spring")
        ]
        
        result = self.engine.customize_for_job(self.sample_resume, self.sample_job)
        
        # Verify customizations were applied
        assert result.summary == "Enhanced summary for Python role"
        assert "Python web applications" in result.experiences[0].highlights[0]
        assert result.skills[0].category == "Programming"
        
        # Verify AI client was called for each customization
        assert self.mock_ai_client.customize_content_with_params.call_count == 3
    
    def test_enhance_summary_success(self):
        """Test successful summary enhancement."""
        mock_response = AIResponse(success=True, content="Enhanced summary content")
        self.mock_ai_client.customize_content_with_params.return_value = mock_response
        
        result = self.engine.enhance_summary("Original summary", self.sample_job)
        
        assert result == "Enhanced summary content"
        self.mock_ai_client.customize_content_with_params.assert_called_once()
    
    def test_enhance_summary_failure(self):
        """Test summary enhancement failure."""
        mock_response = AIResponse(success=False, content="", error_message="API error")
        self.mock_ai_client.customize_content_with_params.return_value = mock_response
        
        result = self.engine.enhance_summary("Original summary", self.sample_job)
        
        assert result is None
    
    def test_enhance_summary_empty_input(self):
        """Test summary enhancement with empty input."""
        result = self.engine.enhance_summary("", self.sample_job)
        assert result is None
        
        result = self.engine.enhance_summary("   ", self.sample_job)
        assert result is None
    
    def test_optimize_experience_success(self):
        """Test successful experience optimization."""
        mock_response = AIResponse(
            success=True, 
            content="- Developed scalable Python applications\n- Led cross-functional development team"
        )
        self.mock_ai_client.customize_content_with_params.return_value = mock_response
        
        result = self.engine.optimize_experience(self.sample_resume.experiences, self.sample_job)
        
        assert len(result) == 1
        assert len(result[0].highlights) == 2
        assert "Python applications" in result[0].highlights[0]
        assert "cross-functional" in result[0].highlights[1]
    
    def test_optimize_experience_uses_unedited(self):
        """Test that experience optimization uses unedited highlights when available."""
        mock_response = AIResponse(success=True, content="- Enhanced highlight")
        self.mock_ai_client.customize_content_with_params.return_value = mock_response
        
        result = self.engine.optimize_experience(self.sample_resume.experiences, self.sample_job)
        
        # Verify the method was called and returned expected result
        self.mock_ai_client.customize_content_with_params.assert_called_once()
        assert len(result) == 1
        assert result[0].highlights == ["Enhanced highlight"]
    
    def test_optimize_experience_fallback_to_highlights(self):
        """Test experience optimization falls back to highlights when unedited is empty."""
        # Create experience without unedited highlights
        experience_no_unedited = Experience(
            company="Test Corp",
            titles=[JobTitle(name="Developer", startdate="2020", enddate="2023")],
            highlights=["Original highlight 1", "Original highlight 2"],
            unedited=[]
        )
        
        mock_response = AIResponse(success=True, content="- Enhanced highlight")
        self.mock_ai_client.customize_content_with_params.return_value = mock_response
        
        result = self.engine.optimize_experience([experience_no_unedited], self.sample_job)
        
        # Verify the method was called and returned expected result
        self.mock_ai_client.customize_content_with_params.assert_called_once()
        assert len(result) == 1
        assert result[0].highlights == ["Enhanced highlight"]
    
    def test_optimize_experience_empty_list(self):
        """Test experience optimization with empty list."""
        result = self.engine.optimize_experience([], self.sample_job)
        assert result == []
    
    def test_adjust_skills_success(self):
        """Test successful skills adjustment."""
        mock_response = AIResponse(
            success=True,
            content="Programming:\n  - Python\n  - JavaScript\n  - Java\n\nFrameworks:\n  - Django\n  - React\n  - Spring"
        )
        self.mock_ai_client.customize_content_with_params.return_value = mock_response
        
        result = self.engine.adjust_skills(self.sample_resume.skills, self.sample_job)
        
        assert len(result) == 2
        assert result[0].category == "Programming"
        assert "Python" in result[0].skills
        assert result[1].category == "Frameworks"
        assert "Django" in result[1].skills
    
    def test_adjust_skills_parsing_failure(self):
        """Test skills adjustment with unparseable response."""
        mock_response = AIResponse(success=True, content="Invalid format response")
        self.mock_ai_client.customize_content_with_params.return_value = mock_response
        
        result = self.engine.adjust_skills(self.sample_resume.skills, self.sample_job)
        
        # Should return original skills when parsing fails
        assert result == self.sample_resume.skills
    
    def test_adjust_skills_ai_failure(self):
        """Test skills adjustment with AI failure."""
        mock_response = AIResponse(success=False, content="", error_message="API error")
        self.mock_ai_client.customize_content_with_params.return_value = mock_response
        
        result = self.engine.adjust_skills(self.sample_resume.skills, self.sample_job)
        
        # Should return original skills when AI fails
        assert result == self.sample_resume.skills
    
    def test_adjust_skills_empty_list(self):
        """Test skills adjustment with empty list."""
        result = self.engine.adjust_skills([], self.sample_job)
        assert result == []
    
    def test_build_job_context(self):
        """Test job context building."""
        context = self.engine._build_job_context(self.sample_job)
        
        assert "Job Title: Senior Python Developer" in context
        assert "Company: Python Corp" in context
        assert "Description: Looking for experienced Python developer" in context
        assert "Requirements: Python, Django, REST APIs" in context
        assert "Preferred Skills: PostgreSQL, Docker" in context
        assert "Industry: Technology" in context
        assert "Experience Level: Senior" in context
    
    def test_build_job_context_minimal(self):
        """Test job context building with minimal job profile."""
        minimal_job = JobProfile(
            title="Developer",
            company="Corp",
            description="Job description"
        )
        
        context = self.engine._build_job_context(minimal_job)
        
        assert "Job Title: Developer" in context
        assert "Company: Corp" in context
        assert "Description: Job description" in context
        # Optional fields should not appear
        assert "Requirements:" not in context
        assert "Industry:" not in context
    
    def test_parse_skills_response_success(self):
        """Test successful skills response parsing."""
        response_content = """Programming:
  - Python
  - JavaScript
  - Java

Frameworks:
  - Django
  - React
  - Spring"""
        
        result = self.engine._parse_skills_response(response_content)
        
        assert len(result) == 2
        assert result[0].category == "Programming"
        assert result[0].skills == ["Python", "JavaScript", "Java"]
        assert result[1].category == "Frameworks"
        assert result[1].skills == ["Django", "React", "Spring"]
    
    def test_parse_skills_response_different_formats(self):
        """Test skills parsing with different bullet formats."""
        response_content = """Programming:
- Python
• JavaScript
  - Java

Frameworks:
- Django"""
        
        result = self.engine._parse_skills_response(response_content)
        
        assert len(result) == 2
        assert result[0].skills == ["Python", "JavaScript", "Java"]
        assert result[1].skills == ["Django"]
    
    def test_parse_skills_response_invalid(self):
        """Test skills parsing with invalid format."""
        response_content = "Invalid format without proper structure"
        
        result = self.engine._parse_skills_response(response_content)
        
        assert result is None
    
    def test_parse_skills_response_exception(self):
        """Test skills parsing with exception."""
        # Test with content that would cause an exception during parsing
        # by passing None which will cause an AttributeError when split() is called
        result = self.engine._parse_skills_response(None)
        assert result is None