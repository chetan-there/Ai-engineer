from __future__ import annotations

from .models import AgentResponse


def summarize_runs(runs: list[AgentResponse], golden_cases: list[dict] | None = None) -> dict:
    total = len(runs)
    if total == 0:
        return {
            "total_cases": 0,
            "resolution_rate": 0.0,
            "escalation_rate": 0.0,
            "visual_id_accuracy": 0.0,
            "estimated_backlog_reduction": 0.0,
        }

    resolved = sum(run.trace.outcome == "resolved" for run in runs)
    escalated = sum(run.trace.escalated for run in runs)
    visual_accuracy = 0.0

    if golden_cases:
        visual_cases = [
            (run, case)
            for run, case in zip(runs, golden_cases)
            if case.get("image_id") and case.get("expected_product_id")
        ]
        if visual_cases:
            correct = sum(
                run.trace.product_id == case["expected_product_id"]
                for run, case in visual_cases
            )
            visual_accuracy = correct / len(visual_cases)

    resolution_rate = resolved / total
    escalation_rate = escalated / total
    return {
        "total_cases": total,
        "resolution_rate": resolution_rate,
        "escalation_rate": escalation_rate,
        "visual_id_accuracy": visual_accuracy,
        "first_contact_resolution_proxy": resolution_rate,
        "estimated_backlog_reduction": min(resolution_rate, 0.5),
    }
