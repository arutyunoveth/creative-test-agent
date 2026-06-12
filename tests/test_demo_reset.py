"""Tests for demo data reset utility."""

import json


def test_import_reset_demo_data():
    """Script should import without errors."""
    import scripts.reset_demo_data
    assert hasattr(scripts.reset_demo_data, "reset_demo_data")


async def test_seed_creates_demo_data():
    """Seed should create demo-tagged entities via the API."""
    from httpx import ASGITransport, AsyncClient
    from src.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create demo brand profile
        resp = await client.post("/brand-profiles", json={
            "name": "DemoBrand",
            "tone_of_voice": "Test",
            "target_audience": "Test",
            "metadata": {"demo": True, "demo_scenario": "test"},
        })
        assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
        brand_id = resp.json()["id"]
        assert resp.json()["metadata"]["demo"] is True

        # Create demo audience profile
        resp = await client.post("/audience-profiles", json={
            "name": "DemoAudience",
            "segment_description": "Test segment",
            "metadata": {"demo": True, "demo_scenario": "test"},
        })
        assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
        assert resp.json()["metadata"]["demo"] is True

        # Create demo rubric
        resp = await client.post("/test-rubrics", json={
            "name": "DemoRubric",
            "criteria": [{"name": "test", "description": "test"}],
            "metadata": {"demo": True, "demo_scenario": "test"},
        })
        assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
        assert resp.json()["metadata"]["demo"] is True

        # Create demo creative asset
        resp = await client.post("/creative-assets", json={
            "title": "DemoAsset",
            "asset_type": "text",
            "text_content": "Demo",
            "metadata": {"demo": True, "demo_scenario": "test"},
        })
        assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
        asset_id = resp.json()["id"]

    # Reset demo data
    from scripts.reset_demo_data import reset_demo_data
    counts = reset_demo_data()

    assert counts["brand_profiles"] >= 1
    assert counts["audience_profiles"] >= 1
    assert counts["creative_assets"] >= 1


async def test_reset_does_not_remove_non_demo_data():
    """Reset should leave non-demo entities untouched."""
    from httpx import ASGITransport, AsyncClient
    from src.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/brand-profiles", json={
            "name": "RealBrand",
            "tone_of_voice": "Real",
        })
        assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
        real_brand_id = resp.json()["id"]

    from scripts.reset_demo_data import reset_demo_data
    reset_demo_data()

    # Real brand should still exist
    from src.modules.brand_profiles.service import get_profile
    profile = get_profile(real_brand_id)
    assert profile is not None, "Non-demo brand was removed by reset"
    assert profile.name == "RealBrand"


async def test_seed_after_reset_works():
    """Seeding after reset should recreate demo data."""
    from scripts.reset_demo_data import reset_demo_data
    reset_demo_data()

    from httpx import ASGITransport, AsyncClient
    from src.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/brand-profiles", json={
            "name": "RebornBrand",
            "metadata": {"demo": True},
        })
        assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
        assert resp.json()["metadata"]["demo"] is True


def test_reset_returns_counts():
    """reset_demo_data should return a dict with counts per entity type."""
    from scripts.reset_demo_data import reset_demo_data
    counts = reset_demo_data()
    assert isinstance(counts, dict)
    for key in ("brand_profiles", "audience_profiles", "creative_assets",
                "test_rubrics", "test_runs"):
        assert key in counts
        assert isinstance(counts[key], int)
