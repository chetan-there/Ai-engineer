# Evaluation Report

## Scope

This report summarizes automated evaluation for the BrandAssist AI capstone POC.

## Test Harness

- Golden behavior checks: `tests/test_golden_cases.py`
- Metrics sanity checks: `tests/test_metrics.py`
- Mode/orchestration checks: `tests/test_modes_and_orchestration.py`
- Warranty registration flow: `tests/test_warranty_registration.py`
- Context guardrails: `tests/test_context_guardrails.py`

Run:

```bash
source .venv/bin/activate
PYTHONPATH=. pytest -q
```

## Latest Result

- Status: passing
- Output: `18 passed`

## Multi-Dimensional Evaluation Suite (45 cases)

Beyond the pass/fail unit tests, the project ships a scenario suite that scores the
agent on **eight quality dimensions** per turn and writes a wide, reviewable report.

- Cases: `data/evals/eval_cases.json` (45 curated utterances across every flow, including
  a dedicated **error-handling** group: unknown customer/product, gibberish input,
  order request with no ID, and a verbose message with a buried order ID)
- Runner: `scripts/run_eval_suite.py`
- Output: `data/evals/eval_report.csv` (per-case detail) + `data/evals/eval_summary.md`

Run:

```bash
source .venv/bin/activate
# True LLM-as-judge run (needs a reachable provider key, e.g. GROQ_API_KEY):
python scripts/run_eval_suite.py --runtime llm --retriever hybrid --graph
# Fully offline/reproducible run (deterministic agent + heuristic judge):
python scripts/run_eval_suite.py --runtime deterministic --no-judge
```

The four qualitative dimensions use an **LLM-as-judge**; if no provider key is reachable
they fall back to transparent heuristics, and the report records which path ran
(`Judge` column + summary header) so the numbers are never misrepresented.

### Scoring scale

`PASS` / `FAIL`, mirrored numerically as `1` / `0` (the `... Score` columns) so pass
rates can be aggregated per dimension.

### Legend - evaluation dimensions

| Dimension | Type | What it asks |
| --- | --- | --- |
| **Completeness** | LLM judge | Does the answer fully address the request? (A clarifying question is complete when information was genuinely missing.) |
| **Action** | deterministic | Were the expected tools called, with no unwarranted escalation (no `create_ticket` when none was expected)? |
| **Route** | deterministic | Did the request reach the correct intent/handler branch? Single-agent analog of "which subagent handled it." |
| **Latency** | deterministic | Did the turn finish within the latency budget (default 12000 ms)? |
| **Coherence** | LLM judge | Is the answer logical, on-topic, and well-formed? |
| **Conciseness** | LLM judge | Is it appropriately brief, with no filler? |
| **Response** | LLM judge | Overall, does the answer match the expected response? (A "must-not-do" violation - e.g. approving a claim or issuing a refund - fails here.) |
| **Cost** | deterministic | Did the turn stay within the estimated token-cost budget (default $0.02)? Cost is computed from real token usage and per-model pricing. |

### Legend - report columns

| Column | Meaning |
| --- | --- |
| `Case ID` | Stable identifier for the scenario |
| `Utterance` | The simulated customer message (`[image=...]` marks an attached labeled photo) |
| `Expected Actions` / `Actual Actions` | Tools the agent should call / did call |
| `Expected Route` / `Actual Route` | Intent/handler the request should map to / did map to |
| `Expected Response` | Description of the ideal answer; doubles as the LLM-judge rubric |
| `Agent Response` | The agent's actual answer text |
| `<Dimension> Evaluation` | `PASS` / `FAIL` verdict for that dimension |
| `<Dimension> Evaluation Score` | Numeric mirror (`1` pass / `0` fail) |
| `<Dimension> Evaluation Reasoning` | Short justification for the verdict |
| `Latency (ms)` | Wall-clock time for the turn |
| `Cost (USD)` | Estimated provider cost for the turn (from token usage x per-model pricing) |
| `LLM Tokens` / `LLM Calls` | Total tokens and number of LLM calls made during the turn |
| `Intent Source` | How the route was decided: `llm:<provider>`, `rule`, `rule_fallback`, or `context_inherited` |
| `Outcome` | Final turn outcome: `resolved`, `clarify`, `escalated`, or `unsupported` |
| `Judge` | Which judge produced the qualitative scores: `llm` or `heuristic` |
| `Warnings` | Any trace warnings raised during the turn |

### Legend - vocabulary

- **Route values (intents):** `order_status`, `warranty`, `warranty_registration`,
  `return_policy`, `setup`, `troubleshooting`, `general_support`, `ambiguous`.
- **Tools (actions):** `order_lookup`, `orders_by_customer_lookup`, `product_lookup`,
  `warranty_check`, `register_warranty`, `create_ticket`.
- **Outcomes:** `resolved` (answered), `clarify` (asked for missing info),
  `escalated` (handed to a human via a ticket), `unsupported` (out-of-catalog / unidentifiable).
- **Judge types:** *LLM-as-judge* scores Completeness/Coherence/Conciseness/Response via a
  provider model; *heuristic* is the deterministic fallback used when no provider is reachable.

### Latest baseline (deterministic agent + heuristic judge)

This baseline is the reproducible floor; the LLM routing path is expected to lift the
Route and Action numbers when run with a reachable provider key.

| Dimension | Pass | Rate |
| --- | --- | --- |
| Completeness | 45/45 | 100.0% |
| Action | 44/45 | 97.8% |
| Route | 38/45 | 84.4% |
| Latency | 45/45 | 100.0% |
| Coherence | 45/45 | 100.0% |
| Conciseness | 45/45 | 100.0% |
| Response | 45/45 | 100.0% |
| Cost | 45/45 | 100.0% |

**Overall cell pass rate: 352/360 (97.8%).** The Route gap concentrates on
weak-keyword phrasings (e.g. "How do I set this up?", "Water leaks from the base")
that the deterministic router misses - exactly the cases LLM-assisted routing recovers.
(Cost is $0 in this offline baseline because no provider calls were made.)

## Key Signals

- Golden-case behavior is stable across setup, troubleshooting, warranty, order
  status, unsupported visuals, and escalation scenarios.
- Hybrid retrieval improves policy-document recall in warranty-related prompts.
- Chroma vector retrieval returns symptom-relevant troubleshooting docs over the
  rich (182-document) synthetic knowledge base.
- LangGraph orchestration path reproduces deterministic workflow outcomes.
- Context guardrails: bare identifiers (e.g. a lone order ID) trigger clarification
  rather than a hallucinated intent, and clarifications do not open tickets.

## Modes Under Test

- Deterministic runtime (reproducible, used by the test suite).
- LLM runtime via provider routing (`GROQ_API_KEY` / `OPENROUTER_API_KEY` / `HF_API_KEY`
  / `OPENAI_API_KEY`) with deterministic fallback.
- Image identification via a free multimodal model (Groq `llama-4-scout` by default),
  mapped to the catalog through the vision alias map.

## Known Gaps

- No CI pipeline yet to enforce score thresholds on pull requests.
- LLM and vision features are optional and depend on a provider API key.
- Retrieval metrics (`hit@k`, MRR) are not yet persisted as a separate report artifact.
