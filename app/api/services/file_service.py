import os
import uuid
from pathlib import Path
from fastapi import UploadFile

def generate_unique_filename(prefix: str, original_filename: str) -> str:
    """Generates a unique filename with a prefix and UUID."""
    file_extension = Path(original_filename).suffix
    return f"{prefix}_{uuid.uuid4()}{file_extension}"

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