from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage
import operator
from models.llm_config import LLMConfig
from tools.jira_tool import fetch_tickets

# Initialize LLM
llm = LLMConfig.get_llm()

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    greeted: bool = False

def agent_node(state: AgentState):
    messages = state["messages"]
    last_msg = messages[-1].content.lower()
    # Greet user and trigger tool
    if "hi" in last_msg:
        return {"messages": [AIMessage(content="Hi! Fetching your tickets...")], "greeted": True}
    
    # Otherwise, LLM handles conversation
    response = llm.invoke(messages)
    return {"messages": [response], "greeted": state["greeted"]}

def tool_node(state: AgentState):
    if state["greeted"]:
        tickets = fetch_tickets()  # Call Jira tool
        return {"messages": [AIMessage(content=tickets)], "greeted": False}
    return state

workflow = StateGraph(state_schema=AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    lambda state: "tools" if state["greeted"] else END,
    {"tools": "tools", END: END}
)
workflow.add_edge("tools", END)

app = workflow.compile()
