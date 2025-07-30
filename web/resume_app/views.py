"""Views for resume customization web interface."""

import os
import uuid
import logging
from pathlib import Path
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.conf import settings

from .forms import JobCustomizationForm
from app.resume_builder import ResumeBuilder

logger = logging.getLogger(__name__)


def index(request):
    """Main page with job customization form."""
    form = JobCustomizationForm()
    return render(request, 'resume_app/index.html', {'form': form})


def generate_resume(request):
    """Generate resume directly without AI customization."""
    if request.method != 'POST':
        return redirect('resume_app:index')
    
    form = JobCustomizationForm(request.POST)
    if not form.is_valid():
        return render(request, 'resume_app/index.html', {'form': form})
    
    try:
        # Initialize resume builder
        resume_builder = ResumeBuilder()
        
        # Load resume data directly (no AI customization)
        resume_data = resume_builder.load_resume()
        
        # Generate PDF
        filename = f"resume_{uuid.uuid4().hex[:8]}.pdf"
        output_path = resume_builder.generate_pdf(resume_data, filename)
        
        messages.success(request, 'Resume generated successfully!')
        
        # Simple response - direct download
        return render(request, 'resume_app/preview.html', {
            'filename': filename,
            'download_url': f'/download/{filename}/'
        })
            
    except Exception as e:
        logger.error(f"Resume generation failed: {str(e)}")
        messages.error(request, f'Resume generation failed: {str(e)}')
        return render(request, 'resume_app/index.html', {'form': form})


def download_resume(request, filename):
    """Download generated resume PDF."""
    file_path = settings.RESUME_OUTPUT_DIR / filename
    
    if not file_path.exists():
        raise Http404("Resume file not found")
    
    try:
        with open(file_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    except Exception as e:
        logger.error(f"Failed to serve file {filename}: {str(e)}")
        raise Http404("Error serving file")


def create_sample_resume():
    """Create a sample resume YAML file for demonstration."""
    sample_data = """basic:
  name: "John Doe"
  address:
    - "123 Main Street"
    - "San Francisco, CA 94105"
  contact:
    email: "john.doe@email.com"
    phone: "+1 (555) 123-4567"
  websites:
    - text: "LinkedIn"
      url: "https://linkedin.com/in/johndoe"
    - text: "GitHub"
      url: "https://github.com/johndoe"

summary: "Experienced software engineer with 5+ years developing scalable web applications and leading cross-functional teams. Passionate about clean code, system architecture, and mentoring junior developers."

experiences:
  - company: "Tech Solutions Inc."
    titles:
      - name: "Senior Software Engineer"
        startdate: "2021"
        enddate: "Present"
      - name: "Software Engineer"
        startdate: "2019"
        enddate: "2021"
    highlights:
      - "Led development of microservices architecture serving 1M+ daily users"
      - "Mentored 3 junior developers and improved team code review process"
      - "Reduced application response time by 40% through database optimization"
      - "Implemented CI/CD pipeline reducing deployment time from 2 hours to 15 minutes"
    unedited:
      - "Built and maintained scalable web applications using modern frameworks"
      - "Collaborated with product and design teams on feature development"
      - "Optimized database queries and improved application performance"
      - "Set up automated testing and deployment processes"

  - company: "StartupCorp"
    titles:
      - name: "Full Stack Developer"
        startdate: "2018"
        enddate: "2019"
    highlights:
      - "Developed MVP for B2B SaaS platform from concept to launch"
      - "Built responsive frontend using React and modern CSS frameworks"
      - "Designed and implemented RESTful APIs with comprehensive documentation"
    unedited:
      - "Created full-stack web applications for early-stage startup"
      - "Worked directly with founders on product strategy and technical decisions"
      - "Built user interfaces and backend services"

education:
  - school: "University of California, Berkeley"
    degrees:
      - names: ["Bachelor of Science in Computer Science"]
        startdate: "2014"
        enddate: "2018"
        gpa: 3.7
    achievements:
      - "Dean's List (Fall 2016, Spring 2017)"
      - "Computer Science Honor Society"

projects:
  - "Open source contributor to popular Python web framework (500+ GitHub stars)"
  - "Personal finance tracking app with 10K+ downloads on mobile app stores"
  - "Machine learning model for stock price prediction (published research paper)"

skills:
  - category: "Programming Languages"
    skills: ["Python", "JavaScript", "TypeScript", "Java", "Go"]
  - category: "Web Frameworks"
    skills: ["Django", "Flask", "React", "Node.js", "Express"]
  - category: "Databases"
    skills: ["PostgreSQL", "MongoDB", "Redis", "Elasticsearch"]
  - category: "Cloud & DevOps"
    skills: ["AWS", "Docker", "Kubernetes", "Jenkins", "Terraform"]
  - category: "Tools & Technologies"
    skills: ["Git", "Linux", "REST APIs", "GraphQL", "Microservices"]
"""
    
    # Ensure data directory exists
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Write sample resume
    with open(data_dir / 'sample_resume.yaml', 'w') as f:
        f.write(sample_data)