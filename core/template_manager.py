"""Template management for LaTeX resume generation."""

import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from dataclasses import asdict

from models.resume_data import ResumeData


class TemplateValidationError(Exception):
    """Exception raised for template validation errors."""
    pass


class SimpleTemplateEngine:
    """Simple LaTeX template engine with basic placeholder replacement."""
    
    def __init__(self):
        """Initialize the simple template engine."""
        pass
        
    def render_template(self, template_content: str, resume_data: ResumeData) -> str:
        """Render template with simple placeholder replacement.
        
        Args:
            template_content: LaTeX template content with placeholders
            resume_data: Resume data to populate template
            
        Returns:
            Rendered LaTeX content
            
        Raises:
            TemplateValidationError: If template rendering fails
        """
        try:
            # Prepare all template data
            template_vars = self._prepare_template_data(resume_data)
            
            # Replace all placeholders
            rendered = template_content
            for key, value in template_vars.items():
                placeholder = f"{{{{{key}}}}}"
                rendered = rendered.replace(placeholder, str(value))
            
            return rendered
            
        except Exception as e:
            raise TemplateValidationError(f"Template rendering failed: {e}")
    
    def _prepare_template_data(self, resume_data: ResumeData) -> Dict[str, str]:
        """Prepare resume data for simple template replacement.
        
        Args:
            resume_data: Resume data object
            
        Returns:
            Dictionary with all template variables as strings
        """
        template_vars = {}
        
        # Basic info
        if resume_data.basic:
            template_vars['NAME'] = resume_data.basic.name
            template_vars['EMAIL'] = resume_data.basic.contact.email
            template_vars['PHONE'] = resume_data.basic.contact.phone
            
            # Handle websites
            portfolio_link = ""
            linkedin_link = ""
            github_link = ""
            
            for website in resume_data.basic.websites:
                if 'portfolio' in website.text.lower() or 'web' in website.text.lower():
                    portfolio_link = f"Portfolio: \\href{{{website.url}}}{{{website.text}}}"
                elif 'linkedin' in website.text.lower():
                    linkedin_link = f"\\href{{{website.url}}}{{LinkedIn: {website.text}}}"
                elif 'github' in website.text.lower():
                    github_link = f"\\href{{{website.url}}}{{GitHub: {website.text}}}"
            
            template_vars['PORTFOLIO_LINK'] = portfolio_link
            template_vars['LINKEDIN_LINK'] = linkedin_link
            template_vars['GITHUB_LINK'] = github_link
        
        # Education
        if resume_data.education and resume_data.education[0]:
            edu = resume_data.education[0]
            template_vars['EDUCATION_SCHOOL'] = edu.school
            template_vars['EDUCATION_LOCATION'] = ""  # Can be added later
            
            if edu.degrees and edu.degrees[0]:
                degree = edu.degrees[0]
                template_vars['EDUCATION_DEGREE'] = ', '.join(degree.names)
                template_vars['EDUCATION_DATES'] = f"{degree.startdate} - {degree.enddate}"
                template_vars['EDUCATION_GPA'] = f"GPA: {degree.gpa}" if degree.gpa else ""
            else:
                template_vars['EDUCATION_DEGREE'] = ""
                template_vars['EDUCATION_DATES'] = ""
                template_vars['EDUCATION_GPA'] = ""
            
            template_vars['EDUCATION_COURSEWORK'] = ', '.join(edu.achievements) if edu.achievements else ""
        else:
            template_vars.update({
                'EDUCATION_SCHOOL': "",
                'EDUCATION_LOCATION': "",
                'EDUCATION_DEGREE': "",
                'EDUCATION_DATES': "",
                'EDUCATION_GPA': "",
                'EDUCATION_COURSEWORK': ""
            })
        
        # Skills section
        skills_section = ""
        if resume_data.skills:
            for skill_cat in resume_data.skills:
                skills_list = ', '.join(skill_cat.skills)
                skills_section += f"    \\resumeSubItem{{{skill_cat.category}}}{{{skills_list}}}\n"
        template_vars['SKILLS_SECTION'] = skills_section
        
        # Experience section
        experience_section = ""
        if resume_data.experiences:
            for exp in resume_data.experiences:
                if exp.titles and exp.titles[0]:
                    title = exp.titles[0]
                    experience_section += f"    \\resumeSubheading\n"
                    experience_section += f"      {{{exp.company}}}{{}}\n"
                    experience_section += f"      {{{title.name}}}{{{title.startdate} - {title.enddate}}}\n"
                    
                    if exp.highlights:
                        experience_section += f"      \\resumeItemListStart\n"
                        for highlight in exp.highlights:
                            # Escape LaTeX special characters
                            safe_highlight = self._escape_latex(highlight)
                            experience_section += f"        \\resumeItemWithoutTitle{{{safe_highlight}}}\n"
                        experience_section += f"      \\resumeItemListEnd\n"
                    
                    experience_section += f"    \\vspace{{2pt}}\n"
        template_vars['EXPERIENCE_SECTION'] = experience_section
        
        # Projects section
        projects_section = ""
        if resume_data.projects:
            for project in resume_data.projects:
                safe_name = self._escape_latex(project.name)
                safe_desc = self._escape_latex(project.description)
                projects_section += f"    \\resumeSubItem{{\\textbf{{{safe_name}}}}}{{{safe_desc}}}\n"
                projects_section += f"    \\vspace{{3pt}}\n"
        template_vars['PROJECTS_SECTION'] = projects_section
        
        # Research section
        research_section = ""
        if resume_data.research:
            for research in resume_data.research:
                safe_title = self._escape_latex(research.title)
                safe_desc = self._escape_latex(research.description)
                research_section += f"    \\resumeSubItem{{{safe_title}}}{{{safe_desc}}}\n"
                research_section += f"    \\vspace{{2pt}}\n"
        template_vars['RESEARCH_SECTION'] = research_section
        
        return template_vars
    
    def _escape_latex(self, text: str) -> str:
        """Escape LaTeX special characters in text.
        
        Args:
            text: Text to escape
            
        Returns:
            LaTeX-safe text
        """
        if not text:
            return ""
        
        # LaTeX special characters that need escaping
        replacements = {
            '&': '\\&',
            '%': '\\%',
            '$': '\\$',
            '#': '\\#',
            '^': '\\textasciicircum{}',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '~': '\\textasciitilde{}',
            '\\': '\\textbackslash{}'
        }
        
        result = text
        for char, replacement in replacements.items():
            result = result.replace(char, replacement)
        
        return result



