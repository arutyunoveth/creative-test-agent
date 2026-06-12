"""Tests for build_client_pilot_pack.py script."""

import os
import sys
import tempfile

SOURCES_DIR = os.path.join(os.path.dirname(__file__), "..")


def test_import_build_client_pilot_pack():
    """Script should import without errors."""
    sys.path.insert(0, SOURCES_DIR)
    import scripts.build_client_pilot_pack  # noqa: F401


def test_build_pack_creates_directory():
    """build_pack() should create the output directory."""
    sys.path.insert(0, SOURCES_DIR)
    from scripts.build_client_pilot_pack import build_pack

    with tempfile.TemporaryDirectory() as tmpdir:
        pack_dir = os.path.join(tmpdir, "client_pilot_pack")
        result = build_pack(pack_dir)
        assert os.path.isdir(result), f"Directory not created: {result}"


def test_build_pack_creates_manifest():
    """build_pack() should create a manifest.txt."""
    sys.path.insert(0, SOURCES_DIR)
    from scripts.build_client_pilot_pack import build_pack

    with tempfile.TemporaryDirectory() as tmpdir:
        pack_dir = os.path.join(tmpdir, "client_pilot_pack")
        build_pack(pack_dir)
        manifest = os.path.join(pack_dir, "manifest.txt")
        assert os.path.isfile(manifest), f"Missing manifest: {manifest}"
        with open(manifest) as f:
            content = f.read()
        assert "Client Pilot Pack" in content


def test_build_pack_includes_docs():
    """build_pack() should include docs/client_pilot/ contents."""
    sys.path.insert(0, SOURCES_DIR)
    from scripts.build_client_pilot_pack import build_pack

    with tempfile.TemporaryDirectory() as tmpdir:
        pack_dir = os.path.join(tmpdir, "client_pilot_pack")
        build_pack(pack_dir)
        scope_doc = os.path.join(pack_dir, "docs", "client_pilot", "pilot_scope_ru.md")
        assert os.path.isfile(scope_doc), f"Missing: {scope_doc}"


def test_build_pack_includes_profiles():
    """build_pack() should include config/pilot_profiles/."""
    sys.path.insert(0, SOURCES_DIR)
    from scripts.build_client_pilot_pack import build_pack

    with tempfile.TemporaryDirectory() as tmpdir:
        pack_dir = os.path.join(tmpdir, "client_pilot_pack")
        build_pack(pack_dir)
        profile = os.path.join(pack_dir, "config", "pilot_profiles", "novabank_demo.json")
        assert os.path.isfile(profile), f"Missing: {profile}"


def test_build_pack_includes_scripts():
    """build_pack() should include scripts like load_pilot_profile.py."""
    sys.path.insert(0, SOURCES_DIR)
    from scripts.build_client_pilot_pack import build_pack

    with tempfile.TemporaryDirectory() as tmpdir:
        pack_dir = os.path.join(tmpdir, "client_pilot_pack")
        build_pack(pack_dir)
        loader = os.path.join(pack_dir, "scripts", "load_pilot_profile.py")
        assert os.path.isfile(loader), f"Missing: {loader}"


def test_build_pack_creates_zip():
    """build_pack() should create a .zip archive alongside the directory."""
    sys.path.insert(0, SOURCES_DIR)
    from scripts.build_client_pilot_pack import build_pack

    with tempfile.TemporaryDirectory() as tmpdir:
        pack_dir = os.path.join(tmpdir, "client_pilot_pack")
        build_pack(pack_dir)
        zip_path = f"{pack_dir}.zip"
        assert os.path.isfile(zip_path), f"Missing zip: {zip_path}"
        assert os.path.getsize(zip_path) > 0


def test_build_pack_includes_makefile():
    """build_pack() should include Makefile."""
    sys.path.insert(0, SOURCES_DIR)
    from scripts.build_client_pilot_pack import build_pack

    with tempfile.TemporaryDirectory() as tmpdir:
        pack_dir = os.path.join(tmpdir, "client_pilot_pack")
        build_pack(pack_dir)
        makefile = os.path.join(pack_dir, "Makefile")
        assert os.path.isfile(makefile), f"Missing: {makefile}"
