from tools.jira_tool import fetch_tickets_by_status, fetch_statuses
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage
import operator
from models.llm_config import LLMConfig

# Initialize LLM
llm = LLMConfig.get_llm()

# State
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    greeted: bool = False
    status_filter: str | None = None  # Added for status filtering

# Nodes
def agent_node(state: AgentState):
    messages = state["messages"]
    last_msg = messages[-1].content.lower() if messages else ""

    # Check if user asked about a specific status
    statuses = [s.lower() for s in fetch_statuses()]
    requested_status = None
    for s in statuses:
        if s in last_msg:
            requested_status = s
            break

    if "show me my tickets" in last_msg:
        return {
            "messages": [AIMessage(content="Hi! Fetching your tickets...")],
            "greeted": True,
            "status_filter": None
        }

    elif requested_status:
        return {
            "messages": [AIMessage(content=f"Fetching tickets with status '{requested_status}'...")],
            "greeted": True,
            "status_filter": requested_status
        }

    # Only pass non-empty human messages to LLM to avoid Gemini 400 error
    human_messages = [m for m in messages if isinstance(m, HumanMessage) and m.content.strip()]
    if not human_messages:
        return {
            "messages": [],
            "greeted": state.get("greeted", False),
            "status_filter": None
        }

    response = llm.invoke(human_messages)
    return {
        "messages": [response],
        "greeted": state.get("greeted", False),
        "status_filter": None
    }

def tool_node(state: AgentState):
    if state.get("greeted", False):
        tickets = fetch_tickets_by_status(state.get("status_filter"))
        return {
            "messages": [AIMessage(content=tickets)],
            "greeted": False,
            "status_filter": None
        }
    return state

# Graph
workflow = StateGraph(state_schema=AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    lambda state: "tools" if state.get("greeted", False) else END,
    {"tools": "tools", END: END}
)
workflow.add_edge("tools", END)

# Compile Graph
app = workflow.compile()
