from __future__ import annotations

from src.brandassist_ai.pii import contains_pii, redact_pii


def test_redacts_email():
    redacted, found = redact_pii("Contact me at jane.doe@example.com please")
    assert "jane.doe@example.com" not in redacted
    assert "[REDACTED_EMAIL]" in redacted
    assert found == ["EMAIL"]


def test_redacts_phone_and_card():
    redacted, found = redact_pii("Call 415-555-0199, card 4111 1111 1111 1111")
    assert "415-555-0199" not in redacted
    assert "4111 1111 1111 1111" not in redacted
    assert "CARD" in found and "PHONE" in found


def test_preserves_business_identifiers():
    text = "Order A2002 for customer CUST-077, serial ACME-12345"
    redacted, found = redact_pii(text)
    assert redacted == text
    assert found == []


def test_contains_pii_helper():
    assert contains_pii("email: a@b.co")
    assert not contains_pii("just a normal question about my microwave")


def test_empty_input_is_safe():
    assert redact_pii("") == ("", [])
