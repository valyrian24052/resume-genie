"""Unit tests for LaTeX generation system."""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.latex_generator import LaTeXGenerator, LaTeXGenerationError
from core.template_manager import TemplateManager
from models.resume_data import (
    ResumeData, BasicInfo, ContactInfo, Website, Experience, JobTitle,
    Education, Degree, SkillCategory
)


class TestTemplateManager(unittest.TestCase):
    """Test cases for TemplateManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_manager = TemplateManager(self.temp_dir)
        
        # Create test template
        self.test_template_content = r"""
\documentclass{article}
\begin{document}
Test template with <<name>>
\end{document}
"""
        self.test_template_path = Path(self.temp_dir) / "test.tex"
        with open(self.test_template_path, 'w') as f:
            f.write(self.test_template_content)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_get_available_templates(self):
        """Test getting list of available templates."""
        templates = self.template_manager.get_available_templates()
        self.assertIn("test", templates)
    
    def test_load_template(self):
        """Test loading template content."""
        content = self.template_manager.load_template("test")
        self.assertEqual(content.strip(), self.test_template_content.strip())
    
    def test_load_template_with_extension(self):
        """Test loading template with .tex extension."""
        content = self.template_manager.load_template("test.tex")
        self.assertEqual(content.strip(), self.test_template_content.strip())
    
    def test_load_nonexistent_template(self):
        """Test loading non-existent template raises error."""
        with self.assertRaises(FileNotFoundError):
            self.template_manager.load_template("nonexistent")
    
    def test_validate_template_syntax_valid(self):
        """Test validation of valid template syntax."""
        valid_template = r"""
\documentclass{article}
\begin{document}
\begin{itemize}
\item Test
\end{itemize}
\end{document}
"""
        self.assertTrue(self.template_manager.validate_template_syntax(valid_template))
    
    def test_validate_template_syntax_invalid_braces(self):
        """Test validation fails for unbalanced braces."""
        invalid_template = r"""
