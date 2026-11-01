"""Embedding backends. All return L2-normalised float32 vectors so dot product == cosine."""
import hashlib
import re
import threading

import numpy as np

from app.core.config import settings

HASH_DIM = 768
_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = set("the a an and or of to in on for with is are was were be been it this that these those as by at from "
            "who whom what when where which how why do does did can could will would should has have had not".split())
_lock = threading.Lock()
_st_model = None


class EmbeddingError(Exception):
    pass


def _normalise(m: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(m, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (m / norms).astype(np.float32)


def _hash_embed(texts: list[str]) -> np.ndarray:
    """Dependency-free feature-hashing embedding (unigrams + bigrams). Lexical, not semantic."""
    out = np.zeros((len(texts), HASH_DIM), dtype=np.float32)
    for i, text in enumerate(texts):
        toks = [t for t in _TOKEN.findall(text.lower()) if t not in _STOP]
        feats = toks + [f"{a}_{b}" for a, b in zip(toks, toks[1:])]
        for f in feats:
            h = int(hashlib.md5(f.encode()).hexdigest(), 16)
            sign = 1.0 if (h >> 1) & 1 else -1.0
            out[i, h % HASH_DIM] += sign
        out[i] = np.sign(out[i]) * np.sqrt(np.abs(out[i]))
    return _normalise(out)


def _get_st_model():
    global _st_model
    with _lock:
        if _st_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                _st_model = SentenceTransformer(settings.embedding_model)
            except Exception as exc:
                raise EmbeddingError(
                    f"Could not load embedding model '{settings.embedding_model}': {exc}. "
                    "Check your internet connection for the first download, or set EMBEDDING_BACKEND=hash."
                ) from exc
    return _st_model


def embed_texts(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, HASH_DIM), dtype=np.float32)
    if settings.embedding_backend == "hash":
        return _hash_embed(texts)
    try:
        model = _get_st_model()
        vecs = model.encode(texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
        return np.asarray(vecs, dtype=np.float32)
    except EmbeddingError:
        raise
    except Exception as exc:
        raise EmbeddingError(f"Embedding generation failed: {exc}") from exc
