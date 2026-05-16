"""Health & system routes: GET /health, GET /health/debug"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter
from core.config import settings
from core.lifespan import container

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subsystems": {
            "chromadb": container.retrieval_system is not None,
            "clip_model": (
                container.retrieval_system is not None
                and container.retrieval_system.clip_model is not None
            ),
            "gemini_dispatcher": container.response_generator is not None,
            "dispatcher_agent": container.dispatcher_agent is not None,
            "web_search": container.web_search_agent is not None,
        },
        "config": {
            "use_gemini": settings.use_gemini_for_dispatcher,
            "gemini_model": settings.gemini_model_name,
            "top_k": settings.top_k,
            "history_turns": settings.history_turns,
        },
    }


@router.get("/health/debug")
def health_debug():
    collection_count = 0
    if container.retrieval_system:
        try:
            collection_count = container.retrieval_system.collection.count()
        except Exception:
            pass

    return {
        "google_api_key_present": bool(settings.google_api_key),
        "gemini_api_key_present": bool(settings.gemini_api_key),
        "tavily_api_key_present": bool(settings.tavily_api_key),
        "web_search_enabled": settings.enable_web_search,
        "search_agent_initialized": container.web_search_agent is not None,
        "chromadb_path": settings.chroma_db_dir,
        "collection_name": settings.collection_name,
        "collection_count": collection_count,
    }
