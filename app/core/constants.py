# app/core/constants.py
"""
Application constants and configurations.
"""
from pathlib import Path

# Directory configurations
CORE_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = CORE_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
TENDERS_DIR = DATA_DIR / "tenders"
PROPOSALS_DIR = DATA_DIR / "proposals"
TEMP_DIR = DATA_DIR / "temp_files"
SSE_DATA_FILE = DATA_DIR / "sse_data.json"

# Project metadata
PROJECT_NAME = "AI Service API"
DESCRIPTION = "API for processing PDF documents and files"
VERSION = "1.0.0"

# File type configurations
ALLOWED_PDF_TYPES = ["application/pdf"]
ALLOWED_ZIP_TYPES = ["application/zip", "application/x-zip-compressed"]
ALLOWED_TYPES = ALLOWED_PDF_TYPES + ALLOWED_ZIP_TYPES

# File prefixes
PREFIX_PRINCIPAL = "PRINCIPAL"
PREFIX_ATTACHMENTS = "ATTACHMENT"

# Error messages
ERROR_INVALID_FILE_TYPE = "Invalid file type. Expected PDF or ZIP."
ERROR_PDF_PROCESSING = "Error processing PDF file."
ERROR_FILE_NOT_FOUND = "File not found."

def create_directories():
    """Creates all necessary directories if they don't exist."""
    print(f"Ensuring data directories exist inside: {DATA_DIR}")
    for directory in [DATA_DIR, TENDERS_DIR, PROPOSALS_DIR, TEMP_DIR]:
        directory.mkdir(parents=True, exist_ok=True)