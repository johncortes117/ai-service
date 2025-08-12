# schemas.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# =====================================================
# SCHEMAS FOR PROPOSAL UPLOAD ENDPOINT
# =====================================================

class ProposalUploadResponse(BaseModel):
    """Schema for successful proposal upload response"""
    message: str
    tender_id: str
    contractor_id: str
    company_name: str
    principal_file: str
    attachment_files: List[str]
    total_attachments: int
    directory: str

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str

# =====================================================
# SCHEMAS FOR TENDER OPERATIONS
# =====================================================

class TenderUploadResponse(BaseModel):
    """Schema for tender upload response"""
    message: str
    tender_id: str
    filename: Optional[str] = None
    status: str  # "created" or "exists"
    directory: str

# =====================================================
# SCHEMAS FOR JSON GENERATION ENDPOINT
# =====================================================

class ProposalData(BaseModel):
    """Schema for individual proposal data"""
    contractorId: str
    companyName: str
    principalText: str
    lastPageText: str
    attachments: Dict[str, Any]

class TenderJsonData(BaseModel):
    """Schema for complete tender JSON data"""
    tenderName: str
    tenderText: str
    proposals: List[ProposalData]

class TenderJsonResponse(BaseModel):
    """Schema for tender JSON generation response"""
    message: str
    tender_id: str
    total_proposals: int
    data: TenderJsonData
