from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from ..services import llmService
from .state import TenderAnalysisState
from .schemas.masterChecklist import MasterChecklist
from .prompts import CREATE_MASTER_CHECKLIST_PROMPT


async def createMasterChecklistNode(state: TenderAnalysisState) -> Dict[str, Any]:
    """
    Reads the tender text and uses an LLM to generate a dynamic,
    structured, and categorized MasterChecklist of all requirements.
    """
    print("--- EXECUTING NODE: createMasterChecklistNode ---")
    
    tenderText = state.get("tenderText")
    
    if not tenderText:
        raise ValueError("Tender text not found in state. Cannot create checklist.")

    messages = [
        SystemMessage(content=CREATE_MASTER_CHECKLIST_PROMPT),
        HumanMessage(content=tenderText)
    ]
    
    try:
        structured_response = await llmService.invoke_json(
            messages=messages,
            output_schema=MasterChecklist,
            model_name="gpt-4o-mini",
            temperature=0.3
        )
        
        print("--- MasterChecklist CREATED SUCCESSFULLY ---")
        return {"masterChecklist": structured_response}

    except Exception as e:
        print(f"--- ERROR in createMasterChecklistNode: {e} ---")
        return {"error": f"Failed to create MasterChecklist: {e}"}