import pytest

from src.shared.errors import AppError
from src.shared.llm.policy import validate_llm_provider


def test_stub_provider_is_allowed():
    validate_llm_provider("stub")


def test_ollama_provider_is_allowed_in_local_mode():
    validate_llm_provider("ollama")


def test_lmstudio_provider_is_allowed_in_local_mode():
    validate_llm_provider("lmstudio")


def test_openai_provider_is_forbidden():
    with pytest.raises(AppError) as exc:
        validate_llm_provider("openai")
    assert exc.value.code == "cloud_llm_forbidden"


def test_anthropic_provider_is_forbidden():
    with pytest.raises(AppError) as exc:
        validate_llm_provider("anthropic")
    assert exc.value.code == "cloud_llm_forbidden"


def test_gemini_provider_is_forbidden():
    with pytest.raises(AppError) as exc:
        validate_llm_provider("gemini")
    assert exc.value.code == "cloud_llm_forbidden"


def test_perplexity_provider_is_forbidden():
    with pytest.raises(AppError) as exc:
        validate_llm_provider("perplexity")
    assert exc.value.code == "cloud_llm_forbidden"