class TemplateManager:
    """Manages LaTeX templates for resume generation."""
    
    def __init__(self, template_directory: str = "templates"):
        """Initialize template manager with template directory.
        
        Args:
            template_directory: Path to directory containing LaTeX templates
        """
        self.template_directory = Path(template_directory)
        self.template_engine = SimpleTemplateEngine()
        self._ensure_template_directory()
    
    def _ensure_template_directory(self) -> None:
        """Ensure template directory exists."""
        if not self.template_directory.exists():
            raise FileNotFoundError(f"Template directory not found: {self.template_directory}")
    
    def get_available_templates(self) -> List[str]:
        """Get list of available template names.
        
        Returns:
            List of template names (without .tex extension)
        """
        templates = []
        if self.template_directory.exists():
            for file_path in self.template_directory.glob("*.tex"):
                templates.append(file_path.stem)
        return sorted(templates)
    
    def load_template(self, template_name: str) -> str:
        """Load template content from file.
        
        Args:
            template_name: Name of template (with or without .tex extension)
            
        Returns:
            Template content as string
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            IOError: If template file cannot be read
        """
        # Ensure .tex extension
        if not template_name.endswith('.tex'):
            template_name += '.tex'
        
        template_path = self.template_directory / template_name
        
        if not template_path.exists():
            available = self.get_available_templates()
            raise FileNotFoundError(
                f"Template '{template_name}' not found. Available templates: {available}"
            )
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            raise IOError(f"Failed to read template '{template_name}': {e}")
    
    def validate_template_syntax(self, template_content: str) -> bool:
        """Validate basic LaTeX template syntax.
        
        Args:
            template_content: Template content to validate
            
        Returns:
            True if template appears to have valid basic syntax
        """
        # Check for basic LaTeX document structure
        has_documentclass = r'\documentclass' in template_content
        has_begin_document = r'\begin{document}' in template_content
        has_end_document = r'\end{document}' in template_content
        
        if not (has_documentclass and has_begin_document and has_end_document):
            return False
        
        # Check for balanced braces (basic check)
        open_braces = template_content.count('{')
        close_braces = template_content.count('}')
        
        if open_braces != close_braces:
            return False
        
        # Check for balanced begin/end environments
        begin_pattern = r'\\begin\{([^}]+)\}'
        end_pattern = r'\\end\{([^}]+)\}'
        
        begin_matches = re.findall(begin_pattern, template_content)
        end_matches = re.findall(end_pattern, template_content)
        
        # Each begin should have a corresponding end
        begin_counts = {}
        for env in begin_matches:
            begin_counts[env] = begin_counts.get(env, 0) + 1
        
        end_counts = {}
        for env in end_matches:
            end_counts[env] = end_counts.get(env, 0) + 1
        
        return begin_counts == end_counts
    
    def get_template_path(self, template_name: str) -> Path:
        """Get full path to template file.
        
        Args:
            template_name: Name of template (with or without .tex extension)
            
        Returns:
            Path object for template file
        """
        if not template_name.endswith('.tex'):
            template_name += '.tex'
        
        return self.template_directory / template_name
    
    def template_exists(self, template_name: str) -> bool:
        """Check if template exists.
        
        Args:
            template_name: Name of template (with or without .tex extension)
            
        Returns:
            True if template exists
        """
        return self.get_template_path(template_name).exists()
    
    def render_resume(self, template_name: str, resume_data: ResumeData) -> str:
        """Render resume using simple template engine.
        
        Args:
            template_name: Name of template to use
            resume_data: Resume data to populate template
            
        Returns:
            Rendered LaTeX content
            
        Raises:
            FileNotFoundError: If template doesn't exist
            TemplateValidationError: If rendering fails
        """
        template_content = self.load_template(template_name)
        return self.template_engine.render_template(template_content, resume_data)