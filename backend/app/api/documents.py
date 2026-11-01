import hashlib
import json
import sqlite3

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.core.config import settings
from app.database.db import get_conn, now, row_to_dict
from app.services import vector_store
from app.services.chunking import chunk_pages
from app.services.embeddings import EmbeddingError, embed_texts
from app.services.pdf_service import PDFError, extract_pages
from app.services.rag import summarize_document

router = APIRouter(prefix="/api/documents", tags=["documents"])


def process_document(doc_id: int, path: str) -> None:
    """Extract -> chunk -> embed -> store. Runs in the background; records status/error."""
    try:
        pages = extract_pages(path)
        chunks = chunk_pages(pages, settings.chunk_size, settings.chunk_overlap)
        if not chunks:
            raise PDFError("The PDF contains no usable text.")
        vectors = embed_texts([c["text"] for c in chunks])
        vector_store.save_vectors(doc_id, vectors)
        with get_conn() as c:
            c.executemany("INSERT INTO chunks(document_id, idx, page, text) VALUES (?,?,?,?)",
                          [(doc_id, ch["idx"], ch["page"], ch["text"]) for ch in chunks])
            c.execute("UPDATE documents SET status='ready', pages=?, chunk_count=? WHERE id=?",
                      (len(pages), len(chunks), doc_id))
    except (PDFError, EmbeddingError) as exc:
        _fail(doc_id, str(exc))
    except Exception as exc:  # never leave a document stuck in 'processing'
        _fail(doc_id, f"Unexpected processing error: {exc}")
    finally:
        try:
            import os
            os.remove(path)
        except OSError:
            pass


def _fail(doc_id: int, message: str) -> None:
    vector_store.delete_vectors(doc_id)
    with get_conn() as c:
        c.execute("UPDATE documents SET status='failed', error=? WHERE id=?", (message, doc_id))


@router.post("", status_code=202)
async def upload_document(background: BackgroundTasks, file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only .pdf files are accepted.")
    limit = settings.max_upload_mb * 1024 * 1024
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, f"File is larger than {settings.max_upload_mb} MB.")
    if not data.startswith(b"%PDF"):
        raise HTTPException(400, "The file is not a valid PDF.")
    digest = hashlib.sha256(data).hexdigest()
    try:
        with get_conn() as c:
            cur = c.execute(
                "INSERT INTO documents(filename, sha256, size_bytes, status, created_at) VALUES (?,?,?,?,?)",
                (file.filename, digest, len(data), "processing", now()))
            doc_id = cur.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(409, "This document has already been uploaded.")
    path = settings.data_dir / "uploads" / f"{doc_id}.pdf"
    path.write_bytes(data)
    background.add_task(process_document, doc_id, str(path))
    return _get(doc_id)


def _get(doc_id: int) -> dict:
    with get_conn() as c:
        row = c.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Document not found.")
    return row_to_dict(row)


@router.get("")
def list_documents():
    with get_conn() as c:
        rows = c.execute("SELECT * FROM documents ORDER BY id DESC").fetchall()
    return [row_to_dict(r) for r in rows]


@router.get("/{doc_id}")
def get_document(doc_id: int):
    return _get(doc_id)


@router.delete("/{doc_id}")
def delete_document(doc_id: int):
    _get(doc_id)
    vector_store.delete_vectors(doc_id)
    with get_conn() as c:
        c.execute("DELETE FROM documents WHERE id=?", (doc_id,))  # chunks cascade
    return {"deleted": doc_id}


@router.post("/{doc_id}/summarize")
def summarize(doc_id: int):
    doc = _get(doc_id)
    if doc["status"] != "ready":
        raise HTTPException(409, "Document is not ready yet.")
    try:
        result = summarize_document(doc_id)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    with get_conn() as c:
        c.execute("UPDATE documents SET summary=? WHERE id=?", (json.dumps(result), doc_id))
    return result
