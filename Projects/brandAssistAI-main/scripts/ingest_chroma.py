from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import chromadb


def chunk_text(text: str, chunk_size: int = 280, overlap: int = 60) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def ingest(db_path: Path, chroma_path: Path, collection_name: str) -> None:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT doc_id, product_id, kind, title, text FROM knowledge_documents ORDER BY doc_id"
        ).fetchall()

    client = chromadb.PersistentClient(path=str(chroma_path))
    collection = client.get_or_create_collection(collection_name)

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []
    for doc_id, product_id, kind, title, text in rows:
        for idx, chunk in enumerate(chunk_text(text)):
            ids.append(f"{doc_id}::chunk::{idx}")
            documents.append(chunk)
            metadatas.append(
                {
                    "doc_id": doc_id,
                    "product_id": product_id or "global",
                    "kind": kind,
                    "title": title,
                    "chunk_idx": idx,
                }
            )

    if ids:
        # Replace by deleting existing ids first.
        try:
            collection.delete(ids=ids)
        except Exception:
            pass
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
    print(f"Ingested {len(ids)} chunks from {len(rows)} documents into {collection_name}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest SQLite knowledge documents into Chroma.")
    parser.add_argument("--db-path", default="data/brandassist.db")
    parser.add_argument("--chroma-path", default="data/chroma")
    parser.add_argument("--collection", default="brandassist_kb")
    args = parser.parse_args()
    ingest(Path(args.db_path), Path(args.chroma_path), args.collection)


if __name__ == "__main__":
    main()
