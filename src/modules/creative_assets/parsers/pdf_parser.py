from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from src.modules.creative_assets.parsers.base import FileParser, ParsedCreativeAsset
from src.shared.errors import AppError


class PdfParser(FileParser):
    def parse(self, file_path: str, metadata: dict | None = None) -> ParsedCreativeAsset:
        path = Path(file_path)
        if path.stat().st_size == 0:
            raise AppError(code="empty_file", message="Uploaded PDF is empty.", status_code=400)
        try:
            reader = PdfReader(str(path))
        except Exception:
            raise AppError(
                code="file_parse_failed",
                message="Could not parse PDF file. It may be corrupted or encrypted.",
                status_code=400,
            )

        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)

        extracted = "\n\n".join(pages).strip()
        warnings = []
        if not extracted:
            warnings.append("pdf_contains_no_extractable_text")

        return ParsedCreativeAsset(
            extracted_text=extracted,
            metadata={
                "parser": "pdf_parser",
                "page_count": len(reader.pages),
                **(metadata or {}),
            },
            parser_name="pdf_parser",
            warnings=warnings,
        )


def parse_pdf(raw_bytes: bytes) -> ParsedCreativeAsset:
    if not raw_bytes:
        raise AppError(code="empty_file", message="Uploaded PDF is empty.", status_code=400)
    try:
        reader = PdfReader(BytesIO(raw_bytes))
    except Exception:
        raise AppError(
            code="file_parse_failed",
            message="Could not parse PDF file. It may be corrupted or encrypted.",
            status_code=400,
        )

    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    extracted = "\n\n".join(pages).strip()
    warnings = []
    if not extracted:
        warnings.append("pdf_contains_no_extractable_text")

    return ParsedCreativeAsset(
        extracted_text=extracted,
        metadata={
            "parser": "pdf_parser",
            "page_count": len(reader.pages),
        },
        parser_name="pdf_parser",
        warnings=warnings,
    )
