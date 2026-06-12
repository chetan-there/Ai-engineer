from __future__ import annotations

from src.brandassist_ai import SupportAgent


def test_warranty_registration_success() -> None:
    agent = SupportAgent()
    response = agent.run(
        "Please register warranty for this microchef product. customer CUST-001 serial SEAL-12345",
        image_id="microchef-front",
    )
    assert response.trace.outcome == "resolved"
    assert any(call.name == "register_warranty" for call in response.trace.tool_calls)
    assert "Warranty registered successfully" in response.answer


def test_warranty_registration_requires_serial() -> None:
    agent = SupportAgent()
    response = agent.run(
        "Register warranty for this product customer CUST-001",
        image_id="microchef-front",
    )
    assert response.trace.outcome == "clarify"
    assert not response.trace.escalated
