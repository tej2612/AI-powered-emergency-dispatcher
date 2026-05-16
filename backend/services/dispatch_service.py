"""Dispatch service — wraps DispatcherAgent for use by routes."""

from __future__ import annotations

from core.lifespan import AppContainer
from schemas.dispatch import DispatcherState, Responder


def _build(raw: dict) -> DispatcherState:
    return DispatcherState(
        location=raw.get("location"),
        disaster_type=raw.get("disaster_type") or [],
        dispatched_units=[Responder(**u) for u in (raw.get("dispatched_units") or [])],
        analysis=raw.get("analysis", ""),
    )


def analyze(session_id: str, ctx: AppContainer) -> DispatcherState:
    """Re-run dispatch analysis for an existing session."""
    if session_id not in ctx.sessions:
        return DispatcherState(analysis="Session not found.")
    history = ctx.sessions[session_id].get_full_history()
    raw = ctx.dispatcher_agent.analyze_conversation(history)
    return _build(raw)
