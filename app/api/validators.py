"""
Validation utilities for file uploads and API requests
"""
from typing import List, Optional
from fastapi import HTTPException, UploadFile, status
import mimetypes

# File size limits (in bytes)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_TOTAL_FILES_SIZE = 200 * 1024 * 1024  # 200MB

# Allowed file types
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/jpeg',
    'image/png',
    'image/gif'
}

ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif'}


async def validate_file(file: UploadFile, required: bool = True) -> None:
    """
    Validate uploaded file
    
    Args:
        file: The uploaded file
        required: Whether the file is required
        
    Raises:
        HTTPException: If validation fails
    """
    if not file and required:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is required"
        )
    
    if not file:
        return
    
    # Check file size
    file_size = 0
    if hasattr(file, 'size') and file.size:
        file_size = file.size
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size allowed: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Check file extension
    filename = file.filename or ""
    file_extension = filename.lower().split('.')[-1] if '.' in filename else ""
    
    if f".{file_extension}" not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check MIME type
    content_type = file.content_type
    if content_type not in ALLOWED_MIME_TYPES:
        # Try to guess from filename
        guessed_type, _ = mimetypes.guess_type(filename)
        if guessed_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )


async def validate_files_list(files: List[UploadFile]) -> None:
    """
    Validate a list of uploaded files
    
    Args:
        files: List of uploaded files
        
    Raises:
        HTTPException: If validation fails
    """
    if not files:
        return
    
    total_size = 0
    
    for file in files:
        await validate_file(file, required=False)
        
        if hasattr(file, 'size') and file.size:
            total_size += file.size
    
    if total_size > MAX_TOTAL_FILES_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Total files size too large. Maximum allowed: {MAX_TOTAL_FILES_SIZE // (1024*1024)}MB"
        )


def validate_tender_id(tender_id: str) -> str:
    """
    Validate tender ID format
    
    Args:
        tender_id: The tender ID to validate
        
    Returns:
        str: The validated tender ID
        
    Raises:
        HTTPException: If validation fails
    """
    if not tender_id or not tender_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tender ID is required"
        )
    
    tender_id = tender_id.strip()
    
    if not tender_id.isalnum():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tender ID must contain only alphanumeric characters"
        )
    
    if len(tender_id) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tender ID must be 50 characters or less"
        )
    
    return tender_id


def validate_contractor_id(contractor_id: str) -> str:
    """
    Validate contractor ID format
    
    Args:
        contractor_id: The contractor ID to validate
        
    Returns:
        str: The validated contractor ID
        
    Raises:
        HTTPException: If validation fails
    """
    if not contractor_id or not contractor_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contractor ID is required"
        )
    
    contractor_id = contractor_id.strip()
    
    if not contractor_id.isalnum():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contractor ID must contain only alphanumeric characters"
        )
    
    if len(contractor_id) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contractor ID must be 50 characters or less"
        )
    
    return contractor_id


def validate_company_name(company_name: str) -> str:
    """
    Validate and clean company name
    
    Args:
        company_name: The company name to validate
        
    Returns:
        str: The validated and cleaned company name
        
    Raises:
        HTTPException: If validation fails
    """
    if not company_name or not company_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name is required"
        )
    
    company_name = company_name.strip()
    
    if len(company_name) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name must be 200 characters or less"
        )
    
    # Clean but preserve original structure
    cleaned_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_', '.')).strip()
    
    if not cleaned_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name contains invalid characters"
        )
    
    return cleaned_name
