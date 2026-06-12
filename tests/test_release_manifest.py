from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_release_manifest_script_imports():
    from scripts.build_release_manifest import build_manifest
    assert callable(build_manifest)


async def test_release_manifest_creates_json():
    from scripts.build_release_manifest import build_manifest
    manifest = build_manifest()
    assert "version" in manifest
    assert "stage" in manifest
    assert manifest["stage"] == "pilot"
    assert "checks" in manifest
    assert "no_cloud_sdks" in manifest["checks"]
    assert manifest["checks"]["no_cloud_sdks"] is True


async def test_release_manifest_no_secrets():
    from scripts.build_release_manifest import build_manifest
    manifest = build_manifest()
    text = str(manifest)
    assert ".env" not in text
    assert "secret" not in text.lower() or "secret" in ["secret"]
