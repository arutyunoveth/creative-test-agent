import httpx

from src.shared.config.settings import get_settings
from src.shared.errors import AppError
from src.shared.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self):
        settings = get_settings()
        self.model = settings.llm_model or "qwen3:8b"
        self.base_url = (settings.llm_base_url or "http://localhost:11434").rstrip("/")
        self.timeout = settings.llm_timeout_seconds

    def generate(self, prompt: str, metadata: dict | None = None) -> dict:
        try:
            resp = httpx.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "provider": "ollama",
                "content": data.get("response", ""),
                "metadata": {
                    "model": self.model,
                    "base_url": self.base_url,
                    "duration_ns": data.get("total_duration"),
                    **(metadata or {}),
                },
            }
        except httpx.ConnectError:
            raise AppError(
                code="llm_connection_error",
                message=f"Cannot connect to Ollama at {self.base_url}. Is the server running?",
                status_code=503,
            )
        except httpx.TimeoutException:
            raise AppError(
                code="llm_timeout",
                message=f"Ollama request timed out after {self.timeout}s.",
                status_code=504,
            )
        except httpx.HTTPStatusError as e:
            raise AppError(
                code="llm_http_error",
                message=f"Ollama returned HTTP {e.response.status_code}: {e.response.text[:200]}",
                status_code=502,
            )

    def healthcheck(self) -> dict:
        try:
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=5)
            resp.raise_for_status()
            return {
                "provider": "ollama",
                "model": self.model,
                "base_url": self.base_url,
                "available": True,
                "local_only_mode": True,
            }
        except Exception:
            return {
                "provider": "ollama",
                "model": self.model,
                "base_url": self.base_url,
                "available": False,
                "local_only_mode": True,
            }
