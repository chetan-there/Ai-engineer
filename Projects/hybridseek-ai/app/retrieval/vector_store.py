# app/retrieval/vector_store.py
# Manages a FAISS index for fast approximate nearest-neighbor search.
#
# WHY FAISS?
#   Facebook AI Similarity Search (FAISS) can search millions of vectors
#   in milliseconds using optimized C++ under the hood.
#   It's the industry standard for local/self-hosted vector search.
#   Alternatives: Chroma (easier API), Pinecone/Weaviate (cloud, managed).
#
# HOW VECTOR SEARCH WORKS:
#   1. Embed all document chunks → store as vectors in FAISS index
#   2. At query time → embed the query
#   3. Find K nearest vectors by cosine similarity (dot product here, since we L2-normalize)
#   4. Return the corresponding text chunks
#
# INDEX PERSISTENCE:
#   We save the FAISS index + chunk metadata to disk so they survive
#   server restarts without re-embedding every time.

import faiss
import numpy as np
import json
import logging
from pathlib import Path
from app.config import settings
from app.retrieval.embedder import embed_texts, embed_query

logger = logging.getLogger(__name__)

# File paths for persistence
FAISS_INDEX_PATH = settings.index_dir / "faiss.index"
CHUNKS_META_PATH = settings.index_dir / "chunks_meta.json"


class VectorStore:
    """
    Wrapper around FAISS for storing and searching document chunk embeddings.
    """

    def __init__(self):
        self.index: faiss.Index | None = None
        self.chunks: list[dict] = []   # parallel list — chunks[i] matches index vector i

    def build(self, chunks: list[dict]) -> None:
        """
        Embed all chunks and build a FAISS index from scratch.
        Call this after uploading a new document.

        Args:
            chunks: List of chunk dicts from chunker.py
        """
        if not chunks:
            raise ValueError("Cannot build index from empty chunk list.")

        texts = [c["text"] for c in chunks]
        logger.info(f"Embedding {len(texts)} chunks for FAISS index...")

        embeddings = embed_texts(texts)  # shape: (N, dim)
        dim = embeddings.shape[1]

        # IndexFlatIP = Inner Product (dot product)
        # Since embeddings are L2-normalized, dot product == cosine similarity
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings.astype(np.float32))
        self.chunks = chunks

        logger.info(f"FAISS index built: {self.index.ntotal} vectors, dim={dim}")
        self._save()

    def search(self, query: str, top_k: int = None) -> list[dict]:
        """
        Search for the most semantically similar chunks to a query.

        Returns:
            List of chunk dicts, each augmented with a "vector_score" field.
            Sorted by score descending (most relevant first).
        """
        if self.index is None:
            raise RuntimeError("Vector store is empty. Upload a document first.")

        top_k = top_k or settings.top_k_vector
        query_vec = embed_query(query).astype(np.float32)  # shape: (1, dim)

        scores, indices = self.index.search(query_vec, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:   # FAISS returns -1 for padding when fewer than top_k results exist
                continue
            chunk = self.chunks[idx].copy()
            chunk["vector_score"] = float(score)
            results.append(chunk)

        logger.info(f"Vector search returned {len(results)} results for query: '{query[:60]}...'")
        return results

    def _save(self) -> None:
        """Persist index and chunk metadata to disk."""
        faiss.write_index(self.index, str(FAISS_INDEX_PATH))
        with open(CHUNKS_META_PATH, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        logger.info(f"FAISS index saved to {FAISS_INDEX_PATH}")

    def load(self) -> bool:
        """
        Load index + metadata from disk.
        Returns True if successful, False if no saved index found.
        """
        if FAISS_INDEX_PATH.exists() and CHUNKS_META_PATH.exists():
            self.index = faiss.read_index(str(FAISS_INDEX_PATH))
            with open(CHUNKS_META_PATH, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)
            logger.info(f"Loaded FAISS index: {self.index.ntotal} vectors")
            return True

        logger.warning("No saved FAISS index found. Upload a document to create one.")
        return False

    @property
    def is_ready(self) -> bool:
        return self.index is not None and self.index.ntotal > 0


# Module-level singleton — shared across all API requests
vector_store = VectorStore()
vector_store.load()   # Try to restore from disk on startup
