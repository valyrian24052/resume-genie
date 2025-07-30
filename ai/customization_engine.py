"""AI-powered resume customization engine."""

import logging
from typing import List, Optional, Dict, Any
from copy import deepcopy

from models.resume_data import ResumeData, Experience, SkillCategory
from models.job_profile import JobProfile
from .ai_client import AIClient, AIResponse
from .prompt_loader import PromptLoader, PromptConfig
from .context_builder import ContextBuilder


logger = logging.getLogger(__name__)


class CustomizationEngine:
    """Engine for AI-powered resume customization based on job profiles."""
    
    def __init__(self, ai_client: AIClient, prompt_config_path: str = "config/prompts.yaml"):
        """Initialize customization engine with AI client and prompt configuration.
        
        Args:
            ai_client: Configured AI client for API communication
            prompt_config_path: Path to prompt configuration file
        """
        self.ai_client = ai_client
        self.prompt_loader = PromptLoader(prompt_config_path)
        self.context_builder = ContextBuilder()
        
        # Load prompt configuration
        if not self.prompt_loader.load():
            logger.warning("Failed to load prompt configuration, using fallback prompts")
            self._use_fallback_prompts = True
        else:
            self._use_fallback_prompts = False
            logger.info("Successfully loaded external prompt configuration")
        
        # Fallback prompts (original hardcoded prompts)
        self._fallback_prompts = {
            'summary': """You are a professional resume writer. Customize the given resume summary to better align with the job requirements. 
            Keep the same tone and style but emphasize relevant skills and experiences that match the job profile. 
            Return only the customized summary text, no additional formatting or explanations.""",
            
            'experience': """You are a professional resume writer. Customize the given work experience highlights to better align with the job requirements.
            Emphasize achievements and responsibilities that are most relevant to the target job. Keep the same factual content but adjust the emphasis and wording.
            Return the customized highlights as a bullet-point list, one highlight per line starting with '- '.""",
            
            'skills': """You are a professional resume writer. Given a list of skills and a job profile, reorder and emphasize the skills that are most relevant to the job.
            You may also suggest grouping skills differently if it better matches the job requirements. Keep all original skills but prioritize the most relevant ones.
            Return the skills in the same format as provided, maintaining the category structure.""",
            
            'projects': """You are a professional resume writer. Customize the given project descriptions to better align with the job requirements.
            Emphasize technologies and achievements that are most relevant to the target job. Keep project names and structure unchanged but optimize descriptions.
            Return the projects in the same format as provided, maintaining all original fields but with enhanced descriptions."""
        }
    
    def customize_for_job(self, resume_data: ResumeData, job_profile: JobProfile) -> ResumeData:
        """Customize entire resume for a specific job profile.
        
        Args:
            resume_data: Original resume data to customize
            job_profile: Job profile to customize for
            
        Returns:
            Customized resume data with AI-enhanced content
        """
        logger.info(f"Starting resume customization for job: {job_profile.title} at {job_profile.company}")
        
        # Create a deep copy to avoid modifying the original
        customized_resume = deepcopy(resume_data)
        
        # Set resume data in context builder for rich context generation
        self.context_builder.set_resume_data(resume_data)
        
        # Check if AI is available
        if not self.ai_client.is_available():
            logger.warning("AI endpoint is not available, returning original resume without customization")
            return customized_resume
        
        # Customize summary if present
        if customized_resume.summary:
            customized_summary = self.enhance_summary(customized_resume.summary, job_profile)
            if customized_summary:
                customized_resume.summary = customized_summary
                logger.info("Successfully customized resume summary")
        
        # Customize experience highlights
        customized_resume.experiences = self.optimize_experience(customized_resume.experiences, job_profile)
        
        # Customize skills organization
        customized_resume.skills = self.adjust_skills(customized_resume.skills, job_profile)
        
        # Customize projects
        customized_resume.projects = self.optimize_projects(customized_resume.projects, job_profile)
        
        logger.info("Resume customization completed")
        return customized_resume
    
    def enhance_summary(self, current_summary: str, job_profile: JobProfile) -> Optional[str]:
        """Enhance resume summary for specific job profile.
        
        Args:
            current_summary: Original summary text
            job_profile: Job profile for customization context
            
        Returns:
            Enhanced summary text or None if customization failed
        """
        if not current_summary.strip():
            return None
        
        # Get prompt configuration
        prompt_text = self._get_prompt_text('summary')
        context = self._build_context_from_template('summary', current_summary, job_profile)
        model_params = self._get_model_params('summary')
        
        logger.debug("Requesting AI customization for resume summary")
        response = self.ai_client.customize_content_with_params(
            prompt=prompt_text,
            context=context,
            model_params=model_params
        )
        
        if response.success:
            logger.info("Successfully enhanced resume summary")
            return response.content
        else:
            logger.warning(f"Failed to enhance summary: {response.error_message}")
            return None
    
    def optimize_experience(self, experiences: List[Experience], job_profile: JobProfile) -> List[Experience]:
        """Optimize experience highlights for specific job profile.
        
        Args:
            experiences: List of original experience entries
            job_profile: Job profile for customization context
            
        Returns:
            List of experiences with optimized highlights
        """
        if not experiences:
            return experiences
        
        job_context = self._build_job_context(job_profile)
        optimized_experiences = []
        
        for exp in experiences:
            optimized_exp = deepcopy(exp)
            
            # Use unedited highlights if available, otherwise use current highlights
            highlights_to_optimize = exp.unedited if exp.unedited else exp.highlights
            
            if highlights_to_optimize:
                highlights_text = "\n".join([f"- {highlight}" for highlight in highlights_to_optimize])
                
                # Get prompt configuration
                prompt_text = self._get_prompt_text('experience')
                context = self._build_context_from_template('experience', highlights_text, job_profile)
                model_params = self._get_model_params('experience')
                
                logger.debug(f"Requesting AI customization for experience at {exp.company}")
                response = self.ai_client.customize_content_with_params(
                    prompt=prompt_text,
                    context=context,
                    model_params=model_params
                )
                
                if response.success:
                    # Parse the response back into a list of highlights
                    customized_highlights = []
                    for line in response.content.split('\n'):
                        line = line.strip()
                        if line.startswith('- '):
                            customized_highlights.append(line[2:])  # Remove '- ' prefix
                        elif line and not line.startswith('-'):
                            customized_highlights.append(line)
                    
                    if customized_highlights:
                        optimized_exp.highlights = customized_highlights
                        logger.info(f"Successfully optimized experience highlights for {exp.company}")
                    else:
                        logger.warning(f"AI returned empty highlights for {exp.company}, keeping original")
                else:
                    logger.warning(f"Failed to optimize experience for {exp.company}: {response.error_message}")
            
            optimized_experiences.append(optimized_exp)
        
        return optimized_experiences
    
    def adjust_skills(self, skills: List[SkillCategory], job_profile: JobProfile) -> List[SkillCategory]:
        """Adjust skills organization and emphasis for specific job profile.
        
        Args:
            skills: List of original skill categories
            job_profile: Job profile for customization context
            
        Returns:
            List of skill categories with adjusted organization
        """
        if not skills:
            return skills
        
        job_context = self._build_job_context(job_profile)
        
        # Convert skills to text format for AI processing
        skills_text = ""
        for skill_cat in skills:
            skills_text += f"{skill_cat.category}:\n"
            for skill in skill_cat.skills:
                skills_text += f"  - {skill}\n"
            skills_text += "\n"
        
        # Get prompt configuration
        prompt_text = self._get_prompt_text('skills')
        context = self._build_context_from_template('skills', skills_text.strip(), job_profile)
        model_params = self._get_model_params('skills')
        
        logger.debug("Requesting AI customization for skills organization")
        response = self.ai_client.customize_content_with_params(
            prompt=prompt_text,
            context=context,
            model_params=model_params
        )
        
        if response.success:
            # Parse the response back into skill categories
            adjusted_skills = self._parse_skills_response(response.content)
            if adjusted_skills:
                logger.info("Successfully adjusted skills organization")
                return adjusted_skills
            else:
                logger.warning("Failed to parse AI skills response, keeping original")
        else:
            logger.warning(f"Failed to adjust skills: {response.error_message}")
        
        return skills
    
    def optimize_projects(self, projects: List, job_profile: JobProfile) -> List:
        """Optimize project descriptions for specific job profile.
        
        Args:
            projects: List of original project entries
            job_profile: Job profile for customization context
            
        Returns:
            List of projects with optimized descriptions
        """
        if not projects:
            return projects
        
        # Convert projects to text format for AI processing
        projects_text = ""
        for i, project in enumerate(projects):
            projects_text += f"Project {i+1}:\n"
            projects_text += f"Name: {project.name}\n"
            if hasattr(project, 'subtitle') and project.subtitle:
                projects_text += f"Subtitle: {project.subtitle}\n"
            if hasattr(project, 'url') and project.url:
                projects_text += f"URL: {project.url}\n"
            projects_text += f"Description: {project.description}\n"
            if hasattr(project, 'technologies') and project.technologies:
                projects_text += f"Technologies: {', '.join(project.technologies)}\n"
            projects_text += "\n"
        
        # Get prompt configuration
        prompt_text = self._get_prompt_text('projects')
        context = self._build_context_from_template('projects', projects_text.strip(), job_profile)
        model_params = self._get_model_params('projects')
        
        logger.debug("Requesting AI customization for projects")
        response = self.ai_client.customize_content_with_params(
            prompt=prompt_text,
            context=context,
            model_params=model_params
        )
        
        if response.success:
            # Parse the response back into project objects
            optimized_projects = self._parse_projects_response(response.content, projects)
            if optimized_projects:
                logger.info("Successfully optimized project descriptions")
                return optimized_projects
            else:
                logger.warning("Failed to parse AI projects response, keeping original")
        else:
            logger.warning(f"Failed to optimize projects: {response.error_message}")
        
        return projects
    
    def _parse_projects_response(self, response_content: str, original_projects: List) -> Optional[List]:
        """Parse AI response back into project objects.
        
        Args:
            response_content: AI response containing formatted projects
            original_projects: Original project objects to preserve structure
            
        Returns:
            List of parsed project objects or None if parsing failed
        """
        try:
            from copy import deepcopy
            optimized_projects = deepcopy(original_projects)
            
            # Simple parsing - look for "Description:" lines and update them
            lines = response_content.split('\n')
            project_index = -1
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('Project ') and ':' in line:
                    # Extract project number
                    try:
                        project_num = int(line.split()[1].rstrip(':'))
                        project_index = project_num - 1
                    except (ValueError, IndexError):
                        continue
                
                elif line.startswith('Description:') and project_index >= 0 and project_index < len(optimized_projects):
                    # Extract new description
                    new_description = line[12:].strip()  # Remove "Description: "
                    if new_description:
                        optimized_projects[project_index].description = new_description
            
            return optimized_projects
            
        except Exception as e:
            logger.error(f"Failed to parse projects response: {str(e)}")
            return None
    
    def _build_job_context(self, job_profile: JobProfile) -> str:
        """Build job context string for AI prompts.
        
        Args:
            job_profile: Job profile to build context from
            
        Returns:
            Formatted job context string
        """
        return self.context_builder.build_job_context(job_profile)
    
    def _get_prompt_config(self, prompt_type: str) -> Optional[PromptConfig]:
        """Get prompt configuration for a specific type.
        
        Args:
            prompt_type: Type of prompt (e.g., 'summary', 'experience', 'skills')
            
        Returns:
            PromptConfig object or None if not available
        """
        if self._use_fallback_prompts:
            return None
        
        return self.prompt_loader.get_prompt(prompt_type)
    
    def _get_prompt_text(self, prompt_type: str) -> str:
        """Get prompt text for a specific type.
        
        Args:
            prompt_type: Type of prompt
            
        Returns:
            Prompt text (from config or fallback)
        """
        if not self._use_fallback_prompts:
            config = self._get_prompt_config(prompt_type)
            if config:
                return config.system_prompt
        
        return self._fallback_prompts.get(prompt_type, "")
    
    def _build_context_from_template(self, prompt_type: str, content: str, 
                                   job_profile: JobProfile, **kwargs) -> str:
        """Build context using prompt template with enhanced context builder.
        
        Args:
            prompt_type: Type of prompt
            content: Original content to customize
            job_profile: Job profile for context
            **kwargs: Additional context variables
            
        Returns:
            Formatted context string
        """
        if self._use_fallback_prompts:
            # Use enhanced context even for fallback
            job_context = self.context_builder.build_job_context(job_profile)
            return f"Job Context: {job_context}\n\nOriginal Content: {content}"
        
        config = self._get_prompt_config(prompt_type)
        if not config:
            # Fallback to enhanced context format
            job_context = self.context_builder.build_job_context(job_profile)
            return f"Job Context: {job_context}\n\nOriginal Content: {content}"
        
        # Build context variables using ContextBuilder
        context_vars = self.context_builder.build_context_variables(
            prompt_type, content, job_profile, **kwargs
        )
        
        try:
            formatted_context = config.context_template.format(**context_vars)
            logger.debug(f"Successfully built context for {prompt_type} prompt")
            return formatted_context
        except KeyError as e:
            logger.warning(f"Missing context variable {e} for prompt {prompt_type}, using fallback")
            job_context = self.context_builder.build_job_context(job_profile)
            return f"Job Context: {job_context}\n\nOriginal Content: {content}"
        except Exception as e:
            logger.error(f"Error formatting context template for {prompt_type}: {str(e)}")
            job_context = self.context_builder.build_job_context(job_profile)
            return f"Job Context: {job_context}\n\nOriginal Content: {content}"
    

    
    def _get_model_params(self, prompt_type: str) -> Dict[str, Any]:
        """Get model parameters for a specific prompt type.
        
        Args:
            prompt_type: Type of prompt
            
        Returns:
            Dictionary of model parameters
        """
        if not self._use_fallback_prompts:
            config = self._get_prompt_config(prompt_type)
            if config:
                return config.model_params
        
        # Return default parameters for fallback
        return {
            "model": "gpt-4o-mini",
            "max_tokens": 1000,
            "temperature": 0.7
        }
    
    def _parse_skills_response(self, response_content: str) -> Optional[List[SkillCategory]]:
        """Parse AI response back into skill categories.
        
        Args:
            response_content: AI response containing formatted skills
            
        Returns:
            List of parsed skill categories or None if parsing failed
        """
        try:
            skills = []
            current_category = None
            current_skills = []
            
            for line in response_content.split('\n'):
                line = line.strip()
                
                if not line:
                    continue
                
                # Check if this is a category header (ends with colon)
                if line.endswith(':') and not line.startswith('-'):
                    # Save previous category if exists
                    if current_category and current_skills:
                        skills.append(SkillCategory(category=current_category, skills=current_skills))
                    
                    # Start new category
                    current_category = line[:-1].strip()
                    current_skills = []
                
                # Check if this is a skill item (starts with dash or bullet)
                elif line.startswith('- ') or line.startswith('• '):
                    skill = line[2:].strip()
                    if skill:
                        current_skills.append(skill)
                elif line.startswith('  - '):
                    skill = line[4:].strip()
                    if skill:
                        current_skills.append(skill)
            
            # Add the last category
            if current_category and current_skills:
                skills.append(SkillCategory(category=current_category, skills=current_skills))
            
            return skills if skills else None
            
        except Exception as e:
            logger.error(f"Failed to parse skills response: {str(e)}")
            return None