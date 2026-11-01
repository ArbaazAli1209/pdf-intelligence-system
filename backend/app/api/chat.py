import json

from fastapi import APIRouter, HTTPException

from app.database.db import get_conn, now, row_to_dict
from app.models.schemas import AskRequest, ConversationCreate
from app.services.embeddings import EmbeddingError
from app.services.rag import answer_question

router = APIRouter(prefix="/api/conversations", tags=["chat"])


def _conv(conv_id: int) -> dict:
    with get_conn() as c:
        row = c.execute("SELECT * FROM conversations WHERE id=?", (conv_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Conversation not found.")
    return row_to_dict(row)


def _messages(conv_id: int) -> list[dict]:
    with get_conn() as c:
        rows = c.execute("SELECT * FROM messages WHERE conversation_id=? ORDER BY id", (conv_id,)).fetchall()
    return [row_to_dict(r) for r in rows]


@router.post("", status_code=201)
def create_conversation(body: ConversationCreate):
    with get_conn() as c:
        if body.document_ids:
            q = ",".join("?" * len(body.document_ids))
            found = c.execute(f"SELECT COUNT(*) n FROM documents WHERE id IN ({q})", body.document_ids).fetchone()["n"]
            if found != len(set(body.document_ids)):
                raise HTTPException(404, "One or more selected documents do not exist.")
        cur = c.execute("INSERT INTO conversations(title, document_ids, created_at) VALUES (?,?,?)",
                        (body.title or "New conversation", json.dumps(body.document_ids), now()))
        conv_id = cur.lastrowid
    return _conv(conv_id)


@router.get("")
def list_conversations():
    with get_conn() as c:
        rows = c.execute("SELECT * FROM conversations ORDER BY id DESC").fetchall()
    return [row_to_dict(r) for r in rows]


@router.get("/{conv_id}")
def get_conversation(conv_id: int):
    return {**_conv(conv_id), "messages": _messages(conv_id)}


@router.delete("/{conv_id}")
def delete_conversation(conv_id: int):
    _conv(conv_id)
    with get_conn() as c:
        c.execute("DELETE FROM conversations WHERE id=?", (conv_id,))
    return {"deleted": conv_id}


@router.post("/{conv_id}/clear")
def clear_conversation(conv_id: int):
    _conv(conv_id)
    with get_conn() as c:
        c.execute("DELETE FROM messages WHERE conversation_id=?", (conv_id,))
    return {"cleared": conv_id}


@router.post("/{conv_id}/ask")
def ask(conv_id: int, body: AskRequest):
    conv = _conv(conv_id)
    with get_conn() as c:
        ready = [r["id"] for r in c.execute("SELECT id FROM documents WHERE status='ready'")]
    doc_ids = [d for d in conv["document_ids"] if d in ready]
    if not doc_ids:
        raise HTTPException(400, "This conversation has no ready documents. Select or upload a processed PDF.")
    history = _messages(conv_id)
    try:
        result = answer_question(body.question, doc_ids, body.mode, history)
    except EmbeddingError as exc:
        raise HTTPException(503, str(exc))
    with get_conn() as c:
        if not history and conv["title"] == "New conversation":
            c.execute("UPDATE conversations SET title=? WHERE id=?", (body.question[:60], conv_id))
        c.execute("INSERT INTO messages(conversation_id, role, content, created_at) VALUES (?,?,?,?)",
                  (conv_id, "user", body.question, now()))
        cur = c.execute(
            "INSERT INTO messages(conversation_id, role, content, sources, mode, created_at) VALUES (?,?,?,?,?,?)",
            (conv_id, "assistant", result["answer"], json.dumps(result["sources"]), result["mode"], now()))
        msg_id = cur.lastrowid
    return {"id": msg_id, "role": "assistant", "content": result["answer"],
            "sources": result["sources"], "mode": result["mode"]}
