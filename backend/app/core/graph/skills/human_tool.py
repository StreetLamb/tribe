# This is an example showing how to create a simple calculator skill

from typing import Annotated

from langchain_core.tools import tool


@tool
def AskHuman(query: Annotated[str, "query to ask the human"]) -> None:
    """Ask the human a question to gather additional inputs"""
    pass
