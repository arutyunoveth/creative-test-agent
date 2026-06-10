from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CTA_", env_file=".env")

    app_name: str = "Creative Test Agent API"
    debug: bool = False
    database_url: str = "sqlite:///./creative_test_agent.db"
    local_only_mode: bool = True
    allow_cloud_llm: bool = False
    llm_provider: str = "stub"
    llm_model: str | None = None
    llm_base_url: str | None = None
    llm_timeout_seconds: int = 60
    storage_root: str = "./data/storage"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
