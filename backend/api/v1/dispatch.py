"""
Dispatch routes:
  POST /dispatch/analyze — re-run dispatch analysis for a session
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from core.lifespan import AppContainer, container
from schemas.dispatch import DispatchAnalyzeRequest, DispatcherState
import services.dispatch_service as dispatch_svc

router = APIRouter(prefix="/dispatch", tags=["dispatch"])


def get_container() -> AppContainer:
    return container


@router.post("/analyze", response_model=DispatcherState)
def analyze(req: DispatchAnalyzeRequest, ctx: AppContainer = Depends(get_container)):
    """Re-run dispatch analysis for an existing session without generating a new response."""
    return dispatch_svc.analyze(req.session_id, ctx)
