# constants.py
"""
Constants, settings, and configurations for the API module.
"""
from pathlib import Path

# Project configuration
PROJECT_NAME = "AI Service API"
DESCRIPTION = "API for processing PDF documents and files"
VERSION = "1.0.0"

# --- Directory Configurations (using pathlib for robust path handling) ---
BASE_DIR = Path("./")
DATA_DIR = BASE_DIR / "data"
TENDERS_DIR = DATA_DIR / "tenders"
PROPOSALS_DIR = DATA_DIR / "proposals"
TEMP_DIR = DATA_DIR / "temp_files"
SSE_DATA_FILE = DATA_DIR / "sse_data.json"

# --- File Type Configurations ---
ALLOWED_PDF_TYPES = ["application/pdf"]
ALLOWED_ZIP_TYPES = ["application/zip", "application/x-zip-compressed"]
ALLOWED_TYPES = ALLOWED_PDF_TYPES + ALLOWED_ZIP_TYPES

# --- File Prefixes ---
PREFIX_PRINCIPAL = "PRINCIPAL"
PREFIX_ATTACHMENTS = "ANEXO"

# --- Response Messages ---
ERROR_INVALID_FILE_TYPE = "Invalid file type. Expected PDF or ZIP."
ERROR_PDF_PROCESSING = "Error processing PDF file."
ERROR_FILE_NOT_FOUND = "File not found."

# --- Function to ensure directories exist on startup ---
def create_directories():
    """Creates all necessary directories if they don't exist."""
    # Este es el bloque que faltaba
    for directory in [DATA_DIR, TENDERS_DIR, PROPOSALS_DIR, TEMP_DIR]:
        directory.mkdir(parents=True, exist_ok=True)