"""Utils package for AI Service API"""

from .proposal_utils import (
    processPdfZipFiles,
    createProposalStructure,
    saveFileWithUuid,
    saveAttachmentWithOriginalName,
    getNextTenderId,
    checkTenderExists,
    saveTenderPdf,
    getContractorsByTender
)

from .pdf_json_utils import (
    extractTextFromPdf,
    extractLastPageFromPdf,
    generateTenderJsonData,
    generateTenderJsonDataAsync
)


# Wrappers para funciones SSE usando ruta fija
from app.api.service_utils import saveSseData as _saveSseData, streamSseData as _streamSseData, hasStateTransitioned as _hasStateTransitioned

DATA_FILE = "./data/sse_data.json"

def saveSseData(payload):
    return _saveSseData(payload, DATA_FILE)

def streamSseData():
    return _streamSseData(DATA_FILE)

def hasStateTransitioned(from_state="En Análisis", to_state="Completado"):
    return _hasStateTransitioned(DATA_FILE, from_state, to_state)

__all__ = [
    "processPdfZipFiles",
    "createProposalStructure", 
    "saveFileWithUuid",
    "saveAttachmentWithOriginalName",
    "getNextTenderId",
    "checkTenderExists",
    "saveTenderPdf",
    "getContractorsByTender",
    "extractTextFromPdf",
    "extractLastPageFromPdf",
    "generateTenderJsonData",
    "generateTenderJsonDataAsync",
    "saveSseData",
    "streamSseData",
    "hasStateTransitioned"
]