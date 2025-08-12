import os
import shutil
import zipfile
import uuid
import asyncio
import concurrent.futures
from typing import List, Dict, Any
from fastapi import UploadFile, HTTPException

from app.core import constants
from . import pdf_service, file_service

# --- Tender and Proposal Management ---

async def upload_new_tender(file: UploadFile) -> Dict[str, Any]:
    """Orchestrates uploading a tender with a new sequential ID."""
    tender_id = file_service.get_next_tender_id(constants.TENDERS_DIR)
    return await upload_tender_with_id(tender_id, file)

async def upload_tender_with_id(tender_id: str, file: UploadFile) -> Dict[str, Any]:
    """Orchestrates uploading a tender with a specific ID."""
    if file.content_type not in constants.ALLOWED_PDF_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Expected PDF.")

    tender_dir = constants.TENDERS_DIR / f"tender_{tender_id}"
    tender_dir.mkdir(exist_ok=True)
    
    filename = f"TENDER_{tender_id}.pdf"
    file_path = tender_dir / filename

    if file_path.exists():
        return {
            "message": "Tender already exists, no new files created.",
            "tender_id": tender_id, "status": "exists", "directory": str(tender_dir)
        }

    await file_service.save_upload_file(file, file_path)
    return {
        "message": "Tender PDF uploaded successfully.", "tender_id": tender_id,
        "filename": filename, "status": "created", "directory": str(tender_dir)
    }

async def upload_proposal(
    tender_id: str, contractor_id: str, company_name: str,
    principal_file: UploadFile, attachment_files: List[UploadFile]
) -> Dict[str, Any]:
    """Creates directory structure and saves all proposal files."""
    company_name_clean = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
    company_name_clean = company_name_clean or "UNKNOWN_COMPANY"
    
    proposal_dir = constants.PROPOSALS_DIR / f"tender_{tender_id}" / f"contractor_{contractor_id}" / company_name_clean
    proposal_dir.mkdir(parents=True, exist_ok=True)

    p_filename = file_service.generate_unique_filename(constants.PREFIX_PRINCIPAL, principal_file.filename)
    await file_service.save_upload_file(principal_file, proposal_dir / p_filename)

    saved_attachments = []
    for attachment in attachment_files:
        a_filename = file_service.generate_unique_filename(constants.PREFIX_ATTACHMENTS, attachment.filename)
        await file_service.save_upload_file(attachment, proposal_dir / a_filename)
        saved_attachments.append(a_filename)
    
    return {
        "message": "Files received and classified correctly.",
        "directory": str(proposal_dir), "principal_file": p_filename,
        "attachment_files": saved_attachments, "total_attachments": len(saved_attachments)
    }

# --- Data Retrieval and Generation ---

def get_tender_contractors(tender_id: str) -> List[Dict[str, Any]]:
    """Gets contractors and their companies for a specific tender."""
    tender_proposals_dir = constants.PROPOSALS_DIR / f"tender_{tender_id}"
    if not tender_proposals_dir.exists(): return []

    contractors = []
    for contractor_dir in tender_proposals_dir.glob("contractor_*"):
        if contractor_dir.is_dir():
            companies = [company.name for company in contractor_dir.iterdir() if company.is_dir()]
            contractors.append({
                "contractorId": contractor_dir.name.replace("contractor_", ""),
                "companies": companies, "totalCompanies": len(companies)
            })
    return contractors

def get_all_tenders_and_contractors() -> Dict[str, Any]:
    """Gets all contractors for all existing tenders."""
    tenders_data = {}
    if not constants.PROPOSALS_DIR.exists(): return {"totalTenders": 0, "tenders": {}}
    
    for tender_dir in constants.PROPOSALS_DIR.glob("tender_*"):
        if tender_dir.is_dir():
            tender_id = tender_dir.name.replace("tender_", "")
            tenders_data[tender_id] = get_tender_contractors(tender_id)
            
    return {"totalTenders": len(tenders_data), "tenders": tenders_data}

def get_contractors_for_batch(tender_ids: List[str]) -> Dict[str, Any]:
    """Gets contractors for a batch of tender IDs."""
    return {tender_id: get_tender_contractors(tender_id) for tender_id in tender_ids}

