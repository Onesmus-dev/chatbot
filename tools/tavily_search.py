# tools/tavily_search.py

import requests
import os

def search_tavily(query: str) -> str:
    """Use Tavily API to search the web and return the answer."""
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    if not TAVILY_API_KEY:
        return "Tavily API key not found in environment."

    response = requests.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
        json={"query": query, "search_depth": "basic", "include_answer": True}
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("answer", "No answer found.")
    else:
        return f"Tavily API error: {response.status_code}"
