"""
Utilities for PDF and ZIP file processing
"""
import json
import os
import shutil
import zipfile
from pathlib import Path
from fastapi import UploadFile, HTTPException
import fitz  # PyMuPDF

# Directory configuration
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)


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


async def extractLastPageFromUploadFile(file: UploadFile) -> str:
    """Extract text from the last page of an uploaded PDF file"""
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Expected PDF, received: {file.content_type}"
        )
    
    temp_file_path = None
    try:
        # Create temporary file
        file_extension = Path(file.filename).suffix
        temp_filename = f"temp_lastpage_{hash(file.filename)}{file_extension}"
        temp_file_path = os.path.join(TEMP_DIR, temp_filename)
        
        # Save uploaded file to temp location
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract text from last page
        last_page_text = extractLastPageFromPdf(temp_file_path)
        
        return last_page_text
        
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


async def processPdfZipFiles(file: UploadFile) -> dict:
    """Function to process PDF or ZIP files containing PDFs"""
    allowed_types = ["application/pdf", "application/zip", "application/x-zip-compressed"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Expected PDF or ZIP, received: {file.content_type}"
        )
    
    temp_file_path = None
    extract_dir = None
    
    try:
        file_extension = Path(file.filename).suffix
        temp_filename = f"temp_{hash(file.filename)}{file_extension}"
        temp_file_path = os.path.join(TEMP_DIR, temp_filename)
        
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        processed_files = []
        
        if file.content_type == "application/pdf":
            extracted_text = extractTextFromPdf(temp_file_path)
            processed_files.append({
                "filename": file.filename,
                "type": "pdf",
                "text_length": len(extracted_text),
                "status": "processed",
                "content": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
            })
            
        elif file.content_type in ["application/zip", "application/x-zip-compressed"]:
            extract_dir = os.path.join(TEMP_DIR, f"extracted_{hash(file.filename)}")
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            for root, dirs, files in os.walk(extract_dir):
                for filename in files:
                    if filename.lower().endswith('.pdf'):
                        pdf_path = os.path.join(root, filename)
                        try:
                            extracted_text = extractTextFromPdf(pdf_path)
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


def createProposalStructure(tender_id: str, contractor_id: str, company_name: str) -> str:
    """
    Create directory structure for a proposal
    New structure: data/proposals/tender_{tender_id}/contractor_{contractor_id}/company_name/
    Returns the path of the created directory
    """
    # Clean names to avoid issues with special characters
    # Allow alphanumeric, spaces, hyphens, underscores, and dots
    company_name_clean = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
    
    # Replace multiple spaces with single space and remove leading/trailing spaces
    company_name_clean = ' '.join(company_name_clean.split())
    
    # If name becomes empty after cleaning, use a default
    if not company_name_clean:
        company_name_clean = "UNKNOWN_COMPANY"
    
    # Add prefixes to make directories more descriptive
    tender_dir_name = f"tender_{tender_id}"
    contractor_dir_name = f"contractor_{contractor_id}"
    
    # Create structure: data/proposals/tender_X/contractor_Y/company_name/
    base_dir = "./data/proposals"
    proposal_dir = os.path.join(base_dir, tender_dir_name, contractor_dir_name, company_name_clean)
    
    try:
        os.makedirs(proposal_dir, exist_ok=True)
    except Exception as e:
        raise Exception(f"Error creating directory structure: {e}")
    
    return proposal_dir


