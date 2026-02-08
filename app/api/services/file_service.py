import os
import uuid
from pathlib import Path
from fastapi import UploadFile

def generate_unique_filename(prefix: str, original_filename: str) -> str:
    """
    Generates a unique filename preserving original name for better LLM mapping.
    Prevents prefix duplication when user uploads files that already contain the prefix.
    
    Format: PREFIX_original_name_uuid.extension
    Example: ATTACHMENT_anexo_1_a1b2c3d4.pdf
    """
    file_path = Path(original_filename)
    file_stem = file_path.stem
    file_extension = file_path.suffix
    
    if file_stem.upper().startswith(prefix.upper() + "_"):
        file_stem = file_stem[len(prefix) + 1:]
    
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{file_stem}_{unique_id}{file_extension}"

async def save_upload_file(file: UploadFile, full_path: Path):
    """Saves a FastAPI UploadFile to the specified path."""
    await file.seek(0)
    with open(full_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    await file.seek(0)

def get_next_tender_id(tenders_dir: Path) -> str:
    """Returns the next available tender ID by checking existing tender directories."""
    if not tenders_dir.exists():
        return "1"
    
    existing_ids = [
        int(p.name.replace("tender_", ""))
        for p in tenders_dir.iterdir()
        if p.is_dir() and p.name.startswith("tender_") and p.name.replace("tender_", "").isdigit()
    ]
    
    return str(max(existing_ids) + 1) if existing_ids else "1"