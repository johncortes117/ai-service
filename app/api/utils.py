"""
Utilities for PDF and ZIP file processing
"""
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
    
    tempFilePath = None
    try:
        # Create temporary file
        fileExtension = Path(file.filename).suffix
        tempFilename = f"temp_lastpage_{hash(file.filename)}{fileExtension}"
        tempFilePath = os.path.join(TEMP_DIR, tempFilename)
        
        # Save uploaded file to temp location
        with open(tempFilePath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract text from last page
        lastPageText = extractLastPageFromPdf(tempFilePath)
        
        return lastPageText
        
    finally:
        # Clean up temporary file
        if tempFilePath and os.path.exists(tempFilePath):
            os.remove(tempFilePath)


async def processPdfZipFiles(file: UploadFile) -> dict:
    """Function to process PDF or ZIP files containing PDFs"""
    allowedTypes = ["application/pdf", "application/zip", "application/x-zip-compressed"]
    if file.content_type not in allowedTypes:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Expected PDF or ZIP, received: {file.content_type}"
        )
    
    tempFilePath = None
    extractDir = None
    
    try:
        fileExtension = Path(file.filename).suffix
        tempFilename = f"temp_{hash(file.filename)}{fileExtension}"
        tempFilePath = os.path.join(TEMP_DIR, tempFilename)
        
        with open(tempFilePath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        processedFiles = []
        
        if file.content_type == "application/pdf":
            extractedText = extractTextFromPdf(tempFilePath)
            processedFiles.append({
                "filename": file.filename,
                "type": "pdf",
                "text_length": len(extractedText),
                "status": "processed",
                "content": extractedText[:500] + "..." if len(extractedText) > 500 else extractedText
            })
            
        elif file.content_type in ["application/zip", "application/x-zip-compressed"]:
            extractDir = os.path.join(TEMP_DIR, f"extracted_{hash(file.filename)}")
            os.makedirs(extractDir, exist_ok=True)
            
            with zipfile.ZipFile(tempFilePath, 'r') as zipRef:
                zipRef.extractall(extractDir)
            
            for root, dirs, files in os.walk(extractDir):
                for filename in files:
                    if filename.lower().endswith('.pdf'):
                        pdfPath = os.path.join(root, filename)
                        try:
                            extractedText = extractTextFromPdf(pdfPath)
                            processedFiles.append({
                                "filename": filename,
                                "type": "pdf_from_zip",
                                "text_length": len(extractedText),
                                "status": "processed",
                                "content": extractedText[:500] + "..." if len(extractedText) > 500 else extractedText
                            })
                        except Exception as e:
                            processedFiles.append({
                                "filename": filename,
                                "type": "pdf_from_zip",
                                "status": "error",
                                "error": str(e)
                            })
        
        return {
            "original_filename": file.filename,
            "content_type": file.content_type,
            "processed_files": processedFiles,
            "total_files": len(processedFiles)
        }
        
    finally:
        if tempFilePath and os.path.exists(tempFilePath):
            os.remove(tempFilePath)
        if extractDir and os.path.exists(extractDir):
            shutil.rmtree(extractDir)


def createProposalStructure(tenderId: str, contractorId: str, companyName: str) -> str:
    """
    Create directory structure for a proposal
    New structure: data/propuestas/tender_{tenderId}/contractor_{contractorId}/companyName/
    Returns the path of the created directory
    """
    # Clean names to avoid issues with special characters
    companyNameClean = "".join(c for c in companyName if c.isalnum() or c in (' ', '-', '_')).rstrip()
    
    # Add prefixes to make directories more descriptive
    tenderDirName = f"tender_{tenderId}"
    contractorDirName = f"contractor_{contractorId}"
    
    # Create structure: data/propuestas/tender_X/contractor_Y/companyName/
    baseDir = "./data/propuestas"
    proposalDir = os.path.join(baseDir, tenderDirName, contractorDirName, companyNameClean)
    os.makedirs(proposalDir, exist_ok=True)
    
    return proposalDir


async def saveFileWithUuid(file: UploadFile, directory: str, prefix: str) -> str:
    """
    Save a file with unique UUID and return the saved filename
    """
    import uuid
    
    fileExtension = os.path.splitext(file.filename)[1]
    filename = f"{prefix}_{uuid.uuid4()}{fileExtension}"
    filePath = os.path.join(directory, filename)
    
    with open(filePath, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
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


def createTenderDirectory(tenderId: str) -> str:
    """
    Create tender directory structure: data/tenders/tender_{tenderId}/
    Returns the directory path
    """
    baseDir = "./data/tenders"
    tenderDirName = f"tender_{tenderId}"
    tenderDir = os.path.join(baseDir, tenderDirName)
    os.makedirs(tenderDir, exist_ok=True)
    
    return tenderDir


def checkTenderExists(tenderId: str) -> bool:
    """
    Check if a tender directory already exists and contains files
    """
    tenderDirName = f"tender_{tenderId}"
    tenderDir = os.path.join("./data/tenders", tenderDirName)
    if not os.path.exists(tenderDir):
        return False
    
    # Check if directory has any PDF files
    for item in os.listdir(tenderDir):
        if item.lower().endswith('.pdf'):
            return True
    
    return False


async def saveTenderPdf(file: UploadFile, tenderId: str) -> str:
    """
    Save tender PDF file with specific naming convention
    """
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Expected PDF, received: {file.content_type}"
        )
    
    tenderDir = createTenderDirectory(tenderId)
    
    # Create filename: TENDER_{tenderId}.pdf
    filename = f"TENDER_{tenderId}.pdf"
    filePath = os.path.join(tenderDir, filename)
    
    with open(filePath, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return filename
