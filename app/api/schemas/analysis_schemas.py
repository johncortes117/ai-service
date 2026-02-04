from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class AnalysisStatus(BaseModel):
    """Schema for tracking the status of a tender analysis"""
    tender_id: str = Field(description="ID of the tender being analyzed")
    status: Literal["pending", "processing", "completed", "failed"] = Field(
        description="Current status of the analysis"
    )
    progress: int = Field(
        ge=0, le=100, 
        description="Progress percentage (0-100)"
    )
    current_step: Optional[str] = Field(
        default=None,
        description="Current step being executed (e.g., 'Creating master checklist')"
    )
    message: Optional[str] = Field(
        default=None,
        description="Human-readable status message"
    )
    started_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when analysis started"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when analysis completed"
    )
    error_details: Optional[str] = Field(
        default=None,
        description="Error message if status is 'failed'"
    )


class AnalysisProgressEvent(BaseModel):
    """Schema for SSE progress events"""
    event_type: Literal["progress", "node_complete", "error", "complete"] = Field(
        description="Type of event being emitted"
    )
    tender_id: str = Field(description="ID of the tender")
    progress: int = Field(ge=0, le=100, description="Progress percentage")
    node_name: Optional[str] = Field(
        default=None,
        description="Name of the graph node (e.g., 'createMasterChecklist')"
    )
    message: str = Field(description="Event message")
    timestamp: datetime = Field(default_factory=datetime.now)


class AnalysisHistoryItem(BaseModel):
    """Schema for a single analysis history entry"""
    tender_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_proposals: int = 0
    has_report: bool = False


class AnalysisHistoryResponse(BaseModel):
    """Schema for analysis history list response"""
    total: int = Field(description="Total number of analyses")
    analyses: list[AnalysisHistoryItem] = Field(description="List of analysis history items")
