# app/retrieval/bm25_retriever.py
# BM25 (Best Match 25) — probabilistic keyword-based retrieval.
#
# WHY BM25?
#   Vector search is great for semantics but can MISS exact terms.
#   Example: "What is Article 370?" — vector search might return
#   general constitutional law chunks, but BM25 will nail the
#   exact phrase "Article 370" every time.
#
#   In production RAG systems, BM25 is almost always used alongside
#   vector search (hybrid retrieval) for this reason.
#
# HOW BM25 WORKS (simplified):
#   For each document chunk, BM25 scores it based on:
#     1. Term Frequency (TF): how often query words appear in the chunk
#     2. Inverse Document Frequency (IDF): rare words score higher
#     3. Document length normalization: short documents aren't penalized
#   The "25" refers to the 25th iteration of the BM formula — it has
#   two tunable parameters: k1 (term saturation) and b (length norm).
#
# TOKENIZATION:
#   BM25 works on token lists, not raw strings.
#   We lowercase and split on whitespace — simple but effective.
#   Production systems use NLTK/spaCy for better tokenization.

from rank_bm25 import BM25Okapi
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class BM25Retriever:
    """
    Wraps rank_bm25's BM25Okapi for document chunk retrieval.
    Must be rebuilt whenever new documents are indexed.
    """

    def __init__(self):
        self.bm25: BM25Okapi | None = None
        self.chunks: list[dict] = []

    def build(self, chunks: list[dict]) -> None:
        """
        Build the BM25 index from a list of chunk dicts.

        Args:
            chunks: List of chunk dicts from chunker.py
        """
        if not chunks:
            raise ValueError("Cannot build BM25 index from empty chunk list.")

        self.chunks = chunks
        tokenized_corpus = [self._tokenize(c["text"]) for c in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

        logger.info(f"BM25 index built with {len(chunks)} documents.")

    def search(self, query: str, top_k: int = None) -> list[dict]:
        """
        Retrieve top-K chunks most relevant to the query by BM25 score.

        Returns:
            List of chunk dicts, each with a "bm25_score" field added.
            Sorted by score descending.
        """
        if self.bm25 is None:
            raise RuntimeError("BM25 index not built. Upload a document first.")

        top_k = top_k or settings.top_k_bm25
        query_tokens = self._tokenize(query)

        # get_scores returns a score for EVERY document in the corpus
        scores = self.bm25.get_scores(query_tokens)

        # Get top-k indices by score (argsort ascending, then flip)
        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] == 0.0:
                # Score of 0 means no query term appeared in this chunk
                continue
            chunk = self.chunks[idx].copy()
            chunk["bm25_score"] = float(scores[idx])
            results.append(chunk)

        logger.info(f"BM25 search returned {len(results)} results for query: '{query[:60]}'")
        return results

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """
        Simple whitespace tokenizer with lowercasing.

        Production upgrade: use NLTK's word_tokenize or spaCy for:
          - Removing stopwords
          - Stemming / lemmatization
          - Handling punctuation
        """
        return text.lower().split()

    @property
    def is_ready(self) -> bool:
        return self.bm25 is not None


# Module-level singleton
bm25_retriever = BM25Retriever()
