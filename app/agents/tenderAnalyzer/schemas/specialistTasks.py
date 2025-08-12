from pydantic import BaseModel, Field
from .masterChecklist import Requirement

class SpecialistTask(BaseModel):
    """
    Represents a single, focused task for a specialist agent.
    This is the "surgical package" created by the router.
    """
    requirementToVerify: Requirement = Field(description="The specific requirement object from the MasterChecklist to be audited.")
    evidenceText: str = Field(description="The full text content of the specific annex where the evidence should be found.")
    mainFormText: str = Field(description="The full text of the main proposal form for additional context.")