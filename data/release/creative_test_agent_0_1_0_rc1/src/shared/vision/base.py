from abc import ABC, abstractmethod

from src.shared.vision.schemas import VisionResult


class VisionAnalyzer(ABC):
    @abstractmethod
    def analyze_image(self, image_path: str, metadata: dict | None = None) -> VisionResult:
        ...
