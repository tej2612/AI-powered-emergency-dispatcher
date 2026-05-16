# Emergency Response System — API Reference

> **Base URL:** `http://localhost:8000/api/v1`  
> **Content-Type:** `application/json`  
> **CORS:** Configured to allow `http://localhost:5173` (Vite dev server)

---

## Table of Contents

1. [Health & System](#1-health--system)
2. [Chat & Conversation](#2-chat--conversation)
3. [Retrieval](#3-retrieval)
4. [Dispatch](#4-dispatch)
5. [Responders](#5-responders)
6. [Web Search (Debug)](#6-web-search-debug)
7. [Shared Schemas](#7-shared-schemas)

---

## 1. Health & System

### `GET /health`

Returns the operational status of all subsystems.

**Response `200 OK`**
```json
{
  "status": "healthy",
  "timestamp": "2026-05-16T22:00:00+05:30",
  "subsystems": {
    "chromadb": true,
    "clip_model": true,
    "gemini_dispatcher": true,
    "dispatcher_agent": true,
    "web_search": true
  },
  "config": {
    "use_gemini": true,
    "gemini_model": "gemini-2.5-flash",
    "top_k": 5,
    "history_turns": 6
  }
}
```

---

### `GET /health/debug`

Detailed debug info about API key presence and subsystem config. Does not expose key values.

**Response `200 OK`**
```json
{
  "google_api_key_present": true,
  "gemini_api_key_present": true,
  "tavily_api_key_present": true,
  "web_search_enabled": true,
  "search_agent_initialized": true,
  "chromadb_path": "D:/Capstone_Prototype/ChromaDB/chromadb_store_multimodal",
  "collection_name": "crisis_multimodal",
  "collection_count": 4821
}
```

---

## 2. Chat & Conversation

### `POST /chat`

Core endpoint. Sends a caller message through the full pipeline:
retrieval → optional web search → Gemini response generation → dispatch analysis.

**Request Body**
```json
{
  "session_id": "abc-123-xyz",
  "message": "There's a massive fire at 5th and Main, people are trapped inside",
  "enable_web_search": true
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | `string` | ✅ | Client-managed UUID that tracks the conversation. A new UUID starts a fresh session. |
| `message` | `string` | ✅ | The caller's raw emergency message. |
| `enable_web_search` | `boolean` | ❌ | If `false`, skips Tavily search. Defaults to `true`. |

**Response `200 OK`**
```json
{
  "session_id": "abc-123-xyz",
  "response": "911 dispatch here — I've received your report of a fire at 5th and Main with trapped individuals. Units are being dispatched immediately. Are you currently inside the building or at a safe distance?",
  "retrieved_results": [
    {
      "id": "wildfire_california_..._918318861522313216_0",
      "tweet_text": "Massive fire engulfs apartment complex, residents evacuating...",
      "tweet_id": "918318861522313216",
      "image_id": "918318861522313216_0",
      "disaster_type": "Wildfire",
      "extracted_location": "Santa Rosa, CA",
      "source_file": "california_wildfire_with_captions.tsv",
      "score": 0.91,
      "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgAB...",
      "image_caption": "Massive fire engulfs apartment complex...",
      "image_damage": "HIGH",
      "image_info": "INFORMATIVE"
    }
  ],
  "dispatcher_state": {
    "location": "5th and main",
    "disaster_type": ["fire"],
    "dispatched_units": [
      {
        "id": "FR-001",
        "name": "Santa Rosa Fire Station 1",
        "units": 3,
        "eta": "5 mins"
      }
    ],
    "analysis": "Location confirmed: 5th And Main. Emergency type: fire. Dispatching 1 units including Santa Rosa Fire Station 1. ETA: 5 mins."
  },
  "web_search": {
    "enabled": true,
    "queries": {
      "primary": "fire 5th Main Street trapped people rescue",
      "secondary": [
        "building fire evacuation procedures",
        "trapped occupants fire rescue protocol"
      ]
    },
    "primary_results": {
      "answer": "In a building fire with trapped occupants, firefighters use thermal imaging cameras...",
      "results": [
        {
          "title": "NFPA: Building Fire Rescue Protocols",
          "url": "https://nfpa.org/...",
          "score": 0.88
        }
      ]
    },
    "secondary_results": [
      {
        "query": "building fire evacuation procedures",
        "results": {
          "answer": "Standard fire evacuation includes...",
          "results": []
        }
      }
    ]
  }
}
```

**Error Responses**

| Status | Body | Cause |
|---|---|---|
| `400` | `{"detail": "message field is required"}` | Empty or missing message |
| `422` | Pydantic validation error | Malformed request body |
| `500` | `{"detail": "Internal pipeline error: ..."}` | LLM or ChromaDB failure |

---

### `DELETE /chat/{session_id}`

Clears the conversation history and resets the dispatcher state for a given session.

**Path Parameters**

| Parameter | Type | Description |
|---|---|---|
| `session_id` | `string` | The session UUID to clear |

**Response `200 OK`**
```json
{
  "session_id": "abc-123-xyz",
  "status": "cleared",
  "message": "Conversation history and dispatcher state reset."
}
```

**Error `404`**
```json
{
  "detail": "Session 'abc-123-xyz' not found."
}
```

---

### `GET /chat/{session_id}/history`

Returns the full conversation history for a session.

**Response `200 OK`**
```json
{
  "session_id": "abc-123-xyz",
  "history": [
    { "role": "user", "content": "There's a fire at 5th and Main" },
    { "role": "assistant", "content": "911 dispatch here..." }
  ],
  "turn_count": 2
}
```

---

## 3. Retrieval

### `POST /retrieval/search`

Standalone endpoint to search the ChromaDB vector store without generating an LLM response. Useful for testing retrieval quality independently.

**Request Body**
```json
{
  "query": "flooding in residential area with people on rooftops",
  "top_k": 5,
  "filter_disaster_type": "Flood"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `query` | `string` | ✅ | Free-text search query |
| `top_k` | `integer` | ❌ | Number of results (default: 5, max: 20) |
| `filter_disaster_type` | `string` | ❌ | One of: `Wildfire`, `Earthquake`, `Flood`, `Hurricane`, `Other` |

**Response `200 OK`**
```json
{
  "query": "flooding in residential area with people on rooftops",
  "total_results": 5,
  "results": [
    {
      "id": "srilanka_flood_..._823456789012345678_1",
      "tweet_text": "Families stranded on rooftops as floodwaters rise in Colombo...",
      "tweet_id": "823456789012345678",
      "image_id": "823456789012345678_1",
      "disaster_type": "Flood",
      "extracted_location": "Colombo, Sri Lanka",
      "source_file": "srilanka_floods_with_captions.tsv",
      "score": 0.87,
      "image_base64": "data:image/jpeg;base64,...",
      "image_caption": "Families stranded on rooftops...",
      "image_damage": "HIGH",
      "image_info": "INFORMATIVE"
    }
  ]
}
```

---

### `GET /retrieval/collection/stats`

Returns statistics about the ChromaDB collection.

**Response `200 OK`**
```json
{
  "collection_name": "crisis_multimodal",
  "total_documents": 4821,
  "disaster_type_breakdown": {
    "Wildfire": 1204,
    "Earthquake": 1056,
    "Flood": 1389,
    "Hurricane": 1172
  }
}
```

---

## 4. Dispatch

### `POST /dispatch/analyze`

Re-runs dispatch analysis on a given conversation history without generating a new chat response. Useful for refreshing the dispatcher panel.

**Request Body**
```json
{
  "session_id": "abc-123-xyz"
}
```

**Response `200 OK`**
```json
{
  "session_id": "abc-123-xyz",
  "location": "5th and main",
  "disaster_type": ["fire"],
  "dispatched_units": [
    {
      "id": "FR-001",
      "name": "Santa Rosa Fire Station 1",
      "units": 3,
      "eta": "5 mins"
    }
  ],
  "analysis": "Location confirmed: 5th And Main. Emergency type: fire. Dispatching 1 units..."
}
```

---

## 5. Responders

### `GET /responders`

Returns all available responder locations and service types from the database.

**Response `200 OK`**
```json
{
  "locations": [
    "santa rosa, california",
    "sacramento, california",
    "los angeles, california",
    "san francisco, california",
    "colombo, sri lanka",
    "kandy, sri lanka",
    "mexico city, mexico",
    "puebla, mexico",
    "mumbai, india",
    "delhi, india"
  ]
}
```

---

### `GET /responders/query`

Finds available responder units for a given location and disaster types.

**Query Parameters**

| Param | Type | Required | Description |
|---|---|---|---|
| `location` | `string` | ✅ | City/area name (e.g. `"los angeles"`) |
| `disaster_types` | `string` (comma-separated) | ✅ | e.g. `"fire,medical"` |

**Example:** `GET /responders/query?location=los+angeles&disaster_types=fire,medical`

**Response `200 OK`**
```json
{
  "location": "los angeles",
  "disaster_types": ["fire", "medical"],
  "responders": [
    {
      "id": "FR-201",
      "name": "LA Fire Station 5",
      "units": 4,
      "eta": "10 mins"
    },
    {
      "id": "FR-202",
      "name": "LA Wildfire Response Unit",
      "units": 3,
      "eta": "12 mins"
    },
    {
      "id": "MD-201",
      "name": "LA Paramedics",
      "units": 5,
      "eta": "8 mins"
    }
  ],
  "total_units": 3
}
```

---

### `GET /responders/{responder_id}`

Returns a single responder by ID.

**Response `200 OK`**
```json
{
  "id": "FR-001",
  "name": "Santa Rosa Fire Station 1",
  "units": 3,
  "eta": "5 mins"
}
```

**Error `404`**
```json
{
  "detail": "Responder 'FR-999' not found."
}
```

---

## 6. Web Search (Debug)

### `POST /search/query`

Standalone endpoint to test the `WebSearchAgent` pipeline directly — Gemini query extraction + Tavily search — without triggering a full chat turn.

**Request Body**
```json
{
  "conversation_history": [
    { "role": "user", "content": "There's a fire at 5th and Main" },
    { "role": "assistant", "content": "Can you confirm your exact location?" }
  ],
  "search_all": true
}
```

**Response `200 OK`**
```json
{
  "queries": {
    "primary": "fire 5th Main Street emergency",
    "secondary": [
      "building fire trapped evacuation",
      "fire suppression techniques urban areas"
    ]
  },
  "primary_results": {
    "answer": "Urban building fires require...",
    "results": [
      {
        "title": "NFPA Building Fire Protocols",
        "url": "https://nfpa.org/...",
        "score": 0.89
      }
    ]
  },
  "secondary_results": [
    {
      "query": "building fire trapped evacuation",
      "results": {
        "answer": "When occupants are trapped...",
        "results": []
      }
    }
  ]
}
```

---

## 7. Shared Schemas

### `RetrievedResult`
```typescript
interface RetrievedResult {
  id: string;
  tweet_text: string;
  tweet_id: string;
  image_id: string | null;
  disaster_type: "Wildfire" | "Earthquake" | "Flood" | "Hurricane" | "Other";
  extracted_location: string;
  source_file: string;
  score: number;                          // 0.0 – 1.0 similarity
  image_base64: string | null;            // "data:image/jpeg;base64,..."
  image_caption: string;
  image_damage: "HIGH" | "MEDIUM" | "LOW" | "" | null;
  image_info: "INFORMATIVE" | "NOT INFORMATIVE" | null;
}
```

### `DispatcherState`
```typescript
interface DispatcherState {
  location: string | null;
  disaster_type: string[];
  dispatched_units: Responder[];
  analysis: string;
}
```

### `Responder`
```typescript
interface Responder {
  id: string;
  name: string;
  units: number;
  eta: string;
}
```

### `ConversationTurn`
```typescript
interface ConversationTurn {
  role: "user" | "assistant";
  content: string;
}
```

### `WebSearchResult`
```typescript
interface WebSearchResult {
  enabled: boolean;
  queries?: {
    primary: string;
    secondary: string[];
  };
  primary_results?: {
    answer: string;
    results: { title: string; url: string; score?: number }[];
  };
  secondary_results?: {
    query: string;
    results: {
      answer: string;
      results: { title: string; url: string }[];
    };
  }[];
  error?: string;
}
```

---

## Notes

- **Session management** is server-side. The client generates a UUID (`crypto.randomUUID()`) on first load and persists it in `sessionStorage`.
- All `image_base64` values are full data URIs ready to drop into an `<img src>` tag.
- The `score` field in `RetrievedResult` is the cosine similarity (converted from ChromaDB distance via `1 - distance`), ranging `0.0`–`1.0`.
- Streaming responses are **not** used in v1. All endpoints are request/response.
