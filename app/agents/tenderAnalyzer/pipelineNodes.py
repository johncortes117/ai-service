from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from ..services import llmService
from .state import TenderAnalysisState
from .schemas.masterChecklist import MasterChecklist
from .schemas.aggregatorSchemas import ExecutiveSummary
from .prompts import CREATE_MASTER_CHECKLIST_PROMPT, AGGREGATE_ANALYSIS_PROMPT
from .specialistSubgraph import specialistAuditorGraph
import json
import os

# Get tender_id from environment for SSE progress tracking
def get_current_tender_id():
    """Helper to get current tender ID from environment or context"""
    return os.environ.get("CURRENT_TENDER_ID", "unknown")

def emit_progress(event_type: str, progress: int, message: str, node_name: str = None):
    """Emit progress event to SSE stream"""
    try:
        from app.api.services.sse_service import emit_progress_event
        tender_id = get_current_tender_id()
        emit_progress_event(tender_id, event_type, progress, message, node_name)
    except Exception as e:
        print(f"Warning: Could not emit progress event: {e}")

async def createMasterChecklistNode(state: TenderAnalysisState) -> Dict[str, Any]:
    """
    Reads the tender text and uses an LLM to generate a dynamic,
    structured, and categorized MasterChecklist of all requirements.
    """
    print("--- EXECUTING NODE: createMasterChecklistNode ---")
    
    # Emit progress: Starting checklist creation
    emit_progress("progress", 15, "Creando lista maestra de requisitos...", "createMasterChecklist")
    
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
        
        # Emit progress: Checklist created successfully
        total_requirements = (
            len(structured_response.get("financialRequirements", [])) +
            len(structured_response.get("technicalRequirements", [])) +
            len(structured_response.get("legalRequirements", []))
        )
        emit_progress(
            "node_complete", 
            25, 
            f"Lista maestra creada: {total_requirements} requisitos identificados",
            "createMasterChecklist"
        )
        
        print("--- MasterChecklist CREATED SUCCESSFULLY ---")
        return {"masterChecklist": structured_response}

    except Exception as e:
        print(f"--- ERROR in createMasterChecklistNode: {e} ---")
        emit_progress("error", 15, f"Error creando checklist: {str(e)}", "createMasterChecklist")
        # Devolvemos un checklist vacío en caso de error para no romper el grafo
        return {"masterChecklist": {"financialRequirements": [], "technicalRequirements": [], "legalRequirements": []}}



def prepareParallelAuditsNode(state: TenderAnalysisState) -> Dict[str, Any]:
    """
    Prepares the list of inputs for the parallel execution (.map).
    Each input is a dictionary that will initialize the state for one sub-graph run.
    """
    print("--- Dispatching proposals for parallel audit ---")
    
    emit_progress("progress", 30, "Preparando análisis de propuestas...", "prepareParallelAudits")
    
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
    
    emit_progress(
        "node_complete", 
        35, 
        f"Preparadas {len(subgraph_inputs)} propuestas para análisis paralelo",
        "prepareParallelAudits"
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
    
    total_proposals = len(subgraph_inputs)
    emit_progress(
        "progress", 
        40, 
        f"Analizando {total_proposals} propuestas en paralelo...",
        "executeParallelAudits"
    )
    
    # Define a configuration to limit concurrency
    config = RunnableConfig(max_concurrency=2)
    
    individual_reports = await specialistAuditorGraph.abatch(
        subgraph_inputs, config=config
    )
    
    emit_progress(
        "node_complete", 
        70, 
        f"Análisis paralelo completado para {len(individual_reports)} propuestas",
        "executeParallelAudits"
    )
    
    print(f"--- Parallel audits completed for {len(individual_reports)} proposals. ---")
    return {"individualReports": individual_reports}


async def aggregateResultsNode(state: TenderAnalysisState) -> Dict[str, Any]:
    """
    Aggregates the individual audit reports from the parallel runs
    into a final, comparative summary and structured data for charts.
    """
    print("--- 📊 EXECUTING NODE: aggregateResultsNode ---")
    
    emit_progress("progress", 75, "Agregando resultados y generando resumen ejecutivo...", "aggregateResults")
    
    individual_reports = state.get("individualReports", [])
    if not individual_reports:
        return {}

    # --- 1. Generate Executive Summary using LLM ---
    
    summary_context = ""
    for report in individual_reports:
        analysis = report.get("finalAnalysis", {})
        bidder = analysis.get("bidderName", "Unknown")
        # Asegúrate que la clave aquí sea la correcta, en nuestro último nodo era 'viabilityTotal'
        score = analysis.get("scores", {}).get("viabilityTotal", 0) 
        
        # --- THE FIX: Look for "CRITICAL" severity, not "HIGH" ---
        critical_findings = [
            f.get("observation", "No details provided.") 
            for f in analysis.get("findings", []) if f.get("severity") == "CRITICAL"
        ]
        
        summary_context += f"Proposal from: {bidder}\n"
        summary_context += f"Viability Score: {score}/100\n"
        if critical_findings:
            summary_context += f"Critical Risks Found: {'; '.join(critical_findings)}\n"
        summary_context += "---\n"

    executive_summary = "No summary could be generated." # Valor por defecto

    try:
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
        print(summary_response)
        executive_summary = summary_response.get("summary", "")

    except Exception as e:
        print(f"--- ❌ ERROR during executive summary LLM call: {e} ---")

    # --- 2. Budget Comparison (Disabled) ---
    # Budget comparison chart is currently disabled in the frontend
    # Return empty structure to satisfy schema
    budget_comparison = {
        "categories": [],
        "proposals": []
    }
    
    analysis_list = [
        report.get("finalAnalysis") 
        for report in individual_reports 
        if report.get("finalAnalysis") is not None
    ]

    emit_progress(
        "node_complete", 
        85, 
        f"Agregación completa. Generados {len(analysis_list)} análisis comparativos",
        "aggregateResults"
    )

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
    
    emit_progress("progress", 90, "Formateando reporte final...", "formatFinalResponse")

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
        
        emit_progress(
            "node_complete", 
            95, 
            "Reporte final generado exitosamente",
            "formatFinalResponse"
        )
        
    except Exception as e:
        print(f"--- ❌ ERROR: Could not save final report to file: {e} ---")
        emit_progress("error", 90, f"Error guardando reporte: {str(e)}", "formatFinalResponse")
    
    return {"finalReport": final_report}