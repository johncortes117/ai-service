from langgraph.graph import StateGraph, END
from .state import ProposalAuditState
from .specialistNodes import (
    projectManagerRouterNode, 
    financialSpecialistNode,
    technicalSpecialistNode,
    legalSpecialistNode,
    compileProposalReportNode
)

workflow = StateGraph(ProposalAuditState)

workflow.add_node("router", projectManagerRouterNode)
workflow.add_node("financial_auditor", financialSpecialistNode)
workflow.add_node("technical_auditor", technicalSpecialistNode)
workflow.add_node("legal_auditor", legalSpecialistNode)
workflow.add_node("report_compiler", compileProposalReportNode)

workflow.set_entry_point("router")

workflow.add_edge("router", "financial_auditor")
workflow.add_edge("router", "technical_auditor")
workflow.add_edge("router", "legal_auditor")

workflow.add_edge(
    ["financial_auditor", "technical_auditor", "legal_auditor"], 
    "report_compiler"
)

workflow.add_edge("report_compiler", END)

specialistAuditorGraph = workflow.compile()