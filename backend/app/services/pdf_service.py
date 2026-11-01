class PDFError(Exception):
    """Raised for unreadable or unusable PDFs; message is safe to show to users."""


MIN_TEXT_CHARS = 50


def extract_pages(path: str):
    """Return [(page_number starting at 1, text)] using PyMuPDF."""
    import fitz  # PyMuPDF

    try:
        doc = fitz.open(path)
    except Exception as exc:
        raise PDFError("The file could not be opened. It may be corrupted or not a valid PDF.") from exc
    try:
        if doc.needs_pass:
            raise PDFError("The PDF is password protected.")
        pages = [(i + 1, page.get_text("text")) for i, page in enumerate(doc)]
    finally:
        doc.close()
    if sum(len(t.strip()) for _, t in pages) < MIN_TEXT_CHARS:
        raise PDFError(
            "No extractable text found. This looks like a scanned/image-only PDF. "
            "OCR is not available in the basic version."
        )
    return pages
