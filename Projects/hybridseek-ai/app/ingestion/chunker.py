# app/ingestion/chunker.py
# Splits page-level text into smaller overlapping chunks for retrieval.
#
# WHY CHUNKING?
#   LLMs have context window limits. Also, retrieving a full 20-page PDF
#   as context for a question about one paragraph is wasteful and noisy.
#   Smaller, focused chunks → better retrieval precision.
#
# CHUNK SIZE TRADE-OFFS:
#   Small chunks (100–300 chars) → precise retrieval, may lose context
#   Medium chunks (400–700 chars) → good balance (our default: 500)
#   Large chunks (800–1200 chars) → more context, noisier retrieval
#
# OVERLAP:
#   If a sentence is split across chunk boundary, overlap lets both
#   adjacent chunks share those boundary words → no information loss.

from app.config import settings
import logging

logger = logging.getLogger(__name__)


def chunk_documents(pages: list[dict]) -> list[dict]:
    """
    Given a list of page dicts (from loader.py), produce a flat list
    of chunk dicts with metadata for citation grounding.

    Each chunk dict:
        {
            "text": str,          ← chunk content
            "source": str,        ← filename
            "page": int,          ← which page this came from
            "chunk_id": int,      ← global unique chunk index
        }
    """
    all_chunks = []
    chunk_id = 0

    for page in pages:
        page_chunks = _split_text(
            text=page["text"],
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap,
        )

        for chunk_text in page_chunks:
            all_chunks.append({
                "text": chunk_text,
                "source": page["source"],
                "page": page["page"],
                "chunk_id": chunk_id,
            })
            chunk_id += 1

    logger.info(f"Created {len(all_chunks)} chunks from {len(pages)} pages "
                f"(chunk_size={settings.chunk_size}, overlap={settings.chunk_overlap})")
    return all_chunks


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    Simple character-based sliding window chunker.

    For production you might prefer:
        - Sentence-aware splitting (spaCy, NLTK)
        - Token-aware splitting (tiktoken for OpenAI models)
        - Recursive character splitter (LangChain's RecursiveCharacterTextSplitter)

    We implement manually here so the logic is transparent.
    """
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        # Try to break at a sentence or word boundary for cleaner chunks
        if end < len(text):
            # Look backwards from `end` for a period, newline, or space
            boundary = _find_boundary(text, start, end)
            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move forward by (chunk_size - overlap) to create overlapping window
        start += chunk_size - overlap

    return chunks


def _find_boundary(text: str, start: int, end: int) -> int:
    """
    Look backwards from `end` to find a clean sentence/word break.
    Returns the best break position, or `end` if none found.
    """
    # Prefer sentence boundary (. ! ?)
    for i in range(end, max(start, end - 100), -1):
        if text[i] in ".!?\n":
            return i + 1

    # Fall back to word boundary (space)
    for i in range(end, max(start, end - 50), -1):
        if text[i] == " ":
            return i + 1

    return end
