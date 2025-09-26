from graphs.jira_agent_graph import app
from langchain_core.messages import HumanMessage, AIMessage
from models.llm_config import LLMConfig

def run_agent():
    print("You can type 'show me my tickets' or ask for tickets by status (e.g., 'show me closed').")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("Exiting agent.")
            break

        # Prepare input state for the workflow
        input_state = {"messages": [HumanMessage(content=user_input)]}

        # Invoke the LangGraph workflow
        result = app.invoke(input_state)

        # Print only AI responses
        for msg in result["messages"]:
            if isinstance(msg, AIMessage):
                print(f"AI: {msg.content}")

if __name__ == "__main__":
    LLMConfig.get_llm()
    run_agent()