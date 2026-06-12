from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    category: str
    aliases: list[str]
    tags: list[str]


@dataclass(frozen=True)
class KnowledgeDoc:
    id: str
    product_id: str | None
    kind: str
    title: str
    text: str


@dataclass(frozen=True)
class Order:
    order_id: str
    product_id: str
    status: str
    delivery_eta: str
    purchase_date: str
    customer_id: str | None = None


@dataclass(frozen=True)
class WarrantyRule:
    product_id: str
    months: int
    requires_order: bool


@dataclass(frozen=True)
class WarrantyRegistration:
    registration_id: str
    customer_id: str
    product_id: str
    serial_number: str
    order_id: str | None
    registered_at: str
    warranty_start_date: str
    warranty_end_date: str
    status: str


@dataclass(frozen=True)
class ImageLabel:
    image_id: str
    source_url: str
    product_id: str | None
    category: str
    quality: str
    observations: list[str]


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any]
    result: dict[str, Any]


@dataclass
class AgentTrace:
    intent: str
    intent_source: str = "rule"
    product_id: str | None = None
    image_confidence: float = 0.0
    image_observations: list[str] = field(default_factory=list)
    retrieved_doc_ids: list[str] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    escalated: bool = False
    outcome: str = "unresolved"
    warnings: list[str] = field(default_factory=list)
    # Cost/usage accounting for the LLM calls made during this turn.
    llm_calls: int = 0
    llm_prompt_tokens: int = 0
    llm_completion_tokens: int = 0
    llm_cost_usd: float = 0.0


@dataclass
class AgentResponse:
    answer: str
    trace: AgentTrace
