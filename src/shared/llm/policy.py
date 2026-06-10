from src.shared.config.settings import get_settings
from src.shared.errors import AppError

LOCAL_PROVIDERS = {"stub", "ollama", "lmstudio"}
CLOUD_PROVIDERS = {"openai", "anthropic", "gemini", "perplexity"}


def validate_llm_provider(provider: str | None = None) -> None:
    settings = get_settings()
    provider = provider or settings.llm_provider

    if provider in LOCAL_PROVIDERS:
        if provider in ("ollama", "lmstudio") and not settings.local_only_mode:
            return
        return

    if provider in CLOUD_PROVIDERS and (
        settings.local_only_mode or not settings.allow_cloud_llm
    ):
        raise AppError(
            code="cloud_llm_forbidden",
            message=(
                f"Cloud LLM provider '{provider}' is forbidden "
                "when local_only_mode=True or allow_cloud_llm=False."
            ),
            status_code=403,
        )
