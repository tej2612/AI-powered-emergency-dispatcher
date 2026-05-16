"""
Retrieval routes:
  POST /retrieval/search             — standalone ChromaDB vector search
  GET  /retrieval/collection/stats   — collection document counts
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from core.lifespan import AppContainer, container
from schemas.retrieval import RetrievalRequest, RetrievalResponse, CollectionStats
import services.retrieval_service as ret_svc

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


def get_container() -> AppContainer:
    return container


@router.post("/search", response_model=RetrievalResponse)
def search(req: RetrievalRequest, ctx: AppContainer = Depends(get_container)):
    """Search ChromaDB for semantically similar crisis reports."""
    top_k = min(req.top_k, 20)  # hard cap
    return ret_svc.search(req.query, top_k, req.filter_disaster_type, ctx)


@router.get("/collection/stats", response_model=CollectionStats)
def stats(ctx: AppContainer = Depends(get_container)):
    """Return total document count and per-disaster breakdown."""
    return ret_svc.collection_stats(ctx)
