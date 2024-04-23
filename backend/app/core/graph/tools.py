from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool


@tool
def nothing(query: str) -> str:
    """Placeholder Tool. Does nothing"""
    return ""


all_tools = {"nothing": nothing, "search": DuckDuckGoSearchRun()}
