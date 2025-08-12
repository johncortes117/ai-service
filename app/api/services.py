from fastapi import UploadFile, HTTPException
import os
import shutil
import zipfile
import fitz  # PyMuPDF
from pathlib import Path

UPLOAD_DIR = "uploads"
TEMP_DIR = "temp_files"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

#-------------------------------------------------------------------------------------
async def procesar_archivos_pdf_zip(file: UploadFile) -> dict:
    """
    Función para procesar archivos PDF o ZIP que contengan PDFs
    """
    # Validar tipo de archivo
    allowed_types = ["application/pdf", "application/zip", "application/x-zip-compressed"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de archivo no válido. Se esperaba PDF o ZIP, recibido: {file.content_type}"
        )
    
    temp_file_path = None
    extract_dir = None
    
    try:
        # Crear nombre único para el archivo temporal
        file_extension = Path(file.filename).suffix
        temp_filename = f"temp_{hash(file.filename)}{file_extension}"
        temp_file_path = os.path.join(TEMP_DIR, temp_filename)
        
        # Guardar archivo temporalmente
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        processed_files = []
        
        # Procesar según el tipo de archivo
        if file.content_type == "application/pdf":
            # Procesar PDF directamente
            texto_extraido = extraer_texto_de_pdf(temp_file_path)
            processed_files.append({
                "filename": file.filename,
                "type": "pdf",
                "text_length": len(texto_extraido),
                "status": "processed",
                "content": texto_extraido[:500] + "..." if len(texto_extraido) > 500 else texto_extraido  # Preview del contenido
            })
            
        elif file.content_type in ["application/zip", "application/x-zip-compressed"]:
            # Extraer y procesar archivos del ZIP
            extract_dir = os.path.join(TEMP_DIR, f"extracted_{hash(file.filename)}")
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Buscar archivos PDF en el ZIP extraído
            for root, dirs, files in os.walk(extract_dir):
                for filename in files:
                    if filename.lower().endswith('.pdf'):
                        pdf_path = os.path.join(root, filename)
                        try:
                            texto_extraido = extraer_texto_de_pdf(pdf_path)
                            processed_files.append({
                                "filename": filename,
                                "type": "pdf_from_zip",
                                "text_length": len(texto_extraido),
                                "status": "processed",
                                "content": texto_extraido[:500] + "..." if len(texto_extraido) > 500 else texto_extraido
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
        # Limpiar archivos temporales (siempre se ejecuta)
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if extract_dir and os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)

#----------------------------------------------------------------------------------------------------------------------------------
def extraer_texto_de_pdf(pdf_path: str) -> str:
    """
    Extrae texto de un archivo PDF usando PyMuPDF (fitz)
    """
    texto = ""
    try:
        doc = fitz.open(pdf_path)

        for pagina_num in range(len(doc)):
            pagina = doc.load_page(pagina_num)
            texto += pagina.get_text()
        
        doc.close()
        
    except Exception as e:
        raise Exception(f"Error al procesar el PDF {pdf_path}: {e}")
    
    if texto.strip() == "":
        # Si no se pudo extraer texto, intentar con OCR o detección alternativa
        return llm_texto_detection(pdf_path)
    else:
        return texto

#----------------------------------------------------------------------------------------------------------------------------------
