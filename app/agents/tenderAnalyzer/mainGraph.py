from langgraph.graph import StateGraph, END
from .state import TenderAnalysisState
from .pipelineNodes import createMasterChecklistNode


workflow = StateGraph(TenderAnalysisState)

workflow.add_node(
    "createMasterChecklist",
    createMasterChecklistNode
)
workflow.set_entry_point("createMasterChecklist")
workflow.add_edge("createMasterChecklist", END)

agent_graph = workflow.compile()