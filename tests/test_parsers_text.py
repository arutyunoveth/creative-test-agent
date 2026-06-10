import tempfile
from pathlib import Path

import pytest

from src.modules.creative_assets.parsers import TextParser
from src.shared.errors import AppError


def _write_tmp(content: str, suffix: str = ".txt") -> str:
    f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode="w")
    f.write(content)
    f.close()
    return f.name


def test_text_parser_plain():
    path = _write_tmp("Hello, this is a creative concept.")
    result = TextParser().parse(path)
    assert result.extracted_text == "Hello, this is a creative concept."
    assert result.parser_name == "text_parser"
    assert len(result.warnings) == 0


def test_text_parser_markdown():
    path = _write_tmp("# Big Idea\n\nThis is the concept.", suffix=".md")
    result = TextParser().parse(path)
    assert "# Big Idea" in result.extracted_text


def test_text_parser_multiline():
    content = "Line 1\nLine 2\nLine 3"
    path = _write_tmp(content)
    result = TextParser().parse(path)
    assert result.extracted_text == content


def test_text_parser_empty_rejected():
    path = _write_tmp("")
    with pytest.raises(AppError) as exc:
        TextParser().parse(path)
    assert exc.value.code == "empty_file"


def test_text_parser_unicode():
    content = "Créative concept avec accents and emoji 🎯"
    path = _write_tmp(content)
    result = TextParser().parse(path)
    assert "Créative" in result.extracted_text
