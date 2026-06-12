# app/generation/generator.py
# LLM-based answer generation with citation grounding.
#
# PROMPT ENGINEERING:
#   We use a structured system prompt that forces the LLM to:
#     1. Answer ONLY from the provided context (reduces hallucination)
#     2. Cite which source chunk each claim comes from
#     3. Say "I don't know" when the answer isn't in context
#   This is called "grounded generation" — a key RAG pattern.
#
# LOCAL MODEL SUPPORT:
#   If you don't have an OpenAI key, swap the client for:
#     - Ollama (llama3, mistral) — 100% local, free
#     - HuggingFace Inference API — free tier available
#   See the comments in generate_answer() for how to swap.

from openai import OpenAI
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Lazy-initialize client so missing API key doesn't crash on import
_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. "
                "Add it to your .env file or use a local model (see generator.py comments)."
            )
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


SYSTEM_PROMPT = """You are HybridSeek AI, a precise document question-answering assistant.

RULES:
1. Answer ONLY using information from the provided context chunks.
2. After each factual claim, cite its source like this: [Source 1], [Source 2], etc.
3. If the context does not contain enough information to answer, say:
   "I couldn't find a clear answer in the uploaded documents."
4. Do NOT use external knowledge or make up information.
5. Be concise but complete. Use bullet points for multi-part answers.

FORMAT:
- Start with a direct answer to the question.
- Follow with supporting details and citations.
- End with: "**Sources used:** [list the source files referenced]"
"""


def generate_answer(query: str, context_str: str) -> str:
    """
    Generate a grounded answer from the LLM given query + retrieved context.

    Args:
        query: The user's question
        context_str: Formatted context string from hybrid.format_context()

    Returns:
        LLM-generated answer string with inline citations
    """
    user_message = f"""CONTEXT:
{context_str}

QUESTION:
{query}

Please answer the question using only the context above. Cite sources inline."""

    try:
        client = get_client()
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.1,      # Low temp → factual, deterministic answers
            max_tokens=1000,
        )
        answer = response.choices[0].message.content
        logger.info(f"Generated answer ({len(answer)} chars) for query: '{query[:60]}'")
        return answer

    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        raise RuntimeError(f"Answer generation failed: {str(e)}")


# ── LOCAL MODEL ALTERNATIVE (Ollama) ─────────────────────────────────────────
# To use Ollama instead of OpenAI:
#
# 1. Install Ollama: https://ollama.ai
# 2. Run: ollama pull llama3
# 3. Replace the generate_answer function with:
#
# def generate_answer(query: str, context_str: str) -> str:
#     import requests
#     payload = {
#         "model": "llama3",
#         "prompt": f"System: {SYSTEM_PROMPT}\n\nContext:\n{context_str}\n\nQuestion: {query}",
#         "stream": False,
#     }
#     resp = requests.post("http://localhost:11434/api/generate", json=payload)
#     return resp.json()["response"]
# ─────────────────────────────────────────────────────────────────────────────
