from fastapi import UploadFile, HTTPException
import os
import shutil
import zipfile
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from ..constants import TEMP_DIR, ALLOWED_TYPES, ERROR_INVALID_FILE_TYPE
from .file_service import create_temp_filepath, save_uploaded_file, generate_unique_filename


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file using PyMuPDF (fitz)
    """
    if fitz is None:
        raise Exception("PyMuPDF (fitz) is not installed. Please install it with: poetry add PyMuPDF")
    
    text = ""
    try:
        # Open PDF document
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        
        # Close document
        doc.close()
        
    except Exception as e:
        raise Exception(f"Error processing PDF {pdf_path}: {e}")
    
    if text.strip() == "":
        # If text extraction failed, try OCR or alternative detection
        return llm_text_detection(pdf_path)
    else:
        return text


def llm_text_detection(pdf_path: str) -> str:
    """Placeholder for OCR or LLM-based text detection"""
    return f"[PDF with no extractable text detected: {os.path.basename(pdf_path)}. OCR implementation pending]"


async def process_pdf_zip_files(file: UploadFile) -> dict:
    """
    Function to process PDF files or ZIP files containing PDFs
    """
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"{ERROR_INVALID_FILE_TYPE} Received: {file.content_type}"
        )
    
    temp_file_path = None
    extract_dir = None
    
    try:
        # Create unique name for temp file
        temp_file_path = create_temp_filepath(file.filename)
        
        # Save file temporarily
        await save_uploaded_file(file, temp_file_path)
        
        processed_files = []
        
        # Process according to file type
        if file.content_type == "application/pdf":
            # Process PDF directly
            extracted_text = extract_text_from_pdf(temp_file_path)
            processed_files.append({
                "filename": file.filename,
                "type": "pdf",
                "text_length": len(extracted_text),
                "status": "processed",
                "content": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text  # Content preview
            })
            
        elif file.content_type in ["application/zip", "application/x-zip-compressed"]:
            # Extract and process files from ZIP
            extract_dir = os.path.join(TEMP_DIR, f"extracted_{hash(file.filename)}")
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Search for PDF files in extracted ZIP
            for root, dirs, files in os.walk(extract_dir):
                for filename in files:
                    if filename.lower().endswith('.pdf'):
                        pdf_path = os.path.join(root, filename)
                        try:
                            extracted_text = extract_text_from_pdf(pdf_path)
                            processed_files.append({
                                "filename": filename,
                                "type": "pdf_from_zip",
                                "text_length": len(extracted_text),
                                "status": "processed",
                                "content": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
                            })
                        except Exception as e:
                            processed_files.append({
                                "filename": filename,
                                "type": "pdf_from_zip",
                                "status": "error",
                                "error": str(e)
                            })
        
        return {
            "original_filename": file.filename,
            "content_type": file.content_type,
            "processed_files": processed_files,
            "total_files": len(processed_files)
        }
        
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if extract_dir and os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)


async def extract_document_information(file: UploadFile) -> dict:
    """
    Simple reusable function to extract text from a PDF document
    
    Args:
        file: UploadFile object containing the PDF document
    
    Returns:
        dict: Basic information with extracted text
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files are supported. Received: {file.filename}"
        )
    
    temp_file_path = None
    
    try:
        # Create temporary file
        temp_file_path = os.path.join(TEMP_DIR, generate_unique_filename("doc", file.filename))
        
        # Save file temporarily
        await save_uploaded_file(file, temp_file_path)
        
        # Extract text content
        extracted_text = extract_text_from_pdf(temp_file_path)
        
        return {
            "filename": file.filename,
            "text": extracted_text,
            "text_length": len(extracted_text),
            "status": "success"
        }
        
    except Exception as e:
        return {
            "filename": file.filename,
            "text": "",
            "text_length": 0,
            "status": "error",
            "error": str(e)
        }
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
