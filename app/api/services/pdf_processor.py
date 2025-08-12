from fastapi import FastAPI, UploadFile, File, HTTPException
import fitz 

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file using PyMuPDF
    """
    text = ""
    
    try:
        with fitz.open(file_path) as pdf:
            for page in pdf:
                page_text = page.get_text()
                text += page_text + " "
        
        return text.strip()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")