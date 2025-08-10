import uuid
import os
from typing import List, Optional
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException

from app.api.services import procesar_archivos_pdf_zip


app = FastAPI(
    title="AI Service API",
    description="API for AI services including blueprint creation and document processing",
    version="0.1.0"
)

@app.get("/")
async def read_root():
    return {"message": "AI Service API is running!", "status": "healthy"}


@app.post("/procesar_y_estructurar_pdfs")
async def procesar_y_estructurar_pdfs(file: UploadFile = File(...)):
    """
    Procesa archivos PDF o ZIP que contengan PDFs
    """
    try:
        result = await procesar_archivos_pdf_zip(file)
        return {
            "message": "Archivos procesados exitosamente",
            **result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")



BASE_UPLOAD_DIRECTORY = "./proposals_uploads"

@app.post("/proposals/upload_differentiated/{id_licitacion}/{nombre_empresa}/{id_proposal}")
async def upload_differentiated_files(
    id_licitacion: str,
    nombre_empresa: str,
    id_proposal: str,
    principal_file: UploadFile = File(...),
    anexos_files: List[UploadFile] = File(...)
):
    """
    Sube y organiza archivos de propuestas con estructura jerárquica:
    proposals_uploads/{id_licitacion}/{nombre_empresa}/{id_proposal}/
    """
    # Crear estructura de directorios: licitacion/empresa/proposal
    proposal_dir = os.path.join(
        BASE_UPLOAD_DIRECTORY, 
        id_licitacion, 
        nombre_empresa, 
        id_proposal
    )
    os.makedirs(proposal_dir, exist_ok=True)

    # Procesar archivo principal
    principal_filename = f"PRINCIPAL_{uuid.uuid4()}{os.path.splitext(principal_file.filename)[1]}"
    principal_path = os.path.join(proposal_dir, principal_filename)
    
    with open(principal_path, "wb") as buffer:
        buffer.write(await principal_file.read())

    # Procesar archivos anexos
    saved_anexos = []
    for anexo_file in anexos_files:
        anexo_filename = f"ANEXO_{uuid.uuid4()}{os.path.splitext(anexo_file.filename)[1]}"
        anexo_path = os.path.join(proposal_dir, anexo_filename)
        
        with open(anexo_path, "wb") as buffer:
            buffer.write(await anexo_file.read())
        saved_anexos.append(anexo_filename)

    return {
        "message": "Archivos recibidos y clasificados correctamente.",
        "id_licitacion": id_licitacion,
        "nombre_empresa": nombre_empresa,
        "id_proposal": id_proposal,
        "ruta_completa": proposal_dir,
        "archivo_principal": principal_filename,
        "archivos_anexos": saved_anexos,
        "total_anexos": len(saved_anexos)
    }