#!/usr/bin/env python3
"""Simple CLI script to scan for personal data in YAML files."""

import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import from core
sys.path.append(str(Path(__file__).parent.parent))

from core.personal_data_scanner import PersonalDataScanner


def main():
    """Main function for the personal data scanner CLI."""
    parser = argparse.ArgumentParser(description='Scan YAML files for personal data')
    parser.add_argument('path', help='Path to YAML file or directory to scan')
    parser.add_argument('-d', '--directory', action='store_true', help='Scan all YAML files in directory')
    parser.add_argument('-q', '--quiet', action='store_true', help='Only show summary')
    
    args = parser.parse_args()
    
    scanner = PersonalDataScanner()
    
    if args.directory:
        print(f"🔍 Scanning directory: {args.path}")
        results = scanner.scan_directory(args.path)
        
        total_issues = 0
        files_with_issues = 0
        
        for file_path, findings in results.items():
            issues = [f for f in findings if f.get('type') != 'error']
            if issues:
                files_with_issues += 1
                total_issues += len(issues)
                
                if not args.quiet:
                    print(f"\n📄 {file_path}:")
                    report = scanner.generate_report(findings)
                    print(report)
        
        print(f"\n📊 Summary:")
        print(f"   Files scanned: {len(results)}")
        print(f"   Files with issues: {files_with_issues}")
        print(f"   Total issues: {total_issues}")
        
    else:
        print(f"🔍 Scanning file: {args.path}")
        findings = scanner.scan_yaml_file(args.path)
        report = scanner.generate_report(findings)
        print(report)
        
        # Check if file is anonymized
        is_anon, issues = scanner.is_anonymized(args.path)
        if is_anon:
            print("\n✅ File appears to be properly anonymized!")
        else:
            print(f"\n⚠️  File contains {len(issues)} personal data items")


if __name__ == '__main__':
    main()