def _generate_tender_json_data_sync(tender_id: str) -> Dict[str, Any]:
    """The synchronous core logic for generating the tender JSON, matching the schema."""
    result = {"tenderName": f"TENDER_{tender_id}", "tenderText": "", "proposals": []}

    tender_dir = constants.TENDERS_DIR / f"tender_{tender_id}"
    try:
        tender_pdf = next(tender_dir.glob("TENDER_*.pdf"))
        result["tenderText"] = pdf_service.extract_text_from_pdf(str(tender_pdf))
        result["tenderName"] = tender_pdf.stem
    except (StopIteration, Exception) as e:
        result["tenderText"] = f"Tender PDF not found or failed to process: {e}"

    proposals_dir = constants.PROPOSALS_DIR / f"tender_{tender_id}"
    if not proposals_dir.exists(): return result

    for contractor_dir in proposals_dir.glob("contractor_*"):
        contractor_id = contractor_dir.name.replace("contractor_", "")
        for company_dir in contractor_dir.iterdir():
            if company_dir.is_dir():
                proposal_data = {
                    "contractorId": contractor_id, "companyName": company_dir.name,
                    "principalText": "", "lastPageText": "", "attachments": {}
                }
                try:
                    p_file = next(company_dir.glob(f"{constants.PREFIX_PRINCIPAL}_*.pdf"))
                    proposal_data["principalText"] = pdf_service.extract_text_from_pdf(str(p_file))
                    proposal_data["lastPageText"] = pdf_service.extract_last_page_from_pdf(str(p_file))
                except StopIteration: pass
                
                for a_file in company_dir.glob(f"{constants.PREFIX_ATTACHMENTS}_*.pdf"):
                    proposal_data["attachments"][a_file.name] = pdf_service.extract_text_from_pdf(str(a_file))
                
                result["proposals"].append(proposal_data)
    return result

async def generate_full_tender_json(tender_id: str) -> Dict[str, Any]:
    """Async wrapper to generate tender JSON data in a thread pool."""
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _generate_tender_json_data_sync, tender_id)

# --- FUNCIÓN QUE FALTABA ---
async def process_uploaded_pdf_or_zip(file: UploadFile) -> Dict[str, Any]:
    """Processes a single uploaded PDF or a ZIP containing PDFs."""
    if file.content_type not in constants.ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=constants.ERROR_INVALID_FILE_TYPE)

    temp_path = constants.TEMP_DIR / f"temp_{uuid.uuid4()}"
    processed_files = []
    
    try:
        await file_service.save_upload_file(file, temp_path)
        
        if file.content_type in constants.ALLOWED_PDF_TYPES:
            text = pdf_service.extract_text_from_pdf(str(temp_path))
            processed_files.append({"filename": file.filename, "text_length": len(text), "status": "processed"})
        else:
            extract_dir = constants.TEMP_DIR / f"extracted_{uuid.uuid4()}"
            extract_dir.mkdir()
            with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            for root, _, files in os.walk(extract_dir):
                for filename in files:
                    if filename.lower().endswith('.pdf'):
                        pdf_path = os.path.join(root, filename)
                        try:
                            text = pdf_service.extract_text_from_pdf(pdf_path)
                            processed_files.append({"filename": filename, "text_length": len(text), "status": "processed"})
                        except Exception as e:
                            processed_files.append({"filename": filename, "status": "error", "error": str(e)})
            shutil.rmtree(extract_dir)
    finally:
        if temp_path.exists():
            temp_path.unlink()
            
    return {
        "original_filename": file.filename,
        "content_type": file.content_type,
        "processed_files": processed_files,
        "total_files_processed": len(processed_files)
    }


def get_proposal_details(tender_id: str, proposal_id: str) -> Dict[str, Any]:
    """
    Finds and returns the details for a single proposal within a tender.
    The proposal_id is now interpreted as the contractor_id.
    """
    # 1. Construimos la ruta directa a la carpeta del contratista
    contractor_dir = constants.PROPOSALS_DIR / f"tender_{tender_id}" / f"contractor_{proposal_id}"

    if not contractor_dir.is_dir():
        raise HTTPException(
            status_code=404, 
            detail=f"Proposal (application) with ID '{proposal_id}' (contractor) not found in tender {tender_id}."
        )

    # 2. Asumimos que dentro de la carpeta del contratista hay UNA carpeta de compañía
    try:
        company_dir = next(d for d in contractor_dir.iterdir() if d.is_dir())
        company_name = company_dir.name
    except StopIteration:
        raise HTTPException(
            status_code=404, 
            detail=f"No company folder found for proposal ID '{proposal_id}' in tender {tender_id}."
        )

    # 3. Recopilamos la información de los archivos dentro de la carpeta de la compañía
    principal_file_info = "Not found"
    try:
        # CORRECCIÓN: Usamos los prefijos del archivo de constantes
        principal_file = next(company_dir.glob(f"{constants.PREFIX_PRINCIPAL}*.pdf"))
        principal_file_info = {
            "filename": principal_file.name,
            "size_bytes": principal_file.stat().st_size
        }
    except StopIteration:
        pass

    attachment_files_info = []
    # CORRECCIÓN: Usamos los prefijos del archivo de constantes
    for attachment_file in company_dir.glob(f"{constants.PREFIX_ATTACHMENTS}*.pdf"):
        attachment_files_info.append({
            "filename": attachment_file.name,
            "size_bytes": attachment_file.stat().st_size
        })

    return {
        "tenderId": tender_id,
        "proposalId": proposal_id, # contractor_id
        "contractorId": proposal_id,
        "companyName": company_name,
        "principalFile": principal_file_info,
        "attachments": attachment_files_info,
        "totalAttachments": len(attachment_files_info),
        "directory": str(company_dir)
    }