# main.py
from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import traceback

# Import services, schemas and constants
from app.api import services
from app.api import schemas
from app.core import constants

# Initialize FastAPI app
app = FastAPI(
    title=constants.PROJECT_NAME,
    description=constants.DESCRIPTION,
    version=constants.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware (assuming CORS_ORIGINS is defined in a config file)
# from app.core.config import CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with CORS_ORIGINS for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure necessary directories exist on startup
@app.on_event("startup")
def on_startup():
    constants.create_directories()

# --- System Endpoints ---

@app.get("/health", summary="Health Check", tags=["System"])
def health_check() -> Dict[str, str]:
    return {"status": "healthy"}

# --- Tender Endpoints ---

@app.post("/tenders/upload", response_model=schemas.TenderUploadResponse, tags=["Tenders"])
async def upload_tender_sequential(file: UploadFile = File(...)):
    """Uploads a tender PDF, assigning the next available sequential ID."""
    try:
        return await services.upload_new_tender(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading tender: {e}")

@app.post("/tenders/upload/{tender_id}", response_model=schemas.TenderUploadResponse, tags=["Tenders"])
async def upload_tender_by_id(tender_id: str, file: UploadFile = File(...)):
    """Uploads a tender PDF for a specific ID."""
    try:
        return await services.upload_tender_with_id(tender_id, file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading tender with ID {tender_id}: {e}")

@app.get("/tenders/contractors_all", tags=["Tenders"])
async def get_all_contractors():
    """Retrieves all tenders and a list of their associated contractors."""
    try:
        return services.get_all_tenders_and_contractors()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving all contractors: {e}")

@app.post("/tenders/contractors_batch", tags=["Tenders"])
async def get_contractors_batch(tender_ids: List[str] = Body(..., embed=True)):
    """Retrieves contractors for a specific list of tender IDs."""
    try:
        results = services.get_contractors_for_batch(tender_ids['tender_ids'])
        return {
            "message": "Batch contractors retrieved successfully",
            "requested_tenders": tender_ids['tender_ids'],
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving batch contractors: {e}")
        
@app.get("/tenders/{tender_id}/contractors", tags=["Tenders"])
async def get_contractors_for_tender(tender_id: str):
    """Retrieves all contractors for a single tender."""
    try:
        contractors = services.get_tender_contractors(tender_id)
        return {
            "message": "Contractors retrieved successfully",
            "tender_id": tender_id,
            "total_contractors": len(contractors),
            "contractors": contractors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving contractors for tender {tender_id}: {e}")
    
@app.get("/tenders/{tender_id}", tags=["Tenders"])
async def get_tender_details(tender_id: str):
    """
    Gets the details of a tender, including its file and a list of its applications (proposals).
    """
    try:
        # Reutilizamos la lógica para obtener los contratistas (aplicaciones)
        applications = services.get_tender_contractors(tender_id)
        
        tender_file = f"TENDER_{tender_id}.pdf"
        tender_path = constants.TENDERS_DIR / f"tender_{tender_id}" / tender_file
        
        if not tender_path.exists() and not applications:
            raise HTTPException(status_code=404, detail=f"Tender with ID {tender_id} not found.")

        return {
            "tenderId": tender_id,
            "tenderFile": tender_file if tender_path.exists() else "File not found",
            "totalApplications": len(applications),
            "applications": applications # Lista de propuestas/contratistas
        }
    except Exception as e:
        # Evita propagar la excepción de HTTPException para personalizar el mensaje
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error retrieving details for tender {tender_id}: {e}")


@app.get("/tenders/{tender_id}/applications/{proposal_id}", tags=["Tenders"])
async def get_application_details(tender_id: str, proposal_id: str):
    """
    Gets the details of a specific application (proposal) within a tender.
    The proposal_id is the company name.
    """
    try:
        # Llamamos a la nueva función del servicio
        details = services.get_proposal_details(tender_id, proposal_id)
        return details
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error retrieving application {proposal_id}: {e}")

# --- Proposal Endpoints ---

@app.post("/proposals/upload/{tender_id}/{contractor_id}/{company_name}", response_model=schemas.ProposalUploadResponse, status_code=status.HTTP_201_CREATED, tags=["Proposals"])
async def upload_proposal_files(
    tender_id: str, contractor_id: str, company_name: str,
    principal_file: UploadFile = File(..., description="Main proposal PDF file"),
    attachment_files: List[UploadFile] = File(default=[], description="List of attachment files")
):
    """Uploads and organizes proposal files into a structured directory."""
    try:
        result = await services.upload_proposal(
            tender_id, contractor_id, company_name, principal_file, attachment_files
        )
        return {**result, "tender_id": tender_id, "contractor_id": contractor_id, "company_name": company_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing proposal files: {e}")

# --- Processing and Data Generation Endpoints ---

@app.post("/process_files", tags=["Processing"])
async def process_pdf_or_zip(file: UploadFile = File(...)):
    """Processes a single PDF or a ZIP file containing multiple PDFs, extracting their text."""
    try:
        result = await services.process_uploaded_pdf_or_zip(file)
        return {
            "message": "Files processed successfully",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")

@app.get("/tenders/{tender_id}/generate_json", response_model=schemas.TenderJsonResponse, tags=["Processing"])
async def generate_tender_json(tender_id: str):
    """Generates a single, consolidated JSON object with all text from the tender and its proposals."""
    try:
        json_data_from_service = await services.generate_full_tender_json(tender_id)
        
        if not json_data_from_service["tenderText"] and not json_data_from_service["proposals"]:
            raise HTTPException(status_code=404, detail=f"No data found for tender_id: {tender_id}")
        
        return {
            "message": "Tender JSON data generated successfully",
            "tender_id": tender_id,
            "total_proposals": len(json_data_from_service["proposals"]),
            "data": json_data_from_service
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating tender JSON: {e}")

# --- Server-Sent Events (SSE) Endpoints ---

@app.post("/sse/data", tags=["SSE"])
async def post_sse_data(payload: Dict[str, Any]):
    """Receives and saves data to be broadcast via SSE."""
    return services.save_sse_data(payload)

@app.get("/sse/stream", tags=["SSE"])
async def stream_sse_endpoint():
    """Endpoint for clients to connect and receive SSE updates."""
    return StreamingResponse(services.stream_sse_data(), media_type="text/event-stream")

@app.get("/sse/executive_summary", tags=["SSE"])
async def get_summary():
    """Checks if the analysis is complete and returns the executive summary if available."""
    return services.get_executive_summary_if_completed()