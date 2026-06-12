"""Tests for backup and restore scripts."""
import json
import os
import tempfile
import zipfile
from pathlib import Path


def test_backup_script_imports():
    from scripts.backup_data import create_backup, get_entity_counts
    assert callable(create_backup)
    assert callable(get_entity_counts)


def test_restore_script_imports():
    from scripts.restore_data import restore_backup
    assert callable(restore_backup)


def test_get_entity_counts():
    from scripts.backup_data import get_entity_counts
    counts = get_entity_counts()
    assert isinstance(counts, dict)
    assert "clients" in counts
    assert "projects" in counts
    assert "test_runs" in counts


def test_backup_creates_zip():
    from scripts.backup_data import create_backup

    with tempfile.TemporaryDirectory() as tmpdir:
        backup_path = os.path.join(tmpdir, "test_backup.zip")
        result = create_backup(backup_path)
        assert os.path.isfile(result)
        assert result == backup_path
        assert zipfile.is_zipfile(result)


def test_backup_zip_contains_manifest():
    from scripts.backup_data import create_backup

    with tempfile.TemporaryDirectory() as tmpdir:
        backup_path = os.path.join(tmpdir, "test_manifest.zip")
        create_backup(backup_path)
        with zipfile.ZipFile(backup_path, "r") as zf:
            names = zf.namelist()
            assert "manifest.json" in names
            manifest = json.loads(zf.read("manifest.json"))
            assert manifest["app"] == "creative-test-agent"
            assert "created_at" in manifest
            assert "counts" in manifest
            assert "database_url_type" in manifest


def test_backup_excludes_env():
    from scripts.backup_data import create_backup

    with tempfile.TemporaryDirectory() as tmpdir:
        backup_path = os.path.join(tmpdir, "test_noenv.zip")
        create_backup(backup_path)
        with zipfile.ZipFile(backup_path, "r") as zf:
            names = zf.namelist()
            env_files = [n for n in names if ".env" in n and not n.startswith("__")]
            assert len(env_files) == 0, f"Found .env files: {env_files}"


def test_backup_has_no_path_traversal():
    from scripts.backup_data import create_backup

    with tempfile.TemporaryDirectory() as tmpdir:
        backup_path = os.path.join(tmpdir, "test_safe.zip")
        create_backup(backup_path)
        with zipfile.ZipFile(backup_path, "r") as zf:
            names = zf.namelist()
            traversal = [n for n in names if ".." in n or n.startswith("/")]
            assert len(traversal) == 0, f"Path traversal: {traversal}"


def test_restore_script_validates_backup_structure():
    from scripts.restore_data import restore_backup

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a valid backup first
        from scripts.backup_data import create_backup
        backup_path = os.path.join(tmpdir, "test_restore.zip")
        create_backup(backup_path)

        # Should not raise
        restore_backup(backup_path, force=True)


def test_restore_script_rejects_missing_manifest():
    from scripts.restore_data import restore_backup

    with tempfile.TemporaryDirectory() as tmpdir:
        bad_zip = os.path.join(tmpdir, "bad.zip")
        with zipfile.ZipFile(bad_zip, "w") as zf:
            zf.writestr("some_file.txt", "data")

        import subprocess
        result = subprocess.run(
            [".venv/bin/python", "scripts/restore_data.py", bad_zip, "--force"],
            capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__ + "/..")),
        )
        assert "ERROR" in result.stderr or "missing manifest" in result.stderr.lower()