\documentclass{article}
\begin{document}
Test {unbalanced
\end{document}
"""
        self.assertFalse(self.template_manager.validate_template_syntax(invalid_template))
    
    def test_validate_template_syntax_invalid_environments(self):
        """Test validation fails for unbalanced environments."""
        invalid_template = r"""
\documentclass{article}
\begin{document}
\begin{itemize}
\item Test
\end{document}
"""
        self.assertFalse(self.template_manager.validate_template_syntax(invalid_template))
    
    def test_template_exists(self):
        """Test checking if template exists."""
        self.assertTrue(self.template_manager.template_exists("test"))
        self.assertFalse(self.template_manager.template_exists("nonexistent"))


class TestLaTeXGenerator(unittest.TestCase):
    """Test cases for LaTeXGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = LaTeXGenerator(self.temp_dir)
        
        # Create test template
        self.test_template_content = r"""
\documentclass{article}
\begin{document}
Name: <<name|latex_escape>>
Email: <<email|latex_escape>>
<% if summary %>Summary: <<summary|latex_escape>><% endif %>
<% for exp in experiences %>
Company: <<exp.company|latex_escape>>
<% for title in exp.titles %>
Title: <<title.name|latex_escape>> (<<title.date_range>>)
<% endfor %>
<% for highlight in exp.highlights %>
- <<highlight|latex_escape>>
<% endfor %>
<% endfor %>
<% for skill_cat in skills %>
<<skill_cat.category|latex_escape>>: <<skill_cat.skill_list|latex_escape>>
<% endfor %>
\end{document}
"""
        self.test_template_path = Path(self.temp_dir) / "test.tex"
        with open(self.test_template_path, 'w') as f:
            f.write(self.test_template_content)
        
        # Create test resume data
        self.resume_data = ResumeData(
            basic=BasicInfo(
                name="John Doe",
                address=["123 Main St", "City, State 12345"],
                contact=ContactInfo(
                    email="john.doe@example.com",
                    phone="555-123-4567"
                ),
                websites=[
                    Website(text="LinkedIn", url="https://linkedin.com/in/johndoe"),
                    Website(text="GitHub", url="https://github.com/johndoe")
                ]
            ),
            summary="Experienced software developer",
            experiences=[
                Experience(
                    company="Tech Corp",
                    titles=[
                        JobTitle(
                            name="Senior Developer",
                            startdate="2020-01",
                            enddate="Present"
                        )
                    ],
                    highlights=[
                        "Led team of 5 developers",
                        "Improved system performance by 40%"
                    ]
                )
            ],
            skills=[
                SkillCategory(
                    category="Programming",
                    skills=["Python", "JavaScript", "Java"]
                )
            ]
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_latex_escape(self):
        """Test LaTeX character escaping."""
        test_cases = [
            ("Hello & World", r"Hello \& World"),
            ("100% complete", r"100\% complete"),
            ("Cost: $50", r"Cost: \$50"),
            ("Section #1", r"Section \#1"),
            ("x^2", r"x\textasciicircum{}2"),
            ("file_name", r"file\_name"),
            ("{braces}", r"\{braces\}"),
            ("~home", r"\textasciitilde{}home"),
            ("back\\slash", r"back\textbackslash{}slash")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.generator._latex_escape(input_text)
                self.assertEqual(result, expected)
    
    def test_format_date_range(self):
        """Test date range formatting."""
        test_cases = [
            ("2020-01", "2023-12", "2020-01 - 2023-12"),
            ("2020-01", "present", "2020-01 - Present"),
            ("2020-01", "current", "2020-01 - Present"),
            ("2020-01", "now", "2020-01 - Present")
        ]
        
        for start, end, expected in test_cases:
            with self.subTest(start=start, end=end):
                result = self.generator._format_date_range(start, end)
                self.assertEqual(result, expected)
    
    def test_join_with_bullets(self):
        """Test joining items with bullets."""
        items = ["Python", "Java & C++", "JavaScript"]
        result = self.generator._join_with_bullets(items)
        expected = r"Python \textbullet Java \& C++ \textbullet JavaScript"
        self.assertEqual(result, expected)
    
    def test_join_with_bullets_empty(self):
        """Test joining empty list returns empty string."""
        result = self.generator._join_with_bullets([])
        self.assertEqual(result, "")
    
    def test_prepare_template_context(self):
        """Test preparation of template context from resume data."""
        context = self.generator._prepare_template_context(self.resume_data)
        
        # Check basic info
        self.assertEqual(context['name'], "John Doe")
        self.assertEqual(context['email'], "john.doe@example.com")
        self.assertEqual(context['phone'], "555-123-4567")
        self.assertEqual(context['address'], ["123 Main St", "City, State 12345"])
        
        # Check summary
        self.assertEqual(context['summary'], "Experienced software developer")
        
        # Check experiences
        self.assertEqual(len(context['experiences']), 1)
        exp = context['experiences'][0]
        self.assertEqual(exp['company'], "Tech Corp")
        self.assertEqual(len(exp['titles']), 1)
        self.assertEqual(exp['titles'][0]['name'], "Senior Developer")
        self.assertEqual(exp['titles'][0]['date_range'], "2020-01 - Present")
        self.assertEqual(exp['highlights'], ["Led team of 5 developers", "Improved system performance by 40%"])
        
        # Check skills
        self.assertEqual(len(context['skills']), 1)
        skill = context['skills'][0]
        self.assertEqual(skill['category'], "Programming")
        self.assertEqual(skill['skills'], ["Python", "JavaScript", "Java"])
        self.assertEqual(skill['skill_list'], "Python, JavaScript, Java")
    
    def test_render_template(self):
        """Test template rendering with resume data."""
        result = self.generator.render_template("test", self.resume_data)
        
        # Check that basic info is rendered
        self.assertIn("Name: John Doe", result)
        self.assertIn("Email: john.doe@example.com", result)
        self.assertIn("Summary: Experienced software developer", result)
        
        # Check that experience is rendered
        self.assertIn("Company: Tech Corp", result)
        self.assertIn("Title: Senior Developer (2020-01 - Present)", result)
        self.assertIn("- Led team of 5 developers", result)
        self.assertIn("- Improved system performance by 40\\%", result)
        
        # Check that skills are rendered
        self.assertIn("Programming: Python, JavaScript, Java", result)
    
    def test_render_template_nonexistent(self):
        """Test rendering non-existent template raises error."""
        with self.assertRaises(LaTeXGenerationError):
            self.generator.render_template("nonexistent", self.resume_data)
    
    def test_generate_latex(self):
        """Test complete LaTeX generation."""
        result = self.generator.generate_latex(self.resume_data, "test")
        
        # Should contain rendered content
        self.assertIn("Name: John Doe", result)
        self.assertIn("Company: Tech Corp", result)
        
        # Should be valid LaTeX structure
        self.assertIn(r"\documentclass{article}", result)
        self.assertIn(r"\begin{document}", result)
        self.assertIn(r"\end{document}", result)
    
    def test_generate_latex_invalid_data(self):
        """Test generation with invalid resume data raises error."""
        invalid_data = ResumeData(
            basic=BasicInfo(
                name="",  # Invalid: empty name
                address=[],
                contact=ContactInfo(email="", phone="")
            )
        )
        
        with self.assertRaises(LaTeXGenerationError):
            self.generator.generate_latex(invalid_data, "test")
    
    def test_validate_template_valid(self):
        """Test validation of valid template."""
        self.assertTrue(self.generator.validate_template("test"))
    
    def test_validate_template_nonexistent(self):
        """Test validation of non-existent template."""
        self.assertFalse(self.generator.validate_template("nonexistent"))
    
    def test_validate_template_invalid_syntax(self):
        """Test validation of template with invalid syntax."""
        # Create template with invalid LaTeX syntax
        invalid_template_path = Path(self.temp_dir) / "invalid.tex"
        with open(invalid_template_path, 'w') as f:
            f.write(r"""
\documentclass{article}
\begin{document}
\begin{itemize}
Test without end
\end{document}
""")
        
        self.assertFalse(self.generator.validate_template("invalid"))


class TestLaTeXGeneratorIntegration(unittest.TestCase):
    """Integration tests for LaTeX generation with real templates."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = LaTeXGenerator("templates")
        
        # Create comprehensive test resume data
        self.resume_data = ResumeData(
            basic=BasicInfo(
                name="Jane Smith",
                address=["456 Oak Ave", "Springfield, IL 62701"],
                contact=ContactInfo(
                    email="jane.smith@email.com",
                    phone="(555) 987-6543"
                ),
                websites=[
                    Website(text="Portfolio", url="https://janesmith.dev"),
                    Website(text="LinkedIn", url="https://linkedin.com/in/janesmith")
                ]
            ),
            summary="Full-stack developer with 5+ years of experience in web applications",
            experiences=[
                Experience(
                    company="StartupCo",
                    titles=[
                        JobTitle(
                            name="Lead Developer",
                            startdate="2022-03",
                            enddate="Present"
                        ),
                        JobTitle(
                            name="Software Engineer",
                            startdate="2020-01",
                            enddate="2022-02"
                        )
                    ],
                    highlights=[
                        "Architected microservices platform serving 1M+ users",
                        "Reduced deployment time by 75% through CI/CD improvements",
                        "Mentored 3 junior developers"
                    ]
                ),
                Experience(
                    company="BigCorp",
                    titles=[
                        JobTitle(
                            name="Junior Developer",
                            startdate="2019-06",
                            enddate="2019-12"
                        )
                    ],
                    highlights=[
                        "Developed REST APIs using Python & Flask",
                        "Improved test coverage from 60% to 95%"
                    ]
                )
            ],
            education=[
                Education(
                    school="University of Technology",
                    degrees=[
                        Degree(
                            names=["Bachelor of Science in Computer Science"],
                            startdate="2015-09",
                            enddate="2019-05",
                            gpa=3.8
                        )
                    ],
                    achievements=[
                        "Summa Cum Laude",
                        "Dean's List for 6 semesters"
                    ]
                )
            ],
            projects=[
                "E-commerce platform with React & Node.js",
                "Machine learning model for stock prediction",
                "Open source contribution to popular Python library"
            ],
            skills=[
                SkillCategory(
                    category="Languages",
                    skills=["Python", "JavaScript", "TypeScript", "Java", "Go"]
                ),
                SkillCategory(
                    category="Frameworks",
                    skills=["React", "Node.js", "Django", "Flask", "Express"]
                ),
                SkillCategory(
                    category="Tools",
                    skills=["Docker", "Kubernetes", "AWS", "Git", "Jenkins"]
                )
            ]
        )
    
    def test_generate_with_resume_template(self):
        """Test generation with the resume.tex template."""
        try:
            result = self.generator.generate_latex(self.resume_data, "resume")
            
            # Should contain basic structure
            self.assertIn(r"\documentclass", result)
            self.assertIn(r"\begin{document}", result)
            self.assertIn(r"\end{document}", result)
            
            # Should contain escaped content
            self.assertIn("Jane Smith", result)
            self.assertIn("jane.smith@email.com", result)
            self.assertIn("StartupCo", result)
            self.assertIn("Lead Developer", result)
            
            # Should handle special characters
            self.assertIn("5+ years", result)  # + should be handled
            
            # Should contain skills
            self.assertIn("Languages", result)
            self.assertIn("Python", result)
            
        except FileNotFoundError:
            self.skipTest("resume.tex template not found")
    
    def test_generate_with_minimal_data(self):
        """Test generation with minimal resume data."""
        minimal_data = ResumeData(
            basic=BasicInfo(
                name="Test User",
                address=["123 Test St"],
                contact=ContactInfo(
                    email="test@example.com",
                    phone="555-0000"
                )
            )
        )
        
        try:
            result = self.generator.generate_latex(minimal_data, "resume")
            
            # Should still generate valid LaTeX
            self.assertIn(r"\documentclass", result)
            self.assertIn(r"\begin{document}", result)
            self.assertIn(r"\end{document}", result)
            self.assertIn("Test User", result)
            
        except FileNotFoundError:
            self.skipTest("resume.tex template not found")


if __name__ == '__main__':
    unittest.main()