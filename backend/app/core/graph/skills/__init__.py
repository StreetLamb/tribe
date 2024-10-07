from langchain.pydantic_v1 import BaseModel
from langchain.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langchain_community.utilities import (WikipediaAPIWrapper)
from app.core.graph.skills.mercurio import mercurio
from app.core.graph.skills.hermes import hermes
from app.core.graph.skills.hades import hades
from app.core.graph.skills.erebos import erebos
from app.core.graph.skills.pluton import pluton

# from .calculator import multiply


class SkillInfo(BaseModel):
    description: str
    tool: BaseTool


managed_skills: dict[str, SkillInfo] = {
    "duckduckgo-search": SkillInfo(
        description="Searches the web using DuckDuckGo", 
        tool=DuckDuckGoSearchRun()
    ),
    "wikipedia": SkillInfo(
        description="Searches Wikipedia",
        tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    ), 
    "yahoo-finance": SkillInfo(
        description="Get information from Yahoo Finance News",
        tool=YahooFinanceNewsTool(),
    ),
    "Mercurio": SkillInfo(
        description="Process a CSV file from S3, make a reports in PDF, and upload it to the app.",
        tool=mercurio,
    ),
    "Hermes": SkillInfo(
        description="Returns a dictionary containing the file path and its metadata",
        tool=hermes,
    ),
    "Hades": SkillInfo(
        description="Searches for money-related files in S3",
        tool=hades,
    ),
    "Erebos": SkillInfo(  
        description="Checks if an email address has been involved in any known data breaches.",
        tool=erebos,
    ),
    "Pluton": SkillInfo(
        description="Validates partial credit card numbers",
        tool=pluton,
    ),
}

# To add more custom tools, follow these steps:
# 1. Create a new Python file in the `skills` folder (e.g., `calculator.py`).
# 2. Define your tool. Refer to `calculator.py` or see https://python.langchain.com/v0.2/docs/how_to/custom_tools/
# 3. Import your new tool here and add it to the `managed_skills` dictionary above.
