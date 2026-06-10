import pytest

from src.shared.config.settings import Settings
from src.shared.errors import AppError
from src.shared.llm.factory import get_llm_provider
from src.shared.llm.lmstudio import LMStudioProvider
from src.shared.llm.ollama import OllamaProvider
from src.shared.llm.stub import StubProvider


def test_factory_returns_stub():
    settings = Settings(llm_provider="stub")
    provider = get_llm_provider(settings)
    assert isinstance(provider, StubProvider)


def test_factory_returns_ollama():
    settings = Settings(llm_provider="ollama", llm_model="qwen3:8b", llm_base_url="http://localhost:11434")
    provider = get_llm_provider(settings)
    assert isinstance(provider, OllamaProvider)


def test_factory_returns_lmstudio():
    settings = Settings(llm_provider="lmstudio", llm_model="local-model", llm_base_url="http://localhost:1234/v1")
    provider = get_llm_provider(settings)
    assert isinstance(provider, LMStudioProvider)


def test_factory_raises_on_unknown_provider():
    settings = Settings(llm_provider="unknown_provider")
    with pytest.raises(AppError) as exc:
        get_llm_provider(settings)
    assert exc.value.code == "unknown_llm_provider"


def test_factory_raises_on_cloud_provider():
    settings = Settings(llm_provider="openai")
    with pytest.raises(AppError) as exc:
        get_llm_provider(settings)
    assert exc.value.code == "cloud_llm_forbidden"


def test_stub_provider_generate():
    settings = Settings(llm_provider="stub")
    provider = get_llm_provider(settings)
    result = provider.generate("test prompt", {"key": "value"})
    assert result["provider"] == "stub"
    assert "test prompt" in result["content"]
    assert result["metadata"]["key"] == "value"


def test_ollama_provider_config():
    settings = Settings(llm_provider="ollama", llm_model="qwen3:8b", llm_base_url="http://localhost:11434")
    provider = get_llm_provider(settings)
    assert isinstance(provider, OllamaProvider)


def test_lmstudio_provider_config():
    settings = Settings(llm_provider="lmstudio", llm_model="test-model", llm_base_url="http://localhost:1234/v1")
    provider = get_llm_provider(settings)
    assert isinstance(provider, LMStudioProvider)
