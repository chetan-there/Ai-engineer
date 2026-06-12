# 🔍 HybridSeek AI

> **Production-grade Hybrid RAG System** — BM25 + Vector Search, FastAPI, Sentence Transformers, FAISS, Ragas Evaluation

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 What is HybridSeek AI?

HybridSeek AI is a **document question-answering system** that:

1. Accepts PDF or TXT documents via API
2. Chunks, embeds, and indexes them using **FAISS** (vector search) and **BM25** (keyword search)
3. On each query, retrieves relevant chunks using **Hybrid Retrieval** (combining both methods)
4. Sends retrieved context to an **LLM** (GPT-3.5/4 or local model) for grounded answer generation
5. Returns the answer with **source citations** (which chunks were used)
6. Supports **Ragas evaluation** for measuring faithfulness, relevancy, and precision

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────┐
│              FastAPI Backend                │
│  POST /upload     POST /ask    POST /eval   │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────▼─────────┐
         │  Hybrid Retrieval  │
         │  ┌─────────────┐  │
         │  │  BM25 (40%) │  │  ← exact keyword match
         │  └──────┬──────┘  │
         │         │ fuse    │
         │  ┌──────▼──────┐  │
         │  │Vector (60%) │  │  ← semantic similarity
         │  └──────┬──────┘  │
         │         │ rerank  │
         └─────────┼─────────┘
                   │ top-K chunks
         ┌─────────▼─────────┐
         │   LLM Generation  │  ← GPT-3.5 / Ollama
         │   + Citations      │
         └─────────┬─────────┘
                   │
              Answer + Sources
```

---

## 🧠 Tech Stack

| Component | Technology |
|---|---|
| Web Framework | FastAPI + Uvicorn |
| Document Loading | PyPDF |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector Store | FAISS (CPU) |
| Keyword Search | rank-bm25 |
| Hybrid Retrieval | Custom weighted score fusion |
| LLM | OpenAI GPT-3.5/4 (or Ollama locally) |
| Evaluation | Ragas (faithfulness, relevancy, precision) |
| Config | Pydantic Settings + dotenv |

---

## 📁 Project Structure

```
hybridseek-ai/
├── app/
│   ├── main.py              ← FastAPI routes (upload, ask, evaluate)
│   ├── config.py            ← All settings via environment variables
│   ├── ingestion/
│   │   ├── loader.py        ← PDF/TXT document loading
│   │   └── chunker.py       ← Overlapping text chunking
│   ├── retrieval/
│   │   ├── embedder.py      ← Sentence Transformer embeddings
│   │   ├── vector_store.py  ← FAISS index management
│   │   ├── bm25_retriever.py← BM25 keyword retrieval
│   │   └── hybrid.py        ← Score fusion + re-ranking
│   ├── generation/
│   │   └── generator.py     ← LLM prompt + grounded answer
│   └── evaluation/
│       └── ragas_eval.py    ← Ragas metrics pipeline
├── data/
│   ├── uploads/             ← Uploaded documents
│   └── index/               ← Persisted FAISS index
├── tests/
│   └── test_api.py          ← Integration tests
├── .env.example
├── requirements.txt
├── run.sh / run.bat
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/hybridseek-ai.git
cd hybridseek-ai

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env — add your OPENAI_API_KEY
```

### 3. Run

```bash
# Linux/Mac:
./run.sh

# Windows:
run.bat

# Or directly:
uvicorn app.main:app --reload
```

### 4. Use the API

Open **http://localhost:8000/docs** for the interactive Swagger UI.

```bash
# Upload a document
curl -X POST http://localhost:8000/upload \
  -F "file=@your_document.pdf"

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the key findings?"}'
```

---

## 📊 API Reference

### `POST /upload`
Upload a PDF or TXT document for indexing.
- **Input:** `multipart/form-data` with `file` field
- **Returns:** `{ filename, pages_processed, chunks_created, processing_time_ms }`

### `POST /ask`
Ask a question about the indexed document.
- **Input:** `{ "question": "your question here" }`
- **Returns:** `{ answer, citations, retrieval_time_ms, generation_time_ms }`

### `POST /evaluate`
Run Ragas evaluation on QA test cases.
- **Input:** `{ "test_cases": [{ question, answer, contexts, ground_truth }] }`
- **Returns:** `{ faithfulness, answer_relevancy, context_precision }`

### `GET /status`
Check index readiness and configuration.

---

## 🔧 Configuration

Edit `.env` to customize:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo

EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=500          # characters per chunk
CHUNK_OVERLAP=50        # overlap between adjacent chunks

TOP_K_BM25=5            # BM25 candidates
TOP_K_VECTOR=5          # Vector candidates
TOP_K_FINAL=3           # Final chunks after re-ranking

BM25_WEIGHT=0.4         # Weight for keyword search
VECTOR_WEIGHT=0.6       # Weight for semantic search
```

---

## 📈 Ragas Evaluation Metrics

| Metric | Measures | Target |
|---|---|---|
| Faithfulness | Answer grounded in context (anti-hallucination) | > 0.85 |
| Answer Relevancy | Answer addresses the question | > 0.80 |
| Context Precision | Retrieved chunks are useful | > 0.75 |

---

## 🔄 Using a Local LLM (No OpenAI Key)

1. Install [Ollama](https://ollama.ai)
2. Pull a model: `ollama pull llama3`
3. In `app/generation/generator.py`, use the Ollama code block (see comments)

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 💼 Resume Bullets

- **Architected HybridSeek AI**, a production-grade RAG system combining BM25 keyword retrieval (rank-bm25) and dense vector search (FAISS + Sentence Transformers) with weighted score fusion, improving retrieval precision over single-method baselines
- **Built a FastAPI backend** with document ingestion (PDF/TXT), chunked indexing, hybrid retrieval, and LLM-based answer generation with citation grounding
- **Implemented Ragas evaluation pipeline** tracking faithfulness, answer relevancy, and context precision to continuously measure RAG system quality

---

## 🤝 Contributing

Pull requests welcome. For major changes, open an issue first.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
