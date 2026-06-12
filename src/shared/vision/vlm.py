"""Optional local VLM adapter.

Uses the existing local LLM infrastructure (Ollama-compatible API) for vision.
Falls back gracefully if the model or endpoint is unavailable.
"""

import json
import logging

import httpx

from src.shared.vision.base import VisionAnalyzer
from src.shared.vision.schemas import VisionResult

logger = logging.getLogger(__name__)


class LocalVlmAnalyzer(VisionAnalyzer):
    def __init__(self, base_url: str = "", model: str = ""):
        self.base_url = base_url
        self.model = model

    def analyze_image(self, image_path: str, metadata: dict | None = None) -> VisionResult:
        if not self.base_url or not self.model:
            return VisionResult(
                provider="local_vlm",
                visual_summary="",
                detected_text="",
                layout_notes=[],
                visual_risks=[],
                warnings=["local_vlm_unavailable"],
                metadata=metadata or {},
            )

        try:
            import base64
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")

            prompt = (
                "Analyze this marketing creative image. "
                "Return a JSON object with fields: "
                "\"visual_summary\" (brief description), "
                "\"detected_text\" (any visible text), "
                "\"layout_notes\" (list of layout observations), "
                "\"visual_risks\" (list of objects with risk_type, level, description, mitigation)."
            )

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [b64],
                    }
                ],
                "stream": False,
            }

            response = httpx.post(
                f"{self.base_url.rstrip('/')}/api/chat",
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()
            content = result.get("message", {}).get("content", "")

            parsed = {}
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                pass

            return VisionResult(
                provider="local_vlm",
                visual_summary=parsed.get("visual_summary", content),
                detected_text=parsed.get("detected_text", ""),
                layout_notes=parsed.get("layout_notes", []),
                visual_risks=parsed.get("visual_risks", []),
                warnings=[],
                metadata={"vlm_model": self.model, "raw_response_length": len(content)},
            )

        except Exception as exc:
            logger.warning("Local VLM failed: %s", exc)
            return VisionResult(
                provider="local_vlm",
                visual_summary="",
                detected_text="",
                layout_notes=[],
                visual_risks=[],
                warnings=["local_vlm_unavailable", str(exc)],
                metadata=metadata or {},
            )
