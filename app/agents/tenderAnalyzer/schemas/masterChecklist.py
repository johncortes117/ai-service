from pydantic import BaseModel, Field
from typing import List

class Requirement(BaseModel):
    """
    A generic model to capture any single requirement found in the tender.
    The specialist responsible is determined by the list this requirement
    is placed in within the MasterChecklist.
    """
    name: str = Field(description="The specific name of the requirement, e.g., 'Patrimonio Mínimo' or 'Equipo mínimo'.")
    details: str = Field(description="All relevant details, values, and conditions for the requirement, e.g., '>= $80,187.24' or 'Presentar certificados ISO 9001'.")

class MasterChecklist(BaseModel):
    """
    A dynamically generated checklist where the LLM has already classified
    all requirements by assigning them to the appropriate specialist's list.
    """
    financialRequirements: List[Requirement] = Field(description="List of all requirements to be verified by the Financial Specialist.")
    technicalRequirements: List[Requirement] = Field(description="List of all requirements to be verified by the Technical Specialist.")
    legalRequirements: List[Requirement] = Field(description="List of all requirements to be verified by the Legal Specialist.")