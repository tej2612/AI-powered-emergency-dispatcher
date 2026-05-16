"""Pydantic schemas for web search domain."""

from __future__ import annotations
from pydantic import BaseModel


class SearchSourceResult(BaseModel):
    title: str
    url: str
    score: float | None = None


class SearchResultBlock(BaseModel):
    answer: str = ""
    results: list[SearchSourceResult] = []


class SecondarySearchResult(BaseModel):
    query: str
    results: SearchResultBlock


class WebSearchResult(BaseModel):
    enabled: bool = False
    queries: dict[str, str | list[str]] | None = None
    primary_results: SearchResultBlock | None = None
    secondary_results: list[SecondarySearchResult] = []
    error: str | None = None


class SearchQueryRequest(BaseModel):
    conversation_history: list[dict[str, str]]  # [{"role": "user"|"assistant", "content": "..."}]
    search_all: bool = True
