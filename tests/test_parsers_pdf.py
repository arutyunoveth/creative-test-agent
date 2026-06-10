import tempfile
from pathlib import Path

import pytest

from src.modules.creative_assets.parsers import PdfParser
from src.shared.errors import AppError


def _tmp_path(suffix: str = ".pdf") -> str:
    f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    f.close()
    return f.name


def test_pdf_parser_with_real_pdf():
    from pypdf import PdfWriter
    path = _tmp_path()
    writer = PdfWriter()
    writer.add_blank_page(72, 72)
    page = writer.pages[0]
    page.merge_page(writer.add_blank_page(72, 72))
    with open(path, "wb") as f:
        writer.write(f)

    result = PdfParser().parse(path)
    assert result.parser_name == "pdf_parser"
    assert "page_count" in result.metadata


def test_pdf_parser_with_text_content():
    from io import BytesIO
    from pypdf import PdfWriter
    path = _tmp_path()
    writer = PdfWriter()
    writer.add_blank_page(72, 72)
    with open(path, "wb") as f:
        writer.write(f)

    result = PdfParser().parse(path)
    assert result.parser_name == "pdf_parser"


def test_pdf_parser_empty_rejected():
    path = _tmp_path()
    Path(path).write_bytes(b"")
    with pytest.raises(AppError) as exc:
        PdfParser().parse(path)
    assert exc.value.code == "empty_file"


def test_pdf_parser_corrupted_rejected():
    path = _tmp_path()
    Path(path).write_bytes(b"not a pdf content")
    with pytest.raises(AppError) as exc:
        PdfParser().parse(path)
    assert exc.value.code == "file_parse_failed"
