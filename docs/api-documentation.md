# API Documentation
Base URL: `http://localhost:8000`. Interactive docs: `/docs`. Errors use `{"detail": "message"}`.

| Method & path | Description | Success | Errors |
|---|---|---|---|
| `GET /api/health` | Status, embedding backend, LLM mode | 200 | |
| `POST /api/documents` (multipart `file`) | Upload PDF; processing continues in background | 202 document | 400 not a PDF, 409 duplicate, 413 too large |
| `GET /api/documents` | List documents | 200 | |
| `GET /api/documents/{id}` | Document details (status, pages, chunks, error, summary) | 200 | 404 |
| `DELETE /api/documents/{id}` | Delete document, chunks and vectors | 200 | 404 |
| `POST /api/documents/{id}/summarize` | Summary, key points, topics (cached on the document) | 200 | 404, 409 not ready |
| `POST /api/conversations` `{document_ids}` | Create conversation tied to documents | 201 | 404 unknown document |
| `GET /api/conversations` | List conversations | 200 | |
| `GET /api/conversations/{id}` | Conversation with messages | 200 | 404 |
| `DELETE /api/conversations/{id}` | Delete conversation | 200 | 404 |
| `POST /api/conversations/{id}/clear` | Delete its messages | 200 | 404 |
| `POST /api/conversations/{id}/ask` `{question, mode}` | `mode`: `auto`, `llm`, `extractive` | 200 | 400 no ready documents, 503 embedding failure |

## Ask response
```json
{ "id": 2, "role": "assistant", "content": "...",
  "mode": "llm | extractive | no_evidence | error",
  "sources": [{ "document_id": 1, "filename": "sample.pdf", "page": 1, "text": "...", "score": 0.32 }] }
```
Document `status`: `processing`, `ready`, `failed`.
