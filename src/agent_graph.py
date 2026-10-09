import logging
from typing import Any, Dict, List, Optional
from typing_extensions import Annotated, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from src.config import routing_llm
from src.router import route_query
from src.schemas import ExecutionResponse, RoutingDecision, WorkflowDefinition
from src.workflow_registry import get_workflow

from tools.ingestion_tools import (
    filter_records,
    read_csv,
    read_excel,
    read_json,
)
from tools.analysis_tools import (
    check_threshold,
    compare_prices,
    detect_log_anomalies,
    validate_catalog_data,
)
from tools.integration_tools import (
    export_report,
    generate_restock_list,
    send_notification,
)

logger = logging.getLogger(__name__)

ALL_TOOLS = [
    read_csv,
    read_excel,
    read_json,
    filter_records,
    check_threshold,
    compare_prices,
    validate_catalog_data,
    detect_log_anomalies,
    send_notification,
    generate_restock_list,
    export_report,
]

ENTERPRISE_SYSTEM_PROMPT = """You are an autonomous enterprise operations agent executing a verified business workflow.

### WORKFLOW SPECIFICATION (Sourced from Business Registry):
- Identifier: {workflow_id}
- Name: {workflow_name}
- Prescribed Step Sequence: {steps}
- Permitted Tools: {tools_required}
- Decision Criteria & Rules: {decision_logic}
- Target Output Schema: {expected_output}

### EXECUTION INSTRUCTIONS:
1. TOOL DISCIPLINE: Invoke the appropriate tools sequentially to inspect and extract data required by the workflow.
2. RIGID GROUNDING: Base every figure, SKU, variance percentage, and status strictly on data returned by tool executions. Never assume or hallucinate records.
3. DECISION VALIDATION: Explicitly assess whether conditions outlined in the Decision Criteria were met or violated (e.g., threshold breaches, anomaly occurrences).
4. OUTPUT FORMATTING: Format your final response strictly to satisfy the Target Output Schema specified above.
"""


# Graph State
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    query: str
    decision: Optional[RoutingDecision]
    workflow: Optional[WorkflowDefinition]
    final_output: str


# Graph Nodes

# Node 1 : Main Routing Node
def route_node(state: AgentState) -> Dict[str, Any]:
    """Routes the user query to the appropriate Excel-defined workflow and retrieves its configuration.
       Builds the system prompt and initializes graph messages, returning an empty workflow context if no match is found."""
    decision = route_query(state["query"])
    workflow = (
        get_workflow(decision.workflow_id)
        if decision.workflow_id != "UNKNOWN"
        else None
    )

    if not workflow:
        return {
            "decision": decision,
            "workflow": None,
            "messages": [],
        }

    formatted_system_prompt = ENTERPRISE_SYSTEM_PROMPT.format(
        workflow_id=workflow.workflow_id,
        workflow_name=workflow.workflow_name,
        steps=workflow.steps,
        tools_required=workflow.tools_required,
        decision_logic=workflow.decision_logic,
        expected_output=workflow.expected_output,
    )

    return {
        "decision": decision,
        "workflow": workflow,
        "messages": [
            SystemMessage(content=formatted_system_prompt),
            HumanMessage(content=state["query"]),
        ],
    }

# Node 2 : fallback Node
def fallback_node(state: AgentState) -> Dict[str, str]:
    """Fallback when query does not map to any active workflow in Excel."""
    reason = (
        state["decision"].reasoning
        if state["decision"]
        else "No workflow matched."
    )
    fallback_message = (
        "Your request could not be matched to an active workflow in the Excel registry.\n"
        f"Reasoning: {reason}"
    )
    return {"final_output": fallback_message}


# Agent Node 
def agent_node(state: AgentState) -> Dict[str, Any]:
    """Invokes the LLM with available tools and returns its response."""
    llm = routing_llm()
    model_with_tools = llm.bind_tools(ALL_TOOLS)
    response = model_with_tools.invoke(state["messages"])

    return {
        "messages": [response],
        "final_output": response.content if not response.tool_calls else "",
    }


## conditional Edge node
def route_edge(state: AgentState) -> str:
    """Routes execution to the agent if a workflow is found; otherwise, to fallback."""
    return "agent" if state.get("workflow") else "fallback"


def build_agent_graph():
    """Builds and compiles the StateGraph workflow."""
    builder = StateGraph(AgentState)

    builder.add_node("route", route_node)
    builder.add_node("fallback", fallback_node)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(ALL_TOOLS))

    builder.add_edge(START, "route")
    builder.add_conditional_edges(
        "route",
        route_edge,
        {
            "agent": "agent",
            "fallback": "fallback",
        },
    )

    builder.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        },
    )
    builder.add_edge("tools", "agent")
    builder.add_edge("fallback", END)

    return builder.compile()


agent_graph = build_agent_graph()


# Final output Genration
def run_agent(query: str) -> ExecutionResponse:
    """Runs a query through the graph and returns a validated ExecutionResponse."""
    initial_state: AgentState = {
        "messages": [],
        "query": query,
        "decision": None,
        "workflow": None,
        "final_output": "",
    }

    result = agent_graph.invoke(initial_state)
    workflow = result.get("workflow")
    decision = result.get("decision")
    messages = result.get("messages", [])

    # Collect executed tool steps
    executed_steps: List[str] = []
    step_num = 1
    for msg in messages:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for call in msg.tool_calls:
                executed_steps.append(
                    f"{step_num}. Execute {call['name']} [SUCCESS]"
                )
                step_num += 1

    if not executed_steps and not workflow:
        executed_steps.append("1. Routing Fallback [REJECTED]")

    # Extract final text output
    final_text = result.get("final_output", "")
    if not final_text and messages:
        final_text = str(messages[-1].content).strip()

    return ExecutionResponse(
        selected_workflow=(
            f"{workflow.workflow_id} - {workflow.workflow_name}"
            if workflow
            else "None - UNKNOWN"
        ),
        reasoning=(
            decision.reasoning
            if decision
            else "No reasoning recorded."
        ),
        steps_executed=executed_steps,
        result=final_text,
    )