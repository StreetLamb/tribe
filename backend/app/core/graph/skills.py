from collections.abc import Callable

from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import tool
from pydantic import BaseModel


class SkillInfo(BaseModel):
    description: str
    tool: Callable


all_skills: dict[str, SkillInfo] = {
    "search": SkillInfo(
        description="Searches the web using Duck Duck Go", tool=DuckDuckGoSearchRun()
    ),
    "wikipedia": SkillInfo(
        description="Searches Wikipedia",
        tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),
    ),
}
