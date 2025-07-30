"""Personal data scanner to detect and flag personal information in YAML files."""

import re
import yaml
from typing import Dict, List, Any, Tuple
from pathlib import Path


class PersonalDataScanner:
    """Scanner to detect personal information in resume data."""
    
    def __init__(self):
        """Initialize the scanner with detection patterns."""
        self.patterns = {
            'email': {
                'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'description': 'Email address'
            },
            'phone': {
                'pattern': r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
                'description': 'Phone number'
            },
            'url': {
                'pattern': r'https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?',
                'description': 'URL'
            },
            'linkedin_profile': {
                'pattern': r'linkedin\.com/in/[\w-]+',
                'description': 'LinkedIn profile URL'
            },
            'github_profile': {
                'pattern': r'github\.com/[\w-]+',
                'description': 'GitHub profile URL'
            }
        }
        
        # Common personal identifiers that might appear in the codebase
        self.personal_identifiers = [
            'shashank', 'sharma', 'valyrian', 'shashanksharma', 'valyrian24052',
            'mrikal', 'megaminds', 'shopup', 'driotio', 'dosevisor'
        ]
        
        # Placeholder patterns that indicate anonymized data
        self.placeholder_patterns = [
            r'\[.*?\]',  # [Your Name], [Company Name], etc.
            r'your\.email@domain\.com',
            r'\+1-XXX-XXX-XXXX',
            r'https://yourportfolio\.com',
            r'X\.X'  # GPA placeholder
        ]
    
    def scan_yaml_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Scan a YAML file for personal information.
        
        Args:
            file_path: Path to the YAML file to scan
            
        Returns:
            List of dictionaries containing detected personal data with details
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                data = yaml.safe_load(content)
            
            findings = []
            
            # Scan the raw content for patterns
            findings.extend(self._scan_content(content, file_path))
            
            # Scan the parsed data structure
            findings.extend(self._scan_data_structure(data, file_path))
            
            return findings
            
        except FileNotFoundError:
            return [{'type': 'error', 'message': f'File not found: {file_path}'}]
        except yaml.YAMLError as e:
            return [{'type': 'error', 'message': f'YAML parsing error: {e}'}]
        except Exception as e:
            return [{'type': 'error', 'message': f'Unexpected error: {e}'}]
    
    def _scan_content(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Scan raw content for personal data patterns."""
        findings = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip if line contains placeholder patterns
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in self.placeholder_patterns):
                continue
            
            # Check for pattern matches
            for pattern_name, pattern_info in self.patterns.items():
                matches = re.finditer(pattern_info['pattern'], line, re.IGNORECASE)
                for match in matches:
                    findings.append({
                        'type': 'personal_data',
                        'category': pattern_name,
                        'description': pattern_info['description'],
                        'value': match.group(),
                        'file': file_path,
                        'line': line_num,
                        'context': line.strip(),
                        'severity': 'high'
                    })
            
            # Check for personal identifiers
            line_lower = line.lower()
            for identifier in self.personal_identifiers:
                if identifier in line_lower:
                    findings.append({
                        'type': 'personal_identifier',
                        'category': 'name_or_identifier',
                        'description': 'Personal name or identifier',
                        'value': identifier,
                        'file': file_path,
                        'line': line_num,
                        'context': line.strip(),
                        'severity': 'medium'
                    })
        
        return findings
    
    def _scan_data_structure(self, data: Dict[str, Any], file_path: str) -> List[Dict[str, Any]]:
        """Scan parsed YAML data structure for personal information."""
        findings = []
        
        if not isinstance(data, dict):
            return findings
        
        # Check specific fields that commonly contain personal data
        personal_fields = {
            'name': 'Full name',
            'email': 'Email address',
            'phone': 'Phone number',
            'portfolio_url': 'Portfolio URL',
            'linkedin_url': 'LinkedIn URL',
            'github_url': 'GitHub URL',
            'education_school': 'School name',
            'education_location': 'Education location'
        }
        
        for field, description in personal_fields.items():
            if field in data and data[field]:
                value = str(data[field])
                # Skip if it's a placeholder
                if any(re.search(pattern, value, re.IGNORECASE) for pattern in self.placeholder_patterns):
                    continue
                
                findings.append({
                    'type': 'personal_field',
                    'category': field,
                    'description': description,
                    'value': value,
                    'file': file_path,
                    'line': None,
                    'context': f'{field}: {value}',
                    'severity': 'high'
                })
        
        return findings
    
    def scan_directory(self, directory_path: str, file_pattern: str = "*.yaml") -> Dict[str, List[Dict[str, Any]]]:
        """
        Scan all YAML files in a directory for personal information.
        
        Args:
            directory_path: Path to directory to scan
            file_pattern: File pattern to match (default: *.yaml)
            
        Returns:
            Dictionary mapping file paths to their scan results
        """
        results = {}
        directory = Path(directory_path)
        
        if not directory.exists():
            return {'error': [{'type': 'error', 'message': f'Directory not found: {directory_path}'}]}
        
        for file_path in directory.glob(file_pattern):
            if file_path.is_file():
                results[str(file_path)] = self.scan_yaml_file(str(file_path))
        
        return results
    
    def generate_report(self, findings: List[Dict[str, Any]]) -> str:
        """Generate a human-readable report from scan findings."""
        if not findings:
            return "✅ No personal data detected."
        
        report_lines = ["🔍 Personal Data Scan Report", "=" * 40, ""]
        
        # Group findings by severity
        high_severity = [f for f in findings if f.get('severity') == 'high']
        medium_severity = [f for f in findings if f.get('severity') == 'medium']
        errors = [f for f in findings if f.get('type') == 'error']
        
        if errors:
            report_lines.extend(["❌ ERRORS:", ""])
            for error in errors:
                report_lines.append(f"  • {error['message']}")
            report_lines.append("")
        
        if high_severity:
            report_lines.extend(["🚨 HIGH SEVERITY ISSUES:", ""])
            for finding in high_severity:
                report_lines.append(f"  • {finding['description']}: {finding['value']}")
                if finding.get('line'):
                    report_lines.append(f"    Line {finding['line']}: {finding['context']}")
                else:
                    report_lines.append(f"    Context: {finding['context']}")
            report_lines.append("")
        
        if medium_severity:
            report_lines.extend(["⚠️  MEDIUM SEVERITY ISSUES:", ""])
            for finding in medium_severity:
                report_lines.append(f"  • {finding['description']}: {finding['value']}")
                if finding.get('line'):
                    report_lines.append(f"    Line {finding['line']}: {finding['context']}")
                else:
                    report_lines.append(f"    Context: {finding['context']}")
            report_lines.append("")
        
        report_lines.extend([
            f"Total issues found: {len([f for f in findings if f.get('type') != 'error'])}",
            f"Files scanned: {len(set(f.get('file', 'unknown') for f in findings if f.get('file')))}"
        ])
        
        return "\n".join(report_lines)
    
    def is_anonymized(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        Check if a YAML file is properly anonymized.
        
        Args:
            file_path: Path to the YAML file to check
            
        Returns:
            Tuple of (is_anonymized, list_of_issues)
        """
        findings = self.scan_yaml_file(file_path)
        issues = [f for f in findings if f.get('type') != 'error']
        
        return len(issues) == 0, [f"{f['description']}: {f['value']}" for f in issues]