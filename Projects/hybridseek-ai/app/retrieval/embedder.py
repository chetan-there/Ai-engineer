# app/retrieval/embedder.py
# Converts text into dense numerical vectors (embeddings).
#
# WHY EMBEDDINGS?
#   Embeddings capture SEMANTIC MEANING, not just keywords.
#   "What is the capital of France?" and "France's capital city?"
#   → very different words, but nearly identical embedding vectors.
#   This is why vector search beats keyword search for natural language.
#
# MODEL CHOICE:
#   all-MiniLM-L6-v2 (default):
#     - 384-dimensional vectors
#     - Very fast, runs on CPU
#     - Good quality for English
#     - Used widely in production for cost/speed balance
#
#   For production upgrades consider:
#     - BAAI/bge-large-en-v1.5 (better quality)
#     - text-embedding-3-small (OpenAI, paid)
#     - e5-large-v2 (great multilingual)

from sentence_transformers import SentenceTransformer
from app.config import settings
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Module-level singleton — load model ONCE, reuse for all requests
# Loading a model takes ~2 seconds; we don't want that per-request
_model: SentenceTransformer | None = None


def get_embedder() -> SentenceTransformer:
    """Lazy-load the embedding model (singleton pattern)."""
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _model = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded successfully.")
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Convert a list of text strings into a 2D numpy array of embeddings.

    Args:
        texts: List of strings to embed

    Returns:
        numpy array of shape (len(texts), embedding_dim)
        e.g. for all-MiniLM-L6-v2: shape (N, 384)
    """
    if not texts:
        raise ValueError("Cannot embed an empty list of texts.")

    model = get_embedder()

    # show_progress_bar=True is great for CLI — remove for production APIs
    embeddings = model.encode(
        texts,
        show_progress_bar=False,
        batch_size=32,           # process 32 texts at a time
        normalize_embeddings=True,  # L2-normalize → cosine similarity = dot product
    )

    logger.info(f"Embedded {len(texts)} texts → shape {embeddings.shape}")
    return embeddings


def embed_query(query: str) -> np.ndarray:
    """
    Embed a single query string.
    Returns shape (1, embedding_dim) for FAISS compatibility.
    """
    return embed_texts([query])
