from fastapi import UploadFile
import os
import uuid
from pathlib import Path
from ..constants import TEMP_DIR, PREFIX_PRINCIPAL, PREFIX_ATTACHMENTS

# Helper functions for file operations
def generate_unique_filename(prefix: str, original_filename: str) -> str:
    """Generate unique filename with prefix and UUID"""
    file_extension = os.path.splitext(original_filename)[1]
    return f"{prefix}_{uuid.uuid4()}{file_extension}"


def create_temp_filepath(filename: str) -> str:
    """Create a unique temporary file path"""
    file_extension = Path(filename).suffix
    temp_filename = f"temp_{hash(filename)}{file_extension}"
    return os.path.join(TEMP_DIR, temp_filename)


async def save_uploaded_file(file: UploadFile, file_path: str) -> None:
    """Save uploaded file to specified path"""
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)


async def save_file_structure(
    base_directory: str,
    path_structure: list,
    principal_file: UploadFile,
    attachment_files: list[UploadFile],
    prefix_principal: str = PREFIX_PRINCIPAL,
    prefix_attachments: str = PREFIX_ATTACHMENTS
) -> dict:
    """
    Save files in a structured directory format
    
    Args:
        base_directory: Base directory to save files
        path_structure: List with folder structure [level1, level2, level3, ...]
        principal_file: Main file to save
        attachment_files: List of attachment files
        prefix_principal: Prefix for main file
        prefix_attachments: Prefix for attachment files
    
    Returns:
        dict: Information about saved files
    """
    
    # Create directory structure
    target_dir = os.path.join(base_directory, *path_structure)
    os.makedirs(target_dir, exist_ok=True)
    
    # Process main file
    principal_filename = generate_unique_filename(prefix_principal, principal_file.filename)
    principal_path = os.path.join(target_dir, principal_filename)
    
    await save_uploaded_file(principal_file, principal_path)
    
    # Process attachment files
    saved_attachments = []
    for attachment_file in attachment_files:
        attachment_filename = generate_unique_filename(prefix_attachments, attachment_file.filename)
        attachment_path = os.path.join(target_dir, attachment_filename)
        
        await save_uploaded_file(attachment_file, attachment_path)
        saved_attachments.append(attachment_filename)
    
    return {
        "complete_path": target_dir,
        "principal_file": principal_filename,
        "attachment_files": saved_attachments,
        "total_attachments": len(saved_attachments)
    }
