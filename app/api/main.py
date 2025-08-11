import uuid
import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import configuration
from app.core.config import CORS_ORIGINS, MAX_FILE_SIZE, ALLOWED_FILE_EXTENSIONS

# Import utility functions properly
from app.api import utils as utils_module
# Import schemas - commented temporarily to fix server startup
# from app.api.schemas import (
#     ProposalUploadResponse, 
#     ErrorResponse, 
#     TenderUploadResponse, 
#     TenderJsonResponse
# )

# FastAPI app definition
app = FastAPI(
    title="AI Service API",
    description="API for AI services including blueprint creation and document processing",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for Next.js frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # Configured in core/config.py
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Batch contractors endpoint
@app.post("/tenders/contractors_batch")
async def get_contractors_batch(tender_ids: List[str] = Body(..., embed=True)):
    """
    Get contractors and companies for a batch of tenders.
    Receives: { "tender_ids": ["1", "2", ...] }
    Returns: { "tender_id": [ {contractorId, companies, totalCompanies}, ... ], ... }
    """
    try:
        batch_result = utils_module.getContractorsBatch(tender_ids)
        return {
            "message": "Batch contractors retrieved successfully",
            "requested_tenders": tender_ids,
            "results": batch_result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving batch contractors: {str(e)}"
        )

# Health check endpoint
@app.get(
    "/health", 
    summary="Health Check",
    description="Check if the API is running properly",
    response_model=Dict[str, str],
    tags=["System"]
)
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "message": "AI Service API is running!"}


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


@app.post(
    "/proposals/upload_differentiated/{tender_id}/{contractor_id}/{company_name}",
    # response_model=ProposalUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Proposal Files",
    description="Upload and organize proposal files with hierarchical structure",
    responses={
        201: {"description": "Files uploaded successfully"},
        400: {"description": "Invalid input data"},
        413: {"description": "File too large"},
        500: {"description": "Internal server error"}
    },
    tags=["Proposals"]
)
async def upload_differentiated_files(
    tender_id: str,
    contractor_id: str,
    company_name: str,
    principal_file: UploadFile = File(..., description="Main proposal file (PDF recommended)"),
    attachment_files: List[UploadFile] = File(default=[], description="List of attachment files")
) -> Dict[str, Any]:
    """
    Upload and organize proposal files with hierarchical structure.
    
    Creates directory: data/proposals/tender_{tender_id}/contractor_{contractor_id}/{company_name}/
    """
    try:
        # Create directory structure using utility function
        proposal_dir = utils_module.createProposalStructure(tender_id, contractor_id, company_name)
        
        # Save principal file
        principal_filename = await utils_module.saveFileWithUuid(principal_file, proposal_dir, "PRINCIPAL")
        
        # Save attachment files
        saved_attachments = []
        for attachment_file in attachment_files:
            attachment_filename = await utils_module.saveAttachmentWithOriginalName(attachment_file, proposal_dir)
            saved_attachments.append(attachment_filename)

        return {
            "message": "Files received and classified correctly.",
            "tender_id": tender_id,
            "contractor_id": contractor_id,
            "company_name": company_name,
            "principal_file": principal_filename,
            "attachment_files": saved_attachments,
            "total_attachments": len(saved_attachments),
            "directory": proposal_dir
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing files: {str(e)}"
        )


@app.post("/tenders/upload")
async def uploadTenderPdf(file: UploadFile = File(...)):
    """
    Upload a tender PDF file. Creates sequential tender IDs (1, 2, 3...)
    """
    try:
        tenderId = utils_module.getNextTenderId()
        
        if utils_module.checkTenderExists(tenderId):
            return {
                "message": "Tender already exists, no new files created.",
                "tender_id": tenderId,
                "status": "exists",
                "directory": f"./data/tenders/tender_{tenderId}"
            }
        
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
    """
    try:
        if utils_module.checkTenderExists(tender_id):
            return {
                "message": "Tender already exists, no new files created.",
                "tender_id": tender_id,
                "status": "exists",
                "directory": f"./data/tenders/tender_{tender_id}"
            }
        
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
    """
    try:
        json_data = await utils_module.generateTenderJsonDataAsync(tender_id)
        
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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating tender JSON: {str(e)}")


@app.get("/tenders/{tender_id}/contractors")
async def getContractors(tender_id: str):
    """
    Get list of contractors for a specific tender
    """
    try:
        contractors = utils_module.getContractorsByTender(tender_id)
        
        return {
            "message": "Contractors retrieved successfully",
            "tender_id": tender_id,
            "total_contractors": len(contractors),
            "contractors": contractors
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving contractors for tender {tender_id}: {str(e)}"
        )
