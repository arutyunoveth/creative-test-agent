"""Vision analyzer factory.

Mirrors src/shared/llm/factory.py pattern.
"""

from src.shared.config.settings import get_settings
from src.shared.vision.base import VisionAnalyzer
from src.shared.vision.policy import validate_vision_provider
from src.shared.vision.schemas import VisionResult
from src.shared.vision.stub import StubVisionAnalyzer


def get_vision_analyzer() -> VisionAnalyzer:
    settings = get_settings()
    provider = settings.vision_provider

    validate_vision_provider(provider)

    if provider == "stub":
        return StubVisionAnalyzer()

    if provider == "local_ocr":
        from src.shared.vision.ocr import LocalOcrAnalyzer
        return LocalOcrAnalyzer()

    if provider == "local_vlm":
        from src.shared.vision.vlm import LocalVlmAnalyzer
        return LocalVlmAnalyzer(
            base_url=settings.vision_base_url or "",
            model=settings.vision_model or "",
        )

    if provider == "hybrid":
        from src.shared.vision.ocr import LocalOcrAnalyzer
        from src.shared.vision.vlm import LocalVlmAnalyzer

        ocr = LocalOcrAnalyzer()
        vlm = LocalVlmAnalyzer(
            base_url=settings.vision_base_url or "",
            model=settings.vision_model or "",
        )
        return HybridAnalyzer(ocr, vlm)

    return StubVisionAnalyzer()


class HybridAnalyzer(VisionAnalyzer):
    def __init__(self, ocr_analyzer: VisionAnalyzer, vlm_analyzer: VisionAnalyzer):
        self.ocr = ocr_analyzer
        self.vlm = vlm_analyzer

    def analyze_image(self, image_path: str, metadata: dict | None = None) -> VisionResult:
        ocr_result = self.ocr.analyze_image(image_path, metadata)
        vlm_result = self.vlm.analyze_image(image_path, metadata)

        combined = VisionResult(
            provider="hybrid",
            visual_summary=vlm_result.visual_summary or ocr_result.visual_summary,
            detected_text=ocr_result.detected_text or vlm_result.detected_text,
            layout_notes=list(set(ocr_result.layout_notes + vlm_result.layout_notes)),
            visual_risks=ocr_result.visual_risks + vlm_result.visual_risks,
            warnings=ocr_result.warnings + vlm_result.warnings,
            metadata={**ocr_result.metadata, **vlm_result.metadata},
        )
        return combined
