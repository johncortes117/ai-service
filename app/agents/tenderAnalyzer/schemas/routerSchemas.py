from pydantic import BaseModel, Field
from typing import List

class RequirementAnnexMap(BaseModel):
    """Represents the mapping of a single requirement to its referenced annex filename."""
    requirementName: str = Field(description="The exact name of the requirement from the master checklist.")
    annexFilename: str = Field(description="The exact filename of the annex referenced in the proposal form for this requirement (e.g., 'ANEXO_1.pdf').")

class AnnexMapOutput(BaseModel):
    """The expected output from the LLM after mapping all requirements."""
    annexMap: List[RequirementAnnexMap]