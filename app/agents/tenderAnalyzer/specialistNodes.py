# app/agents/specialistNodes.py

from typing import Dict, Any, List
from .state import ProposalAuditState
from .schemas.specialistFindings import FinancialFinding, TechnicalFinding, LegalFinding
from .schemas.routerSchemas import AnnexMapOutput
from .schemas.specialistTasks import SpecialistTask
from .prompts import CREATE_ANNEX_MAP_PROMPT, FINANCIAL_ANALYSIS_PROMPT, TECHNICAL_ANALYSIS_PROMPT, LEGAL_ANALYSIS_PROMPT
from ..services import llmService
from langchain_core.messages import SystemMessage, HumanMessage
from .schemas.masterChecklist import MasterChecklist, Requirement


async def projectManagerRouterNode(state: ProposalAuditState) -> Dict[str, Any]:
    """
    Acts as the intelligent router for a single proposal audit. This version is
    robust against filename mismatches (e.g., case, extensions, underscores).
    """
    proposal = state.get("proposal", {})
    masterChecklist_dict = state.get("masterChecklist", {})
    companyName = proposal.get("companyName", "Unknown name")
    
    print(f"--- 🧠 EXECUTING ROUTER for company: {companyName} ---")

    try:
        masterChecklist = MasterChecklist.model_validate(masterChecklist_dict)
    except Exception as e:
        print(f"--- ❌ ROUTER ERROR: Could not validate MasterChecklist schema: {e} ---")
        return {"technicalTasks": [], "financialTasks": [], "legalTasks": []}

    mainFormText = proposal.get("mainFormText")
    annexes = proposal.get("attachments", {})  # Backend generates "attachments" not "annexes"
    
    all_requirements = (masterChecklist.financialRequirements + 
                        masterChecklist.technicalRequirements + 
                        masterChecklist.legalRequirements)
    
    if not all_requirements:
        print("--- ⏩ ROUTER SKIPPING: No requirements found in MasterChecklist. ---")
        return {"technicalTasks": [], "financialTasks": [], "legalTasks": []}
    
    # Step 1: Create the requirement-to-annex map using the LLM
    requirement_names = [req.name for req in all_requirements]
    available_annexes = list(annexes.keys())
    
    context_for_mapper = f"""Requirements List: {requirement_names}
---
Available Annexes in Proposal: {available_annexes}
---
Main Proposal Form Text:
{mainFormText}"""
    
    messages = [
        SystemMessage(content=CREATE_ANNEX_MAP_PROMPT),
        HumanMessage(content=context_for_mapper)
    ]
    structured_map_response = await llmService.invoke_json(
        messages=messages, output_schema=AnnexMapOutput, model_name="gpt-4o-mini", temperature=0.0
    )
    requirement_to_annex_map = {
        item.get("requirementName"): item.get("annexFilename")
        for item in structured_map_response.get("annexMap", [])
    }
    
    print("--- MAPA REQUISITO -> ANEXO CREADO POR LLM:", requirement_to_annex_map)
    print("--- ANEXOS DISPONIBLES EN LA PROPUESTA:", list(annexes.keys()))

    # Step 2: Prepare surgical tasks for each specialist with robust filename matching
    findings = state.get("findings", [])
    
    def normalize_filename(name: str | None) -> str:
        """Helper to compare filenames flexibly."""
        if not name: return ""
        return name.replace(".pdf", "").replace("_", " ").replace("-", " ").lower().strip()

    def find_real_annex_key(mapped_name: str | None) -> str | None:
        """Finds the actual key in the annexes dict, ignoring case, underscores, and .pdf extension."""
        if not mapped_name: return None
        normalized_mapped_name = normalize_filename(mapped_name)
        for real_key in annexes.keys():
            if normalize_filename(real_key) == normalized_mapped_name:
                return real_key
        return None

    def prepare_tasks_for_specialist(requirements_list: List[Requirement]) -> List[SpecialistTask]:
        tasks = []
        for requirement in requirements_list:
            mapped_filename = requirement_to_annex_map.get(requirement.name)
            real_annex_key = find_real_annex_key(mapped_filename)

            if not real_annex_key:
                findings.append({
                    "agentSource": "Project Manager", "severity": "CRITICAL",
                    "requirementName": requirement.name, "requirementDetails": requirement.details,
                    "isCompliant": False,
                    "observation": f"Omisión Documental: El formulario referencia al anexo '{mapped_filename}', pero este archivo no se encontró entre los documentos entregados. No se puede verificar el requisito.",
                    "recommendation": "Considerar como incumplimiento grave si el requisito es mandatorio."
                })
                continue
            
            tasks.append(SpecialistTask(
                requirementToVerify=requirement,
                evidenceText=annexes[real_annex_key],
                mainFormText=mainFormText
            ))
        return tasks

    financialTasks = prepare_tasks_for_specialist(masterChecklist.financialRequirements)
    technicalTasks = prepare_tasks_for_specialist(masterChecklist.technicalRequirements)
    legalTasks = prepare_tasks_for_specialist(masterChecklist.legalRequirements)

    print(f"--- 📬 Router prepared {len(technicalTasks)} technical, {len(financialTasks)} financial, {len(legalTasks)} legal tasks. ---")
    
    return {
        "findings": findings,
        "technicalTasks": technicalTasks,
        "financialTasks": financialTasks,
        "legalTasks": legalTasks,
    }

