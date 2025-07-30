#!/usr/bin/env python3
"""Utility script to convert existing personal data to anonymous templates."""

import yaml
import re
import argparse
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add the parent directory to the path so we can import from core
sys.path.append(str(Path(__file__).parent.parent))

from core.personal_data_scanner import PersonalDataScanner


class DataAnonymizer:
    """Converts personal resume data to anonymous templates."""
    
    def __init__(self):
        """Initialize the anonymizer with replacement patterns."""
        self.scanner = PersonalDataScanner()
        
        # Mapping of personal data to anonymous placeholders
        self.replacements = {
            # Names and identifiers
            r'\bShashank\s+Sharma\b': '[Your Full Name]',
            r'\bShashank\b': '[Your First Name]',
            r'\bSharma\b': '[Your Last Name]',
            r'\bvalyrian24052\b': '[YourUsername]',
            r'\bValyrian\b': '[YourUsername]',
            r'\bshashanksharma1214\b': '[yourprofile]',
            
            # Contact information
            r'\bShashanksharma\.1214@gmail\.com\b': '[your.email@domain.com]',
            r'\+91-8905253958': '[+1-XXX-XXX-XXXX]',
            
            # URLs and profiles
            r'https://Shashank\.website': '[https://yourportfolio.com]',
            r'https://www\.linkedin\.com/in/shashanksharma1214/': '[https://linkedin.com/in/yourprofile]',
            r'https://github\.com/valyrian24052': '[https://github.com/yourusername]',
            r'https://driftio\.vercel\.app': '[https://project-url.com]',
            r'https://dosevisor\.vercel\.app/': '[https://project-url.com]',
            
            # Educational institutions
            r'\bNational Institute of Technology\b': '[University Name]',
            r'\bKurukshetra, India\b': '[City, State/Country]',
            r'\bBachelor of Technology - Electrical Engineering\b': '[Degree Type] - [Field of Study]',
            r'\b8\.5\b': '[X.X]',
            r'\bJuly 2020 - May 2024\b': '[Start Date] - [End Date]',
            
            # Companies
            r'\bZS Associates\b': '[Company Name 1]',
            r'\bMrikal Studios\b': '[Company Name 2]',
            r'\bMegaminds Technologies\b': '[Company Name 3]',
            r'\bShopup\b': '[Company Name 4]',
            r'\bEcho\b': '[Company Name 5]',
            
            # Locations
            r'\bGurgaon\b': '[City, State]',
            r'\bRemote\b': '[City, State/Remote]',
            
            # Project names
            r'\bDriotio\b': '[Project Name 1]',
            r'\bDoseVisor\b': '[Project Name 2]',
            
            # Specific technical details that might be too identifying
            r'\bData Structures, Artificial Intelligence, Machine Learning, Advanced Topics in Finance\b': '[Relevant Coursework]',
        }
        
        # Generic patterns for common personal data
        self.generic_patterns = {
            # Email pattern
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': '[your.email@domain.com]',
            # Phone pattern
            r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}': '[+1-XXX-XXX-XXXX]',
            # URL pattern (be careful not to replace placeholder URLs)
            r'https?://(?!.*\[)(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?': '[https://project-url.com]',
        }
    
    def anonymize_text(self, text: str) -> str:
        """Apply anonymization replacements to text."""
        if not text:
            return text
        
        result = text
        
        # Apply specific replacements first
        for pattern, replacement in self.replacements.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Apply generic patterns (but skip if already anonymized)
        for pattern, replacement in self.generic_patterns.items():
            # Don't replace if it's already a placeholder
            if not re.search(r'\[.*?\]', result):
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def anonymize_data_structure(self, data: Any) -> Any:
        """Recursively anonymize a data structure."""
        if isinstance(data, dict):
            return {key: self.anonymize_data_structure(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.anonymize_data_structure(item) for item in data]
        elif isinstance(data, str):
            return self.anonymize_text(data)
        else:
            return data
    
    def anonymize_yaml_file(self, input_path: str, output_path: str = None, backup: bool = True) -> bool:
        """
        Anonymize a YAML file.
        
        Args:
            input_path: Path to the input YAML file
            output_path: Path for the output file (defaults to input_path with _anonymous suffix)
            backup: Whether to create a backup of the original file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            input_file = Path(input_path)
            
            if not input_file.exists():
                print(f"❌ Input file not found: {input_path}")
                return False
            
            # Create backup if requested
            if backup:
                backup_path = input_file.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')
                shutil.copy2(input_file, backup_path)
                print(f"📁 Backup created: {backup_path}")
            
            # Load the YAML data
            with open(input_file, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            
            # Anonymize the data
            anonymized_data = self.anonymize_data_structure(data)
            
            # Determine output path
            if output_path is None:
                output_path = input_file.with_stem(f"{input_file.stem}_anonymous")
            
            # Write the anonymized data
            with open(output_path, 'w', encoding='utf-8') as file:
                yaml.dump(anonymized_data, file, default_flow_style=False, allow_unicode=True, indent=2)
            
            print(f"✅ Anonymized file created: {output_path}")
            
            # Scan the result to verify anonymization
            findings = self.scanner.scan_yaml_file(str(output_path))
            issues = [f for f in findings if f.get('type') != 'error']
            
            if issues:
                print(f"⚠️  Warning: {len(issues)} potential personal data items still detected:")
                for issue in issues[:5]:  # Show first 5 issues
                    print(f"   • {issue['description']}: {issue['value']}")
                if len(issues) > 5:
                    print(f"   ... and {len(issues) - 5} more")
            else:
                print("✅ Anonymization verification passed!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error anonymizing file: {e}")
            return False
    
    def scan_and_report(self, file_path: str) -> None:
        """Scan a file and generate a detailed report."""
        print(f"🔍 Scanning {file_path} for personal data...")
        findings = self.scanner.scan_yaml_file(file_path)
        report = self.scanner.generate_report(findings)
        print(report)


def main():
    """Main function for the anonymization script."""
    parser = argparse.ArgumentParser(description='Anonymize personal data in YAML resume files')
    parser.add_argument('input_file', help='Path to the input YAML file')
    parser.add_argument('-o', '--output', help='Path for the output file')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup of original file')
    parser.add_argument('--scan-only', action='store_true', help='Only scan for personal data, do not anonymize')
    parser.add_argument('--verify', help='Verify that a file is properly anonymized')
    
    args = parser.parse_args()
    
    anonymizer = DataAnonymizer()
    
    if args.verify:
        print(f"🔍 Verifying anonymization of {args.verify}...")
        is_anonymous, issues = anonymizer.scanner.is_anonymized(args.verify)
        if is_anonymous:
            print("✅ File is properly anonymized!")
        else:
            print(f"❌ File contains {len(issues)} personal data items:")
            for issue in issues:
                print(f"   • {issue}")
        return
    
    if args.scan_only:
        anonymizer.scan_and_report(args.input_file)
        return
    
    # Perform anonymization
    success = anonymizer.anonymize_yaml_file(
        args.input_file,
        args.output,
        backup=not args.no_backup
    )
    
    if success:
        print("🎉 Anonymization completed successfully!")
    else:
        print("❌ Anonymization failed!")
        exit(1)


if __name__ == '__main__':
    main()