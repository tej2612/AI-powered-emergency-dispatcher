"""
Responder routes:
  GET /responders                     — list all available locations
  GET /responders/query               — query units by location + disaster types
  GET /responders/{responder_id}      — fetch a single responder by ID
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from database.responder_db import (
    find_available_responders,
    get_all_locations,
    get_responder_by_id,
)
from schemas.dispatch import Responder

router = APIRouter(prefix="/responders", tags=["responders"])


@router.get("/")
def list_locations():
    """Return all cities/areas that have responders in the database."""
    return {"locations": get_all_locations()}


@router.get("/query")
def query_responders(
    location: str = Query(..., description="City/area name, e.g. 'los angeles'"),
    disaster_types: str = Query(..., description="Comma-separated types, e.g. 'fire,medical'"),
):
    """Find available responder units for a location and set of disaster types."""
    types_list = [t.strip().lower() for t in disaster_types.split(",") if t.strip()]
    raw = find_available_responders(location, types_list)
    responders = [Responder(**r) for r in raw]
    return {
        "location": location,
        "disaster_types": types_list,
        "responders": responders,
        "total_units": len(responders),
    }


@router.get("/{responder_id}", response_model=Responder)
def get_responder(responder_id: str):
    """Fetch a single responder by ID (e.g. 'FR-001')."""
    result = get_responder_by_id(responder_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Responder '{responder_id}' not found.")
    return Responder(**result)
