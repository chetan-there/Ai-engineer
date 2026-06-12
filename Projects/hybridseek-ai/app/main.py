# app/main.py
# FastAPI application — the main entry point for the HybridSeek AI backend.
#
# ENDPOINTS:
#   GET  /              → health check
#   POST /upload        → ingest a PDF or TXT document
#   POST /ask           → ask a question, get grounded answer + citations
#   POST /evaluate      → run Ragas evaluation metrics
#   GET  /status        → check if index is ready for querying

import logging
import shutil
import time
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.ingestion.loader import load_document
from app.ingestion.chunker import chunk_documents
from app.retrieval.vector_store import vector_store
from app.retrieval.bm25_retriever import bm25_retriever
from app.retrieval.hybrid import hybrid_search, format_context
from app.generation.generator import generate_answer
from app.evaluation.ragas_eval import run_ragas_evaluation

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="HybridSeek AI",
    description=(
        "Production-grade Hybrid RAG system combining BM25 + Vector Search. "
        "Upload documents, ask questions, get grounded answers with citations."
    ),
    version="1.0.0",
    docs_url="/docs",       # Swagger UI at /docs
    redoc_url="/redoc",     # ReDoc UI at /redoc
)

# Allow frontend (Streamlit / HTML UI) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ─────────────────────────────────────────────────
class AskRequest(BaseModel):
    question: str

    class Config:
        json_schema_extra = {
            "example": {"question": "What are the key findings in the document?"}
        }


class AskResponse(BaseModel):
    question: str
    answer: str
    citations: list[dict]
    retrieval_time_ms: float
    generation_time_ms: float


class EvaluateRequest(BaseModel):
    test_cases: list[dict]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def health_check():
    """Basic health check — confirms the API is running."""
    return {
        "status": "✅ HybridSeek AI is running",
        "version": "1.0.0",
        "embedding_model": settings.embedding_model,
        "llm_model": settings.openai_model,
        "index_ready": vector_store.is_ready,
    }


@app.get("/status", tags=["Health"])
def get_status():
    """Returns current index state — how many chunks are indexed."""
    return {
        "vector_index_ready": vector_store.is_ready,
        "bm25_index_ready": bm25_retriever.is_ready,
        "total_chunks": len(vector_store.chunks) if vector_store.is_ready else 0,
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "bm25_weight": settings.bm25_weight,
        "vector_weight": settings.vector_weight,
    }


@app.post("/upload", tags=["Ingestion"])
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF or TXT document for indexing.

    Steps:
    1. Save file to disk
    2. Extract text (page by page)
    3. Chunk into overlapping segments
    4. Build FAISS vector index
    5. Build BM25 index
    6. Persist index to disk

    Supports: .pdf, .txt
    """
    # Validate file type
    suffix = Path(file.filename).suffix.lower()
    if suffix not in [".pdf", ".txt"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: '{suffix}'. Upload a .pdf or .txt file."
        )

    # Save uploaded file
    save_path = settings.upload_dir / file.filename
    try:
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        logger.info(f"Saved uploaded file: {save_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Process pipeline
    try:
        t0 = time.time()

        # Phase 1: Load
        pages = load_document(save_path)
        if not pages:
            raise HTTPException(status_code=422, detail="Document has no extractable text.")

        # Phase 2: Chunk
        chunks = chunk_documents(pages)

        # Phase 3: Build indexes
        vector_store.build(chunks)
        bm25_retriever.build(chunks)

        elapsed = round((time.time() - t0) * 1000, 2)

        return {
            "message": f"✅ Document '{file.filename}' indexed successfully.",
            "filename": file.filename,
            "pages_processed": len(pages),
            "chunks_created": len(chunks),
            "processing_time_ms": elapsed,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Indexing failed for {file.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@app.post("/ask", response_model=AskResponse, tags=["QA"])
def ask_question(body: AskRequest):
    """
    Ask a question about the uploaded document.

    Returns:
    - Grounded answer from LLM
    - Citations (which chunks were used)
    - Timing breakdown (retrieval + generation)
    """
    if not vector_store.is_ready or not bm25_retriever.is_ready:
        raise HTTPException(
            status_code=400,
            detail="No document indexed yet. Call POST /upload first."
        )

    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # ── Retrieval ──────────────────────────────────────────────────────
        t_ret_start = time.time()
        chunks = hybrid_search(question)
        context_str, citations = format_context(chunks)
        retrieval_ms = round((time.time() - t_ret_start) * 1000, 2)

        # ── Generation ─────────────────────────────────────────────────────
        t_gen_start = time.time()
        answer = generate_answer(question, context_str)
        generation_ms = round((time.time() - t_gen_start) * 1000, 2)

        return AskResponse(
            question=question,
            answer=answer,
            citations=citations,
            retrieval_time_ms=retrieval_ms,
            generation_time_ms=generation_ms,
        )

    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"QA pipeline failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"QA pipeline error: {str(e)}")


@app.post("/evaluate", tags=["Evaluation"])
def evaluate_pipeline(body: EvaluateRequest):
    """
    Run Ragas evaluation on provided QA test cases.

    Each test case must have:
      - question: str
      - answer: str (LLM-generated)
      - contexts: list[str] (retrieved chunk texts)
      - ground_truth: str (correct answer, for context_precision)

    Returns faithfulness, answer_relevancy, context_precision scores.
    """
    try:
        scores = run_ragas_evaluation(body.test_cases)
        return {
            "status": "✅ Evaluation complete",
            "num_test_cases": len(body.test_cases),
            "scores": scores,
            "interpretation": {
                "faithfulness": "Measures how grounded the answer is in retrieved context (anti-hallucination)",
                "answer_relevancy": "Measures if the answer actually addresses the question",
                "context_precision": "Measures if retrieved chunks are useful for the question",
            }
        }
    except Exception as e:
        logger.error(f"Ragas evaluation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
