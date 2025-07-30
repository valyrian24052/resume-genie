"""Tests for the ContextBuilder class."""

import unittest
from unittest.mock import Mock
from ai.context_builder import ContextBuilder
from models.resume_data import (
    ResumeData, BasicInfo, ContactInfo, Experience, JobTitle, 
    ProjectData, ResearchData, SkillCategory, Education, Degree
)
from models.job_profile import JobProfile


class TestContextBuilder(unittest.TestCase):
    """Test cases for ContextBuilder functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create sample resume data
        self.resume_data = ResumeData(
            basic=BasicInfo(
                name="John Doe",
                address=["123 Main St", "City, State 12345"],
                contact=ContactInfo(email="john@example.com", phone="555-1234")
            ),
            summary="Experienced software developer with expertise in Python and web development.",
            experiences=[
                Experience(
                    company="Tech Corp",
                    titles=[JobTitle(name="Senior Developer", startdate="2020-01", enddate="2023-12")],
                    highlights=[
                        "Developed scalable web applications using Python and Django",
                        "Led a team of 5 developers on multiple projects",
                        "Improved system performance by 40% through optimization"
                    ]
                ),
                Experience(
                    company="StartupXYZ",
                    titles=[JobTitle(name="Full Stack Developer", startdate="2018-06", enddate="2019-12")],
                    highlights=[
                        "Built REST APIs using Flask and PostgreSQL",
                        "Implemented CI/CD pipelines with Docker and Jenkins"
                    ]
                )
            ],
            projects=[
                ProjectData(
                    name="E-commerce Platform",
                    subtitle="Full-stack web application",
                    description="Built a complete e-commerce platform with user authentication, payment processing, and inventory management",
                    technologies=["Python", "Django", "PostgreSQL", "React"],
                    url="https://github.com/johndoe/ecommerce"
                ),
                ProjectData(
                    name="Data Analytics Dashboard",
                    description="Interactive dashboard for business intelligence and data visualization",
                    technologies=["Python", "Pandas", "Plotly", "Streamlit"]
                )
            ],
            research=[
                ResearchData(
                    title="Machine Learning for Web Performance Optimization",
                    description="Research on using ML algorithms to predict and optimize web application performance",
                    publication_date="2022-03",
                    keywords=["machine learning", "web performance", "optimization"]
                )
            ],
            skills=[
                SkillCategory(
                    category="Programming Languages",
                    skills=["Python", "JavaScript", "Java", "SQL"]
                ),
                SkillCategory(
                    category="Frameworks",
                    skills=["Django", "Flask", "React", "Node.js"]
                ),
                SkillCategory(
                    category="Tools",
                    skills=["Docker", "Jenkins", "Git", "PostgreSQL"]
                )
            ],
            education=[
                Education(
                    school="University of Technology",
                    degrees=[
                        Degree(
                            names=["Bachelor of Science in Computer Science"],
                            startdate="2014-09",
                            enddate="2018-05",
                            gpa=3.8
                        )
                    ]
                )
            ]
        )
        
        # Create sample job profile
        self.job_profile = JobProfile(
            title="Senior Python Developer",
            company="InnovativeTech",
            description="We are looking for a senior Python developer to join our team and work on scalable web applications.",
            requirements=["Python", "Django", "PostgreSQL", "REST APIs"],
            preferred_skills=["Docker", "CI/CD", "React", "Machine Learning"],
            industry="Technology",
            experience_level="Senior"
        )
        
        self.context_builder = ContextBuilder(self.resume_data)
    
    def test_build_experiences_summary(self):
        """Test building experiences summary."""
        summary = self.context_builder.build_experiences_summary(self.job_profile)
        
        self.assertIn("Senior Developer at Tech Corp", summary)
        self.assertIn("Full Stack Developer at StartupXYZ", summary)
        self.assertIn("Developed scalable web applications", summary)
        self.assertIn("Built REST APIs", summary)
    
    def test_build_projects_summary(self):
        """Test building projects summary."""
        summary = self.context_builder.build_projects_summary(self.job_profile)
        
        self.assertIn("E-commerce Platform", summary)
        self.assertIn("Data Analytics Dashboard", summary)
        self.assertIn("Python, Django, PostgreSQL", summary)
        self.assertIn("Built a complete e-commerce platform", summary)
    
    def test_build_skills_summary(self):
        """Test building skills summary."""
        summary = self.context_builder.build_skills_summary(self.job_profile)
        
        self.assertIn("Programming Languages: Python, JavaScript, Java, SQL", summary)
        self.assertIn("Frameworks: Django, Flask, React, Node.js", summary)
        self.assertIn("Tools: Docker, Jenkins, Git, PostgreSQL", summary)
    
    def test_build_research_summary(self):
        """Test building research summary."""
        summary = self.context_builder.build_research_summary(self.job_profile)
        
        self.assertIn("Machine Learning for Web Performance Optimization", summary)
        self.assertIn("2022-03", summary)
        self.assertIn("machine learning, web performance, optimization", summary)
    
    def test_build_education_summary(self):
        """Test building education summary."""
        summary = self.context_builder.build_education_summary()
        
        self.assertIn("University of Technology", summary)
        self.assertIn("Bachelor of Science in Computer Science", summary)
    
    def test_build_full_user_context(self):
        """Test building full user context."""
        context = self.context_builder.build_full_user_context(self.job_profile)
        
        self.assertIn("Name: John Doe", context)
        self.assertIn("Education:", context)
        self.assertIn("Experience:", context)
        self.assertIn("Projects:", context)
        self.assertIn("Skills:", context)
        self.assertIn("Research:", context)
        self.assertIn("Current Summary:", context)
    
    def test_extract_target_skills_from_job(self):
        """Test extracting target skills from job profile."""
        skills = self.context_builder.extract_target_skills_from_job(self.job_profile)
        
        self.assertIn("Python", skills)
        self.assertIn("Django", skills)
        self.assertIn("PostgreSQL", skills)
        self.assertIn("Docker", skills)
        self.assertIn("CI/CD", skills)
    
    def test_build_job_context(self):
        """Test building job context."""
        context = self.context_builder.build_job_context(self.job_profile)
        
        self.assertIn("Job Title: Senior Python Developer", context)
        self.assertIn("Company: InnovativeTech", context)
        self.assertIn("Requirements: Python, Django, PostgreSQL, REST APIs", context)
        self.assertIn("Preferred Skills: Docker, CI/CD, React, Machine Learning", context)
        self.assertIn("Industry: Technology", context)
        self.assertIn("Experience Level: Senior", context)
    
    def test_build_context_variables_summary(self):
        """Test building context variables for summary prompt."""
        variables = self.context_builder.build_context_variables(
            'summary', 
            'Original summary text', 
            self.job_profile
        )
        
        self.assertIn('job_context', variables)
        self.assertIn('content', variables)
        self.assertIn('experiences_summary', variables)
        self.assertIn('projects_summary', variables)
        self.assertIn('skills_summary', variables)
        self.assertIn('education_summary', variables)
        self.assertIn('research_summary', variables)
        
        self.assertEqual(variables['content'], 'Original summary text')
    
    def test_build_context_variables_experience(self):
        """Test building context variables for experience prompt."""
        variables = self.context_builder.build_context_variables(
            'experience', 
            'Original experience text', 
            self.job_profile
        )
        
        self.assertIn('job_context', variables)
        self.assertIn('content', variables)
        self.assertIn('full_context', variables)
        self.assertIn('target_skills', variables)
        
        self.assertEqual(variables['content'], 'Original experience text')
    
    def test_build_context_variables_skills(self):
        """Test building context variables for skills prompt."""
        variables = self.context_builder.build_context_variables(
            'skills', 
            'Original skills text', 
            self.job_profile
        )
        
        self.assertIn('job_context', variables)
        self.assertIn('content', variables)
        self.assertIn('target_skills', variables)
        self.assertIn('user_experience_level', variables)
        self.assertIn('relevant_projects', variables)
        
        self.assertEqual(variables['content'], 'Original skills text')
    
    def test_empty_resume_data(self):
        """Test behavior with empty resume data."""
        empty_builder = ContextBuilder()
        
        summary = empty_builder.build_experiences_summary()
        self.assertEqual(summary, "No professional experience listed")
        
        projects = empty_builder.build_projects_summary()
        self.assertEqual(projects, "No projects listed")
        
        skills = empty_builder.build_skills_summary()
        self.assertEqual(skills, "No skills listed")
    
    def test_infer_experience_level(self):
        """Test experience level inference."""
        # Test with current data (should be senior level)
        level = self.context_builder._infer_experience_level()
        self.assertIn("Senior", level)
        
        # Test with minimal data
        minimal_resume = ResumeData(
            basic=BasicInfo(
                name="Jane Doe",
                address=["123 St"],
                contact=ContactInfo(email="jane@example.com", phone="555-0000")
            ),
            experiences=[
                Experience(
                    company="Company",
                    titles=[JobTitle(name="Developer", startdate="2023-01", enddate="2023-12")],
                    highlights=["Did some work"]
                )
            ]
        )
        
        minimal_builder = ContextBuilder(minimal_resume)
        level = minimal_builder._infer_experience_level()
        self.assertIn("Entry", level)


if __name__ == '__main__':
    unittest.main()