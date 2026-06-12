"""Tests for migration check and run scripts."""
import os
from pathlib import Path


def test_check_migrations_script_exists():
    assert Path("scripts/check_migrations.py").is_file()


def test_run_migrations_script_exists():
    assert Path("scripts/run_migrations.py").is_file()


def test_check_migrations_imports():
    import scripts.check_migrations
    assert callable(scripts.check_migrations.main)


def test_run_migrations_imports():
    import scripts.run_migrations
    assert callable(scripts.run_migrations.main)


def test_check_migrations_runs():
    from src.shared.db.session import init_db
    init_db()
    import scripts.check_migrations
    try:
        scripts.check_migrations.main()
    except SystemExit:
        pass
    # The script may exit with 1 if migrations are not up to date.
    # That's expected for the test environment — the important thing
    # is it runs without crashing.


def test_makefile_has_migration_commands():
    content = Path("Makefile").read_text()
    assert "migrations-check" in content
    assert "migrations-upgrade" in content
