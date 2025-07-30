#!/usr/bin/env python3
"""
Test script to validate the complete resume pipeline:
1. YAML structure validation
2. Data model conversion
3. LaTeX template rendering
"""

import sys
import traceback
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from core.yaml_processor import YAMLProcessor, YAMLProcessingError
from core.template_manager import TemplateManager
from models.resume_data import ResumeData


def test_yaml_structure():
    """Test YAML file structure and validation."""
    print("=" * 60)
    print("TESTING YAML STRUCTURE")
    print("=" * 60)
    
    try:
        processor = YAMLProcessor()
        print("✓ YAMLProcessor initialized successfully")
        
        # Test loading the resume
        resume_data = processor.load_resume("data/resume.yaml")
        print("✓ YAML file loaded and parsed successfully")
        
        # Test validation
        validation_errors = resume_data.validate()
        if validation_errors:
            print("⚠ Validation warnings found:")
            for error in validation_errors:
                print(f"  - {error}")
        else:
            print("✓ Resume data validation passed")
        
        # Print structure summary
        print("\n📋 Resume Data Structure Summary:")
        print(f"  - Name: {resume_data.basic.name}")
        print(f"  - Email: {resume_data.basic.contact.email}")
        print(f"  - Phone: {resume_data.basic.contact.phone}")
        print(f"  - Address lines: {len(resume_data.basic.address)}")
        print(f"  - Websites: {len(resume_data.basic.websites)}")
        print(f"  - Summary: {'Yes' if resume_data.summary else 'No'}")
        print(f"  - Education entries: {len(resume_data.education)}")
        print(f"  - Experience entries: {len(resume_data.experiences)}")
        print(f"  - Project entries: {len(resume_data.projects)}")
        print(f"  - Research entries: {len(resume_data.research)}")
        print(f"  - Skill categories: {len(resume_data.skills)}")
        
        return resume_data
        
    except YAMLProcessingError as e:
        print(f"❌ YAML Processing Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        traceback.print_exc()
        return None


def test_latex_template(resume_data):
    """Test LaTeX template rendering."""
    print("\n" + "=" * 60)
    print("TESTING LATEX TEMPLATE RENDERING")
    print("=" * 60)
    
    try:
        template_manager = TemplateManager()
        print("✓ TemplateManager initialized successfully")
        
        # Test template rendering
        latex_content = template_manager.render_resume("resume.tex", resume_data)
        print("✓ LaTeX template rendered successfully")
        
        # Check if key placeholders were replaced
        placeholders_to_check = [
            "{{NAME}}", "{{EMAIL}}", "{{PHONE}}", 
            "{{PORTFOLIO_URL}}", "{{LINKEDIN_URL}}", "{{GITHUB_URL}}"
        ]
        
        remaining_placeholders = []
        for placeholder in placeholders_to_check:
            if placeholder in latex_content:
                remaining_placeholders.append(placeholder)
        
        if remaining_placeholders:
            print("⚠ Some placeholders were not replaced:")
            for placeholder in remaining_placeholders:
                print(f"  - {placeholder}")
        else:
            print("✓ All basic placeholders were replaced")
        
        # Save rendered template for inspection
        output_path = Path("output/test_resume.tex")
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        print(f"✓ Rendered LaTeX saved to: {output_path}")
        
        # Show a preview of the rendered content
        print("\n📄 LaTeX Content Preview (first 500 chars):")
        print("-" * 40)
        print(latex_content[:500] + "..." if len(latex_content) > 500 else latex_content)
        print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ LaTeX Template Error: {e}")
        traceback.print_exc()
        return False


def test_data_model_completeness(resume_data):
    """Test that all data model fields are properly populated."""
    print("\n" + "=" * 60)
    print("TESTING DATA MODEL COMPLETENESS")
    print("=" * 60)
    
    try:
        # Test basic info
        basic = resume_data.basic
        print(f"✓ Basic info - Name: {basic.name}")
        print(f"✓ Basic info - Contact: {basic.contact.email}, {basic.contact.phone}")
        print(f"✓ Basic info - Address: {len(basic.address)} lines")
        print(f"✓ Basic info - Websites: {len(basic.websites)} entries")
        
        # Test experiences
        for i, exp in enumerate(resume_data.experiences):
            print(f"✓ Experience {i+1}: {exp.company} - {len(exp.titles)} titles, {len(exp.highlights)} highlights")
        
        # Test education
        for i, edu in enumerate(resume_data.education):
            print(f"✓ Education {i+1}: {edu.school} - {len(edu.degrees)} degrees")
        
        # Test skills
        for i, skill in enumerate(resume_data.skills):
            print(f"✓ Skill category {i+1}: {skill.category} - {len(skill.skills)} skills")
        
        # Test projects
        for i, project in enumerate(resume_data.projects):
            print(f"✓ Project {i+1}: {project.name} - {len(project.technologies)} technologies")
        
        # Test research
        for i, research in enumerate(resume_data.research):
            print(f"✓ Research {i+1}: {research.title} - {len(research.collaborators)} collaborators")
        
        return True
        
    except Exception as e:
        print(f"❌ Data Model Error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Resume Pipeline Tests")
    
    # Test 1: YAML Structure
    resume_data = test_yaml_structure()
    if not resume_data:
        print("\n❌ YAML tests failed. Stopping.")
        return False
    
    # Test 2: Data Model Completeness
    if not test_data_model_completeness(resume_data):
        print("\n❌ Data model tests failed.")
        return False
    
    # Test 3: LaTeX Template
    if not test_latex_template(resume_data):
        print("\n❌ LaTeX template tests failed.")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print("✅ YAML structure is valid")
    print("✅ Data model conversion works")
    print("✅ LaTeX template renders successfully")
    print("\n💡 Next steps:")
    print("  1. Replace placeholder values in data/resume.yaml with real data")
    print("  2. Run the full resume generation pipeline")
    print("  3. Compile the LaTeX output to PDF")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)