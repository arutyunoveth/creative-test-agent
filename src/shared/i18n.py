import json
from pathlib import Path

LOCALES_DIR = Path(__file__).parent / "locales"

_translators: dict[str, "Translator"] = {}


class Translator:
    def __init__(self, lang: str = "ru"):
        self.lang = lang if lang in ("ru", "en") else "ru"
        self._data = self._load(self.lang)

    def _load(self, lang: str) -> dict:
        path = LOCALES_DIR / f"{lang}.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def t(self, text: str) -> str:
        return self._data.get(text, text)


def get_translator(lang: str = "ru") -> Translator:
    if lang not in _translators:
        _translators[lang] = Translator(lang)
    return _translators[lang]
