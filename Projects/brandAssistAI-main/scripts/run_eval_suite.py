"""
BrandAssist AI - multi-dimensional evaluation suite.

Runs the support agent over a curated set of utterances and scores each turn on
seven dimensions, writing a wide CSV in the requested template plus a short
markdown summary.

Dimensions
----------
Deterministic (computed from the trace):
  * Action      - did the agent call the expected tools (and not over-escalate)?
  * Route       - did it route to the expected intent/handler branch?
                  (single-agent equivalent of "which subagent handled it")
  * Latency     - did the turn finish within the latency budget?
  * Cost        - did the turn stay within the estimated token-cost budget?

LLM-as-judge (one call per case returns all four verdicts):
  * Completeness - does the answer fully address the request?
  * Coherence    - is it logical, on-topic and well-formed?
  * Conciseness  - is it appropriately brief (no padding)?
  * Response     - overall, does it match the expected response?

If no LLM provider key is configured (or the judge call fails), the qualitative
metrics fall back to transparent heuristics so the suite always produces output.

Scoring scale: PASS / FAIL (with a 1/0 numeric mirror for aggregation).

Usage
-----
  python scripts/run_eval_suite.py
  python scripts/run_eval_suite.py --runtime llm --retriever hybrid --graph \
      --latency-budget-ms 12000 --sleep 0.4
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.brandassist_ai import SupportAgent  # noqa: E402
from src.brandassist_ai.llm_router import LLMRouter  # noqa: E402

EVAL_DIR = ROOT / "data" / "evals"
CASES_PATH = EVAL_DIR / "eval_cases.json"
REPORT_CSV = EVAL_DIR / "eval_report.csv"
SUMMARY_MD = EVAL_DIR / "eval_summary.md"

QUALITATIVE = ["completeness", "coherence", "conciseness", "response"]
ALL_METRICS = ["completeness", "action", "route", "latency", "coherence", "conciseness", "response", "cost"]

# Column order follows the requested evaluation template exactly.
CSV_COLUMNS = [
    "Case ID",
    "Expected Actions",
    "Expected Route",
    "Utterance",
    "Agent Response",
    "Expected Response",
    "Actual Route",
    "Completeness Evaluation",
    "Action Evaluation",
    "Route Evaluation",
    "Latency Evaluation",
    "Coherence Evaluation",
    "Actual Actions",
    "Conciseness Evaluation",
    "Response Evaluation",
    "Completeness Evaluation Score",
    "Completeness Evaluation Reasoning",
    "Action Evaluation Score",
    "Action Evaluation Reasoning",
    "Route Evaluation Score",
    "Route Evaluation Reasoning",
    "Latency Evaluation Score",
    "Latency Evaluation Reasoning",
    "Coherence Evaluation Score",
    "Coherence Evaluation Reasoning",
    "Conciseness Evaluation Score",
    "Conciseness Evaluation Reasoning",
    "Response Evaluation Score",
    "Response Evaluation Reasoning",
    "Cost Evaluation",
    "Cost Evaluation Score",
    "Cost Evaluation Reasoning",
    # Helpful trailing columns (outside the template) for demo/debugging.
    "Latency (ms)",
    "Cost (USD)",
    "LLM Tokens",
    "LLM Calls",
    "Intent Source",
    "Outcome",
    "Judge",
    "Warnings",
]

_JUDGE_SYSTEM_PROMPT = (
    "You are a strict QA evaluator for a customer-support AI agent. "
    "You are given the customer's utterance, a description of the expected/ideal response, "
    "and the agent's actual response. Judge the actual response on four dimensions and reply "
    "with compact JSON only (no markdown), using exactly this shape:\n"
    '{"completeness":{"verdict":"PASS|FAIL","reason":"<=30 words"},'
    '"coherence":{"verdict":"PASS|FAIL","reason":"<=30 words"},'
    '"conciseness":{"verdict":"PASS|FAIL","reason":"<=30 words"},'
    '"response":{"verdict":"PASS|FAIL","reason":"<=30 words"}}\n'
    "Definitions: completeness = fully addresses what the user asked (a clarifying question is "
    "complete when information was genuinely missing); coherence = logical, on-topic, well-formed; "
    "conciseness = appropriately brief with no filler; response = overall match to the expected response. "
    "Critically: if the expected response says the agent must NOT do something (approve a claim, issue a "
    "refund, bypass policy, guess an unidentifiable product) and the actual response does it, fail the "
    "relevant dimensions."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the BrandAssist multi-dimensional eval suite.")
    parser.add_argument("--runtime", default="llm", choices=["llm", "deterministic"],
                        help="Agent runtime mode (default: llm, matching production).")
    parser.add_argument("--retriever", default="hybrid", choices=["lexical", "hybrid", "chroma"],
                        help="Retriever mode (default: hybrid).")
    parser.add_argument("--graph", action="store_true", default=True,
                        help="Run through the LangGraph orchestrator (default: on).")
    parser.add_argument("--no-graph", dest="graph", action="store_false",
                        help="Disable the LangGraph orchestrator.")
    parser.add_argument("--latency-budget-ms", type=float, default=12000.0,
                        help="Latency budget per turn in ms (default: 12000).")
    parser.add_argument("--cost-budget-usd", type=float, default=0.02,
                        help="Estimated cost budget per turn in USD (default: 0.02).")
    parser.add_argument("--sleep", type=float, default=0.3,
                        help="Seconds to sleep between cases to ease free-tier rate limits.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Only run the first N cases (smoke testing).")
    parser.add_argument("--no-judge", action="store_true",
                        help="Skip the LLM judge and use heuristics for qualitative metrics.")
    return parser.parse_args()


def load_cases() -> list[dict]:
    with CASES_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _verdict(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


def eval_action(expected: list[str], actual: list[str]) -> tuple[bool, str]:
    expected_set, actual_set = set(expected), set(actual)
    missing = expected_set - actual_set
    # Over-escalation guard: a ticket when none was expected is a failure.
    unexpected_ticket = "create_ticket" in actual_set and "create_ticket" not in expected_set
    if missing:
        return False, f"Missing expected tool(s): {sorted(missing)}. Actual: {sorted(actual_set) or 'none'}."
    if unexpected_ticket:
        return False, f"Unexpected escalation: create_ticket was called but not expected. Actual: {sorted(actual_set)}."
    if not expected_set:
        return True, f"No tools expected; agent called {sorted(actual_set) or 'none'} (acceptable)."
    return True, f"All expected tools present: {sorted(expected_set)}."


def eval_route(expected: str, actual: str) -> tuple[bool, str]:
    if expected == actual:
        return True, f"Routed to expected intent/handler '{expected}'."
    return False, f"Expected route '{expected}' but routed to '{actual}'."


def eval_latency(elapsed_ms: float, budget_ms: float) -> tuple[bool, str]:
    if elapsed_ms <= budget_ms:
        return True, f"{elapsed_ms:.0f} ms within {budget_ms:.0f} ms budget."
    return False, f"{elapsed_ms:.0f} ms exceeded {budget_ms:.0f} ms budget."


def eval_cost(cost_usd: float, tokens: int, calls: int, budget_usd: float) -> tuple[bool, str]:
    detail = f"${cost_usd:.6f} over {calls} LLM call(s), {tokens} tokens"
    if cost_usd <= budget_usd:
        return True, f"{detail} (within ${budget_usd:.4f} budget)."
    return False, f"{detail} (exceeded ${budget_usd:.4f} budget)."


def heuristic_qualitative(case: dict, answer: str, outcome: str) -> dict:
    """Transparent fallback when no LLM judge is available."""
    answer = answer or ""
    length = len(answer)
    complete_outcomes = {"resolved", "clarify", "unsupported", "escalated"}
    completeness = bool(answer) and (outcome in complete_outcomes)
    coherence = bool(answer.strip()) and length >= 15
    conciseness = length <= 900
    response = bool(answer) and outcome != "unresolved"
    note = "Heuristic fallback (no LLM judge)."
    return {
        "completeness": {"verdict": _verdict(completeness), "reason": f"{note} Outcome={outcome}, len={length}."},
        "coherence": {"verdict": _verdict(coherence), "reason": f"{note} Non-empty and readable length={length}."},
        "conciseness": {"verdict": _verdict(conciseness), "reason": f"{note} Length={length} (budget 900)."},
        "response": {"verdict": _verdict(response), "reason": f"{note} Produced an answer with outcome={outcome}."},
    }


def llm_qualitative(router: LLMRouter, case: dict, answer: str) -> dict | None:
    user_prompt = (
        f"Customer utterance:\n{case['message']}\n\n"
        f"Expected response (ideal behavior):\n{case['expected_response']}\n\n"
        f"Agent actual response:\n{answer}"
    )
    try:
        text = router.complete(system_prompt=_JUDGE_SYSTEM_PROMPT, user_prompt=user_prompt).strip()
        if text.startswith("```"):
            text = text.strip("`")
            if "\n" in text:
                text = text.split("\n", 1)[1]
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            text = text[start : end + 1]
        data = json.loads(text)
        result = {}
        for metric in QUALITATIVE:
            entry = data.get(metric, {}) or {}
            verdict = str(entry.get("verdict", "")).upper()
            verdict = "PASS" if verdict == "PASS" else "FAIL"
            result[metric] = {"verdict": verdict, "reason": str(entry.get("reason", "")).strip() or "(no reason given)"}
        return result
    except Exception:  # network/provider/parse variability
        return None


def run() -> None:
    load_dotenv()
    args = parse_args()
    cases = load_cases()
    if args.limit:
        cases = cases[: args.limit]

    agent = SupportAgent(runtime_mode=args.runtime, retriever_mode=args.retriever)
    judge_router = LLMRouter()
    use_judge = (not args.no_judge) and judge_router.is_enabled()

    print(f"Running {len(cases)} cases | runtime={args.runtime} retriever={args.retriever} "
          f"graph={args.graph} | judge={'LLM' if use_judge else 'heuristic'}")
    if args.no_judge:
        print("  (LLM judge disabled by flag)")
    elif not judge_router.is_enabled():
        print("  (No provider API key found; falling back to heuristic judge)")

    rows: list[dict] = []
    metric_pass = {m: 0 for m in ALL_METRICS}
    judge_llm_rows = 0
    intent_llm_turns = 0

    for idx, case in enumerate(cases, start=1):
        start = time.perf_counter()
        try:
            response = agent.run(
                case["message"],
                image_id=case.get("image_id"),
                use_graph=args.graph,
            )
            error = None
        except Exception as exc:  # keep the suite resilient
            error = exc
            response = None
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        if response is None:
            answer = f"[ERROR] {error}"
            actual_route = "error"
            actual_actions: list[str] = []
            outcome = "error"
            intent_source = "n/a"
            warnings: list[str] = [str(error)]
            cost_usd = 0.0
            llm_tokens = 0
            llm_calls = 0
        else:
            trace = response.trace
            answer = response.answer
            actual_route = trace.intent
            actual_actions = [c.name for c in trace.tool_calls]
            outcome = trace.outcome
            intent_source = trace.intent_source
            warnings = list(trace.warnings)
            cost_usd = trace.llm_cost_usd
            llm_tokens = trace.llm_prompt_tokens + trace.llm_completion_tokens
            llm_calls = trace.llm_calls

        # Deterministic metrics.
        action_pass, action_reason = eval_action(case["expected_actions"], actual_actions)
        route_pass, route_reason = eval_route(case["expected_route"], actual_route)
        latency_pass, latency_reason = eval_latency(elapsed_ms, args.latency_budget_ms)
        cost_pass, cost_reason = eval_cost(cost_usd, llm_tokens, llm_calls, args.cost_budget_usd)

        # Qualitative metrics.
        qual = None
        judge_used = "heuristic"
        if response is not None and use_judge:
            qual = llm_qualitative(judge_router, case, answer)
            if qual is not None:
                judge_used = "llm"
                judge_llm_rows += 1
        if qual is None:
            qual = heuristic_qualitative(case, answer, outcome)
        if intent_source.startswith("llm"):
            intent_llm_turns += 1

        verdicts = {
            "completeness": qual["completeness"]["verdict"] == "PASS",
            "action": action_pass,
            "route": route_pass,
            "latency": latency_pass,
            "coherence": qual["coherence"]["verdict"] == "PASS",
            "conciseness": qual["conciseness"]["verdict"] == "PASS",
            "response": qual["response"]["verdict"] == "PASS",
            "cost": cost_pass,
        }
        for metric, passed in verdicts.items():
            metric_pass[metric] += int(passed)

        row = {
            "Case ID": case["id"],
            "Expected Actions": ", ".join(case["expected_actions"]) or "(none)",
            "Expected Route": case["expected_route"],
            "Utterance": case["message"] + (f"  [image={case['image_id']}]" if case.get("image_id") else ""),
            "Agent Response": answer,
            "Expected Response": case["expected_response"],
            "Actual Route": actual_route,
            "Completeness Evaluation": _verdict(verdicts["completeness"]),
            "Action Evaluation": _verdict(verdicts["action"]),
            "Route Evaluation": _verdict(verdicts["route"]),
            "Latency Evaluation": _verdict(verdicts["latency"]),
            "Coherence Evaluation": _verdict(verdicts["coherence"]),
            "Actual Actions": ", ".join(actual_actions) or "(none)",
            "Conciseness Evaluation": _verdict(verdicts["conciseness"]),
            "Response Evaluation": _verdict(verdicts["response"]),
            "Completeness Evaluation Score": int(verdicts["completeness"]),
            "Completeness Evaluation Reasoning": qual["completeness"]["reason"],
            "Action Evaluation Score": int(verdicts["action"]),
            "Action Evaluation Reasoning": action_reason,
            "Route Evaluation Score": int(verdicts["route"]),
            "Route Evaluation Reasoning": route_reason,
            "Latency Evaluation Score": int(verdicts["latency"]),
            "Latency Evaluation Reasoning": latency_reason,
            "Coherence Evaluation Score": int(verdicts["coherence"]),
            "Coherence Evaluation Reasoning": qual["coherence"]["reason"],
            "Conciseness Evaluation Score": int(verdicts["conciseness"]),
            "Conciseness Evaluation Reasoning": qual["conciseness"]["reason"],
            "Response Evaluation Score": int(verdicts["response"]),
            "Response Evaluation Reasoning": qual["response"]["reason"],
            "Cost Evaluation": _verdict(verdicts["cost"]),
            "Cost Evaluation Score": int(verdicts["cost"]),
            "Cost Evaluation Reasoning": cost_reason,
            "Latency (ms)": f"{elapsed_ms:.0f}",
            "Cost (USD)": f"{cost_usd:.6f}",
            "LLM Tokens": llm_tokens,
            "LLM Calls": llm_calls,
            "Intent Source": intent_source,
            "Outcome": outcome,
            "Judge": judge_used,
            "Warnings": "; ".join(warnings),
        }
        rows.append(row)

        passed_count = sum(verdicts.values())
        flag = "ok " if passed_count == len(ALL_METRICS) else "!! "
        print(f"  [{idx:>2}/{len(cases)}] {flag}{case['id']:<32} {passed_count}/{len(ALL_METRICS)} pass "
              f"| route={actual_route} | {elapsed_ms:.0f}ms")

        if args.sleep:
            time.sleep(args.sleep)

    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    with REPORT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)
    write_summary(total, metric_pass, use_judge, args, judge_llm_rows, intent_llm_turns)

    print(f"\nWrote {total} rows to {REPORT_CSV.relative_to(ROOT)}")
    print(f"Wrote summary to {SUMMARY_MD.relative_to(ROOT)}\n")
    print(f"LLM intent routing actually used on {intent_llm_turns}/{total} turns "
          f"(rest fell back to rules).")
    print(f"LLM judge actually used on {judge_llm_rows}/{total} rows "
          f"(rest used heuristics).")
    if judge_llm_rows == 0 or intent_llm_turns == 0:
        print("  NOTE: provider calls did not succeed in this environment; numbers reflect the "
              "deterministic/heuristic fallback path. Run locally with reachable provider keys "
              "for the true LLM-as-judge report.")
    print("\nPass rates by dimension:")
    for metric in ALL_METRICS:
        rate = (metric_pass[metric] / total * 100) if total else 0.0
        print(f"  {metric:<13} {metric_pass[metric]:>2}/{total}  ({rate:5.1f}%)")
    overall = sum(metric_pass.values())
    denom = total * len(ALL_METRICS)
    print(f"\nOverall cell pass rate: {overall}/{denom} ({(overall / denom * 100) if denom else 0:.1f}%)")


def write_summary(total: int, metric_pass: dict[str, int], use_judge: bool, args: argparse.Namespace,
                  judge_llm_rows: int, intent_llm_turns: int) -> None:
    judge_label = (
        f"LLM-as-judge on {judge_llm_rows}/{total} rows"
        if judge_llm_rows else "heuristic fallback (no provider calls succeeded)"
    )
    lines = [
        "# BrandAssist AI - Evaluation Summary",
        "",
        f"- Cases: **{total}**",
        f"- Runtime mode: `{args.runtime}` | Retriever: `{args.retriever}` | LangGraph: `{args.graph}`",
        f"- Qualitative judge: **{judge_label}**",
        f"- LLM intent routing used on **{intent_llm_turns}/{total}** turns (rest = rule fallback)",
        f"- Latency budget: {args.latency_budget_ms:.0f} ms/turn",
        f"- Scale: PASS / FAIL (1 = pass, 0 = fail)",
        "",
    ]
    if judge_llm_rows == 0 or intent_llm_turns == 0:
        lines += [
            "> **Note:** provider API calls did not succeed in the environment that generated this "
            "report, so the scores reflect the deterministic agent + heuristic judge fallback. "
            "Re-run with reachable provider keys for the true LLM-as-judge results.",
            "",
        ]
    lines += [
        "## Pass rate by dimension",
        "",
        "| Dimension | Type | Pass | Rate |",
        "| --- | --- | --- | --- |",
    ]
    kind = {
        "completeness": "LLM judge", "coherence": "LLM judge",
        "conciseness": "LLM judge", "response": "LLM judge",
        "action": "deterministic", "route": "deterministic", "latency": "deterministic",
        "cost": "deterministic",
    }
    for metric in ALL_METRICS:
        rate = (metric_pass[metric] / total * 100) if total else 0.0
        lines.append(f"| {metric.title()} | {kind[metric]} | {metric_pass[metric]}/{total} | {rate:.1f}% |")
    overall = sum(metric_pass.values())
    denom = total * len(ALL_METRICS)
    lines += [
        "",
        f"**Overall cell pass rate:** {overall}/{denom} ({(overall / denom * 100) if denom else 0:.1f}%)",
        "",
        f"Full per-case detail: [`eval_report.csv`](eval_report.csv)",
        "",
    ]
    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    run()
