# app/config.py
# Central configuration — all settings come from environment variables.
# Never hardcode secrets or paths.

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # ── LLM ──────────────────────────────────────────────────────────────────
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"

    # ── Embeddings ───────────────────────────────────────────────────────────
    # all-MiniLM-L6-v2: fast, lightweight, runs 100% locally — great for dev
    embedding_model: str = "all-MiniLM-L6-v2"

    # ── Chunking ─────────────────────────────────────────────────────────────
    # chunk_size: how many characters per chunk
    # chunk_overlap: shared characters between adjacent chunks
    #   → prevents answers from being split across chunk boundaries
    chunk_size: int = 500
    chunk_overlap: int = 50

    # ── Retrieval ────────────────────────────────────────────────────────────
    top_k_bm25: int = 5       # BM25 returns this many chunks
    top_k_vector: int = 5     # Vector search returns this many chunks
    top_k_final: int = 3      # After re-ranking, keep this many

    # ── Hybrid Weights ───────────────────────────────────────────────────────
    # Vector search weighted higher → semantic understanding > exact keywords
    bm25_weight: float = 0.4
    vector_weight: float = 0.6

    # ── Paths ────────────────────────────────────────────────────────────────
    upload_dir: Path = Path("data/uploads")
    index_dir: Path = Path("data/index")

    class Config:
        env_file = ".env"
        extra = "ignore"


# Module-level singleton — import `settings` everywhere
settings = Settings()

# Ensure required directories exist on startup
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.index_dir.mkdir(parents=True, exist_ok=True)
