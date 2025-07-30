"""
PDF compilation module for the AI Resume Builder.

This module provides functionality to compile LaTeX documents to PDF using latexmk,
with comprehensive error handling and cleanup capabilities.
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class PDFCompilationError(Exception):
    """Errors related to PDF compilation"""
    pass


@dataclass
class CompilationResult:
    """Result object with success status and error details"""
    success: bool
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    latex_log: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        """Check if compilation was successful"""
        return self.success
    
    @property
    def has_errors(self) -> bool:
        """Check if compilation had errors"""
        return not self.success


class PDFCompiler:
    """Main compilation class for converting LaTeX to PDF using latexmk"""
    
    def __init__(self, latex_command: str = "latexmk", cleanup_temp: bool = True):
        """
        Initialize PDF compiler.
        
        Args:
            latex_command: LaTeX compiler command (default: latexmk)
            cleanup_temp: Whether to cleanup temporary files after compilation
        """
        self.latex_command = latex_command
        self.cleanup_temp = cleanup_temp
        
    def compile_to_pdf(self, latex_content: str, output_path: str) -> CompilationResult:
        """
        Compile LaTeX content to PDF using latexmk.
        
        Args:
            latex_content: The LaTeX document content as string
            output_path: Path where the PDF should be saved
            
        Returns:
            CompilationResult with success status and details
            
        Raises:
            PDFCompilationError: If compilation fails critically
        """
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create temporary directory for compilation
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp(prefix="resume_builder_")
            temp_tex_path = Path(temp_dir) / "resume.tex"
            temp_pdf_path = Path(temp_dir) / "resume.pdf"
            
            # Write LaTeX content to temporary file
            with open(temp_tex_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            # Run latexmk compilation
            result = self._run_latex_compilation(temp_tex_path, temp_dir)
            
            if result.success and temp_pdf_path.exists():
                # Copy PDF to final destination
                shutil.copy2(temp_pdf_path, output_path)
                
                # Validate the generated PDF
                if self.validate_pdf(output_path):
                    result.output_path = output_path
                    logger.info(f"PDF successfully compiled to {output_path}")
                else:
                    result.success = False
                    result.error_message = "Generated PDF failed validation"
                    logger.error("Generated PDF failed validation")
            
            return result
            
        except Exception as e:
            logger.error(f"PDF compilation failed: {str(e)}")
            return CompilationResult(
                success=False,
                error_message=f"Compilation failed: {str(e)}"
            )
        finally:
            # Cleanup temporary files if requested
            if self.cleanup_temp and temp_dir:
                self.cleanup_temp_files(temp_dir)
    
    def _run_latex_compilation(self, tex_path: Path, work_dir: str) -> CompilationResult:
        """
        Run the actual LaTeX compilation process.
        
        Args:
            tex_path: Path to the .tex file
            work_dir: Working directory for compilation
            
        Returns:
            CompilationResult with compilation status
        """
        try:
            # Build latexmk command
            cmd = [
                self.latex_command,
                "-pdf",           # Generate PDF
                "-interaction=nonstopmode",  # Don't stop on errors
                "-output-directory=" + work_dir,
                str(tex_path)
            ]
            
            logger.debug(f"Running LaTeX compilation: {' '.join(cmd)}")
            
            # Run compilation
            process = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            # Read log file if it exists
            log_path = Path(work_dir) / "resume.log"
            latex_log = None
            if log_path.exists():
                try:
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        latex_log = f.read()
                except Exception as e:
                    logger.warning(f"Could not read LaTeX log: {e}")
            
            if process.returncode == 0:
                return CompilationResult(
                    success=True,
                    latex_log=latex_log
                )
            else:
                error_msg = self._parse_latex_errors(process.stderr, latex_log)
                return CompilationResult(
                    success=False,
                    error_message=error_msg,
                    latex_log=latex_log
                )
                
        except subprocess.TimeoutExpired:
            return CompilationResult(
                success=False,
                error_message="LaTeX compilation timed out after 60 seconds"
            )
        except FileNotFoundError:
            return CompilationResult(
                success=False,
                error_message=f"LaTeX compiler '{self.latex_command}' not found. Please install LaTeX."
            )
        except Exception as e:
            return CompilationResult(
                success=False,
                error_message=f"Unexpected error during compilation: {str(e)}"
            )
    
    def _parse_latex_errors(self, stderr: str, latex_log: Optional[str]) -> str:
        """
        Parse LaTeX compilation errors to provide helpful error messages.
        
        Args:
            stderr: Standard error output from latexmk
            latex_log: Content of the LaTeX log file
            
        Returns:
            Formatted error message
        """
        error_lines = []
        
        if stderr:
            error_lines.append("LaTeX compilation errors:")
            error_lines.append(stderr.strip())
        
        if latex_log:
            # Look for common LaTeX errors in the log
            log_lines = latex_log.split('\n')
            for i, line in enumerate(log_lines):
                if '! ' in line:  # LaTeX error marker
                    error_lines.append(f"LaTeX Error: {line.strip()}")
                    # Include next few lines for context
                    for j in range(1, min(4, len(log_lines) - i)):
                        if log_lines[i + j].strip():
                            error_lines.append(f"  {log_lines[i + j].strip()}")
                        else:
                            break
        
        if not error_lines:
            error_lines.append("LaTeX compilation failed with unknown error")
        
        return '\n'.join(error_lines)
    
    def cleanup_temp_files(self, base_path: str) -> None:
        """
        Clean up temporary LaTeX files.
        
        Args:
            base_path: Base directory path containing temporary files
        """
        try:
            if os.path.exists(base_path):
                shutil.rmtree(base_path)
                logger.debug(f"Cleaned up temporary files in {base_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temporary files in {base_path}: {e}")
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """
        Validate that the PDF is readable and properly formatted.
        
        Args:
            pdf_path: Path to the PDF file to validate
            
        Returns:
            True if PDF is valid, False otherwise
        """
        try:
            pdf_file = Path(pdf_path)
            
            # Check if file exists and has content
            if not pdf_file.exists():
                logger.error(f"PDF file does not exist: {pdf_path}")
                return False
            
            if pdf_file.stat().st_size == 0:
                logger.error(f"PDF file is empty: {pdf_path}")
                return False
            
            # Basic PDF header validation
            with open(pdf_path, 'rb') as f:
                header = f.read(8)
                if not header.startswith(b'%PDF-'):
                    logger.error(f"Invalid PDF header in {pdf_path}")
                    return False
            
            logger.debug(f"PDF validation successful: {pdf_path}")
            return True
            
        except Exception as e:
            logger.error(f"PDF validation failed for {pdf_path}: {e}")
            return False