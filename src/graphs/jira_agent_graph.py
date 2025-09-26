import logging
import operator
from typing import TypedDict, Annotated
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, StateGraph
from models.llm_config import LLMConfig
from tools.jira_tool import fetch_and_summarize_ticket, fetch_statuses, fetch_tickets_by_status

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # Removed FileHandler
)
logger = logging.getLogger(__name__)

# Initialize LLM
llm = LLMConfig.get_llm()
logger.info("Initialized LLM for Jira agent")

# State
class AgentState(TypedDict):
    """State schema for the Jira agent workflow."""
    messages: Annotated[list, operator.add]
    greeted: bool
    status_filter: str | None
    ticket_to_summarize: str | None

def agent_node(state: AgentState):
    """Process user input and determine the next action based on the message content."""
    logger.info("Executing agent_node")
    try:
        messages = state["messages"]
        last_msg = messages[-1].content.lower() if messages else ""
        logger.debug("Last message: %s", last_msg)

        statuses = [s.lower() for s in fetch_statuses()]
        requested_status = None
        for s in statuses:
            if s in last_msg:
                requested_status = s
                break

        if "show me my tickets" in last_msg:
            logger.info("Detected 'show me my tickets' command")
            return {
                "messages": [AIMessage(content="Hi! Fetching your tickets...")],
                "greeted": True,
                "status_filter": None,
                "ticket_to_summarize": None
            }

        elif requested_status:
            logger.info("Detected status filter: %s", requested_status)
            return {
                "messages": [AIMessage(content=f"Fetching tickets with status '{requested_status}'...")],
                "greeted": True,
                "status_filter": requested_status,
                "ticket_to_summarize": None
            }

        elif "summarize ticket" in last_msg:
            parts = last_msg.split()
            ticket_key = next((p for p in parts if "-" in p), None)
            if ticket_key:
                logger.info("Detected summarize ticket command for: %s", ticket_key)
                return {
                    "messages": [AIMessage(content=f"Summarizing ticket {ticket_key}...")],
                    "ticket_to_summarize": ticket_key
                }

        # Default LLM fallback
        human_messages = [m for m in messages if isinstance(m, HumanMessage) and m.content.strip()]
        if not human_messages:
            logger.debug("No human messages found, returning default state")
            return {
                "messages": [],
                "greeted": state.get("greeted", False),
                "status_filter": None,
                "ticket_to_summarize": None
            }

        logger.debug("Invoking LLM for default response")
        response = llm.invoke(human_messages)
        logger.info("LLM response generated")
        return {
            "messages": [response],
            "greeted": state.get("greeted", False),
            "status_filter": None,
            "ticket_to_summarize": None
        }
    except Exception as e:
        logger.error("Error in agent_node: %s", e)
        raise

def tool_node(state: AgentState):
    """Fetch tickets based on the status filter if greeted."""
    logger.info("Executing tool_node")
    try:
        if state.get("greeted", False):
            logger.debug("Fetching tickets with status filter: %s", state.get("status_filter"))
            tickets = fetch_tickets_by_status(state.get("status_filter"))
            logger.info("Tickets fetched successfully")
            return {
                "messages": [AIMessage(content=tickets)],
                "greeted": False,
                "status_filter": None,
                "ticket_to_summarize": None
            }
        logger.debug("No action required in tool_node")
        return state
    except Exception as e:
        logger.error("Error in tool_node: %s", e)
        raise

def summarize_ticket_node(state: AgentState):
    """Summarize a specific ticket if a ticket key is provided."""
    logger.info("Executing summarize_ticket_node")
    try:
        ticket_key = state.get("ticket_to_summarize")
        if ticket_key:
            logger.debug("Summarizing ticket: %s", ticket_key)
            summary = fetch_and_summarize_ticket(ticket_key)
            logger.info("Ticket %s summarized successfully", ticket_key)
            return {
                "messages": [AIMessage(content=summary)],
                "ticket_to_summarize": None
            }
        logger.debug("No ticket to summarize")
        return state
    except Exception as e:
        logger.error("Error in summarize_ticket_node: %s", e)
        raise

# Graph
logger.info("Setting up workflow graph")
workflow = StateGraph(state_schema=AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.add_node("summarizer", summarize_ticket_node)
workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    lambda state: (
        "tools" if state.get("greeted", False)
        else "summarizer" if state.get("ticket_to_summarize") else END
    ),
    {"tools": "tools", "summarizer": "summarizer", END: END}
)

workflow.add_edge("tools", END)
workflow.add_edge("summarizer", END)

# Compile Graph
logger.info("Compiling workflow graph")
app = workflow.compile()
logger.info("Workflow graph compiled successfully")