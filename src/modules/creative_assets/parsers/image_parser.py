from pathlib import Path

from PIL import Image

from src.modules.creative_assets.parsers.base import FileParser, ParsedCreativeAsset


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
        return ParsedCreativeAsset(
            extracted_text="",
            metadata={
                "parser": "image_parser",
                "image": img_meta,
                **(metadata or {}),
            },
            parser_name="image_parser",
            warnings=["image_text_extraction_not_implemented"],
        )
