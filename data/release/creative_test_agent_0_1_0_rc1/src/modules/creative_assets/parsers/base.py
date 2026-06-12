from abc import ABC, abstractmethod


class ParsedCreativeAsset:
    def __init__(
        self,
        extracted_text: str = "",
        metadata: dict | None = None,
        parser_name: str = "",
        warnings: list[str] | None = None,
    ):
        self.extracted_text = extracted_text
        self.metadata = metadata or {}
        self.parser_name = parser_name
        self.warnings = warnings or []


class FileParser(ABC):
    @abstractmethod
    def parse(self, file_path: str, metadata: dict | None = None) -> ParsedCreativeAsset:
        ...


EXTENSION_MAP: dict[str, type[FileParser]] = {}


def register_parser(ext: str, parser_cls: type[FileParser]) -> None:
    EXTENSION_MAP[ext.lower()] = parser_cls


def get_parser(ext: str) -> FileParser | None:
    parser_cls = EXTENSION_MAP.get(ext.lower())
    if parser_cls is None:
        return None
    return parser_cls()


def parse_file(file_path: str, mime_type: str, ext: str) -> ParsedCreativeAsset:
    parser = get_parser(ext)
    if parser is None:
        from src.shared.errors import AppError
        raise AppError(
            code="unsupported_file_type",
            message=f"No parser available for extension '{ext}'.",
            status_code=400,
        )
    return parser.parse(file_path, {"mime_type": mime_type})
