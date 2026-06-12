"""Tests for load_pilot_profile.py script."""

import json
import os
import sys
import tempfile

SOURCES_DIR = os.path.join(os.path.dirname(__file__), "..")


def _make_profile(profile_name: str = "test_profile", demo: bool = True) -> dict:
    return {
        "profile_name": profile_name,
        "demo": demo,
        "description": "Test profile for unit tests",
        "brand": {
            "name": "TestBrand",
            "tone_of_voice": "Test tone",
            "target_audience": "Test audience",
            "restrictions": "Test restrictions",
            "claims_policy": "Test claims policy",
        },
        "audiences": [
            {
                "name": "Test Audience One",
                "segment_description": "First test segment",
                "pains": "Test pains",
                "motivations": "Test motivations",
                "objections": "Test objections",
            },
        ],
        "rubric": {
            "name": "Test Rubric",
            "criteria": [
                {"name": "test_criterion", "description": "A test criterion"},
            ],
            "scale_min": 1,
            "scale_max": 10,
        },
        "creative_assets": [
            {
                "title": "Test Creative",
                "asset_type": "text",
                "text_content": "Test content for the creative.",
                "variant": "A",
                "variant_description": "test variant",
            },
        ],
        "report_preferences": {
            "default_mode": "internal",
            "formats": ["markdown"],
        },
    }


def test_import_load_pilot_profile():
    """Script should import without errors."""
    sys.path.insert(0, SOURCES_DIR)
    import scripts.load_pilot_profile  # noqa: F401


def test_load_profile_creates_brand():
    """load_profile() should create a brand profile."""
    sys.path.insert(0, SOURCES_DIR)
    from scripts.load_pilot_profile import load_profile
    from src.shared.db.repository import db_session
    from src.modules.brand_profiles.models import BrandProfile

    profile = _make_profile("test_load_brand")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(profile, f)
        tmp_path = f.name

    try:
        created = load_profile(tmp_path)
        assert created >= 1, "Should have created at least 1 entity"

        with db_session() as db:
            brands = db.query(BrandProfile).all()
            brand_names = [b.name for b in brands]
            assert "TestBrand" in brand_names
    finally:
        os.unlink(tmp_path)


def test_load_profile_idempotent():
    """Loading the same profile twice should not create duplicates."""
    sys.path.insert(0, SOURCES_DIR)
    from scripts.load_pilot_profile import load_profile
    from src.shared.db.repository import db_session
    from src.modules.brand_profiles.models import BrandProfile

    uid = "test_idempotent"
    profile = _make_profile(uid)
    profile["brand"]["name"] = f"IdempotentBrand_{uid}"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(profile, f)
        tmp_path = f.name

    try:
        first = load_profile(tmp_path)
        second = load_profile(tmp_path)
        assert first >= 1
        assert second == 0, "Second load should create 0 new entities"

        with db_session() as db:
            count = db.query(BrandProfile).filter(
                BrandProfile.name == f"IdempotentBrand_{uid}"
            ).count()
            assert count == 1, "Should only have 1 brand profile"
    finally:
        os.unlink(tmp_path)


def test_load_profile_minimal():
    """Minimal profile (brand only) should work."""
    sys.path.insert(0, SOURCES_DIR)
    from scripts.load_pilot_profile import load_profile
    from src.shared.db.repository import db_session
    from src.modules.brand_profiles.models import BrandProfile

    profile = {
        "profile_name": "minimal_test",
        "demo": False,
        "description": "Minimal",
        "brand": {"name": "MinimalBrand"},
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(profile, f)
        tmp_path = f.name

    try:
        created = load_profile(tmp_path)
        assert created >= 1

        with db_session() as db:
            brands = db.query(BrandProfile).filter(BrandProfile.name == "MinimalBrand").all()
            assert len(brands) == 1
    finally:
        os.unlink(tmp_path)


def test_load_profile_custom_name():
    """Custom profile_name passed as argument overrides JSON profile_name."""
    sys.path.insert(0, SOURCES_DIR)
    from scripts.load_pilot_profile import load_profile

    uid = "test_custom_name"
    profile = _make_profile("original_name")
    profile["brand"]["name"] = f"CustomBrand_{uid}"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(profile, f)
        tmp_path = f.name

    try:
        first = load_profile(tmp_path, profile_name="custom_override")
        second = load_profile(tmp_path, profile_name="custom_override")
        assert first >= 1
        assert second == 0, "Second load with same custom name should create 0 entities"
    finally:
        os.unlink(tmp_path)
