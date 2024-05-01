from typing import Any

from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.tools.google_finance import GoogleFinanceQueryRun
from langchain_community.tools.google_jobs import GoogleJobsQueryRun
from langchain_community.tools.google_scholar import GoogleScholarQueryRun
from langchain_community.tools.google_trends import GoogleTrendsQueryRun
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langchain_community.utilities import (
    GoogleFinanceAPIWrapper,
    GoogleJobsAPIWrapper,
    GoogleScholarAPIWrapper,
    GoogleTrendsAPIWrapper,
    WikipediaAPIWrapper,
)
from pydantic import BaseModel


class SkillInfo(BaseModel):
    description: str
    tool: Any


all_skills: dict[str, SkillInfo] = {
    "duckduckgo-search": SkillInfo(
        description="Searches the web using DuckDuckGo", tool=DuckDuckGoSearchRun()
    ),
    "wikipedia": SkillInfo(
        description="Searches Wikipedia",
        tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),  # type: ignore[call-arg]
    ),
    "google-finance": SkillInfo(
        description="Get information from Google Finance Page via SerpApi.",
        tool=GoogleFinanceQueryRun(api_wrapper=GoogleFinanceAPIWrapper()),  # type: ignore[call-arg]
    ),
    "google-jobs": SkillInfo(
        description="Fetch current job postings from Google Jobs via SerpApi.",
        tool=GoogleJobsQueryRun(api_wrapper=GoogleJobsAPIWrapper()),  # type: ignore[call-arg]
    ),
    "google-scholar": SkillInfo(
        description="Fetch papers from Google Scholar via SerpApi.",
        tool=GoogleScholarQueryRun(api_wrapper=GoogleScholarAPIWrapper()),
    ),
    "google-trends": SkillInfo(
        description="Get information from Google Trends Page via SerpApi.",
        tool=GoogleTrendsQueryRun(api_wrapper=GoogleTrendsAPIWrapper()),  # type: ignore[call-arg]
    ),
    "yahoo-finance": SkillInfo(
        description="Get information from Yahoo Finance News.",
        tool=YahooFinanceNewsTool(),
    ),
}
