# app/ingestion/loader.py
# Responsible for reading raw documents (PDF or TXT) from disk.
# Returns a list of plain text strings, one per page/file.

from pathlib import Path
from pypdf import PdfReader
import logging

logger = logging.getLogger(__name__)


def load_document(file_path: str | Path) -> list[dict]:
    """
    Load a PDF or TXT document and return a list of page dicts.

    Each dict contains:
        {
            "text": str,        ← raw text content
            "source": str,      ← filename
            "page": int         ← page number (0-indexed for TXT)
        }

    Industry note:
        In production you might also handle .docx, HTML, markdown, etc.
        LangChain's document loaders abstract many of these — we implement
        PDF/TXT manually so you understand what's happening under the hood.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return _load_pdf(file_path)
    elif suffix == ".txt":
        return _load_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Use PDF or TXT.")


def _load_pdf(file_path: Path) -> list[dict]:
    """Extract text from each page of a PDF."""
    reader = PdfReader(str(file_path))
    pages = []

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()

        if not text:
            logger.warning(f"Page {page_num} of {file_path.name} has no extractable text. "
                           "It may be a scanned image — consider adding OCR (pytesseract).")
            continue

        pages.append({
            "text": text,
            "source": file_path.name,
            "page": page_num,
        })

    logger.info(f"Loaded {len(pages)} pages from {file_path.name}")
    return pages


def _load_txt(file_path: Path) -> list[dict]:
    """Load a plain text file as a single 'page'."""
    text = file_path.read_text(encoding="utf-8", errors="ignore").strip()

    if not text:
        raise ValueError(f"TXT file is empty: {file_path.name}")

    logger.info(f"Loaded TXT file: {file_path.name} ({len(text)} characters)")
    return [{"text": text, "source": file_path.name, "page": 0}]
