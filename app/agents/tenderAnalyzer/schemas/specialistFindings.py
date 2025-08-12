from pydantic import BaseModel, Field
from typing import Optional, Union, Literal

class BaseFinding(BaseModel):
    """
    The base model with fields common to ALL findings.
    """
    requirementName: str = Field(
        description="The name of the requirement being checked."
    )
    requirementDetails: str = Field(
        description="The specific details of the requirement from the tender, e.g., '>= $80,187.24'."
    )
    isCompliant: bool = Field(
        description="The final verdict. True if the proposal complies with the tender's requirement."
    )
    severity: Literal["OK", "WARNING", "CRITICAL"] = Field(
        description="The severity of the finding. OK for compliance, WARNING for minor issues, CRITICAL for major failures."
    )
    observation: str = Field(
        description="The agent's summary and reasoning for its conclusion."
    )
    recommendation: str = Field(
        description="The agent's suggested action for the user."
    )

class FinancialFinding(BaseFinding):
    """
    The specific output schema for the Financial Specialist.
    """
    declaredValue: Optional[str] = Field(
        description="The value for the requirement as declared in the main proposal form."
    )
    foundInAnnexValue: Optional[str] = Field(
        description="The value found in the corresponding annex document as evidence."
    )
    isConsistent: bool = Field(
        description="True if the declared value matches the value found in the annex."
    )

class TechnicalFinding(BaseFinding):
    """
    The specific output schema for the Technical Specialist.
    """
    declaredValue: Optional[str] = Field(
        description="The value or statement declared in the main proposal form."
    )
    foundInAnnexValue: Optional[str] = Field(
        description="The evidence or statement found in the corresponding annex."
    )
    isConsistent: bool = Field(
        description="True if the declaration is consistent with the annex."
    )

class LegalFinding(BaseFinding):
    """
    The specific output schema for the Legal Specialist.
    """
    declaredCompliance: Optional[str] = Field(
        description="The bidder's stated compliance in the main form (e.g., 'Sí', 'Acepto')."
    )
    annexEvidenceSummary: Optional[str] = Field(
        description="A summary of the evidence found in the legal annex."
    )
    isConsistent: bool = Field(
        description="True if the declaration is consistent with the annex's content."
    )

AnyFinding = Union[FinancialFinding, TechnicalFinding, LegalFinding]