from fastapi import APIRouter

from src.shared.config.settings import get_settings
from src.shared.llm.factory import get_llm_provider
from src.shared.llm.schemas import LLMProviderHealth

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/health", response_model=LLMProviderHealth)
def llm_health():
    settings = get_settings()
    provider = get_llm_provider(settings)

    health = getattr(provider, "healthcheck", None)
    if health is not None and callable(health):
        return LLMProviderHealth(**health())

    return LLMProviderHealth(
        provider=settings.llm_provider,
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        available=True,
        local_only_mode=settings.local_only_mode,
    )
