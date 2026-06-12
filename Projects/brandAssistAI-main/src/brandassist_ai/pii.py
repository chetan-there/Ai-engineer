"""
Lightweight PII redaction for outbound LLM prompts.

The structured data in this project is synthetic and pseudonymized, but a real
customer can still type sensitive personal data into the chat box (email, phone,
card number). Before any free-text reaches an external LLM provider we scrub the
obvious direct identifiers and replace them with typed placeholders.

Pseudonymous business identifiers - order IDs (A2002), customer IDs (CUST-077),
and device serials (ACME-12345) - are deliberately preserved, because the agent
needs them to call tools and they carry no standalone personal information.
"""

from __future__ import annotations

import re

# Order matters: redact the most specific / longest patterns first so a phone
# pattern does not partially consume a card number, etc.
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("EMAIL", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("SSN", re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")),
    ("CARD", re.compile(r"(?<!\d)(?:\d[ -]?){13,16}(?!\d)")),
    ("PHONE", re.compile(r"(?<!\d)\+?\d(?:[\d\-\s().]{7,})\d(?!\d)")),
]


def redact_pii(text: str) -> tuple[str, list[str]]:
    """Return (redacted_text, sorted list of redacted PII types found)."""
    if not text:
        return text, []
    found: set[str] = set()
    redacted = text
    for label, pattern in _PATTERNS:
        if pattern.search(redacted):
            found.add(label)
            redacted = pattern.sub(f"[REDACTED_{label}]", redacted)
    return redacted, sorted(found)


def contains_pii(text: str) -> bool:
    _, found = redact_pii(text)
    return bool(found)
