# 🚨 Emergency Response System

An AI-powered 911 dispatcher prototype built for a Capstone project. It combines **multimodal RAG** (ChromaDB + CLIP), **Gemini 2.5 Flash** for dispatcher dialogue, and **real-time web search** (Tavily) to assist emergency call handling.

---

## Architecture

```
Emergency_Response_7/
├── backend/          # FastAPI (Python, uv)
├── frontend/         # Vite + React + TypeScript
├── api.md            # Full API reference
│
│   ── Standalone scripts (untouched originals) ──
├── setup_chromadb.py             # Initial ChromaDB setup
├── setup_chromadb_multimodal.py  # Multimodal collection setup
├── capstone_metrics.py           # Evaluation metrics
├── rag_testing.py                # RAG pipeline tests
├── nerbert.py                    # NER utilities
├── scripts/                      # One-off utility scripts
└── requirements.txt              # Legacy pip reference
```

### System Flow

```
Caller message
    │
    ├─► ChromaDB (CLIP embeddings) ──► Top-K similar crisis reports
    │
    ├─► WebSearchAgent (Gemini + Tavily) ──► Real-time web summary
    │
    └─► GeminiDispatcher (gemini-2.5-flash)
            ├── context: retrieved reports + web summary + history
            └── output: professional 911 dispatcher response
                    │
                    └─► DispatcherAgent (flan-t5-base)
                            └── location + disaster type → responder units
```

---

## Backend

**Stack:** FastAPI · uv · Pydantic v2 · ChromaDB · CLIP · Gemini API · Tavily

### Structure

```
backend/
├── main.py               # FastAPI entry point
├── pyproject.toml        # uv project config
├── .env                  # API keys (never committed)
├── core/
│   ├── config.py         # Pydantic Settings
│   └── lifespan.py       # Startup/shutdown + AppContainer
├── api/v1/
│   ├── router.py         # Aggregates all routers
│   ├── health.py         # GET /health, GET /health/debug
│   ├── chat.py           # POST /chat, DELETE /chat/{id}
│   ├── retrieval.py      # POST /retrieval/search
│   ├── dispatch.py       # POST /dispatch/analyze
│   ├── responders.py     # GET /responders, /responders/query
│   └── search.py         # POST /search/query
├── schemas/              # Pydantic v2 request/response models
├── services/             # Business logic (pipeline orchestration)
├── models/               # AI model wrappers (copied from original)
├── utils/                # Conversation, image, web search utils
├── database/             # Responder lookup database
└── ingestion/            # PySpark + ChromaDB ingestion pipeline
```

### Setup

1. **Install uv** (if not already):
   ```bash
   pip install uv
   ```

2. **Create and populate `.env`:**
   ```env
   GOOGLE_API_KEY=your_google_api_key
   GEMINI_API_KEY=your_gemini_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

3. **Install dependencies:**
   ```bash
   cd backend
   uv sync
   ```

4. **Start the server:**
   ```bash
   uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

5. **Explore the API:**
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc
   - Health check: http://127.0.0.1:8000/api/v1/health

> See [api.md](./api.md) for the full API reference with request/response schemas.

### Key Design Decisions

| Decision | Rationale |
|---|---|
| **Per-session ConversationManager** | Supports concurrent users; each UUID session is isolated |
| **Uppercase property shims** on `Settings` | Copied model code uses `config.DEVICE`, `config.TOP_K`, etc. — zero rewrites needed |
| **Services layer** | Routes stay thin (HTTP only); all pipeline logic lives in `services/` |
| **Lifespan context manager** | Models load once at startup, clean shutdown on exit |

---

## Frontend

**Stack:** Vite · React · TypeScript · Axios

### Structure

```
frontend/src/
├── api/              # Typed API client functions (one file per domain)
├── types/            # TypeScript interfaces mirroring Pydantic schemas
├── hooks/
│   ├── useChat.ts    # Conversation state + API calls
│   └── useSession.ts # UUID session via sessionStorage
└── components/
    ├── chat/         # ChatPanel, MessageBubble, MessageInput
    ├── retrieval/    # RetrievedResultsPanel, CrisisCard
    ├── dispatch/     # DispatcherPanel, ResponderCard
    └── search/       # WebSearchPanel
```

### Setup

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

The Vite dev server proxies `/api` → `http://127.0.0.1:8000` automatically — no CORS config needed during development.

### UI Layout

```
┌────────────────────────────────────────────────────────────────┐
│  🚨 Emergency Response System          ● SYSTEM LIVE           │
├─────────────────┬──────────────────────┬───────────────────────┤
│  🎙️ Emergency   │  📊 Retrieved Crisis  │  🤖 AI Dispatcher     │
│     Call        │     Data             │                       │
│                 ├──────────────────────┤  📍 Location          │
│  [Chat thread]  │  🔍 Real-Time        │  🔥 Emergency Type    │
│                 │     Intelligence     │                       │
│  [Input + send] │                      │  [Responder units]    │
└─────────────────┴──────────────────────┴───────────────────────┘
```

---

## Running Both Together

```bash
# Terminal 1 — Backend
cd Emergency_Response_7/backend
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 — Frontend
cd Emergency_Response_7/frontend
npm run dev
```

Then open **http://localhost:5173** in your browser.

---

## Dataset

The system is trained on **[CrisisMMD](https://crisisnlp.qcri.org/crisismmd)** — a multimodal crisis dataset of Twitter posts with images from real disaster events:

| Disaster | Region |
|---|---|
| 🔥 Wildfire | California, USA |
| 🌋 Earthquake | Mexico |
| 🌊 Flood | Sri Lanka |
| 🌀 Hurricane Maria | Puerto Rico |

Only `informative` text + image pairs are stored. Embeddings are a weighted blend: **70% text / 20% image / 10% location**.

---

## ChromaDB Setup

Before running, the vector database must be populated:

```bash
cd backend
# Set up the multimodal collection
uv run python ../setup_chromadb_multimodal.py

# Or ingest new data
uv run python ingestion/spark_ingestion.py
```

The ChromaDB store is expected at `D:/Capstone_Prototype/ChromaDB/chromadb_store_multimodal` (configurable via `.env` → `CHROMA_DB_DIR`).

---

## API Reference

See **[api.md](./api.md)** for the complete reference including:
- All 12 endpoints across 6 domains
- Full JSON request/response examples
- TypeScript interface definitions
- Error response table
