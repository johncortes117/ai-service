# services/__init__.py
"""
Services package for the AI Service API.

This package exposes high-level business logic functions to be used directly
by the API endpoints in main.py. It abstracts away the lower-level details
of file handling, PDF processing, and data manipulation.
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

from .analysis_service import (
    start_tender_analysis,
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

    # AI Analysis Orchestration Service
    "start_tender_analysis",
]