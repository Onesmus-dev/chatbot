# Import typing for structured state definition
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.types import Command, interrupt

# LangGraph core imports
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Define the chatbot state
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Create a graph builder with that state
graph_builder = StateGraph(State)

def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]
# --- Set up Cohere LLM ---
from langchain_community.llms import Cohere
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Now access them using os.environ
cohere_key = os.getenv("COHERE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


# Set API key as environment variable
os.environ['COHERE_API_KEY'] = cohere_key

# Initialize the LLM
llm = Cohere(cohere_api_key=cohere_key, model="command")

# Import the Tavily tool
from tools.tavily_search import search_tavily

# Add in-memory checkpointer
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()  # Using MemorySaver for state memory (short-term)

# Chatbot logic
def chatbot(state: State):
    user_message = state["messages"][-1].content.lower()

    # Use Tavily for web search queries
    if "search" in user_message or "lookup" in user_message:
        tool_result = search_tavily(user_message)
        return {"messages": [{"role": "assistant", "content": tool_result}]}
    
    # Use LLM otherwise
    bot_response = llm.invoke(user_message)
    return {"messages": [{"role": "assistant", "content": bot_response}]}

# Register the chatbot node in the graph
graph_builder.add_node("chatbot", chatbot)

# Set the flow: START -> chatbot -> END
graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")

# Compile the graph with memory (checkpointer)
graph = graph_builder.compile(checkpointer=memory)  # Attaching memory

# OPTIONAL: Try visualizing the graph
try:
    from IPython.display import Image, display
    display(Image(graph.get_graph().draw_mermaid_png()))
except:
    pass  # Skip if IPython/display isn't available

#  Function to stream chat updates, with thread_id to persist memory
import uuid
thread_id = str(uuid.uuid4())  # One unique ID per session (you can replace with user ID)

def stream_graph_updates(user_input: str):
    config = {"configurable": {"thread_id": thread_id}}  # The  Correct place to set memory session
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}, config=config):
        for value in event.values():
            print("Assistant:", value["messages"][-1]["content"])

# Run chatbot loop
while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except KeyboardInterrupt:
        print("\nGoodbye!")
        break
