"""Page-aware text chunking. Each chunk keeps the page number it came from."""
import re


def _split_page(text: str, size: int, overlap: int) -> list[str]:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            window_start = start + int(size * 0.75)
            cut = max(text.rfind(". ", window_start, end), text.rfind("\n", window_start, end))
            if cut != -1:
                end = cut + 1
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def chunk_pages(pages, size: int = 900, overlap: int = 150) -> list[dict]:
    """pages: [(page_number, text)] -> [{idx, page, text}]"""
    if overlap >= size:
        raise ValueError("overlap must be smaller than chunk size")
    out: list[dict] = []
    for page_no, text in pages:
        for piece in _split_page(text, size, overlap):
            out.append({"idx": len(out), "page": page_no, "text": piece})
    return out
