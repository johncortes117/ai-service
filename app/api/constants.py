"""
Constants for the API module
"""

# Project configuration
PROJECT_NAME = "AI Service API"
DESCRIPTION = "API for processing PDF documents and files"
VERSION = "1.0.0"

# Directory configurations
BASE_UPLOAD_DIRECTORY = "./Data"
UPLOAD_DIR = "uploads"
TEMP_DIR = "temp_files"

# File type configurations
ALLOWED_PDF_TYPES = ["application/pdf"]
ALLOWED_ZIP_TYPES = ["application/zip", "application/x-zip-compressed"]
ALLOWED_TYPES = ALLOWED_PDF_TYPES + ALLOWED_ZIP_TYPES

# File prefixes
PREFIX_PRINCIPAL = "PRINCIPAL"
PREFIX_ATTACHMENTS = "ANEXO"

# Response messages
ERROR_INVALID_FILE_TYPE = "Invalid file type. Expected PDF or ZIP."
ERROR_PDF_PROCESSING = "Error processing PDF file."
ERROR_FILE_NOT_FOUND = "File not found."
