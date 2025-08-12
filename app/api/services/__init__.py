# services/__init__.py
"""
Services package for the AI Service API.
...
"""

from .tender_service import (
    upload_new_tender,
    upload_tender_with_id,
    upload_proposal,
    get_tender_contractors,
    get_all_tenders_and_contractors,
    get_contractors_for_batch,
    generate_full_tender_json,
    process_uploaded_pdf_or_zip,
    get_proposal_details,  
)

from .sse_service import (
    save_sse_data,
    stream_sse_data,
    get_executive_summary_if_completed,
)

__all__ = [
    # Tender and Proposal Services
    "upload_new_tender",
    "upload_tender_with_id",
    "upload_proposal",
    "get_tender_contractors",
    "get_all_tenders_and_contractors",
    "get_contractors_for_batch",
    "generate_full_tender_json",
    "process_uploaded_pdf_or_zip",
    "get_proposal_details",  

    # Server-Sent Events (SSE) Services
    "save_sse_data",
    "stream_sse_data",
    "get_executive_summary_if_completed",
]