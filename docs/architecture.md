# Architecture

## Components
| Module | File | Responsibility |
|---|---|---|
| API | `backend/app/api/documents.py`, `chat.py` | HTTP endpoints, validation, background processing |
| PDF | `services/pdf_service.py` | PyMuPDF extraction, scanned/encrypted detection |
| Chunking | `services/chunking.py` | Page-aware overlapping chunks |
| Embeddings | `services/embeddings.py` | Sentence Transformers (default) or offline hash embedder |
| Vector store | `services/vector_store.py` | Per-document `.npy` vectors, FAISS IndexFlatIP search |
| RAG | `services/rag.py` | Retrieval, relevance gate, LLM/extractive answers, summaries |
| LLM | `services/llm.py` | Gemini and OpenAI-compatible providers with error mapping |
| Database | `database/db.py` | SQLite schema and helpers |
| Frontend | `frontend/src` | Dashboard, Documents, Chat, summary modal |

## Data model (SQLite)
- `documents(id, filename, sha256 UNIQUE, size_bytes, pages, chunk_count, status, error, summary, created_at)`
- `chunks(id, document_id → documents ON DELETE CASCADE, idx, page, text)`
- `conversations(id, title, document_ids JSON, created_at)`
- `messages(id, conversation_id, role, content, sources JSON, mode, created_at)`
- Vectors: `data/vectors/<document_id>.npy` (row i = chunk idx i).

## Upload flow
`POST /api/documents` validates extension, `%PDF` header, size, SHA-256 duplicate → inserts row (`processing`) → background task: extract → chunk → embed → save vectors + chunks → `ready` (or `failed` with a user-readable error). The frontend polls every 2 s while any document is processing.

## Question flow
`POST /api/conversations/{id}/ask` → keep only the conversation's *ready* documents → embed question → search only those documents' vectors → if best score < `MIN_RELEVANCE` return "no evidence" → otherwise LLM answer (if configured and mode allows) or extractive answer → store messages with sources.

## Design decisions
- SQLite + `.npy` instead of a vector DB: zero infrastructure, adequate for thousands of chunks (exact search).
- Exact search (IndexFlatIP) on normalised vectors = cosine similarity.
- Settings are read from the environment at access time so tests can reconfigure them.
- Extractive answers are labelled and never presented as generated text.
