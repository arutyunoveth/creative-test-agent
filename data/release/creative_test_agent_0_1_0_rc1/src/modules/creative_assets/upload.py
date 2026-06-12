import mimetypes
import os
from pathlib import Path

from src.modules.creative_assets.parsers import parse_file
from src.shared.config.settings import get_settings
from src.shared.errors import AppError
from src.shared.storage.local_storage import LocalStorage

ALLOWED_MIME_MAP = {
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def validate_upload(filename: str, content: bytes, content_type: str | None) -> str:
    settings = get_settings()
    allowed = [e.strip().lower() for e in settings.allowed_upload_types.split(",")]

    ext = Path(filename).suffix.lower()
    if not ext or ext.lstrip(".") not in allowed:
        raise AppError(
            code="unsupported_file_type",
            message=f"File extension '{ext}' is not supported. Allowed: {', '.join(allowed)}",
            status_code=400,
        )

    expected_mime = ALLOWED_MIME_MAP.get(ext)
    if content_type and expected_mime and content_type != expected_mime:
        if not (ext in (".jpg", ".jpeg") and content_type == "image/jpeg"):
            pass

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise AppError(
            code="file_too_large",
            message=f"File exceeds maximum size of {settings.max_upload_size_mb} MB.",
            status_code=400,
        )

    if len(content) == 0:
        raise AppError(code="empty_file", message="Uploaded file is empty.", status_code=400)

    if ".." in filename or filename.startswith("/"):
        raise AppError(
            code="unsafe_filename",
            message="Filename contains path traversal characters.",
            status_code=400,
        )

    name = Path(filename).name
    safe = _safe_filename(name)
    if safe != name:
        raise AppError(
            code="unsafe_filename",
            message="Filename contains unsafe characters.",
            status_code=400,
        )

    return ext


def process_upload(filename: str, content: bytes, content_type: str | None) -> dict:
    ext = validate_upload(filename, content, content_type)
    mime = ALLOWED_MIME_MAP.get(ext, content_type or "application/octet-stream")

    storage = LocalStorage()
    file_path = storage.safe_store(content, ext)

    parsed = parse_file(file_path, mime, ext)

    asset_type = _map_ext_to_asset_type(ext)

    return {
        "file_path": file_path,
        "original_filename": filename,
        "mime_type": mime,
        "file_size_bytes": len(content),
        "asset_type": asset_type,
        "extracted_text": parsed.extracted_text,
        "parser_metadata": parsed.metadata,
        "warnings": parsed.warnings,
        "parser_name": parsed.parser_name,
    }


def _safe_filename(name: str) -> str:
    import re
    cleaned = re.sub(r"[^\w.\- ]", "", name)
    return cleaned


def _map_ext_to_asset_type(ext: str) -> str:
    if ext in (".txt", ".md"):
        return "text"
    elif ext == ".pdf":
        return "pdf"
    elif ext in (".png", ".jpg", ".jpeg", ".webp"):
        return "image"
    return "text"
