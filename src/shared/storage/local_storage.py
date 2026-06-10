import os
import shutil
from pathlib import Path

from src.shared.config.settings import get_settings


class LocalStorage:
    def __init__(self, root: str | None = None):
        settings = get_settings()
        self.root = Path(root or settings.storage_root)
        self.root.mkdir(parents=True, exist_ok=True)

    def store(self, path: str, content: bytes) -> str:
        full_path = self.root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)
        return str(full_path)

    def read(self, path: str) -> bytes:
        return (self.root / path).read_bytes()

    def delete(self, path: str) -> None:
        full_path = self.root / path
        if full_path.is_file():
            full_path.unlink()
        elif full_path.is_dir():
            shutil.rmtree(str(full_path))

    def exists(self, path: str) -> bool:
        return (self.root / path).exists()
