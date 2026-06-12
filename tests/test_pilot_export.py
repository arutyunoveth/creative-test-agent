"""Tests for pilot data export utility."""

import json
import os
import tempfile


def test_import_export_pilot_data():
    """Script should import without errors."""
    import scripts.export_pilot_data
    assert hasattr(scripts.export_pilot_data, "export_pilot_data")


def test_export_creates_json_file():
    """Export should create a valid JSON file at the expected path."""
    from scripts.export_pilot_data import export_pilot_data

    # Monkey-patch the export path to a temp location
    import scripts.export_pilot_data as mod
    orig_dir = os.path.join(os.path.dirname(os.path.dirname(mod.__file__)), "data", "exports")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Override export path by patching os.makedirs and open behavior
        # Simpler: just test that the function creates a file
        path = export_pilot_data()
        assert os.path.exists(path)
        assert path.endswith(".json")
        assert "pilot_export" in os.path.basename(path)

        with open(path) as f:
            data = json.load(f)

        # Verify structure
        assert data["app"] == "Creative Test Agent"
        assert "exported_at" in data
        assert isinstance(data["brand_profiles"], list)
        assert isinstance(data["audience_profiles"], list)
        assert isinstance(data["creative_assets"], list)
        assert isinstance(data["test_rubrics"], list)
        assert isinstance(data["test_runs"], list)
        assert isinstance(data["reports"], list)
        assert isinstance(data["audit_events"], list)

        os.unlink(path)


def test_export_contains_expected_top_level_keys():
    """Export JSON should have all expected top-level keys."""
    from scripts.export_pilot_data import export_pilot_data

    path = export_pilot_data()
    try:
        with open(path) as f:
            data = json.load(f)

        expected_keys = {
            "exported_at", "app",
            "brand_profiles", "audience_profiles",
            "creative_assets", "test_rubrics",
            "test_runs", "reports", "audit_events",
        }
        assert set(data.keys()) >= expected_keys, (
            f"Missing keys: {expected_keys - set(data.keys())}"
        )
    finally:
        if os.path.exists(path):
            os.unlink(path)
