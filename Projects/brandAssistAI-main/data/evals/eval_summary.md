# BrandAssist AI - Evaluation Summary

- Cases: **45**
- Runtime mode: `deterministic` | Retriever: `hybrid` | LangGraph: `True`
- Qualitative judge: **heuristic fallback (no provider calls succeeded)**
- LLM intent routing used on **0/45** turns (rest = rule fallback)
- Latency budget: 12000 ms/turn
- Scale: PASS / FAIL (1 = pass, 0 = fail)

> **Note:** provider API calls did not succeed in the environment that generated this report, so the scores reflect the deterministic agent + heuristic judge fallback. Re-run with reachable provider keys for the true LLM-as-judge results.

## Pass rate by dimension

| Dimension | Type | Pass | Rate |
| --- | --- | --- | --- |
| Completeness | LLM judge | 45/45 | 100.0% |
| Action | deterministic | 44/45 | 97.8% |
| Route | deterministic | 38/45 | 84.4% |
| Latency | deterministic | 45/45 | 100.0% |
| Coherence | LLM judge | 45/45 | 100.0% |
| Conciseness | LLM judge | 45/45 | 100.0% |
| Response | LLM judge | 45/45 | 100.0% |
| Cost | deterministic | 45/45 | 100.0% |

**Overall cell pass rate:** 352/360 (97.8%)

Full per-case detail: [`eval_report.csv`](eval_report.csv)
