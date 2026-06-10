from src.shared.config.settings import get_settings


def test_default_settings():
    settings = get_settings()
    assert settings.local_only_mode is True
    assert settings.allow_cloud_llm is False
    assert settings.llm_provider == "stub"
    assert settings.app_name == "Creative Test Agent API"
