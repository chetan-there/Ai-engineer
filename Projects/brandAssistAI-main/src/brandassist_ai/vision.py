from __future__ import annotations

import base64
import json
import re
from pathlib import Path

from .models import ImageLabel


# Maps generic visual product types (what a vision model actually sees) to the
# pseudonymized catalog product IDs used across the database and knowledge base.
ALIAS_MAP: dict[str, str] = {
    "microwave": "microchef-20l",
    "router": "wavehub-r5",
    "modem": "wavehub-r5",
    "wifi": "wavehub-r5",
    "wi-fi": "wavehub-r5",
    "air conditioner": "nimbus-ac-1500",
    "air-conditioner": "nimbus-ac-1500",
    "ac unit": "nimbus-ac-1500",
    "kettle": "thermoboil-k1",
    "toaster": "toastpro-2s",
    "fan": "breezefan-f7",
    "air purifier": "aeropure-220",
    "purifier": "aeropure-220",
    "vacuum": "dustmate-v10",
    "soundbar": "sonicbar-s20",
    "sound bar": "sonicbar-s20",
    "speaker": "sonicbar-s20",
    "blender": "blendgo-b2",
    "mixer": "blendgo-b2",
}

_VISION_SYSTEM_PROMPT = (
    "You are a product triage vision assistant for a consumer electronics support desk. "
    "Look at the image and respond with compact JSON only, no markdown:\n"
    '{"product_type": "<generic device type, e.g. microwave, router, kettle>", '
    '"category": "<kitchen|climate|networking|homecare|audio|unknown>", '
    '"observations": ["<short visual fact>", "..."], '
    '"confidence": <0.0-1.0>, "readable": <true|false>}\n'
    "Set readable=false if the image is too blurry/dark to identify the device."
)


def _extract_json(text: str) -> dict:
    """Best-effort parse of a JSON object from a possibly fenced model response."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*", "", cleaned).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


class ImageTriage:
    """Image triage with two paths: deterministic labels (for evals) and a real
    vision model for arbitrary uploaded images."""

    def __init__(self, labels: list[ImageLabel], router: object | None = None) -> None:
        self.by_id = {label.image_id: label for label in labels}
        self.router = router

    def inspect(self, image_id: str | None, uploaded_name: str | None = None) -> dict:
        if not image_id and uploaded_name:
            image_id = Path(uploaded_name).stem.lower().replace(" ", "-")
        if not image_id:
            return self._empty()

        label = self.by_id.get(image_id)
        if not label:
            return {
                "product_id": None,
                "category": "unknown",
                "confidence": 0.2,
                "quality": "unknown",
                "observations": ["image not found in labeled POC dataset"],
                "supported": False,
            }

        if label.quality == "clear" and label.product_id:
            confidence = 0.92
        elif label.quality == "ambiguous" and label.product_id:
            confidence = 0.55
        elif label.quality == "blurry":
            confidence = 0.18
        else:
            confidence = 0.3

        return {
            "product_id": label.product_id,
            "category": label.category,
            "confidence": confidence,
            "quality": label.quality,
            "observations": label.observations,
            "supported": bool(label.product_id),
        }

    def identify_from_bytes(self, image_bytes: bytes, mime: str = "image/png") -> dict:
        """Identify an uploaded image using a real vision model, then map the
        generic product type onto the pseudonymized catalog."""
        if not image_bytes:
            return self._empty()
        if not self.router or not getattr(self.router, "is_vision_enabled", lambda: False)():
            return {
                "product_id": None,
                "category": "unknown",
                "confidence": 0.2,
                "quality": "unknown",
                "observations": ["No vision model configured (set GROQ_API_KEY or OPENROUTER_API_KEY)."],
                "supported": False,
            }

        data_url = f"data:{mime};base64,{base64.b64encode(image_bytes).decode('ascii')}"
        try:
            text = self.router.complete_with_image(
                system_prompt=_VISION_SYSTEM_PROMPT,
                user_prompt="Identify this product and any visible issue.",
                image_data_url=data_url,
            )
            data = _extract_json(text)
        except Exception as exc:  # pragma: no cover - network/provider variability
            return {
                "product_id": None,
                "category": "unknown",
                "confidence": 0.2,
                "quality": "unknown",
                "observations": [f"Vision identification failed: {exc}"],
                "supported": False,
            }

        product_type = str(data.get("product_type") or "").lower()
        matched_id = None
        for key, pid in ALIAS_MAP.items():
            if key in product_type:
                matched_id = pid
                break

        observations = data.get("observations") or []
        if not isinstance(observations, list):
            observations = [str(observations)]
        try:
            confidence = float(data.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5
        readable = bool(data.get("readable", True))

        if not readable:
            quality = "blurry"
            confidence = min(confidence, 0.18)
            matched_id = None
        elif matched_id:
            quality = "clear"
        else:
            quality = "unknown"
            observations = observations + [
                f"Detected '{product_type or 'unknown device'}', which is not in the BrandAssist catalog."
            ]

        return {
            "product_id": matched_id,
            "category": data.get("category", "unknown"),
            "confidence": confidence,
            "quality": quality,
            "observations": observations,
            "supported": bool(matched_id),
        }

    @staticmethod
    def _empty() -> dict:
        return {
            "product_id": None,
            "category": None,
            "confidence": 0.0,
            "quality": "none",
            "observations": [],
            "supported": True,
        }
