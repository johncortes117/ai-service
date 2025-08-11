import uuid
import os
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException

# Import service functions
from .services import (
    process_pdf_zip_files,
    save_file_structure,
    extract_document_information
)
from .constants import BASE_UPLOAD_DIRECTORY

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
        result = await processPdfZipFiles(file)
        return {
            "message": "Files processed successfully",
            **result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/propuestas/upload_differentiated/{tender_id}/{contractor_id}/{company_name}")
async def uploadDifferentiatedFiles(
    tender_id: str,
    contractor_id: str,
    company_name: str,
    principal_file: UploadFile = File(...),
    attachmentFiles: List[UploadFile] = File(...)
):
    """
    Upload and organize proposal files with hierarchical structure:
    data/propuestas/tender_{tender_id}/contractor_{contractor_id}/{company_name}/
    """
    try:
        # Create directory structure using utility function
        proposalDir = createProposalStructure(tender_id, contractor_id, company_name)
        
        # Save principal file
        principalFilename = await saveFileWithUuid(principal_file, proposalDir, "PRINCIPAL")
        
        # Save attachment files
        savedAttachments = []
        for attachmentFile in attachmentFiles:
            attachmentFilename = await saveFileWithUuid(attachmentFile, proposalDir, "ATTACHMENT")
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
        tenderId = getNextTenderId()
        
        # Check if tender already exists
        if checkTenderExists(tenderId):
            return {
                "message": "Tender already exists, no new files created.",
                "tender_id": tenderId,
                "status": "exists",
                "directory": f"./data/tenders/tender_{tenderId}"
            }
        
        # Save the tender PDF
        filename = await saveTenderPdf(file, tenderId)
        
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
        if checkTenderExists(tender_id):
            return {
                "message": "Tender already exists, no new files created.",
                "tender_id": tender_id,
                "status": "exists",
                "directory": f"./data/tenders/tender_{tender_id}"
            }
        
        # Save the tender PDF
        filename = await saveTenderPdf(file, tender_id)
        
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
    
    
    
