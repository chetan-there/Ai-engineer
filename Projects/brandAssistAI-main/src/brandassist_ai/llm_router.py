from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    api_key_env: str
    base_url: str | None
    model_env: str | None


@dataclass(frozen=True)
class VisionProviderConfig:
    name: str
    api_key_env: str
    base_url: str | None
    model_env: str
    default_model: str


# Representative USD pricing per 1K tokens (input, output), matched by substring.
# Free-tier models are priced at the published list rate so the cost estimate is
# meaningful even when the demo itself runs for free.
_PRICE_PER_1K: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.00015, 0.00060),
    "gpt-4o": (0.0025, 0.010),
    "llama-3.1-8b": (0.00005, 0.00008),
    "llama-3.3-70b": (0.00059, 0.00079),
    "llama-4-scout": (0.00011, 0.00034),
    "llama-3.2-11b": (0.00005, 0.00008),
    "qwen": (0.00020, 0.00020),
}
_DEFAULT_PRICE = (0.00010, 0.00020)


def _price_for(model: str) -> tuple[float, float]:
    name = (model or "").lower()
    for key, price in _PRICE_PER_1K.items():
        if key in name:
            return price
    return _DEFAULT_PRICE


class LLMRouter:
    """
    OpenAI-compatible multi-provider router for free-tier resilience.

    Default order: groq -> openrouter -> huggingface -> openai.
    """

    def __init__(self, default_model: str = "gpt-4o-mini") -> None:
        self.default_model = default_model
        self.last_provider: str | None = None
        self.last_model: str | None = None
        # Cumulative usage across all calls on this router instance.
        self.usage = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0}
        self.providers = [
            ProviderConfig("groq", "GROQ_API_KEY", "https://api.groq.com/openai/v1", "GROQ_MODEL"),
            ProviderConfig("openrouter", "OPENROUTER_API_KEY", "https://openrouter.ai/api/v1", "OPENROUTER_MODEL"),
            ProviderConfig("huggingface", "HF_API_KEY", "https://router.huggingface.co/v1", "HF_MODEL"),
            ProviderConfig("openai", "OPENAI_API_KEY", None, "OPENAI_MODEL"),
        ]
        # Vision-capable (multimodal) providers, tried in order.
        self.vision_providers = [
            VisionProviderConfig(
                "groq",
                "GROQ_API_KEY",
                "https://api.groq.com/openai/v1",
                "GROQ_VISION_MODEL",
                "meta-llama/llama-4-scout-17b-16e-instruct",
            ),
            VisionProviderConfig(
                "openrouter",
                "OPENROUTER_API_KEY",
                "https://openrouter.ai/api/v1",
                "OPENROUTER_VISION_MODEL",
                "meta-llama/llama-3.2-11b-vision-instruct:free",
            ),
            VisionProviderConfig(
                "openai",
                "OPENAI_API_KEY",
                None,
                "OPENAI_VISION_MODEL",
                "gpt-4o-mini",
            ),
        ]

    def snapshot_usage(self) -> dict:
        return dict(self.usage)

    @staticmethod
    def usage_delta(before: dict, after: dict) -> dict:
        return {key: after.get(key, 0) - before.get(key, 0) for key in after}

    def _record_usage(self, model: str, usage_obj) -> None:
        if usage_obj is None:
            return
        prompt = (
            getattr(usage_obj, "prompt_tokens", None)
            or getattr(usage_obj, "input_tokens", None)
            or 0
        )
        completion = (
            getattr(usage_obj, "completion_tokens", None)
            or getattr(usage_obj, "output_tokens", None)
            or 0
        )
        rate_in, rate_out = _price_for(model)
        cost = (prompt / 1000.0) * rate_in + (completion / 1000.0) * rate_out
        self.usage["calls"] += 1
        self.usage["prompt_tokens"] += int(prompt)
        self.usage["completion_tokens"] += int(completion)
        self.usage["cost_usd"] += cost

    def is_enabled(self) -> bool:
        return any(os.getenv(provider.api_key_env) for provider in self.providers)

    def is_vision_enabled(self) -> bool:
        return any(os.getenv(provider.api_key_env) for provider in self.vision_providers)

    def complete_with_image(self, system_prompt: str, user_prompt: str, image_data_url: str) -> str:
        from openai import OpenAI

        self.last_provider = None
        self.last_model = None
        errors: list[str] = []
        for provider in self.vision_providers:
            api_key = os.getenv(provider.api_key_env)
            if not api_key:
                continue
            model = os.getenv(provider.model_env) or provider.default_model
            try:
                client = OpenAI(api_key=api_key, base_url=provider.base_url)
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_prompt},
                                {"type": "image_url", "image_url": {"url": image_data_url}},
                            ],
                        },
                    ],
                    max_tokens=500,
                )
                self._record_usage(model, getattr(response, "usage", None))
                text = (response.choices[0].message.content or "").strip()
                if text:
                    self.last_provider = provider.name
                    self.last_model = model
                    return text
                errors.append(f"{provider.name}: empty response")
            except Exception as exc:  # pragma: no cover - network/provider variability
                errors.append(f"{provider.name}: {exc}")
                continue
        raise RuntimeError("No vision provider succeeded: " + "; ".join(errors))

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        from openai import OpenAI

        self.last_provider = None
        self.last_model = None
        errors: list[str] = []
        for provider in self.providers:
            api_key = os.getenv(provider.api_key_env)
            if not api_key:
                continue
            model = os.getenv(provider.model_env) if provider.model_env else None
            model = model or self.default_model
            try:
                client = OpenAI(api_key=api_key, base_url=provider.base_url)
                response = client.responses.create(
                    model=model,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                self._record_usage(model, getattr(response, "usage", None))
                text = (response.output_text or "").strip()
                if text:
                    self.last_provider = provider.name
                    self.last_model = model
                    return text
                errors.append(f"{provider.name}: empty response")
            except Exception as exc:  # pragma: no cover - network/provider variability
                errors.append(f"{provider.name}: {exc}")
                continue
        raise RuntimeError("No provider succeeded: " + "; ".join(errors))
