"""Pydantic schemas for chat domain."""

from __future__ import annotations
from pydantic import BaseModel, Field
from schemas.retrieval import RetrievedResult
from schemas.dispatch import DispatcherState
from schemas.search import WebSearchResult


class ConversationTurn(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Client-managed UUID identifying the conversation session")
    message: str = Field(..., min_length=1, description="Caller's emergency message")
    enable_web_search: bool = Field(True, description="Set False to skip Tavily real-time search")


class ChatResponse(BaseModel):
    session_id: str
    response: str
    retrieved_results: list[RetrievedResult]
    dispatcher_state: DispatcherState
    web_search: WebSearchResult


class ClearSessionResponse(BaseModel):
    session_id: str
    status: str
    message: str


class HistoryResponse(BaseModel):
    session_id: str
    history: list[ConversationTurn]
    turn_count: int
