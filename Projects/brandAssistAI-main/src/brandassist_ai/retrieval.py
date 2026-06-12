from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Protocol

from .models import KnowledgeDoc


TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


class Retriever(Protocol):
    def search(
        self,
        query: str,
        product_id: str | None = None,
        top_k: int = 3,
    ) -> list[KnowledgeDoc]:
        ...


class LexicalRetriever:
    """Small deterministic retriever used for local POC and tests."""

    def __init__(self, docs: list[KnowledgeDoc]) -> None:
        self.docs = docs

    def search(
        self,
        query: str,
        product_id: str | None = None,
        top_k: int = 3,
    ) -> list[KnowledgeDoc]:
        query_terms = Counter(tokenize(query))
        scored: list[tuple[int, KnowledgeDoc]] = []
        for doc in self.docs:
            if product_id and doc.product_id not in {product_id, None}:
                continue
            haystack = Counter(tokenize(f"{doc.title} {doc.kind} {doc.text}"))
            score = sum(min(count, haystack[token]) for token, count in query_terms.items())
            if product_id and doc.product_id == product_id:
                score += 2
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda item: (-item[0], item[1].id))
        return [doc for _, doc in scored[:top_k]]


class HybridRetriever:
    """
    Retrieval mode that combines lexical scoring with policy/category boosts.

    This keeps the POC deterministic while providing a "hybrid" behavior:
    lexical relevance + domain-aware reranking. It is intentionally local and
    fast for testability; can be replaced by lexical + vector RRF in production.
    """

    def __init__(self, docs: list[KnowledgeDoc]) -> None:
        self.docs = docs
        self.lexical = LexicalRetriever(docs)

    def search(
        self,
        query: str,
        product_id: str | None = None,
        top_k: int = 3,
    ) -> list[KnowledgeDoc]:
        lexical_candidates = self.lexical.search(query, product_id=product_id, top_k=max(top_k * 3, 6))
        if not lexical_candidates:
            return []

        query_terms = set(tokenize(query))
        scored: list[tuple[float, KnowledgeDoc]] = []
        for rank, doc in enumerate(lexical_candidates, start=1):
            score = 1.0 / rank  # reciprocal rank backbone
            title_terms = set(tokenize(doc.title))

            # semantic-ish boosts tailored to support-policy retrieval.
            if {"warranty", "policy"} & query_terms and doc.kind == "policy":
                score += 0.75
            if {"setup", "install"} & query_terms and doc.kind == "manual":
                score += 0.35
            if {"fix", "troubleshoot", "failed", "seal"} & query_terms and doc.kind == "troubleshooting":
                score += 0.35
            if query_terms & title_terms:
                score += 0.15
            if product_id and doc.product_id == product_id:
                score += 0.2

            scored.append((score, doc))

        scored.sort(key=lambda item: (-item[0], item[1].id))
        unique_docs: list[KnowledgeDoc] = []
        seen: set[str] = set()
        for _, doc in scored:
            if doc.id in seen:
                continue
            seen.add(doc.id)
            unique_docs.append(doc)
            if len(unique_docs) == top_k:
                break
        return unique_docs


class ChromaRetriever:
    """Vector retriever backed by a local Chroma persistent collection."""

    def __init__(self, docs: list[KnowledgeDoc], persist_directory: str | None = None, collection_name: str = "brandassist_kb") -> None:
        self.docs = docs
        self.docs_by_id = {doc.id: doc for doc in docs}
        self.fallback = HybridRetriever(docs)
        self.persist_directory = persist_directory or str(Path(__file__).resolve().parents[2] / "data" / "chroma")
        self.collection_name = collection_name

    def search(
        self,
        query: str,
        product_id: str | None = None,
        top_k: int = 3,
    ) -> list[KnowledgeDoc]:
        try:
            import chromadb

            client = chromadb.PersistentClient(path=self.persist_directory)
            collection = client.get_collection(self.collection_name)
            where = {"product_id": product_id} if product_id else None
            result = collection.query(query_texts=[query], n_results=top_k, where=where)
            metadatas = result.get("metadatas", [[]])[0]
            doc_ids: list[str] = []
            for meta in metadatas:
                doc_id = meta.get("doc_id") if meta else None
                if doc_id:
                    doc_ids.append(doc_id)
            resolved: list[KnowledgeDoc] = []
            seen: set[str] = set()
            for doc_id in doc_ids:
                if doc_id in seen or doc_id not in self.docs_by_id:
                    continue
                seen.add(doc_id)
                resolved.append(self.docs_by_id[doc_id])
            if resolved:
                return resolved[:top_k]
        except Exception:
            pass
        return self.fallback.search(query, product_id=product_id, top_k=top_k)
