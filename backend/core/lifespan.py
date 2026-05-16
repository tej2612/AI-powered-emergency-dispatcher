"""
Application startup / shutdown lifespan + shared container.

All heavy objects (models, ChromaDB client, agents) are loaded once at startup
and stored in AppContainer, which is dependency-injected into route handlers.
Session-scoped ConversationManagers are stored in container.sessions keyed by
the client-provided session_id UUID.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI

from core.config import settings
from models.model_loader import ModelLoader
from models.retrieval import RetrievalSystem
from models.gemini_dispatcher import GeminiDispatcher
from models.response_generator import ResponseGenerator
from models.dispatcher_agent import DispatcherAgent
from utils.conversation_utils import ConversationManager
from utils.web_search import WebSearchAgent

if TYPE_CHECKING:
    pass


class AppContainer:
    """Holds all singleton application objects."""

    def __init__(self) -> None:
        self.retrieval_system: RetrievalSystem | None = None
        self.response_generator: GeminiDispatcher | ResponseGenerator | None = None
        self.dispatcher_agent: DispatcherAgent | None = None
        self.web_search_agent: WebSearchAgent | None = None
        # Per-session conversation managers keyed by session_id
        self.sessions: dict[str, ConversationManager] = {}

    def get_or_create_session(self, session_id: str) -> ConversationManager:
        """Return existing session or create a fresh one."""
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationManager(settings.history_turns)
        return self.sessions[session_id]


# Module-level singleton — import `container` wherever needed
container = AppContainer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context: load models on startup, clean up on shutdown."""

    print("🚀 Starting Emergency Response API (FastAPI)...")
    print(f"🔧 Device: {settings.device}")
    print(f"📊 ChromaDB path: {settings.chroma_db_dir}")

    loader = ModelLoader(settings)

    if settings.use_gemini_for_dispatcher and settings.google_api_key:
        print("🤖 Using Gemini API for dispatcher responses")
        loader.load_chromadb()
        loader.load_clip_model()
        models = loader.get_models()

        container.retrieval_system = RetrievalSystem(
            models["collection"], models["clip_model"], settings
        )
        container.response_generator = GeminiDispatcher(
            api_key=settings.google_api_key,
            model_name=settings.gemini_model_name,
        )
    else:
        print("🤖 Using LoRA model for dispatcher responses")
        loader.load_all_models()
        models = loader.get_models()

        container.retrieval_system = RetrievalSystem(
            models["collection"], models["clip_model"], settings
        )
        container.response_generator = ResponseGenerator(
            models["model"], models["tokenizer"], settings
        )

    container.dispatcher_agent = DispatcherAgent(settings)

    if settings.enable_web_search and settings.tavily_api_key and settings.gemini_api_key:
        try:
            container.web_search_agent = WebSearchAgent(
                tavily_api_key=settings.tavily_api_key,
                gemini_api_key=settings.gemini_api_key,
            )
            print("✅ Web search agent initialized")
        except Exception as exc:
            print(f"⚠️  Web search agent failed to initialize: {exc}")
    else:
        print("ℹ️  Web search disabled (missing keys or config)")

    print("✅ Application ready")

    yield  # ← server is running while we're here

    # ── Shutdown ──────────────────────────────────────────────────────────────
    print("🛑 Shutting down — clearing sessions...")
    container.sessions.clear()
    print("✅ Shutdown complete")
