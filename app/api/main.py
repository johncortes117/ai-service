import uuid
import os
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException

# Import utility functions from utils.py file (not the utils directory)
import importlib.util
import sys

# Load utils.py specifically as a module
spec = importlib.util.spec_from_file_location("utils_module", "f:/Hackthon/ai-service/app/api/utils.py")
utils_module = importlib.util.module_from_spec(spec)
sys.modules["utils_module"] = utils_module
spec.loader.exec_module(utils_module)

app = FastAPI(
    title="AI Service API",
    description="API for AI services including blueprint creation and document processing",
    version="0.1.0"
)

@app.get("/")
async def read_root():
    return {"message": "AI Service API is running!", "status": "healthy"}


@app.post("/process_and_structure_pdfs")
async def processAndStructurePdfs(file: UploadFile = File(...)):
    """
    Process PDF files or ZIP files containing PDFs
    """
    try:
        result = await utils_module.processPdfZipFiles(file)
        return {
            "message": "Files processed successfully",
            **result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/proposals/upload_differentiated/{tender_id}/{contractor_id}/{company_name}")
async def uploadDifferentiatedFiles(
    tender_id: str,
    contractor_id: str,
    company_name: str,
    principal_file: UploadFile = File(...),
    attachmentFiles: List[UploadFile] = File(...)
):
    """
    Upload and organize proposal files with hierarchical structure.
    
    Creates directory: data/proposals/tender_{tender_id}/contractor_{contractor_id}/{company_name}/
    
    Args:
        tender_id: Unique identifier for the tender
        contractor_id: Unique identifier for the contractor
        company_name: Name of the company (will be cleaned for filesystem)
        principal_file: Main proposal file (required)
        attachmentFiles: List of attachment files (required, can be empty list)
    
    Returns:
        dict: Information about uploaded files and created structure
    """
    try:
        # Create directory structure using utility function
        proposalDir = utils_module.createProposalStructure(tender_id, contractor_id, company_name)
        
        # Save principal file
        principalFilename = await utils_module.saveFileWithUuid(principal_file, proposalDir, "PRINCIPAL")
        
        # Save attachment files
        savedAttachments = []
        for attachmentFile in attachmentFiles:
            attachmentFilename = await utils_module.saveFileWithUuid(attachmentFile, proposalDir, "ATTACHMENT")
            savedAttachments.append(attachmentFilename)

        return {
            "message": "Files received and classified correctly.",
            "tender_id": tender_id,
            "contractor_id": contractor_id,
            "company_name": company_name,
            "principal_file": principalFilename,
            "attachment_files": savedAttachments,
            "total_attachments": len(savedAttachments),
            "directory": proposalDir
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")


@app.post("/tenders/upload")
async def uploadTenderPdf(file: UploadFile = File(...)):
    """
    Upload a tender PDF file. Creates sequential tender IDs (1, 2, 3...)
    If the tender already exists, returns existing information without creating new files.
    """
    try:
        # Get the next available tender ID
        tenderId = utils_module.getNextTenderId()
        
        # Check if tender already exists
        if utils_module.checkTenderExists(tenderId):
            return {
                "message": "Tender already exists, no new files created.",
                "tender_id": tenderId,
                "status": "exists",
                "directory": f"./data/tenders/tender_{tenderId}"
            }
        
        # Save the tender PDF
        filename = await utils_module.saveTenderPdf(file, tenderId)
        
        return {
            "message": "Tender PDF uploaded successfully.",
            "tender_id": tenderId,
            "filename": filename,
            "status": "created",
            "directory": f"./data/tenders/tender_{tenderId}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing tender PDF: {str(e)}")


@app.post("/tenders/upload/{tender_id}")
async def uploadTenderPdfWithId(tender_id: str, file: UploadFile = File(...)):
    """
    Upload a tender PDF file with specific tender ID.
    If the tender already exists, returns existing information without creating new files.
    """
    try:
        # Check if tender already exists
        if utils_module.checkTenderExists(tender_id):
            return {
                "message": "Tender already exists, no new files created.",
                "tender_id": tender_id,
                "status": "exists",
                "directory": f"./data/tenders/tender_{tender_id}"
            }
        
        # Save the tender PDF
        filename = await utils_module.saveTenderPdf(file, tender_id)
        
        return {
            "message": "Tender PDF uploaded successfully.",
            "tender_id": tender_id,
            "filename": filename,
            "status": "created",
            "directory": f"./data/tenders/tender_{tender_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing tender PDF: {str(e)}")


@app.get("/tenders/{tender_id}/generate_json")
async def generateTenderJson(tender_id: str):
    """
    Generate complete JSON data for a tender including all proposals
    Extracts text from tender PDF and all proposal PDFs with proper structure
    """
    try:
        print(f"DEBUG: Starting generateTenderJson for tender_id: {tender_id}")
        
        # Generate the complete JSON data
        print(f"DEBUG: About to call generateTenderJsonDataAsync")
        json_data = await utils_module.generateTenderJsonDataAsync(tender_id)
        print(f"DEBUG: Successfully called generateTenderJsonDataAsync, got data: {type(json_data)}")
        
        # Check if any data was found
        if not json_data["tenderText"] and not json_data["proposals"]:
            raise HTTPException(
                status_code=404, 
                detail=f"No tender or proposal data found for tender_id: {tender_id}"
            )
        
        return {
            "message": "Tender JSON data generated successfully",
            "tender_id": tender_id,
            "total_proposals": len(json_data["proposals"]),
            "data": json_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Exception in generateTenderJson: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating tender JSON: {str(e)}")
