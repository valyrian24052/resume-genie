"""Unit tests for PersonalDataScanner class."""

import unittest
import tempfile
import os
import yaml
from pathlib import Path

from core.personal_data_scanner import PersonalDataScanner


class TestPersonalDataScanner(unittest.TestCase):
    """Test cases for PersonalDataScanner."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scanner = PersonalDataScanner()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_temp_yaml(self, content: dict, filename: str = "test.yaml") -> str:
        """Create a temporary YAML file with given content."""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(content, f)
        return file_path
    
    def test_email_detection(self):
        """Test email address detection."""
        test_data = {
            'email': 'john.doe@example.com',
            'contact': 'Contact me at jane.smith@company.org'
        }
        file_path = self.create_temp_yaml(test_data)
        
        findings = self.scanner.scan_yaml_file(file_path)
        email_findings = [f for f in findings if f.get('category') == 'email']
        
        self.assertGreater(len(email_findings), 0, "Should detect email addresses")
        self.assertTrue(any('john.doe@example.com' in f['value'] for f in email_findings))
    
    def test_phone_detection(self):
        """Test phone number detection."""
        test_data = {
            'phone': '+1-555-123-4567',
            'contact': 'Call me at (555) 987-6543',
            'mobile': '555.111.2222'
        }
        file_path = self.create_temp_yaml(test_data)
        
        findings = self.scanner.scan_yaml_file(file_path)
        phone_findings = [f for f in findings if f.get('category') == 'phone']
        
        self.assertGreater(len(phone_findings), 0, "Should detect phone numbers")
    
    def test_url_detection(self):
        """Test URL detection."""
        test_data = {
            'portfolio': 'https://johndoe.com',
            'github': 'https://github.com/johndoe',
            'linkedin': 'https://linkedin.com/in/johndoe'
        }
        file_path = self.create_temp_yaml(test_data)
        
        findings = self.scanner.scan_yaml_file(file_path)
        url_findings = [f for f in findings if f.get('category') in ['url', 'linkedin_profile', 'github_profile']]
        
        self.assertGreater(len(url_findings), 0, "Should detect URLs")
    
    def test_personal_identifier_detection(self):
        """Test detection of personal identifiers."""
        test_data = {
            'name': 'Shashank Sharma',
            'username': 'valyrian24052',
            'company': 'Mrikal Studios'
        }
        file_path = self.create_temp_yaml(test_data)
        
        findings = self.scanner.scan_yaml_file(file_path)
        identifier_findings = [f for f in findings if f.get('type') == 'personal_identifier']
        
        self.assertGreater(len(identifier_findings), 0, "Should detect personal identifiers")
    
    def test_placeholder_exclusion(self):
        """Test that placeholder values are not flagged as personal data."""
        test_data = {
            'name': '[Your Full Name]',
            'email': '[your.email@domain.com]',
            'phone': '[+1-XXX-XXX-XXXX]',
            'portfolio': '[https://yourportfolio.com]',
            'gpa': '[X.X]'
        }
        file_path = self.create_temp_yaml(test_data)
        
        findings = self.scanner.scan_yaml_file(file_path)
        personal_data_findings = [f for f in findings if f.get('type') in ['personal_data', 'personal_field']]
        
        self.assertEqual(len(personal_data_findings), 0, "Should not flag placeholder values as personal data")
    
    def test_mixed_content(self):
        """Test scanning content with both personal data and placeholders."""
        test_data = {
            'name': '[Your Full Name]',  # Placeholder - should be ignored
            'email': 'real.email@example.com',  # Real email - should be detected
            'phone': '[+1-XXX-XXX-XXXX]',  # Placeholder - should be ignored
            'backup_phone': '+1-555-123-4567',  # Real phone - should be detected
            'company': '[Company Name]',  # Placeholder - should be ignored
            'previous_company': 'Shashank Industries'  # Contains personal identifier - should be detected
        }
        file_path = self.create_temp_yaml(test_data)
        
        findings = self.scanner.scan_yaml_file(file_path)
        
        # Should detect real email and phone, but not placeholders
        email_findings = [f for f in findings if 'real.email@example.com' in f.get('value', '')]
        phone_findings = [f for f in findings if '+1-555-123-4567' in f.get('value', '')]
        identifier_findings = [f for f in findings if f.get('type') == 'personal_identifier']
        
        self.assertGreater(len(email_findings), 0, "Should detect real email")
        self.assertGreater(len(phone_findings), 0, "Should detect real phone")
        self.assertGreater(len(identifier_findings), 0, "Should detect personal identifier")
    
    def test_is_anonymized_method(self):
        """Test the is_anonymized method."""
        # Test with personal data
        personal_data = {
            'name': 'John Doe',
            'email': 'john@example.com'
        }
        personal_file = self.create_temp_yaml(personal_data, 'personal.yaml')
        
        is_anon, issues = self.scanner.is_anonymized(personal_file)
        self.assertFalse(is_anon, "Should detect that file is not anonymized")
        self.assertGreater(len(issues), 0, "Should return list of issues")
        
        # Test with anonymized data
        anon_data = {
            'name': '[Your Full Name]',
            'email': '[your.email@domain.com]'
        }
        anon_file = self.create_temp_yaml(anon_data, 'anonymous.yaml')
        
        is_anon, issues = self.scanner.is_anonymized(anon_file)
        self.assertTrue(is_anon, "Should detect that file is anonymized")
        self.assertEqual(len(issues), 0, "Should return empty issues list")
    
    def test_generate_report(self):
        """Test report generation."""
        findings = [
            {
                'type': 'personal_data',
                'category': 'email',
                'description': 'Email address',
                'value': 'test@example.com',
                'file': 'test.yaml',
                'line': 1,
                'context': 'email: test@example.com',
                'severity': 'high'
            },
            {
                'type': 'personal_identifier',
                'category': 'name_or_identifier',
                'description': 'Personal name or identifier',
                'value': 'shashank',
                'file': 'test.yaml',
                'line': 2,
                'context': 'name: Shashank Doe',
                'severity': 'medium'
            }
        ]
        
        report = self.scanner.generate_report(findings)
        
        self.assertIn('Personal Data Scan Report', report)
        self.assertIn('HIGH SEVERITY', report)
        self.assertIn('MEDIUM SEVERITY', report)
        self.assertIn('test@example.com', report)
        self.assertIn('shashank', report)
    
    def test_empty_findings_report(self):
        """Test report generation with no findings."""
        report = self.scanner.generate_report([])
        self.assertIn('No personal data detected', report)
    
    def test_scan_directory(self):
        """Test directory scanning functionality."""
        # Create multiple test files
        test_files = {
            'file1.yaml': {'name': 'John Doe', 'email': 'john@example.com'},
            'file2.yaml': {'name': '[Your Name]', 'email': '[your.email@domain.com]'},
            'file3.yaml': {'company': 'Shashank Corp', 'phone': '+1-555-123-4567'}
        }
        
        for filename, content in test_files.items():
            self.create_temp_yaml(content, filename)
        
        results = self.scanner.scan_directory(self.temp_dir)
        
        self.assertEqual(len(results), 3, "Should scan all YAML files in directory")
        
        # Check that personal data was found in appropriate files
        file1_results = results.get(os.path.join(self.temp_dir, 'file1.yaml'), [])
        file2_results = results.get(os.path.join(self.temp_dir, 'file2.yaml'), [])
        
        file1_personal = [f for f in file1_results if f.get('type') in ['personal_data', 'personal_field']]
        file2_personal = [f for f in file2_results if f.get('type') in ['personal_data', 'personal_field']]
        
        self.assertGreater(len(file1_personal), 0, "Should find personal data in file1")
        self.assertEqual(len(file2_personal), 0, "Should not find personal data in anonymized file2")
    
    def test_file_not_found(self):
        """Test handling of non-existent files."""
        findings = self.scanner.scan_yaml_file('nonexistent.yaml')
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['type'], 'error')
        self.assertIn('File not found', findings[0]['message'])
    
    def test_invalid_yaml(self):
        """Test handling of invalid YAML files."""
        invalid_yaml_path = os.path.join(self.temp_dir, 'invalid.yaml')
        with open(invalid_yaml_path, 'w') as f:
            f.write('invalid: yaml: content: [unclosed')
        
        findings = self.scanner.scan_yaml_file(invalid_yaml_path)
        
        # Should handle the error gracefully
        error_findings = [f for f in findings if f.get('type') == 'error']
        self.assertGreater(len(error_findings), 0, "Should report YAML parsing error")
    
    def test_pattern_accuracy(self):
        """Test the accuracy of detection patterns."""
        # Test email pattern
        email_pattern = self.scanner.patterns['email']['pattern']
        
        valid_emails = [
            'user@example.com',
            'test.email@domain.org',
            'user+tag@example.co.uk'
        ]
        
        invalid_emails = [
            'not-an-email',
            '@domain.com',
            'user@',
            '[your.email@domain.com]'  # Should not match placeholder
        ]
        
        import re
        for email in valid_emails:
            self.assertTrue(re.search(email_pattern, email), f"Should match valid email: {email}")
        
        for email in invalid_emails:
            if email != '[your.email@domain.com]':  # This one might match the pattern but should be filtered out by placeholder logic
                self.assertFalse(re.search(email_pattern, email), f"Should not match invalid email: {email}")
    
    def test_severity_classification(self):
        """Test that findings are properly classified by severity."""
        test_data = {
            'email': 'test@example.com',  # High severity
            'description': 'This mentions shashank in the text'  # Medium severity
        }
        file_path = self.create_temp_yaml(test_data)
        
        findings = self.scanner.scan_yaml_file(file_path)
        
        high_severity = [f for f in findings if f.get('severity') == 'high']
        medium_severity = [f for f in findings if f.get('severity') == 'medium']
        
        self.assertGreater(len(high_severity), 0, "Should have high severity findings")
        self.assertGreater(len(medium_severity), 0, "Should have medium severity findings")


if __name__ == '__main__':
    unittest.main()