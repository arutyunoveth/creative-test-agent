"""Closed-loop acceptance and offline verification tests."""

from httpx import ASGITransport, AsyncClient
from src.main import app
from src.shared.vision.policy import validate_vision_provider
from src.shared.llm.policy import validate_llm_provider
from src.shared.errors import AppError


async def test_health_endpoints_available():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        health = await client.get("/health")
        db = await client.get("/health/db")
        llm = await client.get("/llm/health")
        vision = await client.get("/vision/health")
    assert health.status_code == 200
    assert db.status_code == 200
    assert llm.status_code == 200
    assert vision.status_code == 200


async def test_default_llm_provider_is_stub():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/llm/health")
    assert resp.json()["provider"] == "stub"


async def test_default_vision_provider_is_stub():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/vision/health")
    assert resp.json()["provider"] == "stub"


def test_cloud_llm_providers_forbidden():
    for provider in ("openai", "anthropic", "gemini", "perplexity"):
        try:
            validate_llm_provider(provider)
            assert False, f"{provider} should be forbidden"
        except AppError as e:
            assert e.code == "cloud_llm_forbidden"


def test_cloud_vision_providers_forbidden():
    for provider in ("google_vision", "aws_textract", "azure_ocr", "openai_vision", "gemini_vision", "claude_vision"):
        try:
            validate_vision_provider(provider)
            assert False, f"{provider} should be forbidden"
        except AppError as e:
            assert e.code == "cloud_vision_forbidden"


def test_local_llm_providers_allowed():
    validate_llm_provider("stub")
    validate_llm_provider("ollama")
    validate_llm_provider("lmstudio")


def test_local_vision_providers_allowed():
    validate_vision_provider("stub")


async def test_no_cloud_sdks_imported():
    """Verify forbidden SDKs are not accidentally importable from app code."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"


async def test_upload_and_run_uses_no_external_runtime():
    """Verify default test flow works without external services."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create = await client.post(
            "/creative-assets",
            json={"title": "Offline Test", "asset_type": "text", "text_content": "Offline content."},
        )
        asset_id = create.json()["id"]
        run = await client.post("/test-runs", json={"creative_asset_id": asset_id})
        run_id = run.json()["id"]
        run_result = await client.post(f"/test-runs/{run_id}/run")
    assert run_result.status_code == 200
    assert run_result.json()["status"] == "completed"
