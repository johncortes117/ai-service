import os
import uuid
from pathlib import Path
from fastapi import UploadFile

def generate_unique_filename(prefix: str, original_filename: str) -> str:
    """
    Generates a unique filename preserving original name for better mapping.
    Handles any user input intelligently, avoiding prefix duplication.
    
    Examples:
        - "anexo_1.pdf" -> "ATTACHMENT_anexo_1_a1b2c3d4.pdf"
        - "ANEXO_1.pdf" -> "ATTACHMENT_ANEXO_1_a1b2c3d4.pdf" (preserves user's naming)
        - "ATTACHMENT_file.pdf" -> "ATTACHMENT_file_a1b2c3d4.pdf" (no duplication)
    """
    file_path = Path(original_filename)
    file_stem = file_path.stem  # filename without extension
    file_extension = file_path.suffix  # .pdf
    
    # Check if the filename already starts with our prefix (case-insensitive)
    # This prevents duplication like "ATTACHMENT_ATTACHMENT_file.pdf"
    if file_stem.upper().startswith(prefix.upper() + "_"):
        # Remove the existing prefix to avoid duplication
        # E.g., "ATTACHMENT_file" -> "file"
        file_stem = file_stem[len(prefix) + 1:]
    
    # Generate short UUID for uniqueness (8 chars is enough for collision avoidance)
    unique_id = str(uuid.uuid4())[:8]
    
    # Format: PREFIX_original_name_uuid.pdf
    # This preserves the original name for LLM mapping while maintaining uniqueness
    return f"{prefix}_{file_stem}_{unique_id}{file_extension}"

async def save_upload_file(file: UploadFile, full_path: Path):
    """Saves a FastAPI UploadFile to a specified Path."""
    await file.seek(0)  # Ensure the pointer is at the beginning
    with open(full_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    await file.seek(0) # Reset for any potential subsequent reads

def get_next_tender_id(tenders_dir: Path) -> str:
    """Gets the next available tender ID by checking existing directories."""
    if not tenders_dir.exists():
        return "1"
    
    existing_ids = [
        int(p.name.replace("tender_", ""))
        for p in tenders_dir.iterdir()
        if p.is_dir() and p.name.startswith("tender_") and p.name.replace("tender_", "").isdigit()
    ]
    
    return str(max(existing_ids) + 1) if existing_ids else "1"