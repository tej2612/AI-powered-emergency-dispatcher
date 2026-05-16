"""Pydantic schemas for retrieval domain."""

from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class RetrievedResult(BaseModel):
    id: str
    tweet_text: str
    tweet_id: str
    image_id: str | None = None
    disaster_type: str  # Wildfire | Earthquake | Flood | Hurricane | Other
    extracted_location: str
    source_file: str
    score: float
    image_base64: str | None = None
    image_caption: str
    image_damage: Literal["HIGH", "MEDIUM", "LOW", ""] | None = None
    image_info: Literal["INFORMATIVE", "NOT INFORMATIVE"] | None = None


class RetrievalRequest(BaseModel):
    query: str
    top_k: int = 5
    filter_disaster_type: str | None = None


class RetrievalResponse(BaseModel):
    query: str
    total_results: int
    results: list[RetrievedResult]


class CollectionStats(BaseModel):
    collection_name: str
    total_documents: int
    disaster_type_breakdown: dict[str, int]
