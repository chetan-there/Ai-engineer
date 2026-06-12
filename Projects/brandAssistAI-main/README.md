# BrandAssist AI

BrandAssist AI is a platform-neutral multimodal consumer-support agent POC.
It handles text and image-context support requests for a synthetic appliance brand,
retrieves grounded product guidance, calls deterministic mock support tools, and
tracks support-operations metrics.

## Quick Start

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Recommended) enable the LLM + image-identification features
cp .env.example .env
#   then open .env and add at least one key, e.g. GROQ_API_KEY=...

# 4. Run the app (the prebuilt data/brandassist.db is used automatically)
streamlit run app.py

# Optional: run the test suite
pytest
```

### What needs a key vs. what doesn't

The app ships with a prebuilt SQLite database, so **no data setup is required**.

- **Without any API key:** the agent still runs end-to-end using the deterministic
  intent rules, hybrid retrieval, tools, and the LangGraph path. Uploaded-image
  identification is disabled (it reports "no vision model configured").
- **With `GROQ_API_KEY` (or `OPENROUTER_API_KEY`) in `.env`:** unlocks LLM-based
  intent classification, response polishing, and **product photo identification**
  via a free vision model. Groq's `llama-4-scout` is the default vision model.

Get a free key from [console.groq.com](https://console.groq.com) or
[openrouter.ai](https://openrouter.ai). LangGraph and Chroma are used for
orchestration and vector retrieval and need no external service.

## Runtime Modes

- `deterministic` runtime: reproducible workflow for local tests and grading.
- `llm` runtime: uses provider routing (`GROQ_API_KEY`, `OPENROUTER_API_KEY`,
  `HF_API_KEY`, or `OPENAI_API_KEY`) for intent classification and response polishing
  with deterministic safety/tooling fallback.
- `lexical` retriever: deterministic token-matching retrieval.
- `hybrid` retriever: lexical retrieval + policy/category reranking for stronger
  support-policy recall.
- `chroma` retriever: vector search over chunked knowledge indexed in Chroma.
- Optional LangGraph execution path for explicit state-machine orchestration.

The Streamlit app is locked to the recommended demo configuration (`llm` runtime,
`hybrid` retriever, LangGraph on) for consistency. All modes remain available
programmatically:

```python
from src.brandassist_ai import SupportAgent

agent = SupportAgent(runtime_mode="deterministic", retriever_mode="hybrid")
response = agent.run("Where is order #A2002?", use_graph=True)
```

## Synthetic SQLite + Chroma Pipeline

Generate pseudonymized marketplace data (30 products, 100 users, 100 orders, 60
registrations, 100 support cases), validate it, then build Chroma index:

```bash
source .venv/bin/activate
python scripts/generate_seed_data.py
python scripts/validate_seed_data.py
python scripts/generate_knowledge_base.py   # rich original manuals/FAQ/troubleshooting per product
python scripts/ingest_chroma.py             # chunk + embed knowledge base into Chroma
```

> The knowledge base is fully synthetic and original (no real manufacturer
> manuals), so it is safe to publish. `generate_knowledge_base.py` writes six
> manual-style documents per product (setup, FAQ, troubleshooting, error codes,
> maintenance, safety) plus global warranty/returns policies. Re-run
> `ingest_chroma.py` after editing it to refresh the vector store.

The Streamlit app (`app.py`) is the demo UI. It supports image context via labeled
samples or your own uploaded product photo (identified by a vision model when an
LLM key is configured).

## Environment Keys

Use `.env.example` as the template for API keys and runtime defaults.

## Responsible AI: Cost & PII

- **PII handling (two layers).** All seed data is synthetic/pseudonymized, so there is no
  real personal data in the repo or database. On top of that, `src/brandassist_ai/pii.py`
  redacts direct identifiers a user might type (email, phone, card number, SSN) into typed
  placeholders **before any text is sent to an LLM provider** (intent classification and
  answer rewriting). Pseudonymous business IDs (order/customer/serial) are preserved so the
  agent can still call tools, and the run trace flags when redaction fires.
- **Cost awareness.** The LLM router records real token usage and estimates per-turn cost
  from per-model pricing. Each run trace carries `llm_calls`, token counts, and
  `llm_cost_usd`, surfaced in the live trace panel and gated as a **Cost** dimension in the
  eval suite (`--cost-budget-usd`, default $0.02).
- **Guardrails.** Bounded tool authority (no auto-approval of refunds/warranty claims),
  image-confidence and low-information-input gates, prompt-injection resistance, and
  escalation on repeated failures. See `docs/SAFETY_MODEL.md`.

## Project Shape

```
app.py                 # Streamlit demo UI
src/brandassist_ai/    # agent, orchestration, retrieval, tools, vision, metrics, data loading
scripts/               # data + knowledge-base generation and Chroma ingest
db/schema.sql          # SQLite schema
data/brand/            # synthetic products, orders, warranties, knowledge base, image labels
data/evals/            # pytest golden support scenarios
tests/                 # eval harness and unit tests
docs/                  # architecture, data model, safety, roadmap, runbook, project map
```

## Documentation

- `docs/ARCHITECTURE.md` - system architecture and orchestration flow.
- `docs/DATA_MODEL.md` - data model and ERD.
- `docs/EVALUATION_REPORT.md` - eval harness, results, and metrics.
- `docs/SAFETY_MODEL.md` - safety guardrails and threat model.
- `docs/ROADMAP.md` - path from POC to production.

## Generated Artifacts

`data/brandassist.db` ships prebuilt so the demo runs immediately. The Chroma
vector store (`data/chroma/`) and the `.venv` are generated locally and are
git-ignored; rebuild the vector store with `python scripts/ingest_chroma.py`.
