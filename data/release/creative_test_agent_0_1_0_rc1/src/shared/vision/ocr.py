"""Optional local OCR adapter.

Uses pytesseract if available. Falls back gracefully if Tesseract is not installed.
"""

import logging

from src.shared.vision.base import VisionAnalyzer
from src.shared.vision.schemas import VisionResult

logger = logging.getLogger(__name__)

_TESSERACT_AVAILABLE = False
_tesseract_get_tesseract_version = None

try:
    import pytesseract
    _TESSERACT_AVAILABLE = True
    _tesseract_get_tesseract_version = pytesseract.get_tesseract_version
except Exception:
    pass


class LocalOcrAnalyzer(VisionAnalyzer):
    def analyze_image(self, image_path: str, metadata: dict | None = None) -> VisionResult:
        if not _TESSERACT_AVAILABLE:
            return VisionResult(
                provider="local_ocr",
                visual_summary="",
                detected_text="",
                layout_notes=[],
                visual_risks=[],
                warnings=["local_ocr_unavailable"],
                metadata=metadata or {},
            )

        try:
            from PIL import Image
            img = Image.open(image_path)
            detected = pytesseract.image_to_string(img)
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            confidence_scores = [int(c) for c in data.get("conf", []) if isinstance(c, (int, str)) and str(c).isdigit()]
            avg_conf = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

            return VisionResult(
                provider="local_ocr",
                visual_summary=f"Text detected via local OCR. Average confidence: {avg_conf:.0f}%.",
                detected_text=detected.strip(),
                layout_notes=[f"OCR confidence: {avg_conf:.0f}%"],
                visual_risks=[],
                warnings=[],
                metadata={"ocr_engine": "tesseract", "avg_confidence": avg_conf},
            )
        except Exception as exc:
            logger.warning("Local OCR failed: %s", exc)
            return VisionResult(
                provider="local_ocr",
                visual_summary="",
                detected_text="",
                layout_notes=[],
                visual_risks=[],
                warnings=["local_ocr_failed", str(exc)],
                metadata=metadata or {},
            )
