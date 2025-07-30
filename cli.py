#!/usr/bin/env python3
"""Command line interface for the resume builder."""

import argparse
import sys
from pathlib import Path

from app.resume_builder import ResumeBuilder


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="AI Resume Builder CLI")
    parser.add_argument("--output", "-o", default="resume.pdf", help="Output PDF filename")
    parser.add_argument("--template", "-t", default="resume", help="LaTeX template to use")
    parser.add_argument("--data", "-d", help="Custom YAML data file (default: data/resume.yaml)")
    
    args = parser.parse_args()
    
    try:
        # Initialize resume builder
        resume_file = Path(args.data) if args.data else None
        resume_builder = ResumeBuilder(resume_file=resume_file, template=args.template)
        
        print("Loading resume data...")
        resume_data = resume_builder.load_resume()
        
        print("Generating LaTeX content...")
        latex_content = resume_builder.latex_generator.generate_latex(resume_data, args.template)
        
        # Save LaTeX content to file for inspection
        latex_file = args.output.replace('.pdf', '.tex')
        with open(latex_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        print(f"LaTeX content saved to: {latex_file}")
        
        print("Generating PDF...")
        output_path = resume_builder.generate_pdf(resume_data, args.output)
        
        print(f"✅ Resume generated successfully: {output_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()