from pathlib import Path

from src.modules.creative_assets.parsers.base import FileParser, ParsedCreativeAsset
from src.shared.errors import AppError


class TextParser(FileParser):
    def parse(self, file_path: str, metadata: dict | None = None) -> ParsedCreativeAsset:
        path = Path(file_path)
        if path.stat().st_size == 0:
            raise AppError(code="empty_file", message="Uploaded file is empty.", status_code=400)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise AppError(
                code="file_parse_failed",
                message="Could not decode text file as UTF-8.",
                status_code=400,
            )
        return ParsedCreativeAsset(
            extracted_text=text,
            metadata={"parser": "text_parser", **(metadata or {})},
            parser_name="text_parser",
        )
