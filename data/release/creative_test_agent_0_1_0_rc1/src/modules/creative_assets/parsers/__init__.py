from .base import ParsedCreativeAsset, parse_file, register_parser
from .image_parser import ImageParser
from .pdf_parser import PdfParser
from .text_parser import TextParser

__all__ = ["ParsedCreativeAsset", "parse_file", "TextParser", "PdfParser", "ImageParser"]

register_parser(".txt", TextParser)
register_parser(".md", TextParser)
register_parser(".pdf", PdfParser)
register_parser(".png", ImageParser)
register_parser(".jpg", ImageParser)
register_parser(".jpeg", ImageParser)
register_parser(".webp", ImageParser)
