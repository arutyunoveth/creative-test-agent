from src.shared.llm.base import LLMProvider


class StubProvider(LLMProvider):
    def generate(self, prompt: str, metadata: dict | None = None) -> dict:
        return {
            "provider": "stub",
            "content": f"Stub response for: {prompt[:60]}...",
            "metadata": metadata or {},
        }
