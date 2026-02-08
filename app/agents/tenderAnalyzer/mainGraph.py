from langgraph.graph import StateGraph, END
from .state import TenderAnalysisState
from .pipelineNodes import (
    createMasterChecklistNode,
    prepareParallelAuditsNode,
    executeParallelAuditsNode,
    aggregateResultsNode,
    formatFinalResponseNode,
)

workflow = StateGraph(TenderAnalysisState)

workflow.add_node("createMasterChecklist", createMasterChecklistNode)
workflow.add_node("prepareParallelAudits", prepareParallelAuditsNode)
workflow.add_node("executeParallelAudits", executeParallelAuditsNode)
workflow.add_node("aggregateResults", aggregateResultsNode)
workflow.add_node("formatFinalResponse", formatFinalResponseNode)

workflow.set_entry_point("createMasterChecklist")
workflow.add_edge("createMasterChecklist", "prepareParallelAudits")
workflow.add_edge("prepareParallelAudits", "executeParallelAudits")
workflow.add_edge("executeParallelAudits", "aggregateResults")
workflow.add_edge("aggregateResults", "formatFinalResponse")
workflow.add_edge("formatFinalResponse", END)

agentGraph = workflow.compile()