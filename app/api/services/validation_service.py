"""Validation service for file uploads and content verification"""

import fitz  # PyMuPDF
from pathlib import Path
from fastapi import HTTPException, UploadFile


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


async def validate_pdf_file(file: UploadFile) -> None:
    """
    Validates that an uploaded file is a valid PDF with extractable content.
    
    Args:
        file: The uploaded file to validate
        
    Raises:
        HTTPException: If validation fails
    """
    # Check file extension
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Expected PDF, got: {file.filename}"
        )
    
    # Check content type
    if file.content_type not in ['application/pdf']:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type. Expected 'application/pdf', got: {file.content_type}"
        )
    
    # Check file size (max 50MB for now)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes
    contents = await file.read()
    file_size = len(contents)
    
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is 50MB, got {file_size / (1024*1024):.2f}MB"
        )
    
    # Reset file pointer for subsequent reads
    await file.seek(0)


def validate_pdf_content(pdf_path: Path) -> dict:
    """
    Validates that a PDF file has extractable text content.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        dict with validation results: {
            'is_valid': bool,
            'page_count': int,
            'has_text': bool,
            'text_length': int,
            'error': Optional[str]
        }
    """
    result = {
        'is_valid': False,
        'page_count': 0,
        'has_text': False,
        'text_length': 0,
        'error': None
    }
    
    try:
        doc = fitz.open(pdf_path)
        result['page_count'] = len(doc)
        
        if result['page_count'] == 0:
            result['error'] = "PDF has no pages"
            doc.close()
            return result
        
        # Extract text from all pages
        full_text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            full_text += page.get_text()
        
        doc.close()
        
        # Check if text was extracted
        text_stripped = full_text.strip()
        result['text_length'] = len(text_stripped)
        result['has_text'] = len(text_stripped) > 0
        
        if not result['has_text']:
            result['error'] = "PDF appears to be image-based or has no extractable text. OCR may be required."
            return result
        
        # Validation passed
        result['is_valid'] = True
        
    except Exception as e:
        result['error'] = f"Error reading PDF: {str(e)}"
    
    return result


async def validate_tender_pdf(file: UploadFile) -> None:
    """
    Comprehensive validation for tender PDF uploads.
    
    Args:
        file: The uploaded tender PDF
        
    Raises:
        HTTPException: If validation fails
    """
    # First, validate file format and size
    await validate_pdf_file(file)
    
    # Note: Content validation (text extraction) will be done after saving
    # to avoid reading the file twice in memory


async def validate_proposal_files(
    principal_file: UploadFile,
    attachment_files: list[UploadFile]
) -> None:
    """
    Validates proposal files (principal + attachments).
    
    Args:
        principal_file: Main proposal PDF
        attachment_files: List of attachment PDFs
        
    Raises:
        HTTPException: If validation fails
    """
    # Validate principal file
    await validate_pdf_file(principal_file)
    
    # Validate each attachment
    for idx, attachment in enumerate(attachment_files):
        try:
            await validate_pdf_file(attachment)
        except HTTPException as e:
            raise HTTPException(
                status_code=400,
                detail=f"Attachment #{idx + 1} validation failed: {e.detail}"
            )
    
    # Check total number of files
    total_files = 1 + len(attachment_files)
    MAX_ATTACHMENTS = 20
    
    if total_files > MAX_ATTACHMENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum {MAX_ATTACHMENTS} files allowed (1 principal + {MAX_ATTACHMENTS - 1} attachments)"
        )