async def financialSpecialistNode(state: ProposalAuditState) -> Dict[str, Any]:
    """
    Acts as the financial specialist. Receives a list of surgical tasks
    from the router and executes them by performing LLM-driven cross-validation.
    """
    print("--- 🕵️ EXECUTING NODE: financialSpecialistNode ---")
    
    financial_tasks: List[SpecialistTask] = state.get("financialTasks", [])
    if not financial_tasks:
        print("--- ⏩ SKIPPING: No financial tasks to perform. ---")
        return {}

    new_findings = []
    
    for task_dict in financial_tasks:
        try:
            task = SpecialistTask.model_validate(task_dict)
        except Exception as e:
            print(f"--- ❌ ERROR: Could not validate task_dict data: {e} ---")
            continue

        print(f"--- Auditing Financial Requirement: {task.requirementToVerify.name} ---")
        
        context_for_llm = f"""
        **Requirement to Verify:**
        {task.requirementToVerify.model_dump_json(indent=2)}
        ---
        **Main Proposal Form Text (for context):**
        {task.mainFormText}
        ---
        **Evidence Document Text (Annex):**
        {task.evidenceText}
        """
        messages = [
            SystemMessage(content=FINANCIAL_ANALYSIS_PROMPT),
            HumanMessage(content=context_for_llm)
        ]

        try:
            finding_result = await llmService.invoke_json(
                messages=messages,
                output_schema=FinancialFinding,
                model_name="gpt-4o-mini",
                temperature=0.0
            )
            finding_result["agentSource"] = "Financial"
            new_findings.append(finding_result)

        except Exception as e:
            error_finding = {
                "requirementName": task.requirementToVerify.name,
                "isCompliant": False,
                "isConsistent": False,
                "severity": "CRITICAL",
                "observation": f"An error occurred during AI analysis: {e}",
                "recommendation": "Manual review required due to system error.",
                "agentSource": "Financial"
            }
            new_findings.append(error_finding)

    print(f"--- ✅ financialSpecialistNode generated {len(new_findings)} new findings. ---")
    
    # This return structure is designed for LangGraph's state update mechanism
    return {"findings": new_findings}


async def technicalSpecialistNode(state: ProposalAuditState) -> Dict[str, Any]:
    """
    Acts as the technical specialist. (Replicates the financial specialist pattern).
    """
    print("--- 🛠️ EXECUTING NODE: technicalSpecialistNode ---")
    
    technical_tasks: List[SpecialistTask] = state.get("technicalTasks", [])
    if not technical_tasks:
        print("--- ⏩ SKIPPING: No technical tasks to perform. ---")
        return {}

    new_findings = []
    
    for task_dict in technical_tasks:
        try:
            task = SpecialistTask.model_validate(task_dict)
        except Exception as e:
            print(f"--- ❌ ERROR: Could not validate task_dict data: {e} ---")
            continue
        
        print(f"--- Auditing Technical Requirement: {task.requirementToVerify.name} ---")
        
        context_for_llm = f"""
        **Requirement to Verify:**
        {task.requirementToVerify.model_dump_json(indent=2)}
        ---
        **Main Proposal Form Text (for context):**
        {task.mainFormText}
        ---
        **Evidence Document Text (Annex):**
        {task.evidenceText}
        """
        messages = [
            SystemMessage(content=TECHNICAL_ANALYSIS_PROMPT),
            HumanMessage(content=context_for_llm)
        ]

        try:
            finding_result = await llmService.invoke_json(
                messages=messages,
                output_schema=TechnicalFinding,
                model_name="gpt-4o-mini",
                temperature=0.0
            )
            finding_result["agentSource"] = "Technical"
            new_findings.append(finding_result)

        except Exception as e:
            error_finding = {
                "requirementName": task.requirementToVerify.name,
                "isCompliant": False,
                "isConsistent": False,
                "severity": "CRITICAL",
                "observation": f"An error occurred during AI analysis: {e}",
                "recommendation": "Manual review required due to system error.",
                "agentSource": "Technical"
            }
            new_findings.append(error_finding)

    print(f"--- ✅ technicalSpecialistNode generated {len(new_findings)} new findings. ---")

    return {"findings": new_findings}


