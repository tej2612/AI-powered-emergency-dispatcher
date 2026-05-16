"""
Search routes:
  POST /search/query — standalone web search (debug / testing)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from core.lifespan import AppContainer, container
from schemas.search import SearchQueryRequest, WebSearchResult
import services.search_service as search_svc

router = APIRouter(prefix="/search", tags=["search"])


def get_container() -> AppContainer:
    return container


@router.post("/query", response_model=WebSearchResult)
def query(req: SearchQueryRequest, ctx: AppContainer = Depends(get_container)):
    """Run the WebSearchAgent pipeline directly for testing/debugging."""
    return search_svc.run_search(req.conversation_history, req.search_all, ctx)
