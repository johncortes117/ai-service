"""
Pydantic models for API request/response schemas
"""
from pydantic import BaseModel
from typing import List, Optional


class FileResponse(BaseModel):
    """Response model for file operations"""
    filename: str
    status: str
    message: Optional[str] = None


class ProcessedFileInfo(BaseModel):
    """Information about a processed file"""
    filename: str
    type: str
    text_length: int
    status: str
    content: Optional[str] = None
    error: Optional[str] = None


class ProcessFileResponse(BaseModel):
    """Response for file processing operations"""
    original_filename: str
    content_type: str
    processed_files: List[ProcessedFileInfo]
    total_files: int


class FileStructureResponse(BaseModel):
    """Response for file structure save operations"""
    complete_path: str
    principal_file: str
    attachment_files: List[str]
    total_attachments: int


class DocumentInfoResponse(BaseModel):
    """Response for document information extraction"""
    filename: str
    text: str
    text_length: int
    status: str
    error: Optional[str] = None
