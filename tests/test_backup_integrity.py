"""Tests for backup integrity checking."""
import os
import tempfile
import zipfile

from scripts.backup_data import create_backup
from scripts.check_backup import check_backup


def test_check_backup_script_imports():
    from scripts.check_backup import check_backup
    assert callable(check_backup)


def test_check_backup_validates_generated_backup():
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_path = os.path.join(tmpdir, "test_check.zip")
        create_backup(backup_path)
        # Should not raise SystemExit(1)
        try:
            check_backup(backup_path)
        except SystemExit as e:
            assert e.code == 0, f"check_backup failed with code {e.code}"


def test_check_backup_fails_on_missing_file():
    from scripts.check_backup import check_backup
    try:
        check_backup("/nonexistent/backup.zip")
    except SystemExit as e:
        assert e.code != 0
    else:
        assert False, "Should have exited with error"


def test_check_backup_fails_on_bad_zip():
    import subprocess
    result = subprocess.run(
        [".venv/bin/python", "scripts/check_backup.py", "/nonexistent/bad.zip"],
        capture_output=True, text=True,
        cwd=os.path.dirname(os.path.abspath(__file__ + "/..")),
    )
    assert result.returncode != 0


def test_check_backup_detects_missing_manifest():
    with tempfile.TemporaryDirectory() as tmpdir:
        bad_zip = os.path.join(tmpdir, "no_manifest.zip")
        with zipfile.ZipFile(bad_zip, "w") as zf:
            zf.writestr("some_file.txt", "data")
        try:
            check_backup(bad_zip)
        except SystemExit as e:
            assert e.code != 0
        else:
            assert False, "Should have exited with error"


def test_backup_integrity_checker_script_exists():
    from pathlib import Path
    assert Path("scripts/check_backup.py").is_file()