async def legalSpecialistNode(state: ProposalAuditState) -> Dict[str, Any]:
    """
    Acts as the legal specialist. (Replicates the financial specialist pattern).
    """
    print("--- ⚖️ EXECUTING NODE: legalSpecialistNode ---")
    
    legal_tasks: List[SpecialistTask] = state.get("legalTasks", [])
    if not legal_tasks:
        print("--- ⏩ SKIPPING: No legal tasks to perform. ---")
        return {}

    new_findings = []
    
    for task_dict in legal_tasks:
        try:
            task = SpecialistTask.model_validate(task_dict)
        except Exception as e:
            print(f"--- ❌ ERROR: Could not validate task_dict data: {e} ---")
            continue
        
        print(f"--- Auditing Legal Requirement: {task.requirementToVerify.name} ---")
        
        context_for_llm = f"""
        **Requirement to Verify:**
        {task.requirementToVerify.model_dump_json(indent=2)}
        ---
        **Main Proposal Form Text (for context):**
        {task.mainFormText}
        ---
        **Evidence Document Text (Annex):**
        {task.evidenceText}
        """
        messages = [
            SystemMessage(content=LEGAL_ANALYSIS_PROMPT),
            HumanMessage(content=context_for_llm)
        ]

        try:
            finding_result = await llmService.invoke_json(
                messages=messages,
                output_schema=LegalFinding,
                model_name="gpt-4o-mini",
                temperature=0.0
            )
            finding_result["agentSource"] = "Legal"
            new_findings.append(finding_result)

        except Exception as e:
            error_finding = {
                "requirementName": task.requirementToVerify.name,
                "isCompliant": False,
                "isConsistent": False,
                "severity": "CRITICAL",
                "observation": f"An error occurred during AI analysis: {e}",
                "recommendation": "Manual review required due to system error.",
                "agentSource": "Legal"
            }
            new_findings.append(error_finding)

    print(f"--- ✅ legalSpecialistNode generated {len(new_findings)} new findings. ---")

    return {"findings": new_findings}


def compileProposalReportNode(state: ProposalAuditState) -> Dict[str, Any]:
    """
    Final node in the sub-graph. Compiles all findings and calculates the
    final scores using the OK, WARNING, CRITICAL severity system.
    """
    proposal = state.get("proposal", {})
    companyName = proposal.get("companyName", "Unknown name")
    print(f"---  compiling final report for company: {companyName} ---")
    
    findings = state.get("findings", [])
    
    findingsSummary = {
        "total": len(findings),
        "critical": sum(1 for f in findings if f.get("severity") == "CRITICAL"),
        "warning": sum(1 for f in findings if f.get("severity") == "WARNING"),
        "ok": sum(1 for f in findings if f.get("severity") == "OK")
    }
    
    POINTS_DEDUCTION = {
        "CRITICAL": 15,
        "WARNING": 5,
        "OK": 0 
    }
    
    scores = {"legal": 100, "technical": 100, "financial": 100}

    for finding in findings:
        severity = finding.get("severity")
        points_to_deduct = POINTS_DEDUCTION.get(severity, 0)
        
        source = finding.get("agentSource")
        if source == "Legal":
            scores["legal"] -= points_to_deduct
        elif source == "Technical":
            scores["technical"] -= points_to_deduct
        elif source == "Financial":
            scores["financial"] -= points_to_deduct

    scores["legal"] = max(0, scores["legal"])
    scores["technical"] = max(0, scores["technical"])
    scores["financial"] = max(0, scores["financial"])
    scores["viabilityTotal"] = int((scores["legal"] + scores["technical"] + scores["financial"]) / 3)

    final_analysis_for_proposal = {
        "bidderName": companyName,
        "summaryData": {
            "totalAmountUSD": 1000000, 
            "deliveryMonths": 12
        },
        "scores": scores,
        "findingsSummary": findingsSummary,
        "findings": findings
    }

    return {"finalAnalysis": final_analysis_for_proposal}