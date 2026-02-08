from typing import TypedDict, List, Dict, Any, Optional, Annotated
from .schemas.masterChecklist import MasterChecklist

class TenderAnalysisState(TypedDict):
    """
    Represents the full state of the tender analysis pipeline.
    """
    tenderText: str
    proposals: List[Dict[str, Any]]
    masterChecklist: Optional[MasterChecklist]
    analysisResults: Optional[List[Dict[str, Any]]]
    subgraphInputs: Optional[List[Dict[str, Any]]]
    individualReports: Optional[List[Dict[str, Any]]]
    executiveSummary: Optional[str]
    finalReport: Optional[Dict[str, Any]]

class ProposalAuditState(TypedDict):
    """
    Represents the state for auditing a single proposal.
    """
    proposal: Dict[str, Any]
    masterChecklist: MasterChecklist
    technicalTasks: Optional[List[Dict[str, Any]]]
    financialTasks: Optional[List[Dict[str, Any]]]
    legalTasks: Optional[List[Dict[str, Any]]]
    findings: Annotated[List[Dict[str, Any]], lambda a, b: a + b]
    scores: Optional[Dict[str, int]]
    finalAnalysis: Optional[Dict[str, Any]]