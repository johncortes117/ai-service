"""
Utility functions for the API
"""
import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from ..services import process_pdf_zip_files as _process_pdf_zip_files


async def processPdfZipFiles(file: UploadFile):
    """Process PDF or ZIP files containing PDFs"""
    return await _process_pdf_zip_files(file)


def createProposalStructure(tender_id: str, contractor_id: str, company_name: str) -> str:
    """Create directory structure for proposals"""
    base_dir = "./data/proposals"
    proposal_dir = os.path.join(
        base_dir, 
        f"tender_{tender_id}", 
        f"contractor_{contractor_id}", 
        company_name
    )
    os.makedirs(proposal_dir, exist_ok=True)
    return proposal_dir


async def saveFileWithUuid(file: UploadFile, directory: str, prefix: str) -> str:
    """Save file with UUID prefix"""
    file_extension = Path(file.filename).suffix
    unique_filename = f"{prefix}_{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(directory, unique_filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return unique_filename


def getNextTenderId() -> str:
    """Get the next available tender ID"""
    base_dir = "./data/tenders"
    if not os.path.exists(base_dir):
        return "1"
    
    # Find highest existing tender ID
    max_id = 0
    for item in os.listdir(base_dir):
        if item.startswith("tender_"):
            try:
                tender_num = int(item.split("_")[1])
                max_id = max(max_id, tender_num)
            except (IndexError, ValueError):
                continue
    
    return str(max_id + 1)


def checkTenderExists(tender_id: str) -> bool:
    """Check if a tender directory already exists"""
    tender_dir = f"./data/tenders/tender_{tender_id}"
    return os.path.exists(tender_dir)


async def saveTenderPdf(file: UploadFile, tender_id: str) -> str:
    """Save tender PDF file"""
    tender_dir = f"./data/tenders/tender_{tender_id}"
    os.makedirs(tender_dir, exist_ok=True)
    
    file_extension = Path(file.filename).suffix
    filename = f"tender_{tender_id}{file_extension}"
    file_path = os.path.join(tender_dir, filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return filename
