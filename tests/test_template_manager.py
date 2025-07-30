"""Unit tests for TemplateManager class."""

import unittest
import tempfile
import os
from pathlib import Path
import shutil

from core.template_manager import TemplateManager


class TestTemplateManager(unittest.TestCase):
    """Test cases for TemplateManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_manager = TemplateManager(self.temp_dir)
        
        # Create test templates
        self.templates = {
            "basic.tex": r"""
\documentclass{article}
\begin{document}
Basic template
\end{document}
""",
            "advanced.tex": r"""
\documentclass[11pt]{article}
\usepackage{geometry}
\begin{document}
\begin{itemize}
\item Advanced template
\end{itemize}
\end{document}
""",
            "invalid.tex": r"""
\documentclass{article}
\begin{document}
\begin{itemize}
Missing end itemize
\end{document}
""",
            "unbalanced.tex": r"""
\documentclass{article}
\begin{document}
Unbalanced {braces
\end{document}
"""
        }
        
        for filename, content in self.templates.items():
            template_path = Path(self.temp_dir) / filename
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_init_with_valid_directory(self):
        """Test initialization with valid template directory."""
        manager = TemplateManager(self.temp_dir)
        self.assertEqual(manager.template_directory, Path(self.temp_dir))
    
    def test_init_with_nonexistent_directory(self):
        """Test initialization with non-existent directory raises error."""
        nonexistent_dir = os.path.join(self.temp_dir, "nonexistent")
        with self.assertRaises(FileNotFoundError):
            TemplateManager(nonexistent_dir)
    
    def test_get_available_templates(self):
        """Test getting list of available templates."""
        templates = self.template_manager.get_available_templates()
        expected = ["advanced", "basic", "invalid", "unbalanced"]
        self.assertEqual(sorted(templates), expected)
    
    def test_get_available_templates_empty_directory(self):
        """Test getting templates from empty directory."""
        empty_dir = tempfile.mkdtemp()
        try:
            manager = TemplateManager(empty_dir)
            templates = manager.get_available_templates()
            self.assertEqual(templates, [])
        finally:
            shutil.rmtree(empty_dir)
    
    def test_load_template_without_extension(self):
        """Test loading template without .tex extension."""
        content = self.template_manager.load_template("basic")
        self.assertEqual(content.strip(), self.templates["basic.tex"].strip())
    
    def test_load_template_with_extension(self):
        """Test loading template with .tex extension."""
        content = self.template_manager.load_template("basic.tex")
        self.assertEqual(content.strip(), self.templates["basic.tex"].strip())
    
    def test_load_nonexistent_template(self):
        """Test loading non-existent template raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError) as context:
            self.template_manager.load_template("nonexistent")
        
        error_message = str(context.exception)
        self.assertIn("Template 'nonexistent.tex' not found", error_message)
        self.assertIn("Available templates:", error_message)
    
    def test_load_template_io_error(self):
        """Test loading template with IO error."""
        # Create a template file and then make it unreadable
        restricted_path = Path(self.temp_dir) / "restricted.tex"
        with open(restricted_path, 'w') as f:
            f.write("test content")
        
        # Make file unreadable (this might not work on all systems)
        try:
            os.chmod(restricted_path, 0o000)
            with self.assertRaises(IOError):
                self.template_manager.load_template("restricted")
        except (OSError, PermissionError):
            # Skip test if we can't change permissions
            self.skipTest("Cannot change file permissions on this system")
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(restricted_path, 0o644)
            except (OSError, PermissionError):
                pass
    
    def test_validate_template_syntax_valid_basic(self):
        """Test validation of valid basic template."""
        content = self.templates["basic.tex"]
        self.assertTrue(self.template_manager.validate_template_syntax(content))
    
    def test_validate_template_syntax_valid_advanced(self):
        """Test validation of valid advanced template."""
        content = self.templates["advanced.tex"]
        self.assertTrue(self.template_manager.validate_template_syntax(content))
    
    def test_validate_template_syntax_missing_documentclass(self):
        """Test validation fails for template missing documentclass."""
        invalid_content = r"""
\begin{document}
Content without documentclass
\end{document}
"""
        self.assertFalse(self.template_manager.validate_template_syntax(invalid_content))
    
    def test_validate_template_syntax_missing_begin_document(self):
        """Test validation fails for template missing begin document."""
        invalid_content = r"""
\documentclass{article}
Content without begin document
\end{document}
"""
        self.assertFalse(self.template_manager.validate_template_syntax(invalid_content))
    
    def test_validate_template_syntax_missing_end_document(self):
        """Test validation fails for template missing end document."""
        invalid_content = r"""
\documentclass{article}
\begin{document}
Content without end document
"""
        self.assertFalse(self.template_manager.validate_template_syntax(invalid_content))
    
    def test_validate_template_syntax_unbalanced_braces(self):
        """Test validation fails for unbalanced braces."""
        content = self.templates["unbalanced.tex"]
        self.assertFalse(self.template_manager.validate_template_syntax(content))
    
    def test_validate_template_syntax_unbalanced_environments(self):
        """Test validation fails for unbalanced environments."""
        content = self.templates["invalid.tex"]
        self.assertFalse(self.template_manager.validate_template_syntax(content))
    
    def test_validate_template_syntax_nested_environments(self):
        """Test validation of properly nested environments."""
        valid_nested = r"""
\documentclass{article}
\begin{document}
\begin{itemize}
\item First item
\begin{enumerate}
\item Nested item
\end{enumerate}
\end{itemize}
\end{document}
"""
        self.assertTrue(self.template_manager.validate_template_syntax(valid_nested))
    
    def test_validate_template_syntax_multiple_same_environments(self):
        """Test validation with multiple instances of same environment."""
        valid_multiple = r"""
\documentclass{article}
\begin{document}
\begin{itemize}
\item First list
\end{itemize}
\begin{itemize}
\item Second list
\end{itemize}
\end{document}
"""
        self.assertTrue(self.template_manager.validate_template_syntax(valid_multiple))
    
    def test_get_template_path(self):
        """Test getting template path."""
        path = self.template_manager.get_template_path("basic")
        expected_path = Path(self.temp_dir) / "basic.tex"
        self.assertEqual(path, expected_path)
    
    def test_get_template_path_with_extension(self):
        """Test getting template path with extension."""
        path = self.template_manager.get_template_path("basic.tex")
        expected_path = Path(self.temp_dir) / "basic.tex"
        self.assertEqual(path, expected_path)
    
    def test_template_exists_true(self):
        """Test template_exists returns True for existing template."""
        self.assertTrue(self.template_manager.template_exists("basic"))
        self.assertTrue(self.template_manager.template_exists("basic.tex"))
    
    def test_template_exists_false(self):
        """Test template_exists returns False for non-existent template."""
        self.assertFalse(self.template_manager.template_exists("nonexistent"))
        self.assertFalse(self.template_manager.template_exists("nonexistent.tex"))
    
    def test_template_directory_with_subdirectories(self):
        """Test that subdirectories are ignored when getting templates."""
        # Create a subdirectory with a .tex file
        subdir = Path(self.temp_dir) / "subdir"
        subdir.mkdir()
        with open(subdir / "sub.tex", 'w') as f:
            f.write(r"\documentclass{article}\begin{document}Sub\end{document}")
        
        templates = self.template_manager.get_available_templates()
        # Should not include templates from subdirectories
        self.assertNotIn("sub", templates)
    
    def test_template_directory_with_non_tex_files(self):
        """Test that non-.tex files are ignored."""
        # Create non-.tex files
        with open(Path(self.temp_dir) / "readme.txt", 'w') as f:
            f.write("This is not a template")
        with open(Path(self.temp_dir) / "config.json", 'w') as f:
            f.write('{"key": "value"}')
        
        templates = self.template_manager.get_available_templates()
        # Should only include .tex files
        for template in templates:
            self.assertIn(template, ["advanced", "basic", "invalid", "unbalanced"])


if __name__ == '__main__':
    unittest.main()