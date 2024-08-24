# mypy: disable-error-code="attr-defined, arg-type"
from langchain.pydantic_v1 import BaseModel
from langchain.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langchain_community.utilities import (
    WikipediaAPIWrapper,
)

from .human_tool import AskHuman

# from .calculator import multiply


class SkillInfo(BaseModel):
    description: str
    tool: BaseTool


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
    "ask-human": SkillInfo(
        description=AskHuman.description,
        tool=AskHuman,
    ),
    # multiply.name: SkillInfo(
    #     description=multiply.description,
    #     tool=multiply,
    # ),
}

# To add more custom tools, follow these steps:
# 1. Create a new Python file in the `skills` folder (e.g., `calculator.py`).
# 2. Define your tool. Refer to `calculator.py` or see https://python.langchain.com/v0.2/docs/how_to/custom_tools/
# 3. Import your new tool here and add it to the `managed_skills` dictionary above.
