# This is an example showing how to create a simple calculator skill

from typing import Annotated

from langchain_core.tools import tool


@tool
def multiply(
    a: Annotated[int, "first number"], b: Annotated[int, "second number"]
) -> int:
    """Multiple two numbers."""
    return a * b
