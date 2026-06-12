"""Verify Alembic can import and access migration metadata."""

import os
import tempfile


def test_alembic_imports():
    """Alembic config and env should be importable without errors."""
    import alembic.config
    import alembic.script

    cfg = alembic.config.Config("alembic.ini")
    script = alembic.script.ScriptDirectory.from_config(cfg)
    heads = script.get_heads()
    assert len(heads) == 1, f"Expected 1 migration head, got {len(heads)}: {heads}"


def test_alembic_migration_applies_cleanly():
    """Apply the migration against a temporary SQLite file, verify tables, downgrade."""
    import alembic.command
    import alembic.config
    from sqlalchemy import create_engine, inspect

    expected_tables = {
        "creative_asset",
        "brand_profile",
        "audience_profile",
        "test_rubric",
        "test_run",
        "report",
        "audit_event",
    }
    # alembic_version is managed by alembic itself, not by our migrations
    # We exclude it from the downgrade check because our downgrade only drops
    # application tables (it does not drop alembic_version).

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_path = f.name

    try:
        cfg = alembic.config.Config("alembic.ini")
        cfg.set_main_option("sqlalchemy.url", f"sqlite:///{temp_path}")
        alembic.command.upgrade(cfg, "head")

        engine = create_engine(f"sqlite:///{temp_path}")
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        missing = expected_tables - tables
        assert not missing, f"Tables missing after upgrade: {missing}"

        alembic.command.downgrade(cfg, "base")
        engine2 = create_engine(f"sqlite:///{temp_path}")
        inspector2 = inspect(engine2)
        tables2 = set(inspector2.get_table_names())
        # Only our application tables should be gone; alembic_version may remain
        remaining = tables2 & expected_tables
        assert not remaining, f"Our tables remain after downgrade: {remaining}"
    finally:
        os.unlink(temp_path)
