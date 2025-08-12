from langgraph.graph import StateGraph, END
from .state import TenderAnalysisState
from .pipelineNodes import (
    createMasterChecklistNode,
    prepareParallelAuditsNode,
    executeParallelAuditsNode,
    aggregateResultsNode,
    formatFinalResponseNode,
)


# 1. Instantiate the graph with the main state
workflow = StateGraph(TenderAnalysisState)

# 2. Add all the nodes of the main pipeline
workflow.add_node("createMasterChecklist", createMasterChecklistNode)
workflow.add_node("prepareParallelAudits", prepareParallelAuditsNode)
workflow.add_node("executeParallelAudits", executeParallelAuditsNode)
workflow.add_node("aggregateResults", aggregateResultsNode)
workflow.add_node("formatFinalResponse", formatFinalResponseNode)

# 3. Define the workflow edges
workflow.set_entry_point("createMasterChecklist")
workflow.add_edge("createMasterChecklist", "prepareParallelAudits")
# The 'prepare' node's output feeds the parallel execution
workflow.add_edge("prepareParallelAudits", "executeParallelAudits")
# After all parallel runs are complete, the results are aggregated
workflow.add_edge("executeParallelAudits", "aggregateResults")
workflow.add_edge("aggregateResults", "formatFinalResponse")
workflow.add_edge("formatFinalResponse", END)

# 4. Compile the final, complete agent
agentGraph = workflow.compile()