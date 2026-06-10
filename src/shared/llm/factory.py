from src.shared.config.settings import Settings, get_settings
from src.shared.errors import AppError
from src.shared.llm.base import LLMProvider
from src.shared.llm.lmstudio import LMStudioProvider
from src.shared.llm.ollama import OllamaProvider
from src.shared.llm.policy import validate_llm_provider
from src.shared.llm.stub import StubProvider


def get_llm_provider(settings: Settings | None = None) -> LLMProvider:
    settings = settings or get_settings()

    validate_llm_provider(settings.llm_provider)

    if settings.llm_provider == "stub":
        return StubProvider()
    elif settings.llm_provider == "ollama":
        return OllamaProvider()
    elif settings.llm_provider == "lmstudio":
        return LMStudioProvider()
    else:
        raise AppError(
            code="unknown_llm_provider",
            message=f"Unknown LLM provider: {settings.llm_provider}",
            status_code=400,
        )
