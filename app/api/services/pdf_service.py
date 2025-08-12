# services/pdf_service.py
import os
import fitz  # PyMuPDF

def llm_text_detection(pdf_path: str) -> str:
    """Placeholder for future OCR or LLM-based text detection."""
    filename = os.path.basename(pdf_path)
    return f"[PDF with no extractable text detected: {filename}. OCR pending implementation]"

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts all text from a PDF file using PyMuPDF."""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        # It's better to raise the exception to be handled by the calling service
        raise Exception(f"Error processing PDF {pdf_path}: {e}")
    
    return text if text.strip() else llm_text_detection(pdf_path)

def extract_last_page_from_pdf(pdf_path: str) -> str:
    """Extracts text from only the last page of a PDF file."""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            if doc.page_count == 0:
                return "[PDF has no pages]"
            
            last_page = doc.load_page(doc.page_count - 1)
            text = last_page.get_text()
    except Exception as e:
        raise Exception(f"Error processing last page of PDF {pdf_path}: {e}")
    
    filename = os.path.basename(pdf_path)
    return text if text.strip() else f"[Last page of PDF has no extractable text: {filename}]"