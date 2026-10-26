from tool_registry import tool
from typing import Literal

import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

tavily_client = TavilyClient(os.getenv("TAVILY_API_KEY"))

#define literals
Topic = Literal["general", "news", "finance"]
Time_Range = Literal["day","week","month","year"]

#adding tools from here for now
@tool
def search_web(query: str, max_results: int = 5, topic: Topic = "general", time_range: Time_Range | None = None, country: str | None = None) -> list | str:
    """Search the web for the given query."""
    try:
        options_country = {}
        options_time_range = {}
        if country:
            options_country['country'] = country

        if time_range:
            options_time_range['time_range'] = time_range

        response = tavily_client.search(
            query,
            max_results=max_results,
            topic=topic,
            **options_time_range,
            **options_country,
        )
        
        return response.get("results", [])
    except Exception as e:
        return f"Error: Search failed - {e}"