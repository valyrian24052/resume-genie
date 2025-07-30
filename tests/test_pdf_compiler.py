"""
Unit tests for the PDF compiler module.
"""

import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from core.pdf_compiler import PDFCompiler, CompilationResult, PDFCompilationError


class TestCompilationResult:
    """Test the CompilationResult dataclass"""
    
    def test_successful_result(self):
        """Test successful compilation result"""
        result = CompilationResult(success=True, output_path="/path/to/output.pdf")
        
        assert result.is_success is True
        assert result.has_errors is False
        assert result.output_path == "/path/to/output.pdf"
        assert result.error_message is None
    
    def test_failed_result(self):
        """Test failed compilation result"""
        result = CompilationResult(
            success=False, 
            error_message="Compilation failed",
            latex_log="Error log content"
        )
        
        assert result.is_success is False
        assert result.has_errors is True
        assert result.output_path is None
        assert result.error_message == "Compilation failed"
        assert result.latex_log == "Error log content"


class TestPDFCompiler:
    """Test the PDFCompiler class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.compiler = PDFCompiler()
        self.temp_dir = tempfile.mkdtemp()
        self.output_path = os.path.join(self.temp_dir, "test_output.pdf")
        
    def teardown_method(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init_default_values(self):
        """Test PDFCompiler initialization with default values"""
        compiler = PDFCompiler()
        
        assert compiler.latex_command == "latexmk"
        assert compiler.cleanup_temp is True
    
    def test_init_custom_values(self):
        """Test PDFCompiler initialization with custom values"""
        compiler = PDFCompiler(latex_command="pdflatex", cleanup_temp=False)
        
        assert compiler.latex_command == "pdflatex"
        assert compiler.cleanup_temp is False
    
    @patch('core.pdf_compiler.subprocess.run')
    @patch('core.pdf_compiler.tempfile.mkdtemp')
    def test_compile_to_pdf_success(self, mock_mkdtemp, mock_subprocess):
        """Test successful PDF compilation"""
        # Setup mocks
        temp_dir = os.path.join(self.temp_dir, "temp_compile")
        os.makedirs(temp_dir, exist_ok=True)
        mock_mkdtemp.return_value = temp_dir
        
        # Create mock PDF file
        temp_pdf = os.path.join(temp_dir, "resume.pdf")
        with open(temp_pdf, 'wb') as f:
            f.write(b'%PDF-1.4\nMock PDF content')
        
        # Mock successful subprocess
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stderr = ""
        mock_subprocess.return_value = mock_process
        
        latex_content = "\\documentclass{article}\\begin{document}Test\\end{document}"
        
        result = self.compiler.compile_to_pdf(latex_content, self.output_path)
        
        assert result.success is True
        assert result.output_path == self.output_path
        assert os.path.exists(self.output_path)
        
        # Verify subprocess was called correctly
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert "latexmk" in call_args
        assert "-pdf" in call_args
        assert "-interaction=nonstopmode" in call_args
    
    @patch('core.pdf_compiler.subprocess.run')
    @patch('core.pdf_compiler.tempfile.mkdtemp')
    def test_compile_to_pdf_latex_error(self, mock_mkdtemp, mock_subprocess):
        """Test PDF compilation with LaTeX errors"""
        temp_dir = os.path.join(self.temp_dir, "temp_compile")
        os.makedirs(temp_dir, exist_ok=True)
        mock_mkdtemp.return_value = temp_dir
        
        # Mock failed subprocess
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.stderr = "LaTeX Error: Undefined control sequence"
        mock_subprocess.return_value = mock_process
        
        latex_content = "\\documentclass{article}\\begin{document}\\invalidcommand\\end{document}"
        
        result = self.compiler.compile_to_pdf(latex_content, self.output_path)
        
        assert result.success is False
        assert "LaTeX Error: Undefined control sequence" in result.error_message
        assert result.output_path is None
    
    @patch('core.pdf_compiler.subprocess.run')
    @patch('core.pdf_compiler.tempfile.mkdtemp')
    def test_compile_to_pdf_timeout(self, mock_mkdtemp, mock_subprocess):
        """Test PDF compilation timeout"""
        temp_dir = os.path.join(self.temp_dir, "temp_compile")
        os.makedirs(temp_dir, exist_ok=True)
        mock_mkdtemp.return_value = temp_dir
        
        # Mock timeout exception
        from subprocess import TimeoutExpired
        mock_subprocess.side_effect = TimeoutExpired("latexmk", 60)
        
        latex_content = "\\documentclass{article}\\begin{document}Test\\end{document}"
        
        result = self.compiler.compile_to_pdf(latex_content, self.output_path)
        
        assert result.success is False
        assert "timed out after 60 seconds" in result.error_message
    
    @patch('core.pdf_compiler.subprocess.run')
    @patch('core.pdf_compiler.tempfile.mkdtemp')
    def test_compile_to_pdf_command_not_found(self, mock_mkdtemp, mock_subprocess):
        """Test PDF compilation when LaTeX command is not found"""
        temp_dir = os.path.join(self.temp_dir, "temp_compile")
        os.makedirs(temp_dir, exist_ok=True)
        mock_mkdtemp.return_value = temp_dir
        
        # Mock FileNotFoundError
        mock_subprocess.side_effect = FileNotFoundError("latexmk not found")
        
        latex_content = "\\documentclass{article}\\begin{document}Test\\end{document}"
        
        result = self.compiler.compile_to_pdf(latex_content, self.output_path)
        
        assert result.success is False
        assert "not found" in result.error_message
        assert "install LaTeX" in result.error_message
    
    def test_parse_latex_errors_with_stderr(self):
        """Test parsing LaTeX errors from stderr"""
        stderr = "This is pdfTeX, Version 3.14159265-2.6-1.40.20\nError: Something went wrong"
        latex_log = None
        
        error_msg = self.compiler._parse_latex_errors(stderr, latex_log)
        
        assert "LaTeX compilation errors:" in error_msg
        assert "Error: Something went wrong" in error_msg
    
    def test_parse_latex_errors_with_log(self):
        """Test parsing LaTeX errors from log file"""
        stderr = ""
        latex_log = """
        This is pdfTeX, Version 3.14159265-2.6-1.40.20
        ! Undefined control sequence.
        l.5 \\invalidcommand
                           
        The control sequence at the end of the top line
        """
        
        error_msg = self.compiler._parse_latex_errors(stderr, latex_log)
        
        assert "LaTeX Error: ! Undefined control sequence." in error_msg
        assert "l.5 \\invalidcommand" in error_msg
    
    def test_parse_latex_errors_no_errors(self):
        """Test parsing when no specific errors are found"""
        stderr = ""
        latex_log = "Normal compilation log without errors"
        
        error_msg = self.compiler._parse_latex_errors(stderr, latex_log)
        
        assert "unknown error" in error_msg
    
    def test_cleanup_temp_files_success(self):
        """Test successful cleanup of temporary files"""
        # Create temporary directory with files
        temp_cleanup_dir = os.path.join(self.temp_dir, "cleanup_test")
        os.makedirs(temp_cleanup_dir)
        test_file = os.path.join(temp_cleanup_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        assert os.path.exists(temp_cleanup_dir)
        assert os.path.exists(test_file)
        
        self.compiler.cleanup_temp_files(temp_cleanup_dir)
        
        assert not os.path.exists(temp_cleanup_dir)
    
    def test_cleanup_temp_files_nonexistent_path(self):
        """Test cleanup with non-existent path"""
        nonexistent_path = "/path/that/does/not/exist"
        
        # Should not raise exception
        self.compiler.cleanup_temp_files(nonexistent_path)
    
    def test_validate_pdf_success(self):
        """Test successful PDF validation"""
        # Create mock PDF file
        pdf_path = os.path.join(self.temp_dir, "valid.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n%Mock PDF content\n')
        
        result = self.compiler.validate_pdf(pdf_path)
        
        assert result is True
    
    def test_validate_pdf_file_not_exists(self):
        """Test PDF validation when file doesn't exist"""
        nonexistent_pdf = os.path.join(self.temp_dir, "nonexistent.pdf")
        
        result = self.compiler.validate_pdf(nonexistent_pdf)
        
        assert result is False
    
    def test_validate_pdf_empty_file(self):
        """Test PDF validation with empty file"""
        empty_pdf = os.path.join(self.temp_dir, "empty.pdf")
        with open(empty_pdf, 'wb') as f:
            pass  # Create empty file
        
        result = self.compiler.validate_pdf(empty_pdf)
        
        assert result is False
    
    def test_validate_pdf_invalid_header(self):
        """Test PDF validation with invalid PDF header"""
        invalid_pdf = os.path.join(self.temp_dir, "invalid.pdf")
        with open(invalid_pdf, 'wb') as f:
            f.write(b'Not a PDF file')
        
        result = self.compiler.validate_pdf(invalid_pdf)
        
        assert result is False
    
    @patch('core.pdf_compiler.subprocess.run')
    @patch('core.pdf_compiler.tempfile.mkdtemp')
    def test_compile_to_pdf_with_log_file(self, mock_mkdtemp, mock_subprocess):
        """Test PDF compilation that reads log file"""
        temp_dir = os.path.join(self.temp_dir, "temp_compile")
        os.makedirs(temp_dir, exist_ok=True)
        mock_mkdtemp.return_value = temp_dir
        
        # Create mock log file
        log_path = os.path.join(temp_dir, "resume.log")
        with open(log_path, 'w') as f:
            f.write("This is pdfTeX, Version 3.14159265\nCompilation successful")
        
        # Create mock PDF file
        temp_pdf = os.path.join(temp_dir, "resume.pdf")
        with open(temp_pdf, 'wb') as f:
            f.write(b'%PDF-1.4\nMock PDF content')
        
        # Mock successful subprocess
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stderr = ""
        mock_subprocess.return_value = mock_process
        
        latex_content = "\\documentclass{article}\\begin{document}Test\\end{document}"
        
        result = self.compiler.compile_to_pdf(latex_content, self.output_path)
        
        assert result.success is True
        assert result.latex_log is not None
        assert "Compilation successful" in result.latex_log
    
    @patch('core.pdf_compiler.subprocess.run')
    @patch('core.pdf_compiler.tempfile.mkdtemp')
    def test_compile_to_pdf_invalid_pdf_generated(self, mock_mkdtemp, mock_subprocess):
        """Test when LaTeX succeeds but generates invalid PDF"""
        temp_dir = os.path.join(self.temp_dir, "temp_compile")
        os.makedirs(temp_dir, exist_ok=True)
        mock_mkdtemp.return_value = temp_dir
        
        # Create mock invalid PDF file
        temp_pdf = os.path.join(temp_dir, "resume.pdf")
        with open(temp_pdf, 'wb') as f:
            f.write(b'Invalid PDF content')  # No PDF header
        
        # Mock successful subprocess
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stderr = ""
        mock_subprocess.return_value = mock_process
        
        latex_content = "\\documentclass{article}\\begin{document}Test\\end{document}"
        
        result = self.compiler.compile_to_pdf(latex_content, self.output_path)
        
        assert result.success is False
        assert "failed validation" in result.error_message
    
    def test_compiler_with_cleanup_disabled(self):
        """Test compiler behavior when cleanup is disabled"""
        compiler = PDFCompiler(cleanup_temp=False)
        
        # Create temporary directory
        temp_cleanup_dir = os.path.join(self.temp_dir, "no_cleanup_test")
        os.makedirs(temp_cleanup_dir)
        test_file = os.path.join(temp_cleanup_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Cleanup should still work when called explicitly
        compiler.cleanup_temp_files(temp_cleanup_dir)
        
        assert not os.path.exists(temp_cleanup_dir)


if __name__ == "__main__":
    pytest.main([__file__])