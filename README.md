# AI-Based PDF Question Answering and Document Intelligence System

Upload PDFs, ask questions in natural language, and get answers grounded in the document with **page references and source excerpts**. Built with Retrieval-Augmented Generation (RAG), semantic search and an optional free-tier LLM. It works fully **without any API key** using local extractive answering.

Live Demo: 

> Individual B.Tech CSE (7th semester) minor project, GGSIPU.

## 1. Project overview
A web app (React + FastAPI) that extracts text from PDFs with PyMuPDF, splits it into page-aware chunks, embeds them with Sentence Transformers, stores vectors locally (FAISS), and answers questions from the most relevant chunks.

## 2. Problem statement
Reading long PDFs (papers, manuals, notes) to find one fact is slow, and general chatbots may answer from memory instead of from the document. This system answers only from the uploaded documents, shows where the answer came from, and says so when the evidence is missing.

## 3. Objectives
- Upload and process multiple PDFs independently.
- Retrieve relevant passages with semantic search.
- Answer with citations (document + page + excerpt).
- Work offline/free (extractive mode) and optionally use a free-tier LLM.
- Provide summaries, chat history and document management.

## 4. Key features
Drag-and-drop upload with validation (type, magic bytes, size, duplicates) · background processing with status · scanned-PDF detection (OCR not included) · semantic retrieval · LLM mode + extractive fallback (clearly labelled) · "not enough evidence" handling · per-conversation document selection (collections never mix) · summaries (key points + topics) · chat history, clear/delete · dark mode · responsive UI.

## 5. Technology stack
| Layer | Tools |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS 3, React Router, Axios, Lucide React |
| Backend | Python, FastAPI, Uvicorn, Pydantic, python-multipart |
| PDF | PyMuPDF |
| AI/RAG | sentence-transformers (`all-MiniLM-L6-v2`), FAISS-CPU (NumPy fallback), httpx for LLM APIs |
| Storage | SQLite (metadata, chunks, chats) + `.npy` vector files |

## 6. System architecture
```
React (Vite) ──HTTP/JSON──> FastAPI
                              ├─ PDF extraction (PyMuPDF)
                              ├─ Chunking (page-aware)
                              ├─ Embeddings (Sentence Transformers)
                              ├─ Vector search (FAISS / NumPy)
                              ├─ RAG pipeline ── LLM (optional) | Extractive
                              └─ SQLite + data/vectors/*.npy
```
Details: `docs/architecture.md`.

## 7. RAG workflow
1. **Ingest:** PDF → pages → chunks (~900 chars, 150 overlap, page number kept) → embeddings → saved.
2. **Retrieve:** question → embedding → top-K similar chunks from the *selected* documents only.
3. **Gate:** if the best similarity is below `MIN_RELEVANCE`, reply "not enough evidence".
4. **Generate:** LLM mode prompts the model with the chunks and asks it to answer only from them; extractive mode returns the most question-similar sentences.
5. **Cite:** the response includes document, page, similarity score and excerpt.

## 8. Folder structure
```
pdf-intelligence-system/
├── frontend/   (src/components, pages, services, hooks, context; vercel.json)
├── backend/    (app/api, core, services, models, database; tests/; requirements.txt)
├── docs/       (architecture.md, api-documentation.md, project-overview.md)
├── README.md  DEPLOYMENT.md  LICENSE  .gitignore
```

## 9. Prerequisites (Windows 10/11 + VS Code)
Python 3.11 (3.12 also expected to work), Node.js LTS, Git (optional), VS Code, ~2 GB free disk (PyTorch + model), internet for first install.

## 10. Install Python (Windows)
1. Download Python 3.11 from https://www.python.org/downloads/windows/.
2. In the installer tick **"Add python.exe to PATH"**, then *Install Now*.
3. Open a **new** PowerShell and check:
```powershell
python --version
pip --version
```

## 11. Install Node.js (Windows)
1. Download the **LTS** installer from https://nodejs.org and accept the defaults.
2. Open a new PowerShell:
```powershell
node --version
npm --version
```

## 12. Backend setup
```powershell
cd pdf-intelligence-system\backend
python -m venv .venv
```
If activation is blocked, run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
(The first install downloads PyTorch; this can take several minutes.)

## 13. Frontend setup
```powershell
cd ..\frontend
npm install
```

## 14. Environment variables
```powershell
cd ..\backend
Copy-Item .env.example .env
cd ..\frontend
Copy-Item .env.example .env
```
| Variable | Where | Meaning |
|---|---|---|
| `CORS_ORIGINS` | backend | Comma-separated allowed frontend origins |
| `DATA_DIR` | backend | Where SQLite/vectors are stored (default `./data`) |
| `MAX_UPLOAD_MB` | backend | Upload size limit (default 20) |
| `EMBEDDING_BACKEND` | backend | `sentence-transformers` (default) or `hash` (offline, lexical only) |
| `EMBEDDING_MODEL` | backend | Default `sentence-transformers/all-MiniLM-L6-v2` |
| `LLM_PROVIDER` | backend | `none`, `gemini`, or `openai_compatible` |
| `LLM_API_KEY` / `LLM_MODEL` / `LLM_BASE_URL` | backend | Provider settings |
| `TOP_K`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `MIN_RELEVANCE` | backend | Retrieval tuning |
| `VITE_API_URL` | frontend | Backend URL (default `http://localhost:8000`) |

