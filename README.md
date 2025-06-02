# 🧠 LangGraph Cohere Chatbot with Tavily Tool and Memory

This is a simple, modular AI chatbot built using **LangGraph**, **LangChain**, **Cohere LLM**, and the **Tavily Search API**.  
It demonstrates tool integration, dynamic conversation flows, and memory-powered sessions — ideal for learning conversational AI workflows.
It is build relying on the langchain bot tutorial and code sniplets. 
---

## 📸 Chatbot Demo

### 🟡 Before Memory
The bot forgets context every time. There's no memory of past questions:

![Before Memory](assets/before%20memory.PNG)

---

### 🟢 After Memory (with `MemorySaver`)
Context is preserved. The bot can remember what was said previously:
checkpointer 
When you invoke the graph again using the same thread_id, the graph loads its saved state, allowing the chatbot to pick up where it left off.

---

## 🧰 Features

- 🤖 Powered by Cohere's `command` LLM
- 🔍 Integrated with [Tavily API](https://app.tavily.com/home) for real-time web searches
- 🧠 Conversational memory using LangGraph `MemorySaver`
- 🌱 Modular code structure with separation of tools and logic
- 🧪 Graph visualization (optional)

---

## 🗂️ Folder Structure
- chatbot/
- ├── main.py # Chatbot logic and LangGraph setup
- ├── tools/
- │ └── tavily_search.py # Tavily tool implementation
- ├── secret_key.py # Contains your API keys (not committed)
- ├── assets/
- │ ├── before-memory.png # Screenshot before memory was added
- │ └── 
- ├── README.md # This file
---
## 🧠 Memory Integration
This project uses LangGraph’s built-in MemorySaver:

- ✅ Keeps track of message history

- ✅ Allows follow-up questions and continuity

- 🔁 Can be replaced with persistent memory like SQLite or Postgres for production

- Memory is activated via:
[from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()

graph = graph_builder.compile(checkpointer=memory)]\
---