"""RAG pipeline: retrieve -> (LLM answer | extractive answer) -> sources. Also summarisation."""
import json
import re
from collections import Counter

import numpy as np

from app.core.config import settings
from app.database.db import get_conn
from app.services import llm, vector_store
from app.services.embeddings import embed_texts

NO_EVIDENCE = (
    "I could not find enough relevant information in the selected document(s) to answer this question. "
    "Try rephrasing it or selecting a different document."
)
SYSTEM_PROMPT = (
    "You answer questions strictly using the provided document excerpts. "
    "Cite the source like [Doc: <name>, p.<page>]. If the excerpts do not contain the answer, "
    "reply exactly: I could not find this in the document. Do not use outside knowledge."
)
STOPWORDS = set(
    "the a an and or of to in on for with is are was were be been it this that these those as by at from "
    "which who what when where how not but can will has have had also into than then their there its our "
    "we you they he she his her i if so such may more most other some any all one two use used using".split()
)


def _sentences(text: str) -> list[str]:
    text = re.sub(r"(?m)^([^\n.!?]{1,60})$\n", r"\1.\n", text)  # short heading-like lines end a sentence
    parts = re.split(r"(?<=[.!?])\s+|\n{2,}", text.replace("\n", " ").strip())
    return [p.strip() for p in parts if len(p.strip()) >= 30]


def retrieve(question: str, doc_ids: list[int], k: int | None = None) -> list[dict]:
    hits = vector_store.search(doc_ids, embed_texts([question])[0], k or settings.top_k)
    if not hits:
        return []
    with get_conn() as c:
        results = []
        for doc_id, idx, score in hits:
            row = c.execute(
                "SELECT c.page, c.text, d.filename FROM chunks c JOIN documents d ON d.id=c.document_id "
                "WHERE c.document_id=? AND c.idx=?", (doc_id, idx)).fetchone()
            if row:
                results.append({"document_id": doc_id, "filename": row["filename"], "page": row["page"],
                                "text": row["text"], "score": round(score, 4)})
    return results


def _extractive(question: str, passages: list[dict]) -> str:
    """Pick the sentences from retrieved passages most similar to the question. No text is generated."""
    cands = [(s, p) for p in passages for s in _sentences(p["text"])]
    if not cands:
        return passages[0]["text"][:400]
    q = embed_texts([question])[0]
    sims = embed_texts([s for s, _ in cands]) @ q
    order = [i for i in np.argsort(-sims)[:3] if sims[i] >= 0.6 * sims.max()]  # best sentences only
    lines = [f"• {cands[i][0]} (p.{cands[i][1]['page']}, {cands[i][1]['filename']})" for i in order]
    return "Relevant passages from your document(s):\n" + "\n".join(lines)


def answer_question(question: str, doc_ids: list[int], mode: str, history: list[dict]) -> dict:
    passages = retrieve(question, doc_ids)
    if not passages or passages[0]["score"] < settings.min_relevance:
        return {"answer": NO_EVIDENCE, "sources": [], "mode": "no_evidence"}
    sources = [p for p in passages if p["score"] >= settings.min_relevance * 0.8]

    use_llm = mode == "llm" or (mode == "auto" and settings.llm_configured)
    note = ""
    if use_llm:
        context = "\n\n".join(f"[Doc: {p['filename']}, p.{p['page']}]\n{p['text']}" for p in sources)
        recent = "\n".join(f"{m['role']}: {m['content'][:300]}" for m in history[-4:])
        prompt = f"Conversation so far:\n{recent}\n\nExcerpts:\n{context}\n\nQuestion: {question}"
        try:
            return {"answer": llm.generate(SYSTEM_PROMPT, prompt), "sources": sources, "mode": "llm"}
        except llm.LLMError as exc:
            if mode == "llm":
                return {"answer": f"LLM unavailable: {exc}", "sources": sources, "mode": "error"}
            note = f"(LLM unavailable: {exc} Showing extractive result instead.)\n\n"
    return {"answer": note + _extractive(question, sources), "sources": sources, "mode": "extractive"}


def summarize_document(doc_id: int) -> dict:
    with get_conn() as c:
        chunks = [dict(r) for r in c.execute(
            "SELECT idx, page, text FROM chunks WHERE document_id=? ORDER BY idx", (doc_id,))]
    if not chunks:
        raise ValueError("Document has no content.")
    if settings.llm_configured:
        step = max(1, len(chunks) // 12)
        sample = "\n\n".join(f"[p.{c['page']}] {c['text']}" for c in chunks[::step][:12])[:12000]
        try:
            raw = llm.generate(
                "Reply with JSON only: {\"summary\": str, \"key_points\": [str], \"topics\": [str]}.",
                f"Summarise this document.\n\n{sample}")
            data = json.loads(re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip())
            return {"summary": data["summary"], "key_points": data["key_points"][:8],
                    "topics": data["topics"][:8], "mode": "llm"}
        except (llm.LLMError, ValueError, KeyError, TypeError):
            pass  # fall through to extractive summary
    sents = [(s, c["page"]) for c in chunks for s in _sentences(c["text"])]
    if not sents:
        sents = [(c["text"][:300], c["page"]) for c in chunks[:3]]
    vecs = embed_texts([s for s, _ in sents])
    centroid = vecs.mean(axis=0)
    rank = np.argsort(-(vecs @ centroid))
    top = sorted(rank[:8])
    words = Counter(w for s, _ in sents for w in re.findall(r"[a-zA-Z]{4,}", s.lower()) if w not in STOPWORDS)
    return {
        "summary": " ".join(sents[i][0] for i in top[:3]),
        "key_points": [f"{sents[i][0]} (p.{sents[i][1]})" for i in top[:6]],
        "topics": [w for w, _ in words.most_common(8)],
        "mode": "extractive",
    }
