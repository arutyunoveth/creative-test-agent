from pathlib import Path

from PIL import Image

from src.modules.creative_assets.parsers.base import FileParser, ParsedCreativeAsset
from src.shared.vision.factory import get_vision_analyzer


class ImageParser(FileParser):
    def parse(self, file_path: str, metadata: dict | None = None) -> ParsedCreativeAsset:
        path = Path(file_path)
        img = Image.open(str(path))
        img_meta = {
            "width": img.width,
            "height": img.height,
            "format": img.format or "",
            "mode": img.mode,
        }

        # Run visual analysis (stub by default, OCR/VLM if configured)
        visual_result = None
        visual_data = {}
        try:
            analyzer = get_vision_analyzer()
            visual_result = analyzer.analyze_image(str(path), metadata={"image": img_meta})
            visual_data = visual_result.model_dump()
        except Exception:
            visual_data = {
                "provider": "error",
                "visual_summary": "",
                "detected_text": "",
                "layout_notes": [],
                "visual_risks": [],
                "warnings": ["visual_analysis_errored"],
                "metadata": {},
            }

        extracted_text = visual_data.get("detected_text") or ""
        warnings = visual_data.get("warnings", [])
        if not warnings:
            warnings = ["image_text_extraction_not_implemented"]

        return ParsedCreativeAsset(
            extracted_text=extracted_text,
            metadata={
                "parser": "image_parser",
                "image": img_meta,
                "visual_analysis": visual_data,
                **(metadata or {}),
            },
            parser_name="image_parser",
            warnings=warnings,
        )
