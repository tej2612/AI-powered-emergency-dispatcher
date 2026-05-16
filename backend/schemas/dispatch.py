"""Pydantic schemas for dispatch domain."""

from __future__ import annotations
from pydantic import BaseModel


class Responder(BaseModel):
    id: str
    name: str
    units: int
    eta: str


class DispatcherState(BaseModel):
    location: str | None = None
    disaster_type: list[str] = []
    dispatched_units: list[Responder] = []
    analysis: str = ""


class DispatchAnalyzeRequest(BaseModel):
    session_id: str
