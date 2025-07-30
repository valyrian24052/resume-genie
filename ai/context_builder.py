"""Context builder for creating rich AI prompt context from user data."""

import logging
from typing import Dict, Any, List, Optional
from models.resume_data import ResumeData, Experience, ProjectData, ResearchData, SkillCategory
from models.job_profile import JobProfile


logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builder for creating rich context from user's full background for AI prompts."""
    
    def __init__(self, resume_data: Optional[ResumeData] = None):
        """Initialize context builder with resume data.
        
        Args:
            resume_data: User's resume data for context building
        """
        self.resume_data = resume_data
    
    def set_resume_data(self, resume_data: ResumeData):
        """Set or update the resume data.
        
        Args:
            resume_data: User's resume data
        """
        self.resume_data = resume_data
    
    def build_experiences_summary(self, job_profile: Optional[JobProfile] = None) -> str:
        """Build a comprehensive summary of user experiences.
        
        Args:
            job_profile: Optional job profile for relevance filtering
            
        Returns:
            Formatted summary of experiences
        """
        if not self.resume_data or not self.resume_data.experiences:
            return "No professional experience listed"
        
        summary_parts = []
        
        for exp in self.resume_data.experiences:
            # Get the most recent or relevant title
            if exp.titles:
                latest_title = exp.titles[-1]  # Assuming titles are in chronological order
                title_info = f"{latest_title.name} at {exp.company}"
                
                # Add date range if available
                if latest_title.startdate and latest_title.enddate:
                    title_info += f" ({latest_title.startdate} - {latest_title.enddate})"
            else:
                title_info = f"Position at {exp.company}"
            
            # Add key highlights (limit to top 2-3 for summary)
            highlights = exp.highlights[:3] if exp.highlights else []
            if highlights:
                highlights_text = "; ".join(highlights)
                summary_parts.append(f"{title_info}: {highlights_text}")
            else:
                summary_parts.append(title_info)
        
        return " | ".join(summary_parts)
    
    def build_projects_summary(self, job_profile: Optional[JobProfile] = None) -> str:
        """Build a comprehensive summary of user projects.
        
        Args:
            job_profile: Optional job profile for relevance filtering
            
        Returns:
            Formatted summary of projects
        """
        if not self.resume_data or not self.resume_data.projects:
            return "No projects listed"
        
        project_summaries = []
        
        for project in self.resume_data.projects:
            project_info = project.name
            
            # Add subtitle if available
            if project.subtitle:
                project_info += f" ({project.subtitle})"
            
            # Add key technologies (limit to top 3)
            if project.technologies:
                tech_list = project.technologies[:3]
                tech_str = ", ".join(tech_list)
                if len(project.technologies) > 3:
                    tech_str += f" and {len(project.technologies) - 3} more"
                project_info += f" - Technologies: {tech_str}"
            
            # Add brief description (truncated)
            if project.description:
                desc = project.description[:100] + "..." if len(project.description) > 100 else project.description
                project_info += f" - {desc}"
            
            project_summaries.append(project_info)
        
        return " | ".join(project_summaries)
    
    def build_skills_summary(self, job_profile: Optional[JobProfile] = None) -> str:
        """Build a comprehensive summary of user skills.
        
        Args:
            job_profile: Optional job profile for relevance filtering
            
        Returns:
            Formatted summary of skills
        """
        if not self.resume_data or not self.resume_data.skills:
            return "No skills listed"
        
        skill_summaries = []
        
        for skill_cat in self.resume_data.skills:
            # Limit skills per category for summary
            skills_list = skill_cat.skills[:5]  # Top 5 skills per category
            skills_str = ", ".join(skills_list)
            if len(skill_cat.skills) > 5:
                skills_str += f" and {len(skill_cat.skills) - 5} more"
            
            skill_summaries.append(f"{skill_cat.category}: {skills_str}")
        
        return " | ".join(skill_summaries)
    
    def build_research_summary(self, job_profile: Optional[JobProfile] = None) -> str:
        """Build a comprehensive summary of user research.
        
        Args:
            job_profile: Optional job profile for relevance filtering
            
        Returns:
            Formatted summary of research
        """
        if not self.resume_data or not self.resume_data.research:
            return "No research experience listed"
        
        research_summaries = []
        
        for research in self.resume_data.research:
            research_info = research.title
            
            # Add publication date if available
            if research.publication_date:
                research_info += f" ({research.publication_date})"
            
            # Add brief description (truncated)
            if research.description:
                desc = research.description[:80] + "..." if len(research.description) > 80 else research.description
                research_info += f" - {desc}"
            
            # Add keywords if available (limit to top 3)
            if research.keywords:
                keywords = research.keywords[:3]
                research_info += f" - Keywords: {', '.join(keywords)}"
            
            research_summaries.append(research_info)
        
        return " | ".join(research_summaries)
    
    def build_education_summary(self) -> str:
        """Build a summary of user education.
        
        Returns:
            Formatted summary of education
        """
        if not self.resume_data or not self.resume_data.education:
            return "No education listed"
        
        education_summaries = []
        
        for edu in self.resume_data.education:
            edu_info = edu.school
            
            # Add degree information
            if edu.degrees:
                degree_names = []
                for degree in edu.degrees:
                    if degree.names:
                        degree_names.extend(degree.names)
                
                if degree_names:
                    edu_info += f" - {', '.join(degree_names)}"
            
            education_summaries.append(edu_info)
        
        return " | ".join(education_summaries)
    
    def build_full_user_context(self, job_profile: Optional[JobProfile] = None) -> str:
        """Build comprehensive user context for AI prompts.
        
        Args:
            job_profile: Optional job profile for relevance filtering
            
        Returns:
            Complete user context string
        """
        if not self.resume_data:
            return "No resume data available"
        
        context_parts = []
        
        # Basic information
        if self.resume_data.basic:
            context_parts.append(f"Name: {self.resume_data.basic.name}")
        
        # Education summary
        education_summary = self.build_education_summary()
        context_parts.append(f"Education: {education_summary}")
        
        # Experience summary
        experience_summary = self.build_experiences_summary(job_profile)
        context_parts.append(f"Experience: {experience_summary}")
        
        # Projects summary
        projects_summary = self.build_projects_summary(job_profile)
        context_parts.append(f"Projects: {projects_summary}")
        
        # Skills summary
        skills_summary = self.build_skills_summary(job_profile)
        context_parts.append(f"Skills: {skills_summary}")
        
        # Research summary (if available)
        if self.resume_data.research:
            research_summary = self.build_research_summary(job_profile)
            context_parts.append(f"Research: {research_summary}")
        
        # Current summary (if available)
        if self.resume_data.summary:
            context_parts.append(f"Current Summary: {self.resume_data.summary}")
        
        return "\n".join(context_parts)
    
    def extract_target_skills_from_job(self, job_profile: JobProfile) -> str:
        """Extract and format target skills from job profile.
        
        Args:
            job_profile: Job profile to extract skills from
            
        Returns:
            Formatted target skills string
        """
        skills = []
        
        if job_profile.requirements:
            skills.extend(job_profile.requirements)
        
        if job_profile.preferred_skills:
            skills.extend(job_profile.preferred_skills)
        
        # Remove duplicates while preserving order
        unique_skills = []
        seen = set()
        for skill in skills:
            if skill.lower() not in seen:
                unique_skills.append(skill)
                seen.add(skill.lower())
        
        return ", ".join(unique_skills) if unique_skills else "No specific skills mentioned in job posting"
    
    def build_job_context(self, job_profile: JobProfile) -> str:
        """Build comprehensive job context string.
        
        Args:
            job_profile: Job profile to build context from
            
        Returns:
            Formatted job context string
        """
        context_parts = [
            f"Job Title: {job_profile.title}",
            f"Company: {job_profile.company}",
            f"Description: {job_profile.description}"
        ]
        
        if job_profile.requirements:
            context_parts.append(f"Requirements: {', '.join(job_profile.requirements)}")
        
        if job_profile.preferred_skills:
            context_parts.append(f"Preferred Skills: {', '.join(job_profile.preferred_skills)}")
        
        if job_profile.industry:
            context_parts.append(f"Industry: {job_profile.industry}")
        
        if job_profile.experience_level:
            context_parts.append(f"Experience Level: {job_profile.experience_level}")
        
        return "\n".join(context_parts)
    
    def build_context_variables(self, prompt_type: str, content: str, 
                              job_profile: JobProfile, **kwargs) -> Dict[str, str]:
        """Build context variables for prompt templates.
        
        Args:
            prompt_type: Type of prompt (summary, experience, skills)
            content: Original content to customize
            job_profile: Job profile for context
            **kwargs: Additional context variables
            
        Returns:
            Dictionary of context variables for template formatting
        """
        # Base context variables
        context_vars = {
            'job_context': self.build_job_context(job_profile),
            'content': content,
            **kwargs
        }
        
        # Add prompt-specific context variables
        if prompt_type == 'summary':
            context_vars.update({
                'experiences_summary': self.build_experiences_summary(job_profile),
                'projects_summary': self.build_projects_summary(job_profile),
                'skills_summary': self.build_skills_summary(job_profile),
                'education_summary': self.build_education_summary()
            })
            
            # Add research summary if available
            if self.resume_data and self.resume_data.research:
                context_vars['research_summary'] = self.build_research_summary(job_profile)
        
        elif prompt_type == 'experience':
            context_vars.update({
                'full_context': self.build_full_user_context(job_profile),
                'target_skills': self.extract_target_skills_from_job(job_profile)
            })
        
        elif prompt_type == 'skills':
            context_vars.update({
                'target_skills': self.extract_target_skills_from_job(job_profile),
                'user_experience_level': self._infer_experience_level(),
                'relevant_projects': self._get_relevant_projects_for_skills(job_profile)
            })
        
        elif prompt_type == 'projects':
            context_vars.update({
                'target_skills': self.extract_target_skills_from_job(job_profile),
                'technical_background': self._build_technical_background()
            })
        
        return context_vars
    
    def _infer_experience_level(self) -> str:
        """Infer user's experience level from resume data.
        
        Returns:
            Inferred experience level string
        """
        if not self.resume_data or not self.resume_data.experiences:
            return "Entry level"
        
        # Simple heuristic based on number of experiences and highlights
        total_experiences = len(self.resume_data.experiences)
        total_highlights = sum(len(exp.highlights) for exp in self.resume_data.experiences)
        
        # Also consider job titles for seniority indicators
        senior_indicators = ['senior', 'lead', 'principal', 'architect', 'manager', 'director']
        has_senior_title = any(
            any(indicator in title.name.lower() for indicator in senior_indicators)
            for exp in self.resume_data.experiences
            for title in exp.titles
        )
        
        if (total_experiences >= 2 and total_highlights >= 6) or has_senior_title:
            return "Senior level"
        elif total_experiences >= 2 and total_highlights >= 4:
            return "Mid level"
        else:
            return "Entry to mid level"
    
    def _get_relevant_projects_for_skills(self, job_profile: JobProfile) -> str:
        """Get projects relevant to job skills.
        
        Args:
            job_profile: Job profile to match against
            
        Returns:
            String describing relevant projects
        """
        if not self.resume_data or not self.resume_data.projects:
            return "No projects available"
        
        # Extract job-related keywords
        job_keywords = set()
        if job_profile.requirements:
            job_keywords.update(word.lower() for req in job_profile.requirements for word in req.split())
        if job_profile.preferred_skills:
            job_keywords.update(word.lower() for skill in job_profile.preferred_skills for word in skill.split())
        
        relevant_projects = []
        
        for project in self.resume_data.projects:
            # Check if project technologies or description match job keywords
            project_text = f"{project.name} {project.description} {' '.join(project.technologies)}".lower()
            
            if any(keyword in project_text for keyword in job_keywords):
                relevant_projects.append(f"{project.name} ({', '.join(project.technologies[:3])})")
        
        if relevant_projects:
            return f"Relevant projects: {', '.join(relevant_projects[:3])}"
        else:
            return f"Projects: {', '.join([p.name for p in self.resume_data.projects[:3]])}"
    
    def _build_technical_background(self) -> str:
        """Build technical background summary for project customization.
        
        Returns:
            String describing technical background
        """
        if not self.resume_data:
            return "No technical background available"
        
        background_parts = []
        
        # Add technical skills
        if self.resume_data.skills:
            tech_skills = []
            for skill_cat in self.resume_data.skills:
                if any(keyword in skill_cat.category.lower() 
                      for keyword in ['programming', 'technical', 'language', 'framework', 'tool']):
                    tech_skills.extend(skill_cat.skills[:3])  # Top 3 from each relevant category
            
            if tech_skills:
                background_parts.append(f"Technical Skills: {', '.join(tech_skills[:8])}")  # Limit total
        
        # Add experience with technical focus
        if self.resume_data.experiences:
            tech_experience = []
            for exp in self.resume_data.experiences:
                # Look for technical highlights
                tech_highlights = [h for h in exp.highlights 
                                 if any(keyword in h.lower() 
                                       for keyword in ['developed', 'built', 'implemented', 'designed', 
                                                     'programmed', 'coded', 'architected'])]
                if tech_highlights:
                    tech_experience.append(f"{exp.company}: {tech_highlights[0][:50]}...")
            
            if tech_experience:
                background_parts.append(f"Technical Experience: {' | '.join(tech_experience[:2])}")
        
        # Add project technologies
        if self.resume_data.projects:
            all_technologies = []
            for project in self.resume_data.projects:
                all_technologies.extend(project.technologies)
            
            # Remove duplicates and limit
            unique_tech = list(dict.fromkeys(all_technologies))[:10]
            if unique_tech:
                background_parts.append(f"Project Technologies: {', '.join(unique_tech)}")
        
        return " | ".join(background_parts) if background_parts else "General technical background"