from __future__ import annotations

from src.brandassist_ai import SupportAgent


def test_general_support_without_product_context_clarifies() -> None:
    agent = SupportAgent()
    response = agent.run("Can you help me fix this?")

    assert response.trace.intent in {"general_support", "troubleshooting"}
    assert response.trace.outcome == "clarify"
    # Clarification must NOT create a ticket / escalate.
    assert not response.trace.escalated
    assert not any(call.name == "create_ticket" for call in response.trace.tool_calls)
    assert "product name/model" in response.answer.lower()
