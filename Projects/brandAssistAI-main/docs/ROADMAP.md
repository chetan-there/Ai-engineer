# Roadmap

## POC -> Production Plan

## Phase 1: Reliability and Benchmarks

- Add retrieval benchmark metrics (`hit@k`, MRR) per scenario.
- Add adversarial eval pack (prompt injection, conflicting policy docs, noisy visual context).
- Add regression snapshots for tool-call sequence and escalation decisions.

## Phase 2: Observability and Cost

- Integrate Langfuse tracing for every run.
- Track token cost and latency by intent and outcome.
- Add daily quality/cost summary artifact.

## Phase 3: Data and Retrieval Hardening

- Chroma vector index with metadata filters is implemented; add RRF fusion of
  lexical + vector results next.
- Expand synthetic KB diversity and contradictory policy test cases.
- Add freshness/version tags for policies and manuals.

## Phase 4: Production Controls

- Add policy engine for sensitive actions.
- Add approval workflow for refund/replacement recommendations.
- Add API deployment surface with auth, rate limits, and audit logging.
