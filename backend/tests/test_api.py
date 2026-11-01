"""End-to-end API tests (FastAPI TestClient). Run offline: hash embeddings + extractive answers."""
from app.services.pdf_service import extract_pages
from tests.conftest import SAMPLE_PDF


def _upload(client, data, name="sample.pdf"):
    return client.post("/api/documents", files={"file": (name, data, "application/pdf")})


def _ready_doc(client, data):
    r = _upload(client, data)
    assert r.status_code == 202
    doc = client.get(f"/api/documents/{r.json()['id']}").json()
    assert doc["status"] == "ready", doc
    return doc


def test_pdf_text_extraction_preserves_pages():
    pages = extract_pages(str(SAMPLE_PDF))
    assert [p for p, _ in pages] == [1, 2]
    assert "photovoltaic" in pages[0][1] and "Hydropower" in pages[1][1]


def test_health_reports_extractive_mode(client):
    h = client.get("/api/health").json()
    assert h["status"] == "ok" and h["answer_mode"] == "extractive"


def test_upload_processes_document(client, sample_pdf_bytes):
    doc = _ready_doc(client, sample_pdf_bytes)
    assert doc["pages"] == 2 and doc["chunk_count"] >= 2
    assert len(client.get("/api/documents").json()) == 1


def test_duplicate_upload_rejected(client, sample_pdf_bytes):
    _upload(client, sample_pdf_bytes)
    assert _upload(client, sample_pdf_bytes).status_code == 409


def test_invalid_files_rejected(client):
    assert _upload(client, b"hello", "notes.txt").status_code == 400
    assert _upload(client, b"not really a pdf", "fake.pdf").status_code == 400


def test_corrupt_pdf_marked_failed(client):
    r = _upload(client, b"%PDF-1.4 garbage that is not a real pdf")
    doc = client.get(f"/api/documents/{r.json()['id']}").json()
    assert doc["status"] == "failed" and doc["error"]


def test_question_answering_with_page_sources(client, sample_pdf_bytes):
    doc = _ready_doc(client, sample_pdf_bytes)
    conv = client.post("/api/conversations", json={"document_ids": [doc["id"]]}).json()
    r = client.post(f"/api/conversations/{conv['id']}/ask",
                    json={"question": "What efficiency do silicon solar panels reach?"})
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "extractive"
    assert body["sources"] and body["sources"][0]["page"] == 1
    assert "18 and 22" in body["content"]
    assert len(client.get(f"/api/conversations/{conv['id']}").json()["messages"]) == 2


def test_unrelated_question_reports_no_evidence(client, sample_pdf_bytes):
    doc = _ready_doc(client, sample_pdf_bytes)
    conv = client.post("/api/conversations", json={"document_ids": [doc["id"]]}).json()
    r = client.post(f"/api/conversations/{conv['id']}/ask", json={"question": "Who won the football world cup?"})
    assert r.json()["mode"] == "no_evidence" and r.json()["sources"] == []


def test_ask_without_documents_and_unknown_ids(client):
    conv = client.post("/api/conversations", json={}).json()
    assert client.post(f"/api/conversations/{conv['id']}/ask", json={"question": "hi"}).status_code == 400
    assert client.get("/api/documents/999").status_code == 404
    assert client.post("/api/conversations", json={"document_ids": [999]}).status_code == 404


def test_clear_conversation(client, sample_pdf_bytes):
    doc = _ready_doc(client, sample_pdf_bytes)
    conv = client.post("/api/conversations", json={"document_ids": [doc["id"]]}).json()
    client.post(f"/api/conversations/{conv['id']}/ask", json={"question": "What is hydropower?"})
    client.post(f"/api/conversations/{conv['id']}/clear")
    assert client.get(f"/api/conversations/{conv['id']}").json()["messages"] == []


def test_summary_generation(client, sample_pdf_bytes):
    doc = _ready_doc(client, sample_pdf_bytes)
    s = client.post(f"/api/documents/{doc['id']}/summarize").json()
    assert s["mode"] == "extractive" and s["summary"] and s["key_points"] and s["topics"]
    assert client.get(f"/api/documents/{doc['id']}").json()["summary"]["summary"] == s["summary"]


def test_delete_document_removes_vectors_and_chunks(client, sample_pdf_bytes):
    from app.core.config import settings
    doc = _ready_doc(client, sample_pdf_bytes)
    vec = settings.data_dir / "vectors" / f"{doc['id']}.npy"
    assert vec.exists()
    assert client.delete(f"/api/documents/{doc['id']}").status_code == 200
    assert not vec.exists()
    assert client.get(f"/api/documents/{doc['id']}").status_code == 404
    assert client.delete(f"/api/documents/{doc['id']}").status_code == 404
