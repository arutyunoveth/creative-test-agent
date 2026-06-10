from pathlib import Path


_PROMPT_DIR = Path(__file__).parent


def load_prompt(name: str, **kwargs) -> str:
    path = _PROMPT_DIR / f"{name}.md"
    template = path.read_text()
    for key, value in kwargs.items():
        template = template.replace("{{" + key + "}}", str(value))
    return template
