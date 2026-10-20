from tool_registry import tool

#adding tools from here for now
@tool
def search_web(query: str, max_results: int = 5, topic: str = "general", time_range: str = None):
    """Search the web for the given query."""
