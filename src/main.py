from graphs.jira_agent_graph import app
from langchain_core.messages import HumanMessage

if __name__ == "__main__":
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break
        input_state = {"messages": [HumanMessage(content=user_input)]}
        result = app.invoke(input_state)
        for msg in result["messages"]:
            print(f"AI: {msg.content}")
