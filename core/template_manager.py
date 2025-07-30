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


class DynamicTemplateEngine:
    """Dynamic LaTeX template engine with iteration and conditional rendering."""
    
    def __init__(self):
        """Initialize the dynamic template engine."""
        self.variable_pattern = re.compile(r'\{\{\{([^}]+)\}\}\}')
        self.loop_pattern = re.compile(r'\{% for (\w+) in (\w+) %\}(.*?)\{% endfor %\}', re.DOTALL)
        self.conditional_pattern = re.compile(r'\{% if (\w+) %\}(.*?)\{% endif %\}', re.DOTALL)
        
    def render_template(self, template_content: str, resume_data: ResumeData) -> str:
        """Render template with dynamic data.
        
        Args:
            template_content: LaTeX template content with dynamic placeholders
            resume_data: Resume data to populate template
            
        Returns:
            Rendered LaTeX content
            
        Raises:
            TemplateValidationError: If template rendering fails
        """
        try:
            # Convert resume data to dictionary for easier access
            data_dict = self._prepare_template_data(resume_data)
            
            # Process template in order: loops, conditionals, then variables
            rendered = self._process_loops(template_content, data_dict)
            rendered = self._process_conditionals(rendered, data_dict)
            rendered = self._process_variables(rendered, data_dict)
            
            return rendered
            
        except Exception as e:
            raise TemplateValidationError(f"Template rendering failed: {e}")
    
    def _prepare_template_data(self, resume_data: ResumeData) -> Dict[str, Any]:
        """Prepare resume data for template processing.
        
        Args:
            resume_data: Resume data object
            
        Returns:
            Dictionary with flattened data for template access
        """
        data_dict = asdict(resume_data)
        
        # Flatten basic info for easier access
        if 'basic' in data_dict:
            basic = data_dict['basic']
            data_dict.update({
                'NAME': basic['name'],
                'EMAIL': basic['contact']['email'],
                'PHONE': basic['contact']['phone'],
            })
            
            # Handle websites
            for website in basic.get('websites', []):
                if 'portfolio' in website['text'].lower():
                    data_dict['PORTFOLIO_URL'] = website['url']
                elif 'linkedin' in website['text'].lower():
                    data_dict['LINKEDIN_URL'] = website['url']
                    data_dict['LINKEDIN_TEXT'] = website['text']
                elif 'github' in website['text'].lower():
                    data_dict['GITHUB_URL'] = website['url']
                    data_dict['GITHUB_TEXT'] = website['text']
        
        # Flatten education for easier access
        if 'education' in data_dict and data_dict['education']:
            edu = data_dict['education'][0]  # Assume first education entry
            data_dict.update({
                'EDUCATION_SCHOOL': edu['school'],
                'EDUCATION_LOCATION': '',  # Add if available in data
                'EDUCATION_DEGREE': ', '.join(edu['degrees'][0]['names']) if edu['degrees'] else '',
                'EDUCATION_GPA': str(edu['degrees'][0].get('gpa', '')) if edu['degrees'] else '',
                'EDUCATION_DATES': f"{edu['degrees'][0]['startdate']} - {edu['degrees'][0]['enddate']}" if edu['degrees'] else '',
                'EDUCATION_COURSEWORK': ', '.join(edu.get('achievements', []))
            })
        
        # Flatten skills for easier access
        if 'skills' in data_dict:
            skills_dict = {}
            for skill_cat in data_dict['skills']:
                category = skill_cat['category'].upper().replace(' ', '_')
                skills_dict[f'SKILLS_{category}'] = ', '.join(skill_cat['skills'])
            data_dict.update(skills_dict)
        
        return data_dict
    
    def _process_loops(self, template_content: str, data_dict: Dict[str, Any]) -> str:
        """Process for loops in template.
        
        Args:
            template_content: Template content with loop syntax
            data_dict: Data dictionary for loop processing
            
        Returns:
            Template content with loops expanded
        """
        def replace_loop(match):
            item_var = match.group(1)
            collection_var = match.group(2)
            loop_body = match.group(3)
            
            if collection_var not in data_dict:
                return ''  # Skip if collection doesn't exist
            
            collection = data_dict[collection_var]
            if not isinstance(collection, list) or not collection:
                return ''  # Skip if empty or not a list
            
            rendered_items = []
            for item in collection:
                # Replace item variables in loop body
                item_body = loop_body
                if isinstance(item, dict):
                    # Handle nested object access
                    item_body = self._replace_nested_variables(item_body, item_var, item)
                else:
                    # Handle simple values
                    placeholder = f'{{{{{item_var}}}}}'
                    item_body = item_body.replace(placeholder, str(item))
                
                rendered_items.append(item_body)
            
            return '\n'.join(rendered_items)
        
        return self.loop_pattern.sub(replace_loop, template_content)
    
    def _replace_nested_variables(self, content: str, item_var: str, item_data: Dict[str, Any]) -> str:
        """Replace nested variable references in content.
        
        Args:
            content: Content with variable references
            item_var: Variable name for the item
            item_data: Data dictionary for the item
            
        Returns:
            Content with variables replaced
        """
        # Pattern to match nested variable access like {{{item.key}}} or {{{item.key.subkey}}}
        nested_pattern = re.compile(rf'\{{{{{item_var}\.([^}}]+)\}}}}')
        
        def replace_nested(match):
            key_path = match.group(1)
            keys = key_path.split('.')
            
            value = item_data
            try:
                for key in keys:
                    if isinstance(value, dict):
                        value = value[key]
                    elif isinstance(value, list) and key.isdigit():
                        value = value[int(key)]
                    elif hasattr(value, key):
                        value = getattr(value, key)
                    else:
                        return f"[{item_var}.{key_path}]"  # Placeholder for missing
                
                if value is None:
                    return ''
                return str(value)
            except (KeyError, IndexError, AttributeError):
                return f"[{item_var}.{key_path}]"  # Placeholder for missing
        
        return nested_pattern.sub(replace_nested, content)
    
    def _process_conditionals(self, template_content: str, data_dict: Dict[str, Any]) -> str:
        """Process conditional statements in template.
        
        Args:
            template_content: Template content with conditional syntax
            data_dict: Data dictionary for conditional evaluation
            
        Returns:
            Template content with conditionals processed
        """
        def replace_conditional(match):
            condition_var = match.group(1)
            conditional_body = match.group(2)
            
            # Check if condition is met
            if condition_var in data_dict:
                value = data_dict[condition_var]
                # Consider non-empty lists, non-empty strings, and True as truthy
                if (isinstance(value, list) and value) or \
                   (isinstance(value, str) and value.strip()) or \
                   (isinstance(value, bool) and value) or \
                   (value is not None and str(value).strip()):
                    return conditional_body
            
            return ''  # Remove conditional block if condition not met
        
        return self.conditional_pattern.sub(replace_conditional, template_content)
    
    def _process_variables(self, template_content: str, data_dict: Dict[str, Any]) -> str:
        """Process variable replacements in template.
        
        Args:
            template_content: Template content with variable placeholders
            data_dict: Data dictionary for variable replacement
            
        Returns:
            Template content with variables replaced
        """
        def replace_variable(match):
            var_name = match.group(1).strip()
            
            if var_name in data_dict:
                value = data_dict[var_name]
                if value is None:
                    return ''
                return str(value)
            else:
                # Log missing variable but don't fail
                print(f"Warning: Template variable '{var_name}' not found in data")
                return f"[{var_name}]"  # Placeholder for missing variables
        
        return self.variable_pattern.sub(replace_variable, template_content)
    
    def validate_template_variables(self, template_content: str, data_dict: Dict[str, Any]) -> List[str]:
        """Validate that all template variables have corresponding data.
        
        Args:
            template_content: Template content to validate
            data_dict: Available data dictionary
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Find all variable references
        variables = self.variable_pattern.findall(template_content)
        
        for var in variables:
            var_name = var.strip()
            if var_name not in data_dict:
                errors.append(f"Missing data for template variable: {var_name}")
        
        # Find all loop references
        loops = self.loop_pattern.findall(template_content)
        for item_var, collection_var, loop_body in loops:
            if collection_var not in data_dict:
                errors.append(f"Missing data for loop collection: {collection_var}")
            elif not isinstance(data_dict[collection_var], list):
                errors.append(f"Loop collection '{collection_var}' is not a list")
        
        # Find all conditional references
        conditionals = self.conditional_pattern.findall(template_content)
        for condition_var, conditional_body in conditionals:
            if condition_var not in data_dict:
                errors.append(f"Missing data for conditional: {condition_var}")
        
        return errors


class TemplateManager:
    """Manages LaTeX templates for resume generation."""
    
    def __init__(self, template_directory: str = "templates"):
        """Initialize template manager with template directory.
        
        Args:
            template_directory: Path to directory containing LaTeX templates
        """
        self.template_directory = Path(template_directory)
        self.dynamic_engine = DynamicTemplateEngine()
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
        """Render resume using dynamic template engine.
        
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
        return self.dynamic_engine.render_template(template_content, resume_data)
    
    def validate_template_with_data(self, template_name: str, resume_data: ResumeData) -> List[str]:
        """Validate template against resume data.
        
        Args:
            template_name: Name of template to validate
            resume_data: Resume data to validate against
            
        Returns:
            List of validation errors
        """
        template_content = self.load_template(template_name)
        data_dict = self.dynamic_engine._prepare_template_data(resume_data)
        return self.dynamic_engine.validate_template_variables(template_content, data_dict)