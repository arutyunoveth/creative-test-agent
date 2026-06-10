"""
Optional smoke test for Ollama.

Skipped by default unless CTA_RUN_LOCAL_LLM_SMOKE_TESTS=true is set.
"""

import os

import pytest

from src.shared.config.settings import Settings
from src.shared.errors import AppError
from src.shared.llm.ollama import OllamaProvider


@pytest.mark.skipif(
    os.environ.get("CTA_RUN_LOCAL_LLM_SMOKE_TESTS", "").lower() not in ("true", "1"),
    reason="Set CTA_RUN_LOCAL_LLM_SMOKE_TESTS=true to run this test",
)
def test_ollama_healthcheck():
    settings = Settings(llm_provider="ollama", llm_base_url=os.environ.get("CTA_LLM_BASE_URL", "http://localhost:11434"))
    provider = OllamaProvider()
    health = provider.healthcheck()
    assert "available" in health
    assert health["provider"] == "ollama"


@pytest.mark.skipif(
    os.environ.get("CTA_RUN_LOCAL_LLM_SMOKE_TESTS", "").lower() not in ("true", "1"),
    reason="Set CTA_RUN_LOCAL_LLM_SMOKE_TESTS=true to run this test",
)
def test_ollama_generate_small_prompt():
    provider = OllamaProvider()
    result = provider.generate("Say hello in one word.")
    assert result["provider"] == "ollama"
    assert "content" in result
    assert len(result["content"]) > 0


@pytest.mark.skipif(
    os.environ.get("CTA_RUN_LOCAL_LLM_SMOKE_TESTS", "").lower() not in ("true", "1"),
    reason="Set CTA_RUN_LOCAL_LLM_SMOKE_TESTS=true to run this test",
)
def test_ollama_connection_error():
    provider = OllamaProvider()
    provider.base_url = "http://localhost:19999"
    with pytest.raises(AppError) as exc:
        provider.generate("test")
    assert exc.value.code == "llm_connection_error"
