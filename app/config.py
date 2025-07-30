"""Application configuration."""

from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"

# Default files
DEFAULT_RESUME_FILE = DATA_DIR / "resume.yaml"
DEFAULT_TEMPLATE = "resume"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)