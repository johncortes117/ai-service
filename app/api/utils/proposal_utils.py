
import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from ..services import process_pdf_zip_files as _process_pdf_zip_files

"""
Utility functions for the API
"""
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


async def saveAttachmentWithOriginalName(file: UploadFile, directory: str) -> str:
    """Save attachment file preserving original filename"""
    # Remove any path separators and clean the filename for security
    clean_filename = os.path.basename(file.filename)
    # Remove any potentially dangerous characters
    clean_filename = "".join(c for c in clean_filename if c.isalnum() or c in "._-")
    
    file_path = os.path.join(directory, clean_filename)
    
    # Handle duplicate filenames by adding a number suffix
    counter = 1
    original_path = file_path
    while os.path.exists(file_path):
        name, ext = os.path.splitext(original_path)
        file_path = f"{name}_{counter}{ext}"
        counter += 1
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return os.path.basename(file_path)


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


def getContractorsByTender(tender_id: str) -> list:
    """Get list of contractors for a specific tender"""
    contractors = []
    proposals_dir = Path(f"./data/proposals/tender_{tender_id}")
    
    if not proposals_dir.exists():
        return contractors
    
    try:
        # Iterate through contractor directories
        for contractor_dir in proposals_dir.iterdir():
            if contractor_dir.is_dir() and contractor_dir.name.startswith("contractor_"):
                contractor_id = contractor_dir.name.replace("contractor_", "")
                
                # Get companies for this contractor
                companies = []
                for company_dir in contractor_dir.iterdir():
                    if company_dir.is_dir():
                        companies.append(company_dir.name)
                
                contractors.append({
                    "contractorId": contractor_id,
                    "companies": companies,
                    "totalCompanies": len(companies)
                })
        
        # Sort contractors by ID
        contractors.sort(key=lambda x: int(x["contractorId"]))
        
    except Exception as e:
        print(f"Error getting contractors for tender {tender_id}: {e}")
    
    return contractors


def getAllTendersContractors() -> dict:
    """Get contractors and companies for all tenders found in data/proposals"""
    result = {}
    proposals_base = Path("./data/proposals")
    tender_count = 0
    if not proposals_base.exists():
        return {"totalTenders": 0, "tenders": {}}
    for tender_dir in proposals_base.iterdir():
        if tender_dir.is_dir() and tender_dir.name.startswith("tender_"):
            tender_id = tender_dir.name.replace("tender_", "")
            contractors = getContractorsByTender(tender_id)
            result[tender_id] = contractors
            tender_count += 1
    return {"totalTenders": tender_count, "tenders": result}
def getContractorsBatch(tender_ids: list) -> dict:
    """Get contractors and companies for a batch of tenders"""
    result = {}
    for tender_id in tender_ids:
        contractors = getContractorsByTender(tender_id)
        result[tender_id] = contractors
    return result
