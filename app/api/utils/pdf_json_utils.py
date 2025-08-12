"""
PDF processing and JSON generation utilities for tender and proposal data
"""
import os
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Any


def extractTextFromPdf(pdfPath: str) -> str:
    """Extract text from PDF file using PyMuPDF (fitz)"""
    text = ""
    try:
        doc = fitz.open(pdfPath)
        for pageNum in range(len(doc)):
            page = doc.load_page(pageNum)
            text += page.get_text()
        doc.close()
    except Exception as e:
        raise Exception(f"Error processing PDF {pdfPath}: {e}")
    
    if text.strip() == "":
        return f"[PDF with no extractable text detected: {os.path.basename(pdfPath)}. OCR pending implementation]"
    else:
        return text


def extractLastPageFromPdf(pdfPath: str) -> str:
    """Extract text from only the last page of a PDF file"""
    text = ""
    try:
        doc = fitz.open(pdfPath)
        totalPages = len(doc)
        
        if totalPages == 0:
            doc.close()
            return "[PDF has no pages]"
        
        # Get only the last page (index is totalPages - 1)
        lastPage = doc.load_page(totalPages - 1)
        text = lastPage.get_text()
        doc.close()
        
    except Exception as e:
        raise Exception(f"Error processing last page of PDF {pdfPath}: {e}")
    
    if text.strip() == "":
        return f"[Last page of PDF has no extractable text: {os.path.basename(pdfPath)}. OCR pending implementation]"
    else:
        return text


def generateTenderJsonData(tender_id: str) -> dict:
    """
    Generate complete JSON data for a tender including all proposals
    Extracts text from tender PDF and all proposal PDFs
    
    Args:
        tender_id: String identifier for the tender (e.g., "1", "2", etc.)
        
    Returns:
        dict: Complete tender data with proposals and text content
    """
    result = {
        "tenderId": tender_id,
        "tenderText": "",
        "proposals": []
    }
    
    # Process tender document
    try:
        tender_dir = Path("data") / "tenders" / f"tender_{tender_id}"
        tender_files = list(tender_dir.glob("*.pdf"))
        
        if tender_files:
            tender_file = tender_files[0]  # Assume first PDF is the main tender
            result["tenderText"] = extractTextFromPdf(str(tender_file))
    except Exception as e:
        print(f"Error processing tender: {e}")
    
    # Process proposals
    try:
        proposals_dir = Path("data") / "proposals" / f"tender_{tender_id}"
        
        if proposals_dir.exists():
            # Iterate through contractors
            for contractor_dir in proposals_dir.iterdir():
                if contractor_dir.is_dir() and contractor_dir.name.startswith("contractor_"):
                    contractor_id = contractor_dir.name.replace("contractor_", "")
                    
                    # Iterate through companies within contractor
                    for company_dir in contractor_dir.iterdir():
                        if company_dir.is_dir():
                            company_name = company_dir.name
                            
                            # Get all PDF files in company directory
                            pdf_files = list(company_dir.glob("*.pdf"))
                            
                            # Separate principal and attachment files
                            principal_files = [f for f in pdf_files if f.name.startswith("PRINCIPAL_")]
                            # All non-principal files are considered attachments (annexes)
                            attachment_files = [f for f in pdf_files if not f.name.startswith("PRINCIPAL_")]
                            
                            # Sort attachment files to ensure consistent ordering
                            attachment_files.sort(key=lambda x: x.name)
                            
                            proposal_data = {
                                "contractorId": contractor_id,
                                "companyName": company_name,
                                "mainFormText": "",
                                "annexIndexText": "",
                                "annexes": {}
                            }
                            
                            # Extract main form text from principal file
                            if principal_files:
                                principal_file = principal_files[0]
                                proposal_data["mainFormText"] = extractTextFromPdf(str(principal_file))
                                # Extract last page for annexIndexText
                                proposal_data["annexIndexText"] = extractLastPageFromPdf(str(principal_file))
                            
                            # Extract annexes using original filenames (with .pdf extension)
                            for attachment_file in attachment_files:
                                # Use original filename with .pdf extension as the key
                                filename_with_pdf = attachment_file.name
                                proposal_data["annexes"][filename_with_pdf] = extractTextFromPdf(str(attachment_file))
                            
                            result["proposals"].append(proposal_data)
    except Exception as e:
        print(f"Error processing proposals: {e}")
    
    return result


async def generateTenderJsonDataAsync(tender_id: str) -> dict:
    """
    Async version of generateTenderJsonData for use in FastAPI endpoints
    """
    # Since file operations are I/O bound, we can run the sync version
    # in a thread pool for better async performance
    import asyncio
    import concurrent.futures
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = await asyncio.get_event_loop().run_in_executor(
            executor, generateTenderJsonData, tender_id
        )
    
    return result
