from __future__ import annotations

from src.brandassist_ai import SupportAgent
from src.brandassist_ai.data_loader import load_golden_cases
from src.brandassist_ai.metrics import summarize_runs


def test_metrics_summary_has_expected_fields() -> None:
    agent = SupportAgent()
    cases = load_golden_cases()
    runs = [agent.run(case["message"], image_id=case["image_id"]) for case in cases]

    metrics = summarize_runs(runs, cases)

    assert metrics["total_cases"] == len(cases)
    assert 0 <= metrics["resolution_rate"] <= 1
    assert 0 <= metrics["escalation_rate"] <= 1
    assert 0 <= metrics["visual_id_accuracy"] <= 1
    assert metrics["resolution_rate"] >= 0.3
