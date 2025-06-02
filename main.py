# main.py

# Import typing for structured state definition
from typing import Annotated
from typing_extensions import TypedDict

# LangGraph core imports
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt

# LangChain / LangGraph tools
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langchain_cohere import ChatCohere

# Load environment variables
from dotenv import load_dotenv
import os, uuid
load_dotenv()

# API keys
cohere_key = os.getenv("COHERE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

# -- Define memory-enabled state
class State(TypedDict):
    messages: Annotated[list, add_messages]

# -- Tool 1: Web search via Tavily
search_tool = TavilySearch(max_results=2)

# -- Tool 2: Human assistance using LangGraph's interrupt
@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human operator."""
    human_response = interrupt({"query": query})
    return human_response["data"]

tools = [search_tool, human_assistance]

# -- Initialize the LLM (ChatCohere supports tools)
llm = ChatCohere(cohere_api_key=cohere_key, model="command-r-plus")
llm_with_tools = llm.bind_tools(tools)

# -- Chatbot logic (calls LLM + uses tool calling)
def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    # Ensure only one tool call per step (required for human interruption)
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}

# -- Set up memory and graph
memory = MemorySaver()
graph_builder = StateGraph(State)

# -- Register nodes
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

# -- Define flow
graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")

# -- Compile with memory
graph = graph_builder.compile(checkpointer=memory)

# -- Optional: Visualize graph
try:
    from IPython.display import Image, display
    display(Image(graph.get_graph().draw_mermaid_png()))
except:
    pass

# -- Streaming function
thread_id = str(uuid.uuid4())
def stream_graph_updates(user_input: str):
    config = {"configurable": {"thread_id": thread_id}}
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}, config=config):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

# -- Run chatbot loop
if __name__ == "__main__":
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break
            stream_graph_updates(user_input)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
