from typing import Any

from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langchain_community.utilities import (
    WikipediaAPIWrapper,
)
from pydantic import BaseModel

# from .calculator import calculator


class SkillInfo(BaseModel):
    description: str
    tool: Any


managed_skills: dict[str, SkillInfo] = {
    "duckduckgo-search": SkillInfo(
        description="Searches the web using DuckDuckGo", tool=DuckDuckGoSearchRun()
    ),
    "wikipedia": SkillInfo(
        description="Searches Wikipedia",
        tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),  # type: ignore[call-arg]
    ),
    "yahoo-finance": SkillInfo(
        description="Get information from Yahoo Finance News.",
        tool=YahooFinanceNewsTool(),
    ),
    # "calculator": SkillInfo(
    #     description=calculator.description,
    #     tool=calculator,
    # ),
}

# To add more custom tools, follow these steps:
# 1. Create a new Python file in the `skills` folder (e.g., `calculator.py`).
# 2. Define your tool. Refer to `calculator.py` or see https://python.langchain.com/v0.1/docs/modules/tools/custom_tools/
# 3. Import your new tool here and add it to the `managed_skills` dictionary above.
