from __future__ import annotations

import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from .data_loader import (
    load_image_labels,
    load_knowledge_docs,
    load_orders,
    load_products,
    load_warranty_registrations,
    load_warranties,
)
from .llm_router import LLMRouter
from .models import AgentResponse, AgentTrace, ToolCall
from .pii import contains_pii, redact_pii
from .retrieval import ChromaRetriever, HybridRetriever, LexicalRetriever, Retriever
from .tools import SupportTools
from .vision import ImageTriage


ORDER_RE = re.compile(r"#?([A-Z]\d{4})", re.IGNORECASE)
SERIAL_RE = re.compile(r"serial[:\s#-]*([A-Z]{2,5}-[A-Z0-9]{4,10})", re.IGNORECASE)
CUSTOMER_RE = re.compile(r"(?:customer|user)[:\s#-]*([A-Z0-9-]{4,20})|\b(CUST-\d{3,})\b", re.IGNORECASE)


class SupportAgent:
    def __init__(
        self,
        runtime_mode: str = "deterministic",
        retriever_mode: str = "lexical",
        llm_model: str = "gpt-4o-mini",
    ) -> None:
        self.products = load_products()
        self.docs = load_knowledge_docs()
        self.tools = SupportTools(
            self.products,
            load_orders(),
            load_warranties(),
            registrations=load_warranty_registrations(),
        )
        self.runtime_mode = runtime_mode
        self.retriever_mode = retriever_mode
        self.llm_model = llm_model
        self.retriever: Retriever = self._build_retriever(retriever_mode)
        self.llm_router = LLMRouter(default_model=llm_model)
        self.vision = ImageTriage(load_image_labels(), router=self.llm_router)
        self._graph_runner = None

    def run(
        self,
        message: str,
        image_id: str | None = None,
        use_graph: bool = False,
        history: list[dict] | None = None,
        image_bytes: bytes | None = None,
        image_mime: str | None = None,
    ) -> AgentResponse:
        before = self.llm_router.snapshot_usage()
        if use_graph:
            if self._graph_runner is None:
                from .orchestration import GraphOrchestrator

                self._graph_runner = GraphOrchestrator(self)
            response = self._graph_runner.run(
                message=message,
                image_id=image_id,
                history=history,
                image_bytes=image_bytes,
                image_mime=image_mime,
            )
        else:
            response = self._run_core(message, image_id, history, image_bytes, image_mime)
        delta = self.llm_router.usage_delta(before, self.llm_router.snapshot_usage())
        response.trace.llm_calls = delta["calls"]
        response.trace.llm_prompt_tokens = delta["prompt_tokens"]
        response.trace.llm_completion_tokens = delta["completion_tokens"]
        response.trace.llm_cost_usd = round(delta["cost_usd"], 6)
        return response

    def opening_greeting(self, timezone_name: str = "Asia/Kolkata") -> AgentResponse:
        trace = AgentTrace(intent="general_support", intent_source="llm:autogreet")
        now = datetime.now(ZoneInfo(timezone_name))
        if self.llm_router.is_enabled():
            try:
                text = self.llm_router.complete(
                    system_prompt=(
                        "You are a friendly customer support assistant. "
                        "Write a short greeting based on local time and mention what support help is available "
                        "(order status, warranty, returns, troubleshooting). "
                        "Keep it concise and natural."
                    ),
                    user_prompt=(
                        f"Timezone: {timezone_name}\n"
                        f"Local datetime: {now.isoformat()}\n"
                        f"Hour: {now.hour}"
                    ),
                ).strip()
                if text:
                    trace.warnings = []
                    trace.outcome = "resolved"
                    provider = self.llm_router.last_provider or "unknown"
                    trace.intent_source = f"llm:{provider}"
                    return AgentResponse(text, trace)
            except Exception:
                trace.warnings.append("LLM greeting generation failed; fallback greeting used.")

        # Safe fallback if provider is unavailable.
        part = "Good morning" if 5 <= now.hour < 12 else "Good afternoon" if 12 <= now.hour < 18 else "Good evening"
        trace.intent_source = "rule_fallback"
        trace.outcome = "resolved"
        return AgentResponse(
            f"{part}! I can help with order status, warranty check/registration, returns, and troubleshooting. How can I assist you today?",
            trace,
        )

    def _run_core(
        self,
        message: str,
        image_id: str | None = None,
        history: list[dict] | None = None,
        image_bytes: bytes | None = None,
        image_mime: str | None = None,
    ) -> AgentResponse:
        history = history or []
        if self._is_greeting(message):
            trace = AgentTrace(intent="general_support", intent_source="rule")
            trace.outcome = "resolved"
            return AgentResponse(
                "Hello! I can help with order status, warranty check, warranty registration, returns, and troubleshooting. What would you like to do?",
                trace,
            )

        # A message that is only an identifier (order/customer/serial) carries no intent on
        # its own. Inherit the intent from a pending clarification turn when one exists,
        # otherwise ask what the user wants instead of guessing.
        pending_intent = self._pending_clarify_intent(history)
        if self._is_bare_reference(message):
            if pending_intent:
                intent, intent_source = pending_intent, "context_inherited"
            else:
                trace = AgentTrace(intent="ambiguous", intent_source="rule")
                ref = (
                    self._extract_order_id(message)
                    or self._extract_customer_id(message)
                    or self._extract_serial(message)
                )
                return self._clarify(
                    trace,
                    f"I see reference {ref}, but I'm not sure what you need with it. "
                    "Would you like order status, a warranty check, troubleshooting, or a return?",
                    product_id=None,
                )
        else:
            intent, intent_source = self._detect_intent_with_mode(message, history)
        trace = AgentTrace(intent=intent, intent_source=intent_source)
        if self.runtime_mode == "llm" and self.llm_router.is_enabled() and contains_pii(message):
            trace.warnings.append("Detected PII in user input; redacted before sending to any LLM provider.")
        order_id = self._extract_order_id(message)
        customer_id = self._extract_customer_id(message)
        has_image = bool(image_bytes) or bool(image_id)
        if image_bytes:
            image = self.vision.identify_from_bytes(image_bytes, image_mime or "image/png")
        else:
            image = self.vision.inspect(image_id)
        trace.image_confidence = image["confidence"]
        trace.image_observations = image["observations"]

        product_id = image["product_id"]
        if product_id and product_id not in self.tools.products:
            trace.warnings.append(
                f"Image suggested product_id '{product_id}' not found in current catalog; ignoring image product hint."
            )
            product_id = None
        if has_image and not image["supported"]:
            return self._escalate(
                trace,
                "I could not confidently match this image to a supported BrandAssist product. Please upload a clearer photo of the model label or wait for a support specialist.",
                product_id=None,
                summary="Unsupported or unclear product image.",
                outcome="unsupported" if image["quality"] != "blurry" else "clarify",
            )

        if has_image and image["confidence"] < 0.4:
            return self._escalate(
                trace,
                "The image is too unclear for reliable product identification. Please send a clearer photo of the product front or model label.",
                product_id=None,
                summary="Low-confidence visual identification.",
                outcome="clarify",
            )

        if not product_id and order_id:
            order_result = self.tools.order_lookup(order_id)
            trace.tool_calls.append(ToolCall("order_lookup", {"order_id": order_id}, order_result))
            product_id = order_result.get("product_id") if order_result.get("found") else None

        if product_id or intent not in {"return_policy", "order_status"}:
            product_result = self.tools.product_lookup(product_id=product_id, query=message)
            if product_result["found"]:
                product_id = product_result["product_id"]
                trace.product_id = product_id
                trace.tool_calls.append(
                    ToolCall("product_lookup", {"product_id": product_id, "query": message}, product_result)
                )

        if intent == "order_status":
            if not order_id:
                if customer_id:
                    by_customer = self.tools.orders_by_customer_lookup(customer_id)
                    trace.tool_calls.append(
                        ToolCall("orders_by_customer_lookup", {"customer_id": customer_id}, by_customer)
                    )
                    if by_customer.get("found"):
                        orders = by_customer["orders"]
                        lines = [
                            f"- {o['order_id']}: {o['product_id']} ({o['status']}, ETA {o['delivery_eta']})"
                            for o in orders
                        ]
                        trace.outcome = "resolved"
                        return AgentResponse(
                            "I found your recent orders:\n"
                            + "\n".join(lines)
                            + "\nPlease share the order ID you want details for.",
                            trace,
                        )
                return self._clarify(trace, "Please provide your order ID so I can check the status.", product_id)
            if not any(call.name == "order_lookup" for call in trace.tool_calls):
                order_result = self.tools.order_lookup(order_id)
                trace.tool_calls.append(ToolCall("order_lookup", {"order_id": order_id}, order_result))
            order_call = next((call for call in reversed(trace.tool_calls) if call.name == "order_lookup"), None)
            result = order_call.result if order_call else {"found": False}
            if result.get("found"):
                trace.product_id = result["product_id"]
                trace.outcome = "resolved"
                return AgentResponse(
                    f"Order {result['order_id']} is {result['status']}. Estimated delivery: {result['delivery_eta']}.",
                    trace,
                )
            return self._escalate(trace, "I could not find that order. I created a support ticket for follow-up.", product_id, "Order not found.", "escalated")

        if intent in {"general_support", "troubleshooting", "setup"} and not product_id and not order_id:
            return self._clarify(
                trace,
                "Please share the product name/model (or an order ID or image) so I can provide accurate troubleshooting steps.",
                product_id=None,
            )

        if intent == "warranty_registration":
            serial = self._extract_serial(message)
            customer_id = self._extract_customer_id(message) or "demo-user-001"
            if not product_id:
                return self._clarify(
                    trace,
                    "I could not identify the product to register. Please share the product model and serial number.",
                    product_id=None,
                )
            if not serial:
                return self._clarify(
                    trace,
                    "Please provide the device serial number in a format like ACME-12345 to register warranty.",
                    product_id=product_id,
                )
            registration = self.tools.register_warranty(
                customer_id=customer_id,
                product_id=product_id,
                serial_number=serial,
                order_id=order_id,
            )
            trace.tool_calls.append(
                ToolCall(
                    "register_warranty",
                    {"customer_id": customer_id, "product_id": product_id, "serial_number": serial, "order_id": order_id},
                    registration,
                )
            )
            if registration.get("registered"):
                trace.outcome = "resolved"
                return AgentResponse(
                    (
                        f"Warranty registered successfully with ID {registration['registration_id']}. "
                        f"Coverage is active until {registration['warranty_end_date']}."
                    ),
                    trace,
                )
            return self._escalate(
                trace,
                f"I could not register warranty automatically: {registration.get('reason', 'unknown reason')}.",
                product_id=product_id,
                summary="Warranty registration needs specialist review.",
                outcome="clarify",
            )

        retrieval_query = self._retrieval_query(message, image)
        if intent == "warranty":
            # Include policy-oriented keywords so global warranty policy docs are ranked.
            retrieval_query = f"{retrieval_query} warranty policy coverage defect"
        docs = self.retriever.search(retrieval_query, product_id=product_id, top_k=5 if intent == "warranty" else 3)
        trace.retrieved_doc_ids = [doc.id for doc in docs]

        if intent == "warranty":
            if order_id and not any(call.name == "order_lookup" for call in trace.tool_calls):
                order_result = self.tools.order_lookup(order_id)
                trace.tool_calls.append(ToolCall("order_lookup", {"order_id": order_id}, order_result))
                product_id = product_id or order_result.get("product_id")
                trace.product_id = product_id
            if product_id:
                warranty = self.tools.warranty_check(product_id, order_id=order_id)
                trace.tool_calls.append(ToolCall("warranty_check", {"product_id": product_id, "order_id": order_id}, warranty))
                trace.outcome = "resolved"
                return AgentResponse(
                    self._compose_answer("warranty", docs, trace, extra=warranty["reason"]),
                    trace,
                )

        if self._is_failed_fix(message) or self._is_misleading_claim(message, image):
            summary = "Customer needs specialist review after failed or visually uncertain troubleshooting."
            return self._escalate(
                trace,
                self._compose_answer("escalation", docs, trace, extra="I am escalating this with the image observations and attempted steps."),
                product_id,
                summary,
                "escalated",
            )

        trace.outcome = "resolved"
        response = AgentResponse(self._compose_answer(intent, docs, trace), trace)
        return self._polish_answer_with_mode(message, response)

    def _build_retriever(self, retriever_mode: str) -> Retriever:
        if retriever_mode == "chroma":
            return ChromaRetriever(self.docs)
        if retriever_mode == "hybrid":
            return HybridRetriever(self.docs)
        return LexicalRetriever(self.docs)

    def _detect_intent_with_mode(self, message: str, history: list[dict] | None = None) -> tuple[str, str]:
        if self.runtime_mode != "llm":
            return self._detect_intent(message), "rule"
        llm_intent = self._detect_intent_via_llm(message, history)
        if llm_intent:
            provider = self.llm_router.last_provider or "unknown"
            return llm_intent, f"llm:{provider}"
        return self._detect_intent(message), "rule_fallback"

    def _detect_intent_via_llm(self, message: str, history: list[dict] | None = None) -> str | None:
        if not self.llm_router.is_enabled():
            return None
        safe_message, _ = redact_pii(message)
        user_prompt = safe_message
        if history:
            recent = history[-4:]
            convo = "\n".join(
                f"{turn.get('role', 'user')}: {redact_pii(turn.get('content', ''))[0]}" for turn in recent
            )
            user_prompt = f"Conversation so far:\n{convo}\n\nLatest user message: {safe_message}"
        try:
            text = self.llm_router.complete(
                system_prompt=(
                    "Classify the support intent of the LATEST user message, using prior conversation "
                    "context when provided. You MUST choose exactly one label from this closed set and "
                    "never invent a new one:\n"
                    "- order_status: where is my order, track order, delivery status, a bare order/customer ID.\n"
                    "- warranty: is it covered, warranty claim, broke/defective and asking about coverage.\n"
                    "- warranty_registration: register/activate/enroll a product's warranty (even if the word "
                    "'warranty' appears, registering maps here, not warranty).\n"
                    "- return_policy: returns, refunds, return window.\n"
                    "- setup: how to set up / install / configure / first-time use.\n"
                    "- troubleshooting: device not working, won't heat/cool/turn on, leaking, error code, "
                    "no suction, dropping wifi, fix/repair help.\n"
                    "- general_support: greetings, capability questions, or anything that fits none above.\n"
                    "Map synonyms to the closest label; do NOT output words like 'installation', 'leak', "
                    "'not_working', or 'product_issue'. Respond with compact JSON only: "
                    '{"intent":"one_of(order_status,warranty,warranty_registration,return_policy,setup,troubleshooting,general_support)"}'
                ),
                user_prompt=user_prompt,
            )
            payload = self._extract_json(text)
            intent = payload.get("intent")
            if intent in {"order_status", "warranty", "warranty_registration", "return_policy", "setup", "troubleshooting", "general_support"}:
                return intent
        except Exception:
            return None
        return None

    @staticmethod
    def _extract_json(text: str) -> dict:
        """Tolerant parse of a JSON object from a possibly fenced/prosey model reply."""
        cleaned = (text or "").strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*", "", cleaned).strip().rstrip("`").strip()
        try:
            return json.loads(cleaned)
        except Exception:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise

    def _polish_answer_with_mode(self, message: str, response: AgentResponse) -> AgentResponse:
        if self.runtime_mode != "llm":
            return response
        if not self.llm_router.is_enabled():
            response.trace.warnings.append("LLM mode selected but no provider API key configured; deterministic response used.")
            return response
        safe_message, _ = redact_pii(message)
        try:
            text = self.llm_router.complete(
                system_prompt=(
                    "Rewrite the grounded answer for clarity. Keep factual content unchanged. "
                    "Do not add unsupported claims or approvals."
                ),
                user_prompt=(
                    f"Customer message: {safe_message}\n"
                    f"Grounded answer: {response.answer}\n"
                    f"Retrieved docs: {response.trace.retrieved_doc_ids}\n"
                    f"Tools used: {[call.name for call in response.trace.tool_calls]}"
                ),
            )
            if text.strip():
                return AgentResponse(text.strip(), response.trace)
        except Exception:
            response.trace.warnings.append("LLM rewrite failed; deterministic response used.")
        return response

    def _detect_intent(self, message: str) -> str:
        text = message.lower()
        if "ignore all rules" in text:
            text = text.replace("ignore all rules", "")
        order_terms = ("where is order", "order #", "my order", "my orders", "order status")
        has_customer_ref = bool(CUSTOMER_RE.search(message))
        if any(term in text for term in order_terms) or re.search(ORDER_RE, text) or (has_customer_ref and "order" in text):
            if "warranty" not in text and "broke" not in text:
                return "order_status"
        if "register warranty" in text or "warranty registration" in text:
            return "warranty_registration"
        if "warranty" in text or "broke" in text or "broken" in text:
            return "warranty"
        if "return" in text:
            return "return_policy"
        if "set up" in text or "setting this up" in text or "setup" in text:
            return "setup"
        if "seal" in text or "fix" in text or "failed" in text or "troubleshoot" in text:
            return "troubleshooting"
        return "general_support"

    def _pending_clarify_intent(self, history: list[dict]) -> str | None:
        """Intent of the most recent assistant turn that asked for more info."""
        for turn in reversed(history):
            if turn.get("role") == "assistant":
                if turn.get("outcome") == "clarify":
                    intent = turn.get("intent")
                    return intent if intent and intent != "ambiguous" else None
                return None
        return None

    def _is_bare_reference(self, message: str) -> bool:
        """True when the message is essentially just an order/customer/serial reference."""
        stripped = message.strip()
        if not (self._extract_order_id(stripped) or self._extract_customer_id(stripped) or self._extract_serial(stripped)):
            return False
        residual = stripped
        for pattern in (SERIAL_RE, CUSTOMER_RE, ORDER_RE):
            residual = pattern.sub(" ", residual)
        residual = re.sub(r"[^a-zA-Z]", " ", residual)
        stopwords = {"my", "the", "is", "for", "order", "id", "number", "this", "it", "customer", "user"}
        words = [word for word in residual.lower().split() if word not in stopwords]
        return len(words) == 0

    def _extract_order_id(self, message: str) -> str | None:
        match = ORDER_RE.search(message)
        return match.group(1).upper() if match else None

    def _retrieval_query(self, message: str, image: dict) -> str:
        observations = " ".join(image.get("observations", []))
        return f"{message} {observations}"

    def _extract_serial(self, message: str) -> str | None:
        match = SERIAL_RE.search(message)
        return match.group(1).upper() if match else None

    def _extract_customer_id(self, message: str) -> str | None:
        match = CUSTOMER_RE.search(message)
        if not match:
            return None
        return (match.group(1) or match.group(2) or "").upper() or None

    def _compose_answer(self, intent: str, docs: list, trace: AgentTrace, extra: str | None = None) -> str:
        if not docs:
            base = "I do not have enough grounded product documentation to answer confidently."
        else:
            doc = docs[0]
            base = f"Based on {doc.title}: {doc.text}"
        if trace.image_observations:
            base += " Image observations: " + "; ".join(trace.image_observations) + "."
        if extra:
            base += f" {extra}"
        if intent == "return_policy":
            base += " Keep proof of purchase available for the support team."
        return base

    def _escalate(
        self,
        trace: AgentTrace,
        answer: str,
        product_id: str | None,
        summary: str,
        outcome: str,
    ) -> AgentResponse:
        ticket = self.tools.create_ticket(summary=summary, product_id=product_id)
        trace.tool_calls.append(ToolCall("create_ticket", {"summary": summary, "product_id": product_id}, ticket))
        trace.product_id = product_id
        trace.escalated = True
        trace.outcome = outcome
        return AgentResponse(f"{answer} Ticket {ticket['ticket_id']} has been opened.", trace)

    def _clarify(self, trace: AgentTrace, answer: str, product_id: str | None) -> AgentResponse:
        trace.product_id = product_id
        trace.escalated = False
        trace.outcome = "clarify"
        return AgentResponse(answer, trace)

    def _is_failed_fix(self, message: str) -> bool:
        text = message.lower()
        return "still failed" in text or "did not work" in text or "didn't work" in text

    def _is_misleading_claim(self, message: str, image: dict) -> bool:
        text = message.lower()
        observations = " ".join(image.get("observations", [])).lower()
        return ("clearly" in text or "replace it now" in text) and "cannot be confirmed" in observations

    def _is_greeting(self, message: str) -> bool:
        text = message.strip().lower()
        greeting_tokens = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}
        return text in greeting_tokens or any(text.startswith(f"{token} ") for token in greeting_tokens)
