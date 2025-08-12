from pydantic import BaseModel, Field

class ExecutiveSummary(BaseModel):
    """Schema for the final executive summary."""
    summary: str = Field(description="A concise, decisive executive summary comparing all proposals and providing a final recommendation.")