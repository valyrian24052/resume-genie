"""Main resume builder application logic."""

from pathlib import Path
from typing import Optional

from core.yaml_processor import YAMLProcessor
from core.latex_generator import LaTeXGenerator
from core.pdf_compiler import PDFCompiler
from ai.ai_client import AIClient
from ai.customization_engine import CustomizationEngine
from models.job_profile import JobProfile
from models.resume_data import ResumeData
from .config import DEFAULT_RESUME_FILE, DEFAULT_TEMPLATE, OUTPUT_DIR


class ResumeBuilder:
    """Main resume builder class."""
    
    def __init__(self, resume_file: Optional[Path] = None, template: str = DEFAULT_TEMPLATE):
        """Initialize resume builder.
        
        Args:
            resume_file: Path to resume YAML file (defaults to your personal resume)
            template: LaTeX template name to use
        """
        self.resume_file = resume_file or DEFAULT_RESUME_FILE
        self.template = template
        self.yaml_processor = YAMLProcessor()
        self.latex_generator = LaTeXGenerator("templates")
        self.pdf_compiler = PDFCompiler()
    
    def load_resume(self) -> ResumeData:
        """Load resume data from YAML file."""
        return self.yaml_processor.load_resume(str(self.resume_file))
    
    def customize_resume(self, job_post: str, api_key: str) -> ResumeData:
        """Customize resume for a job posting using AI.
        
        Args:
            job_post: Complete job posting text
            api_key: OpenAI API key
            
        Returns:
            Customized resume data
        """
        # Load base resume
        resume_data = self.load_resume()
        
        # Create job profile from job post
        job_profile = JobProfile(
            title="Job Application",
            company="Target Company",
            description=job_post,
            requirements=[],
            preferred_skills=[],
            industry="",
            experience_level=""
        )
        
        # Customize with AI if API key provided
        if api_key.strip():
            try:
                ai_client = AIClient(api_key=api_key)
                customization_engine = CustomizationEngine(ai_client)
                resume_data = customization_engine.customize_for_job(resume_data, job_profile)
            except Exception as e:
                print(f"AI customization failed: {e}")
                # Return original resume if AI fails
        
        return resume_data
    
    def generate_pdf(self, resume_data: ResumeData, output_filename: str) -> Path:
        """Generate PDF from resume data.
        
        Args:
            resume_data: Resume data to generate PDF from
            output_filename: Name of output PDF file
            
        Returns:
            Path to generated PDF file
            
        Raises:
            Exception: If PDF generation fails
        """
        output_path = OUTPUT_DIR / output_filename
        
        # Generate LaTeX content
        latex_content = self.latex_generator.generate_latex(resume_data, self.template)
        
        # Compile to PDF
        result = self.pdf_compiler.compile_to_pdf(latex_content, output_path)
        
        if not result.success or not output_path.exists():
            raise Exception(f"PDF generation failed: {result.error_message}")
        
        return output_path