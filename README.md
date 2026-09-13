# Knowledge Inbox

RAG-powered personal knowledge base — save notes and URLs, ask questions, get cited answers.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    React Frontend                         │
│  TanStack Query · Tailwind 4 · TypeScript                │
│  Inbox view (ingest + list) │ Ask view (query + answer)  │
└────────────────┬─────────────┬───────────────────────────┘
                 │ REST API    │
┌────────────────▼─────────────▼───────────────────────────┐
│                    FastAPI Backend                         │
│                                                           │
│  POST /ingest ──► Validate ──► Store item ──► Background  │
│                                               │           │
│                                    ┌──────────▼────────┐  │
│                                    │  process_item()   │  │
│                                    │  1. Fetch URL     │  │
│                                    │  2. Chunk (sent.) │  │
│                                    │  3. Embed (Cohere)│  │
│                                    │  4. Store chunks  │  │
│                                    │  5. Mark ready    │  │
│                                    └───────────────────┘  │
│                                                           │
│  POST /query ──► Embed question ──► Cosine recall (top20) │
│                                 ──► Cohere rerank (top4)  │
│                                 ──► Groq LLM generation   │
│                                 ──► Return cited answer    │
│                                                           │
│  GET /items ──► SQLite query ──► Return items list        │
│  DELETE /items/{id} ──► Cascade delete item + chunks      │
│                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │   SQLite     │  │ Cohere API   │  │    Groq API      │ │
│  │ items,chunks │  │ embed + rank │  │ LLM generation   │ │
│  └─────────────┘  └──────────────┘  └──────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- [Cohere API key](https://dashboard.cohere.com/api-keys) (free tier works)
- [Groq API key](https://console.groq.com/keys) (free tier works)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
uvicorn app.main:app --reload
```

The server starts at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

The app opens at `http://localhost:5173`.

### Run Tests

```bash
cd backend
python -m pytest tests/ -v
```

## API Reference

### `POST /ingest`

Accepts a note or URL for ingestion. Returns `202 Accepted` immediately — processing happens asynchronously in the background.

**Request:**
```json
{
  "type": "note",
  "content": "Key takeaways from the Q3 strategy meeting..."
}
```
```json
{
  "type": "url",
  "content": "https://stripe.com/docs/api/idempotent-requests"
}
```

**Response (202):**
```json
{
  "id": "itm_a1b2c3d4e5f6",
  "type": "note",
  "status": "processing",
  "created_at": "2026-09-13T15:00:00+00:00"
}
```

**Errors:**
| Status | Code | When |
|--------|------|------|
| 400 | `EMPTY_CONTENT` | Content is empty/whitespace |
| 400 | `INVALID_URL` | URL doesn't parse as valid HTTP(S) |
| 413 | `CONTENT_TOO_LARGE` | Content exceeds 50,000 chars |

---

### `GET /items`

Lists all saved items, ordered by creation time (newest first).

**Query Parameters:**
- `status` (optional): Filter by `processing`, `ready`, or `failed`

**Response (200):**
```json
{
  "items": [
    {
      "id": "itm_a1b2c3d4e5f6",
      "type": "note",
      "title": "Key takeaways from the Q3 strategy meeting...",
      "source_url": null,
      "status": "ready",
      "char_count": 1234,
      "created_at": "2026-09-13T15:00:00+00:00",
      "error_reason": null,
      "preview": "Key takeaways from the Q3 strategy meeting..."
    }
  ]
}
```

---

### `POST /query`

Ask a question over your saved knowledge. Returns a cited answer.

**Request:**
```json
{
  "question": "How does our architecture handle idempotency?",
  "top_k": 4
}
```

**Response (200):**
```json
{
  "answer": "Your architecture implements idempotency keys at the API gateway layer [1], caching mutation responses in Redis for 24 hours...",
  "sources": [
    {
      "ref": 1,
      "item_id": "itm_a1b2c3d4e5f6",
      "item_title": "Stripe API Design Guidelines",
      "snippet": "Every POST request carrying an Idempotency-Key header is verified...",
      "score": 0.94
    }
  ]
}
```

**Errors:**
| Status | Code | When |
|--------|------|------|
| 400 | `EMPTY_QUESTION` | Question is empty/whitespace |
| 422 | `NO_CONTENT` | No items with `ready` status in the knowledge base |
| 502 | `UPSTREAM_UNAVAILABLE` | LLM API call failed |

---

### `DELETE /items/{item_id}`

Delete an item and all its associated chunks.

**Response:** `204 No Content`

**Errors:**
| Status | Code | When |
|--------|------|------|
| 404 | `NOT_FOUND` | Item ID doesn't exist |

---

## Design Decisions & Tradeoffs

### Chunking: Sentence-aware packing (not character splitting)

**Choice:** Greedy sentence-packing into ~300-token chunks with 15% sentence-aligned overlap.

**Rationale:** Character-level splitting breaks sentences mid-word, producing chunks with fractured semantics that embed poorly. Sentence-packing preserves complete thoughts, and sentence-aligned overlap ensures boundary concepts appear in both adjacent chunks.

**What breaks at scale:** The regex-based sentence splitter (`(?<=[.!?])\s+(?=[A-Z0-9])`) fails on abbreviations (Dr., U.S.), numbered lists, and non-English text. Production: use a proper sentence tokenizer (spaCy, NLTK punkt) or format-aware chunking for Markdown/HTML.

### Embeddings: Cohere embed-english-v3.0 (not local model)

**Choice:** Cohere's hosted embedding model with asymmetric `input_type` — `search_document` for chunks, `search_query` for questions.

**Rationale:** Cohere v3 embeddings are trained for asymmetric retrieval where queries and documents have different distributions. This produces significantly better recall than symmetric models (like sentence-transformers) where the same encoder treats both identically. The free tier provides 1,000 calls/minute.

**What breaks at scale:** API latency adds ~200ms per embedding call. For bulk ingestion of thousands of documents, batch embedding with rate limiting is needed. At very large scale, host a fine-tuned model locally.

### Retrieval: Two-stage (cosine recall → Cohere rerank)

**Choice:** Broad cosine similarity recall (top 20) → precise cross-attention reranking (top 4) with a minimum relevance threshold (0.15).

**Rationale:** Cosine similarity over embeddings is fast but imprecise — it captures broad semantic similarity but misses nuanced relevance. Cross-attention reranking (where the model sees query and document together) is far more accurate but too expensive to run over all chunks. The two-stage approach gets the best of both: speed from embeddings, precision from reranking.

**What breaks at scale:** Loading all embeddings for cosine scan is O(n). At >10,000 chunks, switch to an ANN index (HNSW via pgvector, Qdrant, or FAISS). The reranking step also has API latency — consider caching frequent queries.

### Vector Storage: SQLite with BLOB embeddings (not a vector DB)

**Choice:** Store embeddings as serialized `float32` numpy arrays in SQLite BLOB columns. Compute cosine similarity in Python at query time.

**Rationale:** Zero infrastructure dependency. For a single-user app with <10,000 chunks, in-memory cosine computation over deserialized BLOBs takes <50ms. SQLite's `ON DELETE CASCADE` handles cleanup, and the database is a single portable file.

**What breaks at scale:** Full-table scan for similarity search becomes the bottleneck at ~50,000+ chunks. Production: migrate to pgvector (PostgreSQL) or a dedicated vector database (Qdrant, Pinecone). The BLOB→numpy deserialization also adds overhead that native vector indexes avoid.

### LLM: Groq (not OpenAI)

**Choice:** Groq's inference API with `openai/gpt-oss-120b` model.

**Rationale:** Fast inference (usually <1s for 800 tokens), generous free tier, and compatible with the OpenAI client format. The 131K context window is more than sufficient for our 4-chunk context window.

**What breaks at scale:** Rate limits (30 RPM on free tier). No streaming support in the current implementation — add SSE for real-time token display. Production: add retry with exponential backoff, fallback models, and response caching.

### Async Ingestion: Background tasks (not synchronous)

**Choice:** `POST /ingest` returns `202 Accepted` immediately. URL fetching, chunking, embedding, and storage happen in a FastAPI `BackgroundTask`.

**Rationale:** URL fetching + embedding can take 3-10 seconds. Blocking the HTTP response on this creates a poor UX and risks timeout. The frontend polls `/items` to detect `processing → ready` transitions.

**What breaks at scale:** FastAPI `BackgroundTasks` run in the same process. For production workloads with many concurrent ingestions, use a proper task queue (Celery, Dramatiq, or a simple Redis queue) to isolate failures and enable horizontal scaling.
