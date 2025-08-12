from langgraph.graph import StateGraph, END
from .state import ProposalAuditState
from .specialistNodes import (
    projectManagerRouterNode, 
    financialSpecialistNode,
    technicalSpecialistNode,
    legalSpecialistNode,
    compileProposalReportNode
)

# Instantiate the workflow for the sub-graph
workflow = StateGraph(ProposalAuditState)

# Add all the nodes for the sub-graph
workflow.add_node("router", projectManagerRouterNode)
workflow.add_node("financial_auditor", financialSpecialistNode)
workflow.add_node("technical_auditor", technicalSpecialistNode)
workflow.add_node("legal_auditor", legalSpecialistNode)
workflow.add_node("report_compiler", compileProposalReportNode) # El nodo que une los resultados

# Define the workflow
# The entry point is the router
workflow.set_entry_point("router")

# After the router, the three specialists are kicked off in parallel.
# LangGraph handles this parallelism automatically because they all
# start from the same node and don't depend on each other.
workflow.add_edge("router", "financial_auditor")
workflow.add_edge("router", "technical_auditor")
workflow.add_edge("router", "legal_auditor")

# After ALL specialists have finished, their results are joined
# and compiled by the report_compiler node.
workflow.add_edge(
    ["financial_auditor", "technical_auditor", "legal_auditor"], 
    "report_compiler"
)

# The compiler is the final step in the sub-graph
workflow.add_edge("report_compiler", END)

# Compile the sub-graph
specialistAuditorGraph = workflow.compile()