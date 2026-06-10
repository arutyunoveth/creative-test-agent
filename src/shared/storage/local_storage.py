import os
import re
import shutil
import uuid
from pathlib import Path

from src.shared.config.settings import get_settings


class LocalStorage:
    def __init__(self, root: str | None = None):
        settings = get_settings()
        self.root = Path(root or settings.storage_root)
        self.root.mkdir(parents=True, exist_ok=True)

    def safe_store(self, content: bytes, ext: str) -> str:
        name = f"{uuid.uuid4().hex}{ext}"
        return self.store(name, content)

    def store(self, path: str, content: bytes) -> str:
        safe = self._sanitize_path(path)
        full_path = self.root / safe
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)
        return str(full_path)

    def read(self, path: str) -> bytes:
        safe = self._sanitize_path(path)
        return (self.root / safe).read_bytes()

    def delete(self, path: str) -> None:
        safe = self._sanitize_path(path)
        full_path = self.root / safe
        if full_path.is_file():
            full_path.unlink()
        elif full_path.is_dir():
            shutil.rmtree(str(full_path))

    def exists(self, path: str) -> bool:
        safe = self._sanitize_path(path)
        return (self.root / safe).exists()

    def absolute_path(self, relative_path: str) -> Path:
        safe = self._sanitize_path(relative_path)
        return self.root / safe

    @staticmethod
    def _sanitize_path(path: str) -> str:
        cleaned = path.lstrip("/")
        parts = []
        for part in cleaned.split("/"):
            if part in ("", ".", ".."):
                continue
            parts.append(part)
        result = "/".join(parts)
        result = re.sub(r"[^\w\-./]", "_", result)
        return result
