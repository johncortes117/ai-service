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
    "generateTenderJsonDataAsync"
]