"""Per-document vector storage. Vectors live in data/vectors/<doc_id>.npy.

Search only touches the selected documents, so collections never mix.
Uses FAISS (IndexFlatIP) when installed, otherwise falls back to a NumPy dot product.
"""
import numpy as np

from app.core.config import settings

try:
    import faiss  # type: ignore
except ImportError:  # pragma: no cover
    faiss = None


def _path(doc_id: int):
    return settings.data_dir / "vectors" / f"{doc_id}.npy"


def save_vectors(doc_id: int, vectors: np.ndarray) -> None:
    np.save(_path(doc_id), vectors.astype(np.float32))


def delete_vectors(doc_id: int) -> None:
    _path(doc_id).unlink(missing_ok=True)


def search(doc_ids: list[int], query_vec: np.ndarray, k: int):
    """Return [(doc_id, chunk_idx, score)] best-first across the given documents."""
    mats, owners = [], []
    for d in doc_ids:
        p = _path(d)
        if not p.exists():
            continue
        m = np.load(p)
        mats.append(m)
        owners.extend((d, i) for i in range(len(m)))
    if not mats:
        return []
    matrix = np.vstack(mats).astype(np.float32)
    q = query_vec.reshape(1, -1).astype(np.float32)
    k = min(k, len(matrix))
    if faiss is not None:
        index = faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)
        scores, ids = index.search(q, k)
        pairs = list(zip(ids[0].tolist(), scores[0].tolist()))
    else:
        sims = (matrix @ q.T).ravel()
        top = np.argsort(-sims)[:k]
        pairs = [(int(i), float(sims[i])) for i in top]
    return [(owners[i][0], owners[i][1], float(s)) for i, s in pairs if i >= 0]
