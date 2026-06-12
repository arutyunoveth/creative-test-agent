from src.shared.vision.base import VisionAnalyzer
from src.shared.vision.schemas import VisionResult


class StubVisionAnalyzer(VisionAnalyzer):
    def analyze_image(self, image_path: str, metadata: dict | None = None) -> VisionResult:
        return VisionResult(
            provider="stub",
            visual_summary="Visual analysis is running in stub mode.",
            detected_text="",
            layout_notes=["Image metadata is available, but real visual analysis is disabled."],
            visual_risks=[],
            warnings=["vision_stub_mode"],
            metadata=metadata or {},
        )
