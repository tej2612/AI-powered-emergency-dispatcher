"""
Chat service — orchestrates the full pipeline:
  retrieval → web search → LLM response → dispatch analysis
"""

from __future__ import annotations

from core.lifespan import AppContainer
from schemas.chat import ChatResponse, ClearSessionResponse, HistoryResponse, ConversationTurn
from schemas.retrieval import RetrievedResult
from schemas.dispatch import DispatcherState, Responder
from schemas.search import WebSearchResult, SearchResultBlock, SearchSourceResult, SecondarySearchResult
from utils.conversation_utils import infer_image_damage_and_info


def _build_retrieved_results(raw: list[dict]) -> list[RetrievedResult]:
    """Annotate raw retrieval dicts with damage/info and convert to schema."""
    results = []
    for r in raw:
        damage, info = infer_image_damage_and_info(r)
        r["image_damage"] = damage
        r["image_info"] = info
        results.append(RetrievedResult(**{
            "id": r.get("id", ""),
            "tweet_text": r.get("tweet_text", ""),
            "tweet_id": r.get("tweet_id", "unknown"),
            "image_id": r.get("image_id"),
            "disaster_type": r.get("disaster_type", "Other"),
            "extracted_location": r.get("extracted_location", ""),
            "source_file": r.get("source_file", ""),
            "score": r.get("score", 0.0),
            "image_base64": r.get("image_base64"),
            "image_caption": r.get("image_caption", ""),
            "image_damage": damage or "",
            "image_info": info,
        }))
    return results


def _extract_search_summary(search_results: dict | None) -> str | None:
    """Condense web search results into a short text block for the LLM prompt."""
    if not search_results or search_results.get("error"):
        return None

    parts: list[str] = []

    primary = search_results.get("primary_results", {})
    if primary.get("answer"):
        parts.append(f"PRIMARY INFORMATION:\n{primary['answer']}")
    if primary.get("results"):
        titles = [f"- {r.get('title', 'Source')}" for r in primary["results"][:3]]
        parts.append("Top Sources:\n" + "\n".join(titles))

    for sec in search_results.get("secondary_results", []):
        query = sec.get("query", "")
        answer = (sec.get("results") or {}).get("answer", "")
        if answer:
            parts.append(f"\nADDITIONAL INFORMATION ({query}):\n{answer}")

    return "\n\n".join(parts) if parts else None


def _build_web_search_schema(raw: dict | None, enabled: bool) -> WebSearchResult:
    """Convert the raw web_search agent dict into the typed schema."""
    if not enabled or raw is None:
        return WebSearchResult(enabled=False)

    if raw.get("error") and not raw.get("primary_results"):
        return WebSearchResult(enabled=True, error=raw["error"])

    def _source_results(results_list: list[dict]) -> list[SearchSourceResult]:
        return [
            SearchSourceResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                score=r.get("score"),
            )
            for r in results_list
        ]

    primary_raw = raw.get("primary_results", {})
    primary = SearchResultBlock(
        answer=primary_raw.get("answer", ""),
        results=_source_results(primary_raw.get("results", [])),
    )

    secondary = [
        SecondarySearchResult(
            query=sec.get("query", ""),
            results=SearchResultBlock(
                answer=(sec.get("results") or {}).get("answer", ""),
                results=_source_results((sec.get("results") or {}).get("results", [])),
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


def _build_dispatcher_state(raw: dict) -> DispatcherState:
    """Convert raw dispatcher dict to typed schema."""
    return DispatcherState(
        location=raw.get("location"),
        disaster_type=raw.get("disaster_type") or [],
        dispatched_units=[Responder(**u) for u in (raw.get("dispatched_units") or [])],
        analysis=raw.get("analysis", ""),
    )


async def process_chat(
    session_id: str,
    message: str,
    enable_web_search: bool,
    ctx: AppContainer,
) -> ChatResponse:
    """Full chat pipeline. Async wrapper; heavy ML calls are synchronous."""

    session = ctx.get_or_create_session(session_id)

    # 1. Vector retrieval
    raw_retrieved = ctx.retrieval_system.retrieve_topk(message)
    retrieved = _build_retrieved_results(raw_retrieved)

    # 2. Web search (optional)
    raw_search: dict | None = None
    web_search_summary: str | None = None

    if enable_web_search and ctx.web_search_agent:
        try:
            history_with_current = session.get_full_history() + [("user", message)]
            raw_search = ctx.web_search_agent.process_conversation(
                history_with_current, search_all=True
            )
            web_search_summary = _extract_search_summary(raw_search)
        except Exception as exc:
            print(f"⚠️  Web search error: {exc}")
            raw_search = {"error": str(exc)}

    # 3. LLM response generation
    llm_response: str = ctx.response_generator.generate_response(
        message,
        raw_retrieved,
        session.get_full_history(),
        web_search_summary=web_search_summary,
    )

    # 4. Update conversation history
    session.add_turn("user", message)
    session.add_turn("assistant", llm_response)

    # 5. Dispatch analysis
    raw_dispatch = ctx.dispatcher_agent.analyze_conversation(session.get_full_history())
    dispatcher_state = _build_dispatcher_state(raw_dispatch)

    return ChatResponse(
        session_id=session_id,
        response=llm_response,
        retrieved_results=retrieved,
        dispatcher_state=dispatcher_state,
        web_search=_build_web_search_schema(raw_search, enable_web_search),
    )


def clear_session(session_id: str, ctx: AppContainer) -> ClearSessionResponse:
    if session_id not in ctx.sessions:
        return ClearSessionResponse(
            session_id=session_id,
            status="not_found",
            message=f"Session '{session_id}' did not exist.",
        )
    ctx.sessions.pop(session_id)
    ctx.dispatcher_agent.reset_state()
    return ClearSessionResponse(
        session_id=session_id,
        status="cleared",
        message="Conversation history and dispatcher state reset.",
    )


def get_history(session_id: str, ctx: AppContainer) -> HistoryResponse:
    if session_id not in ctx.sessions:
        return HistoryResponse(session_id=session_id, history=[], turn_count=0)
    raw = ctx.sessions[session_id].get_full_history()
    turns = [ConversationTurn(role=role, content=text) for role, text in raw]
    return HistoryResponse(session_id=session_id, history=turns, turn_count=len(turns))