async def saveFileWithUuid(file: UploadFile, directory: str, prefix: str) -> str:
    """
    Save a file with unique UUID and return the saved filename
    """
    import uuid
    
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{prefix}_{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(directory, filename)
    
    # Reset file pointer to beginning in case it was read before
    await file.seek(0)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Reset file pointer again for potential future reads
    await file.seek(0)
    
    return filename


def getNextTenderId() -> str:
    """
    Get the next available tender ID by checking existing directories
    Returns the next sequential number as string (without tender_ prefix)
    """
    baseDir = "./data/tenders"
    if not os.path.exists(baseDir):
        return "1"
    
    # Get all directories that start with "tender_"
    existingIds = []
    for item in os.listdir(baseDir):
        itemPath = os.path.join(baseDir, item)
        if os.path.isdir(itemPath) and item.startswith("tender_"):
            # Extract the number part after "tender_"
            try:
                idNumber = item.replace("tender_", "")
                if idNumber.isdigit():
                    existingIds.append(int(idNumber))
            except:
                continue
    
    if not existingIds:
        return "1"
    
    return str(max(existingIds) + 1)


def createTenderDirectory(tender_id: str) -> str:
    """
    Create tender directory structure: data/tenders/tender_{tender_id}/
    Returns the directory path
    """
    base_dir = "./data/tenders"
    tender_dir_name = f"tender_{tender_id}"
    tender_dir = os.path.join(base_dir, tender_dir_name)
    os.makedirs(tender_dir, exist_ok=True)
    
    return tender_dir


def checkTenderExists(tender_id: str) -> bool:
    """
    Check if a tender directory already exists and contains files
    """
    tender_dir_name = f"tender_{tender_id}"
    tender_dir = os.path.join("./data/tenders", tender_dir_name)
    if not os.path.exists(tender_dir):
        return False
    
    # Check if directory has any PDF files
    for item in os.listdir(tender_dir):
        if item.lower().endswith('.pdf'):
            return True
    
    return False


async def saveTenderPdf(file: UploadFile, tender_id: str) -> str:
    """
    Save tender PDF file with specific naming convention
    """
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Expected PDF, received: {file.content_type}"
        )
    
    tender_dir = createTenderDirectory(tender_id)
    
    # Create filename: TENDER_{tender_id}.pdf
    filename = f"TENDER_{tender_id}.pdf"
    file_path = os.path.join(tender_dir, filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return filename


def generateTenderJsonData(tender_id: str) -> dict:
    """
    Generate complete JSON data for a tender including all proposals
    Format required for external endpoint connection
    """
    import json
    from pathlib import Path
    
    # Paths for tender and proposals
    tender_dir = f"./data/tenders/tender_{tender_id}"
    proposals_dir = f"./data/proposals/tender_{tender_id}"
    
    # Initialize result structure
    result = {
        "tenderName": "",
        "tenderText": "",
        "proposals": []
    }
    
    # Extract tender information
    try:
        tender_path = Path(tender_dir)
        if tender_path.exists():
            # Find the tender PDF file
            tender_files = list(tender_path.glob("*.pdf"))
            if tender_files:
                tender_file = tender_files[0]  # Take the first PDF
                result["tenderName"] = tender_file.stem  # Filename without extension
                result["tenderText"] = extractTextFromPdf(str(tender_file))
    except Exception as e:
        print(f"Error processing tender: {e}")
        result["tenderName"] = f"TENDER_{tender_id}"
        result["tenderText"] = f"Error extracting tender content: {e}"
    
    # Extract proposals information
    try:
        proposals_path = Path(proposals_dir)
        if proposals_path.exists():
            # Iterate through each contractor directory
            for contractor_dir in proposals_path.iterdir():
                if contractor_dir.is_dir() and contractor_dir.name.startswith("contractor_"):
                    # Iterate through each company directory
                    for company_dir in contractor_dir.iterdir():
                        if company_dir.is_dir():
                            proposal_data = {
                                "bidderName": company_dir.name,
                                "mainFormText": "",
                                "annexIndexText": "",
                                "annexes": {}
                            }
                            
                            # Process files in company directory
                            pdf_files = list(company_dir.glob("*.pdf"))
                            principal_files = [f for f in pdf_files if f.name.startswith("PRINCIPAL_")]
                            attachment_files = [f for f in pdf_files if f.name.startswith("ATTACHMENT_")]
                            
                            # Extract main form text (PRINCIPAL file)
                            if principal_files:
                                principal_file = principal_files[0]
                                proposal_data["mainFormText"] = extractTextFromPdf(str(principal_file))
                                # Extract last page for annexIndexText
                                proposal_data["annexIndexText"] = extractLastPageFromPdf(str(principal_file))
                            
                            # Extract annexes (ATTACHMENT files)
                            for i, attachment_file in enumerate(attachment_files, 1):
                                annex_key = f"annex{i}"
                                proposal_data["annexes"][annex_key] = extractTextFromPdf(str(attachment_file))
                            
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



def saveSseData(payload: dict, data_file: str) -> dict:
    """
    Guarda el JSON recibido en el archivo para SSE.
    """
    import json
    try:
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return {"message": "Data saved successfully"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error saving data: {str(e)}")


def streamSseData(data_file: str):

    import time
    import json
    import os
    last_is_loading = None
    while True:
        try:
            if os.path.exists(data_file):
                with open(data_file, "r", encoding="utf-8") as f:
                    data = f.read()
                try:
                    json_data = json.loads(data)
                except Exception:
                    json_data = {}
                is_loading = json_data.get("isLoading")
                # Si isLoading cambia a True, envía todo el JSON
                if last_is_loading is not None and is_loading != last_is_loading and is_loading is True:
                    yield f"data: {json.dumps(json_data, ensure_ascii=False)}\n\n"
                else:
                    partial = {"state": json_data.get("state"), "isLoading": is_loading}
                    yield f"data: {json.dumps(partial, ensure_ascii=False)}\n\n"
                last_is_loading = is_loading
            else:
                yield "data: {}\n\n"
        except Exception as e:
            yield f"data: {{'error': '{str(e)}'}}\n\n"
        time.sleep(2)


def hasStateTransitioned(data_file: str, from_state: str = "En Análisis", to_state: str = "Completado") -> bool:
    """
    Comprueba si el estado del JSON en data_file ha cambiado de from_state a to_state.
    """

    if not os.path.exists(data_file):
        return False
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Buscar el estado actual
        current_state = None
        # Soporta tanto nivel raíz como tenderDetails["state"]
        if "state" in data:
            current_state = data["state"]
        elif "tenderDetails" in data and "state" in data["tenderDetails"]:
            current_state = data["tenderDetails"]["state"]
        # Si el estado es igual al estado final, retorna True solo si antes era el estado inicial
        # (esto requiere que la función se llame en el momento del cambio)
        return current_state == to_state
    except Exception:
        return False
