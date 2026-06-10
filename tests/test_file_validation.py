import os
import tempfile

import pytest

from src.modules.creative_assets.upload import validate_upload
from src.shared.errors import AppError


def test_txt_extension_is_valid():
    ext = validate_upload("test.txt", b"hello", "text/plain")
    assert ext == ".txt"


def test_md_extension_is_valid():
    ext = validate_upload("doc.md", b"# Hello", "text/markdown")
    assert ext == ".md"


def test_pdf_extension_is_valid():
    ext = validate_upload("doc.pdf", b"%PDF-1.4 fake", "application/pdf")
    assert ext == ".pdf"


def test_png_extension_is_valid():
    ext = validate_upload("img.png", b"PNG fake", "image/png")
    assert ext == ".png"


def test_jpg_extension_is_valid():
    ext = validate_upload("photo.jpg", b"JPEG fake", "image/jpeg")
    assert ext == ".jpg"


def test_unsupported_extension_rejected():
    with pytest.raises(AppError) as exc:
        validate_upload("file.exe", b"data", "application/x-msdownload")
    assert exc.value.code == "unsupported_file_type"


def test_unsupported_extension_docx_rejected():
    with pytest.raises(AppError) as exc:
        validate_upload("file.docx", b"data", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    assert exc.value.code == "unsupported_file_type"


def test_empty_file_rejected():
    with pytest.raises(AppError) as exc:
        validate_upload("empty.txt", b"", "text/plain")
    assert exc.value.code == "empty_file"


def test_file_too_large_rejected():
    from src.shared.config.settings import get_settings
    original = get_settings().max_upload_size_mb
    try:
        get_settings().max_upload_size_mb = 1
        with pytest.raises(AppError) as exc:
            validate_upload("large.txt", b"x" * (2 * 1024 * 1024), "text/plain")
        assert exc.value.code == "file_too_large"
    finally:
        get_settings().max_upload_size_mb = original


def test_unsafe_filename_rejected():
    with pytest.raises(AppError) as exc:
        validate_upload("foo/../../bar.txt", b"data", "text/plain")
    assert exc.value.code == "unsafe_filename"
