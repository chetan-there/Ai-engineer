# tests/test_api.py
# Integration tests for the HybridSeek AI FastAPI backend.
#
# Run with:
#   pytest tests/ -v
#
# These tests use FastAPI's TestClient which runs the app in-process
# (no server needed) — standard practice for API testing.

import pytest
from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)


# ── Health Tests ─────────────────────────────────────────────────────────────

def test_health_check():
    """API should return 200 and status message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data


def test_status_endpoint():
    """Status endpoint should return index state."""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "vector_index_ready" in data
    assert "bm25_index_ready" in data


# ── Upload Tests ──────────────────────────────────────────────────────────────

def test_upload_txt_document():
    """Uploading a valid TXT file should succeed."""
    content = b"""
    Machine learning is a subset of artificial intelligence.
    It enables computers to learn from experience without being explicitly programmed.
    Supervised learning uses labeled data to train models.
    Unsupervised learning discovers patterns in unlabeled data.
    Neural networks are inspired by the human brain structure.
    Deep learning uses multiple layers of neural networks.
    """ * 5   # repeat to create enough text for chunking

    response = client.post(
        "/upload",
        files={"file": ("test_doc.txt", io.BytesIO(content), "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "chunks_created" in data
    assert data["chunks_created"] > 0


def test_upload_invalid_format():
    """Uploading an unsupported file type should return 400."""
    response = client.post(
        "/upload",
        files={"file": ("test.csv", io.BytesIO(b"col1,col2\na,b"), "text/csv")},
    )
    assert response.status_code == 400


# ── QA Tests ──────────────────────────────────────────────────────────────────

def test_ask_question_after_upload():
    """After uploading, asking a question should return an answer."""
    # First upload a document
    content = b"""
    Artificial intelligence (AI) refers to the simulation of human intelligence processes
    by computer systems. These processes include learning, reasoning, and self-correction.
    The term was coined by John McCarthy in 1956 at the Dartmouth Conference.
    Machine learning is a method of data analysis that automates analytical model building.
    """ * 5

    client.post(
        "/upload",
        files={"file": ("ai_intro.txt", io.BytesIO(content), "text/plain")},
    )

    # Now ask a question
    response = client.post(
        "/ask",
        json={"question": "What is artificial intelligence?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert len(data["citations"]) > 0
    assert "retrieval_time_ms" in data


def test_ask_empty_question():
    """Empty question should return 400."""
    response = client.post("/ask", json={"question": "   "})
    assert response.status_code == 400


# ── Run directly for quick check ──────────────────────────────────────────────
if __name__ == "__main__":
    print("Run with: pytest tests/ -v")
