"""
Optional smoke test for LM Studio.

Skipped by default unless CTA_RUN_LOCAL_LLM_SMOKE_TESTS=true is set.
"""

import os

import pytest

from src.shared.config.settings import Settings
from src.shared.errors import AppError
from src.shared.llm.lmstudio import LMStudioProvider


@pytest.mark.skipif(
    os.environ.get("CTA_RUN_LOCAL_LLM_SMOKE_TESTS", "").lower() not in ("true", "1"),
    reason="Set CTA_RUN_LOCAL_LLM_SMOKE_TESTS=true to run this test",
)
def test_lmstudio_healthcheck():
    provider = LMStudioProvider()
    health = provider.healthcheck()
    assert "available" in health
    assert health["provider"] == "lmstudio"


@pytest.mark.skipif(
    os.environ.get("CTA_RUN_LOCAL_LLM_SMOKE_TESTS", "").lower() not in ("true", "1"),
    reason="Set CTA_RUN_LOCAL_LLM_SMOKE_TESTS=true to run this test",
)
def test_lmstudio_generate_small_prompt():
    provider = LMStudioProvider()
    result = provider.generate("Say hello in one word.")
    assert result["provider"] == "lmstudio"
    assert "content" in result
    assert len(result["content"]) > 0


@pytest.mark.skipif(
    os.environ.get("CTA_RUN_LOCAL_LLM_SMOKE_TESTS", "").lower() not in ("true", "1"),
    reason="Set CTA_RUN_LOCAL_LLM_SMOKE_TESTS=true to run this test",
)
def test_lmstudio_connection_error():
    provider = LMStudioProvider()
    provider.base_url = "http://localhost:19999/v1"
    with pytest.raises(AppError) as exc:
        provider.generate("test")
    assert exc.value.code == "llm_connection_error"
