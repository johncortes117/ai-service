from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from ..services import llmService
from .state import TenderAnalysisState
from .schemas.masterChecklist import MasterChecklist
from .schemas.aggregatorSchemas import ExecutiveSummary
from .prompts import CREATE_MASTER_CHECKLIST_PROMPT, AGGREGATE_ANALYSIS_PROMPT
from .specialistSubgraph import specialistAuditorGraph
import json # Asegúrate de que esta línea esté al principio del archivo

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
        
        # --- LÍNEAS DE DEPURACIÓN CRUCIALES ---
        print("\n" + "="*50)
        print("--- MasterChecklist CREADO POR EL LLM: ---")
        print(json.dumps(structured_response, indent=2, ensure_ascii=False))
        print("="*50 + "\n")
        # ----------------------------------------
        
        print("--- MasterChecklist CREATED SUCCESSFULLY ---")
        return {"masterChecklist": structured_response}

    except Exception as e:
        print(f"--- ERROR in createMasterChecklistNode: {e} ---")
        # Devolvemos un checklist vacío en caso de error para no romper el grafo
        return {"masterChecklist": {"financialRequirements": [], "technicalRequirements": [], "legalRequirements": []}}



def prepareParallelAuditsNode(state: TenderAnalysisState) -> Dict[str, Any]:
    """
    Prepares the list of inputs for the parallel execution (.map).
    Each input is a dictionary that will initialize the state for one sub-graph run.
    """
    print("--- Dispatching proposals for parallel audit ---")
    
    masterChecklist = state.get("masterChecklist")
    proposals = state.get("proposals", [])
    
    subgraph_inputs = []
    
    for proposal in proposals:
        subgraph_inputs.append(
            {
                "proposal": proposal,
                "masterChecklist": masterChecklist,
                "findings": [] 
            }
        )
    
    return {"subgraphInputs": subgraph_inputs}


async def executeParallelAuditsNode(state: TenderAnalysisState) -> Dict[str, Any]:
    """
    Executes the specialist sub-graph in parallel for each proposal.
    """
    print("--- EXECUTING NODE: executeParallelAuditsNode ---")
    
    subgraph_inputs = state.get("subgraphInputs", [])
    if not subgraph_inputs:
        return {}
    
    # Define a configuration to limit concurrency
    config = RunnableConfig(max_concurrency=2)
    
    individual_reports = await specialistAuditorGraph.abatch(
        subgraph_inputs, config=config
    )
    
    print(f"--- Parallel audits completed for {len(individual_reports)} proposals. ---")
    return {"individualReports": individual_reports}


async def aggregateResultsNode(state: TenderAnalysisState) -> Dict[str, Any]:
    """
    Aggregates the individual audit reports from the parallel runs
    into a final, comparative summary and structured data for charts.
    """
    print("--- 📊 EXECUTING NODE: aggregateResultsNode ---")
    
    individual_reports = state.get("individualReports", [])
    if not individual_reports:
        return {}

    # --- 1. Generate Executive Summary using LLM ---
    
    summary_context = ""
    for report in individual_reports:
        # Use .get() for safe access to nested dictionaries
        analysis = report.get("finalAnalysis", {})
        bidder = analysis.get("bidderName", "Unknown")
        score = analysis.get("scores", {}).get("viabilityTotal", 0)
        
        # --- THE FIX: Change "description" to "observation" to match your Finding schemas ---
        high_findings = [
            f.get("observation", "No details provided.") 
            for f in analysis.get("findings", []) if f.get("severity") == "HIGH"
        ]
        
        summary_context += f"Proposal from: {bidder}\n"
        summary_context += f"Viability Score: {score}/100\n"
        if high_findings:
            summary_context += f"Critical Risks Found: {'; '.join(high_findings)}\n"
        summary_context += "---\n"

    messages = [
        SystemMessage(content=AGGREGATE_ANALYSIS_PROMPT),
        HumanMessage(content=summary_context)
    ]
    
    summary_response = await llmService.invoke_json(
        messages=messages,
        output_schema=ExecutiveSummary,
        model_name="gpt-4o-mini",
        temperature=0.2
    )
    executive_summary = summary_response.get("summary", "No summary could be generated.")

    # --- 2. Build Budget Comparison Object (Data Processing) ---
    
    # This section remains a placeholder with mock data for the hackathon demo,
    # ensuring the UI graph always has something to display.
    budget_categories = []
    budget_proposals = []

    if not budget_proposals:
        budget_categories = ["Design", "Development", "Testing", "Deployment"]
        budget_proposals = [
            {"bidderName": report.get("finalAnalysis", {}).get("bidderName", "Unknown"), "valuesUSD": [10, 50, 20, 20]}
            for report in individual_reports
        ]

    budget_comparison = {
        "categories": budget_categories,
        "proposals": budget_proposals
    }
    
    # This prepares the list of final analysis objects for the next node
    analysis_list = [
        report.get("finalAnalysis") 
        for report in individual_reports 
        if report.get("finalAnalysis") is not None
    ]

    print("--- ✅ Aggregation complete. Executive summary and charts data generated. ---")

    return {
        "analysisResults": analysis_list,
        "executiveSummary": executive_summary,
        "budgetComparison": budget_comparison
    }



def formatFinalResponseNode(state: TenderAnalysisState) -> Dict[str, Any]:
    """
    Assembles the final JSON object in the exact format required by the frontend.
    """
    print("--- Assembling final report for the API ---")

    # The sub-graph returns the 'finalAnalysis' for each proposal
    proposals_analysis = state.get("analysisResults", [])
    
    final_report = {
        "executiveSummary": state.get("executiveSummary", "No summary could be generated."),
        "budgetComparison": state.get("budgetComparison", {}),
        "proposalsAnalysis": proposals_analysis
    }
    
    try:
        output_filename = "output_agent.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            # json.dump escribe el diccionario a un archivo en formato JSON
            # indent=2 lo hace legible para los humanos (pretty-print)
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        print(f"--- ✅ Final report saved to {output_filename} ---")
    except Exception as e:
        print(f"--- ❌ ERROR: Could not save final report to file: {e} ---")
    
    return {"finalReport": final_report}