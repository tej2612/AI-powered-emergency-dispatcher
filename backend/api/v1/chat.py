"""
Chat routes:
  POST   /chat                      — send a message through the full pipeline
  DELETE /chat/{session_id}         — clear conversation and dispatcher state
  GET    /chat/{session_id}/history — fetch full conversation history
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from core.lifespan import AppContainer, container
from schemas.chat import ChatRequest, ChatResponse, ClearSessionResponse, HistoryResponse
import services.chat_service as chat_svc

router = APIRouter(prefix="/chat", tags=["chat"])


def get_container() -> AppContainer:
    return container


@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest, ctx: AppContainer = Depends(get_container)):
    """Send an emergency message through retrieval → web search → LLM → dispatch."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message field must not be empty")
    return await chat_svc.process_chat(
        session_id=req.session_id,
        message=req.message,
        enable_web_search=req.enable_web_search,
        ctx=ctx,
    )


@router.delete("/{session_id}", response_model=ClearSessionResponse)
def clear(session_id: str, ctx: AppContainer = Depends(get_container)):
    """Clear conversation history and reset dispatcher state for a session."""
    return chat_svc.clear_session(session_id, ctx)


@router.get("/{session_id}/history", response_model=HistoryResponse)
def history(session_id: str, ctx: AppContainer = Depends(get_container)):
    """Return full conversation history for a session."""
    return chat_svc.get_history(session_id, ctx)
