"""Retrieval service — wraps RetrievalSystem for use by routes."""

from __future__ import annotations

from core.lifespan import AppContainer
from schemas.retrieval import RetrievedResult, RetrievalResponse, CollectionStats
from utils.conversation_utils import infer_image_damage_and_info


def _raw_to_schema(r: dict) -> RetrievedResult:
    damage, info = infer_image_damage_and_info(r)
    return RetrievedResult(
        id=r.get("id", ""),
        tweet_text=r.get("tweet_text", ""),
        tweet_id=r.get("tweet_id", "unknown"),
        image_id=r.get("image_id"),
        disaster_type=r.get("disaster_type", "Other"),
        extracted_location=r.get("extracted_location", ""),
        source_file=r.get("source_file", ""),
        score=r.get("score", 0.0),
        image_base64=r.get("image_base64"),
        image_caption=r.get("image_caption", ""),
        image_damage=damage or "",
        image_info=info,
    )


def search(
    query: str,
    top_k: int,
    filter_disaster_type: str | None,
    ctx: AppContainer,
) -> RetrievalResponse:
    if filter_disaster_type:
        raw = ctx.retrieval_system.retrieve_by_disaster_type(filter_disaster_type, top_k)
    else:
        raw = ctx.retrieval_system.retrieve_topk(query, top_k)

    results = [_raw_to_schema(r) for r in raw]
    return RetrievalResponse(query=query, total_results=len(results), results=results)


def collection_stats(ctx: AppContainer) -> CollectionStats:
    """Return basic stats about the ChromaDB collection."""
    collection = ctx.retrieval_system.collection
    total = collection.count()

    # Best-effort breakdown by disaster_type metadata field
    breakdown: dict[str, int] = {}
    try:
        all_meta = collection.get(include=["metadatas"])["metadatas"]
        for meta in all_meta:
            dt = (meta or {}).get("disaster_type", "Unknown")
            breakdown[dt] = breakdown.get(dt, 0) + 1
    except Exception:
        pass

    return CollectionStats(
        collection_name=collection.name,
        total_documents=total,
        disaster_type_breakdown=breakdown,
    )