Never commit `.env` (it is in `.gitignore`). The API key lives only in the backend.

## 15. Run the backend
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```
Open http://localhost:8000/docs for interactive API docs. The first upload downloads the embedding model (~90 MB) and caches it.

## 16. Run the frontend
In a second terminal:
```powershell
cd frontend
npm run dev
```
Open http://localhost:5173.

## 17. Configure the free LLM API (optional)
**Google Gemini (Google AI Studio):** create a key at https://aistudio.google.com/app/apikey, then in `backend\.env`:
```
LLM_PROVIDER=gemini
LLM_API_KEY=your_key_here
LLM_MODEL=gemini-2.5-flash
```
**Groq / OpenRouter / other OpenAI-compatible APIs:**
```
LLM_PROVIDER=openai_compatible
LLM_API_KEY=your_key_here
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=<model name from the provider's console>
```
Restart the backend. The sidebar shows "Answer mode: llm".

Important free-tier notes (checked October 2026, may change):
- Free-tier availability, models and limits change often. Google no longer publishes per-model free limits in its docs; check your limits in AI Studio.
- Free-tier requests to some providers may be used to improve their products. **Do not upload confidential documents** when using a free API.
- Quota/rate-limit errors are caught: in *Auto* mode the app falls back to extractive answers and tells you why.

## 18. Local fallback (extractive) mode
Leave `LLM_PROVIDER=none` (default). Answers are the sentences from your document most similar to the question, labelled "Extractive (no LLM)". Nothing is generated or paraphrased. In chat you can also force *Extractive only* or *LLM only*.

## 19. API endpoints
See `docs/api-documentation.md`. Summary: `GET /api/health`, `POST/GET /api/documents`, `GET/DELETE /api/documents/{id}`, `POST /api/documents/{id}/summarize`, `POST/GET /api/conversations`, `GET/DELETE /api/conversations/{id}`, `POST /api/conversations/{id}/clear`, `POST /api/conversations/{id}/ask`.

## 20. Running the tests
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest
```
Tests use the offline `hash` embedder and no LLM, so no network, model download or API key is needed. They cover upload, text extraction, chunking, embeddings, retrieval, Q&A, invalid files, summary and deletion. A sample PDF is in `backend/tests/sample_data/sample.pdf`.

## 21. Troubleshooting
| Problem | Fix |
|---|---|
| `python` not recognised | Reinstall Python with "Add to PATH"; open a new terminal |
| `Activate.ps1 cannot be loaded` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `faiss-cpu` fails to install | Use Python 3.11; or remove it from `requirements.txt` (NumPy fallback is automatic) |
| Red banner "Cannot reach the backend" | Start uvicorn; check `VITE_API_URL` and `CORS_ORIGINS` |
| CORS error in browser console | Add your frontend origin to `CORS_ORIGINS`, restart backend |
| Document stuck "Failed: No extractable text" | Scanned PDF; OCR is not included |
| Embedding model download fails | Check internet/proxy, or set `EMBEDDING_BACKEND=hash` |
| 409 on upload | Same file already uploaded |
| LLM quota/key errors | Check key, model name and limits; use extractive mode |
| Port in use | `uvicorn app.main:app --port 8001` and update `VITE_API_URL` |

## 22. Deployment
See `DEPLOYMENT.md`. Read the storage and memory warnings there before deploying on free tiers.

## 23. Limitations
- No OCR (scanned PDFs rejected). Tables/figures are not understood.
- Extractive mode quotes text; it cannot synthesise across passages.
- Retrieval quality depends on the small embedding model; no re-ranking.
- Single-user, no authentication.
- Free hosting has ephemeral storage and low RAM (see DEPLOYMENT.md).
- Answers from an LLM can still contain mistakes; check the cited pages.

## 24. Future enhancements
OCR (Tesseract), authentication, streaming answers, hybrid BM25 + vector search, re-ranking, persistent cloud storage, evaluation set for retrieval accuracy.

## 25. Status of verification
Verified in the development sandbox: Python syntax of all backend/test files; chunking, hash embeddings, vector retrieval, extractive answering, no-evidence handling and summaries (run directly, NumPy fallback). **Not run in the sandbox (no internet to install packages):** the FastAPI endpoints/pytest suite, PyMuPDF extraction, sentence-transformers, FAISS, LLM calls, and the `npm install`/`npm run build` for the frontend. Run `pytest` and `npm run build` on your machine and fix any issue before submission.

## 26. Academic project description
See `docs/project-overview.md` for a structured abstract, methodology, feasibility and report outline for the minor project report.

## 27. License
MIT (see `LICENSE`; put your name in it).
