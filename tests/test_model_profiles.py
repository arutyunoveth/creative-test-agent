"""Model profile CRUD tests."""

import pytest
from src.modules.model_profiles.schemas import CreateModelProfileRequest
from src.modules.model_profiles.service import create_profile, get_profile, list_profiles
from src.shared.db.session import init_db


@pytest.fixture(autouse=True)
def _db():
    init_db()
    yield


def test_list_profiles_returns_list():
    assert isinstance(list_profiles(), list)


def test_create_stub_profile():
    req = CreateModelProfileRequest(profile_name="test-stub", provider="stub", model="stub")
    p = create_profile(req)
    assert p.profile_name == "test-stub"
    assert p.provider == "stub"
    assert p.enabled is False  # default is False per schema


def test_get_by_id():
    req = CreateModelProfileRequest(profile_name="get-test", provider="stub", model="stub")
    p = create_profile(req)
    fetched = get_profile(p.id)
    assert fetched is not None
    assert fetched.id == p.id


def test_get_missing():
    assert get_profile("nonexistent") is None


def test_list_multiple():
    create_profile(CreateModelProfileRequest(profile_name="a", provider="stub", model="stub"))
    create_profile(CreateModelProfileRequest(profile_name="b", provider="stub", model="stub"))
    profiles = list_profiles()
    assert len(profiles) >= 2


def test_forbidden_provider():
    from src.modules.model_profiles.service import FORBIDDEN_PROVIDERS
    assert "openai" in FORBIDDEN_PROVIDERS
    assert "anthropic" in FORBIDDEN_PROVIDERS
    assert "gemini" in FORBIDDEN_PROVIDERS


def test_create_forbidden_provider_raises():
    req = CreateModelProfileRequest(profile_name="bad", provider="openai", model="gpt-4")
    with pytest.raises(ValueError, match="not allowed"):
        create_profile(req)


def test_create_unknown_provider_raises():
    req = CreateModelProfileRequest(profile_name="weird", provider="cohere", model="command")
    with pytest.raises(ValueError, match="not recognized"):
        create_profile(req)


def test_stub_health():
    from src.modules.model_profiles.service import check_profile_health
    req = CreateModelProfileRequest(profile_name="health-test", provider="stub", model="stub")
    p = create_profile(req)
    health = check_profile_health(p.id)
    assert health.reachable is True
    assert health.provider == "stub"


def test_profile_with_ollama():
    req = CreateModelProfileRequest(
        profile_name="ollama-local-test",
        provider="ollama",
        model="qwen2.5:7b",
        base_url="http://localhost:11434",
        timeout_seconds=30,
    )
    p = create_profile(req)
    assert p.provider == "ollama"
    assert p.base_url == "http://localhost:11434"
