"""Web search service — wraps WebSearchAgent for standalone use."""

from __future__ import annotations

from core.lifespan import AppContainer
from schemas.search import WebSearchResult, SearchResultBlock, SearchSourceResult, SecondarySearchResult


def _sources(results_list: list[dict]) -> list[SearchSourceResult]:
    return [
        SearchSourceResult(
            title=r.get("title", ""),
            url=r.get("url", ""),
            score=r.get("score"),
        )
        for r in results_list
    ]


def run_search(
    conversation_history: list[dict[str, str]],
    search_all: bool,
    ctx: AppContainer,
) -> WebSearchResult:
    if not ctx.web_search_agent:
        return WebSearchResult(enabled=False, error="Web search agent not initialized.")

    # Convert [{role, content}] → [(role, content)] tuple format
    history_tuples = [(h["role"], h["content"]) for h in conversation_history]

    try:
        raw = ctx.web_search_agent.process_conversation(history_tuples, search_all=search_all)
    except Exception as exc:
        return WebSearchResult(enabled=True, error=str(exc))

    primary_raw = raw.get("primary_results", {})
    primary = SearchResultBlock(
        answer=primary_raw.get("answer", ""),
        results=_sources(primary_raw.get("results", [])),
    )

    secondary = [
        SecondarySearchResult(
            query=sec.get("query", ""),
            results=SearchResultBlock(
                answer=(sec.get("results") or {}).get("answer", ""),
                results=_sources((sec.get("results") or {}).get("results", [])),
            ),
        )
        for sec in raw.get("secondary_results", [])
    ]

    return WebSearchResult(
        enabled=True,
        queries=raw.get("queries"),
        primary_results=primary,
        secondary_results=secondary,
    )
