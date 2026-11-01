"""Unit tests for chunking, embeddings and vector retrieval (no fixtures needed besides conftest env)."""
import numpy as np
import pytest

from app.services.chunking import chunk_pages
from app.services.embeddings import embed_texts
from app.services import vector_store


def test_chunking_keeps_page_numbers_and_limits_size():
    pages = [(1, "Alpha sentence. " * 200), (2, "Short page text.")]
    chunks = chunk_pages(pages, size=300, overlap=50)
    assert len(chunks) > 2
    assert all(len(c["text"]) <= 300 for c in chunks)
    assert chunks[-1]["page"] == 2 and chunks[-1]["text"] == "Short page text."
    assert [c["idx"] for c in chunks] == list(range(len(chunks)))


def test_chunking_skips_empty_pages_and_validates_overlap():
    assert chunk_pages([(1, "   \n\n  ")]) == []
    with pytest.raises(ValueError):
        chunk_pages([(1, "x")], size=100, overlap=100)


def test_embeddings_are_normalised_and_deterministic():
    v = embed_texts(["solar panels", "wind turbines"])
    assert v.shape[0] == 2
    assert np.allclose(np.linalg.norm(v, axis=1), 1.0, atol=1e-5)
    assert np.allclose(v, embed_texts(["solar panels", "wind turbines"]))


def test_vector_retrieval_returns_most_similar_chunk():
    texts = ["solar panels convert sunlight into electricity",
             "wind turbines use moving air",
             "hydropower dams spin turbines with water"]
    vector_store.save_vectors(1, embed_texts(texts))
    hits = vector_store.search([1], embed_texts(["how do solar panels make electricity"])[0], k=2)
    assert hits[0][0] == 1 and hits[0][1] == 0
    assert hits[0][2] >= hits[1][2]


def test_retrieval_only_searches_selected_documents():
    vector_store.save_vectors(1, embed_texts(["solar energy"]))
    vector_store.save_vectors(2, embed_texts(["solar energy"]))
    hits = vector_store.search([2], embed_texts(["solar energy"])[0], k=5)
    assert {h[0] for h in hits} == {2}
    vector_store.delete_vectors(2)
    assert vector_store.search([2], embed_texts(["solar"])[0], k=5) == []
