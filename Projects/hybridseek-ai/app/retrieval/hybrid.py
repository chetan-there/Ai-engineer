# app/retrieval/hybrid.py
# Hybrid retrieval: combines BM25 + Vector search results with weighted scoring.
# Then applies re-ranking to surface the best chunks.
#
# WHY HYBRID RETRIEVAL?
#   - BM25 excels at: exact terms, product names, IDs, codes, legal citations
#   - Vector excels at: paraphrasing, synonyms, conceptual questions
#   - Hybrid beats either alone → consistently used in production RAG
#     (e.g. Elasticsearch's hybrid search, Azure AI Search, Pinecone hybrid)
#
# COMBINATION STRATEGY — Weighted Score Fusion:
#   Both BM25 and vector scores are on different scales.
#   We normalize each to [0, 1] then combine:
#       hybrid_score = (bm25_weight * bm25_norm) + (vector_weight * vector_norm)
#
# RE-RANKING:
#   We implement a lightweight score-based re-ranker here.
#   In production you'd use a cross-encoder model
#   (e.g. cross-encoder/ms-marco-MiniLM-L-6-v2) which re-scores
#   (query, chunk) pairs for much higher precision — at the cost of latency.

from app.retrieval.bm25_retriever import bm25_retriever
from app.retrieval.vector_store import vector_store
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def hybrid_search(query: str) -> list[dict]:
    """
    Run BM25 + Vector search in parallel, fuse scores, re-rank.

    Returns:
        Top-K chunk dicts after hybrid scoring and re-ranking.
        Each chunk has: text, source, page, chunk_id,
                        bm25_score, vector_score, hybrid_score
    """
    # ── Step 1: Run both retrievers ───────────────────────────────────────
    bm25_results = bm25_retriever.search(query, top_k=settings.top_k_bm25)
    vector_results = vector_store.search(query, top_k=settings.top_k_vector)

    # ── Step 2: Merge into a unified pool keyed by chunk_id ──────────────
    chunk_pool: dict[int, dict] = {}

    for chunk in bm25_results:
        cid = chunk["chunk_id"]
        chunk_pool[cid] = chunk.copy()
        chunk_pool[cid].setdefault("bm25_score", 0.0)
        chunk_pool[cid].setdefault("vector_score", 0.0)

    for chunk in vector_results:
        cid = chunk["chunk_id"]
        if cid in chunk_pool:
            # Chunk appeared in both — add the vector score
            chunk_pool[cid]["vector_score"] = chunk.get("vector_score", 0.0)
        else:
            # Chunk only in vector results
            chunk_pool[cid] = chunk.copy()
            chunk_pool[cid].setdefault("bm25_score", 0.0)
            chunk_pool[cid].setdefault("vector_score", chunk.get("vector_score", 0.0))

    # ── Step 3: Normalize scores to [0, 1] ───────────────────────────────
    all_bm25 = [c["bm25_score"] for c in chunk_pool.values()]
    all_vec = [c["vector_score"] for c in chunk_pool.values()]

    max_bm25 = max(all_bm25) if max(all_bm25) > 0 else 1.0
    max_vec = max(all_vec) if max(all_vec) > 0 else 1.0

    # ── Step 4: Compute hybrid score ──────────────────────────────────────
    for chunk in chunk_pool.values():
        bm25_norm = chunk["bm25_score"] / max_bm25
        vec_norm = chunk["vector_score"] / max_vec

        chunk["hybrid_score"] = (
            settings.bm25_weight * bm25_norm +
            settings.vector_weight * vec_norm
        )

    # ── Step 5: Re-rank by hybrid score and return top-K ─────────────────
    ranked = sorted(
        chunk_pool.values(),
        key=lambda c: c["hybrid_score"],
        reverse=True
    )[:settings.top_k_final]

    logger.info(
        f"Hybrid search: {len(bm25_results)} BM25 + {len(vector_results)} vector "
        f"→ {len(ranked)} final chunks after re-ranking"
    )

    return ranked


def format_context(chunks: list[dict]) -> tuple[str, list[dict]]:
    """
    Convert retrieved chunks into a formatted context string for the LLM,
    plus a clean list of citation metadata for the API response.

    Returns:
        context_str: String to inject into the LLM prompt
        citations: List of {source, page, chunk_id, score} dicts
    """
    context_parts = []
    citations = []

    for i, chunk in enumerate(chunks, start=1):
        context_parts.append(
            f"[Source {i}: {chunk['source']}, Page {chunk['page'] + 1}]\n"
            f"{chunk['text']}"
        )
        citations.append({
            "citation_number": i,
            "source": chunk["source"],
            "page": chunk["page"] + 1,
            "chunk_id": chunk["chunk_id"],
            "hybrid_score": round(chunk.get("hybrid_score", 0.0), 4),
            "text_preview": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
        })

    context_str = "\n\n---\n\n".join(context_parts)
    return context_str, citations
