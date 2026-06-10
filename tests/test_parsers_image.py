import tempfile
from pathlib import Path

from PIL import Image

from src.modules.creative_assets.parsers import ImageParser


def _create_test_image(suffix: str = ".png", size: tuple = (100, 50)) -> str:
    f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    f.close()
    img = Image.new("RGB", size, color="red")
    img.save(f.name, format="PNG" if suffix == ".png" else "JPEG")
    return f.name


def test_image_parser_png():
    path = _create_test_image(".png")
    result = ImageParser().parse(path)
    assert result.parser_name == "image_parser"
    assert result.metadata["image"]["width"] == 100
    assert result.metadata["image"]["height"] == 50
    assert result.metadata["image"]["format"] == "PNG"
    assert "image_text_extraction_not_implemented" in result.warnings


def test_image_parser_jpg():
    path = _create_test_image(".jpg", size=(200, 100))
    result = ImageParser().parse(path)
    assert result.metadata["image"]["width"] == 200
    assert result.metadata["image"]["height"] == 100


def test_image_parser_metadata():
    path = _create_test_image(".png")
    result = ImageParser().parse(path, metadata={"source": "test"})
    assert result.metadata["source"] == "test"
    assert result.extracted_text == ""


def test_image_parser_warning_not_implemented():
    path = _create_test_image(".png")
    result = ImageParser().parse(path)
    assert "image_text_extraction_not_implemented" in result.warnings
