# Safety Model

## Safety Objective

Prevent unsafe or overconfident assistance by constraining autonomy and escalating
ambiguous/high-risk cases.

## Guardrails Implemented

- **Confidence gate on image triage**
  - Unsupported or low-confidence visual IDs trigger clarification/escalation.
- **Bounded tool authority**
  - Agent can look up product/order/warranty info and create tickets.
  - Agent cannot auto-approve refunds, replacements, or warranty claims.
- **Prompt injection resistance**
  - "Ignore all rules" language does not grant expanded privileges.
  - Flow remains grounded in tools + policy retrieval.
- **Escalation policy**
  - Failed troubleshooting loops and uncertain visual claims escalate to human support.
- **Low-information input guard**
  - A bare identifier (e.g. a lone order ID) with no request triggers a clarification
    question instead of an assumed intent, preventing confident off-target answers.
  - Clarifications never open a support ticket.

## PII Handling

Two layers protect personal data:

- **Avoidance by design.** All structured data is synthetic and pseudonymized
  (fictional products, customers, orders) and the knowledge base is original, so the
  repository and database contain no real personal data.
- **Outbound redaction at the LLM boundary.** Free-text a user types can still contain
  PII, so `src/brandassist_ai/pii.py` scrubs direct identifiers - email addresses, phone
  numbers, card numbers, and SSNs - and replaces them with typed placeholders
  (`[REDACTED_EMAIL]`, etc.) before any text is sent to an external LLM provider
  (intent classification and response rewriting). When redaction fires, the run trace
  records a warning so it is visible in the demo.

Pseudonymous business identifiers (order IDs, customer IDs, device serials) are
deliberately preserved: the agent needs them to call tools and they carry no
standalone personal information. Redaction is covered by `tests/test_pii_redaction.py`.

## Threat Model (POC)

- Prompt injection attempts
- Visual misclassification and low-image-quality ambiguity
- Missing order IDs or unverifiable claims
- Retrieval misses leading to unsupported advice

## Residual Risks

- LLM rewrite mode could introduce style drift; mitigated by deterministic fallback.
- No human-in-the-loop approval UI for sensitive actions yet.
- No policy versioning and signed audit logs yet.
