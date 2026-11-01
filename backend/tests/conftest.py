from pathlib import Path

import pytest

SAMPLE_PDF = Path(__file__).parent / "sample_data" / "sample.pdf"


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    """Every test gets a fresh data dir, the offline hash embedder, and no LLM (no paid/API access needed)."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMBEDDING_BACKEND", "hash")
    monkeypatch.setenv("LLM_PROVIDER", "none")
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.delenv("MIN_RELEVANCE", raising=False)


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_pdf_bytes():
    return SAMPLE_PDF.read_bytes()
