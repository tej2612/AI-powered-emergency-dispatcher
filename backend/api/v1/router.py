"""Aggregates all v1 routers into a single APIRouter."""

from fastapi import APIRouter

from api.v1.health import router as health_router
from api.v1.chat import router as chat_router
from api.v1.retrieval import router as retrieval_router
from api.v1.dispatch import router as dispatch_router
from api.v1.responders import router as responders_router
from api.v1.search import router as search_router

v1_router = APIRouter()

v1_router.include_router(health_router)
v1_router.include_router(chat_router)
v1_router.include_router(retrieval_router)
v1_router.include_router(dispatch_router)
v1_router.include_router(responders_router)
v1_router.include_router(search_router)
