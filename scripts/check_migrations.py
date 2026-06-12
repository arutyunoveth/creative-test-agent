#!/usr/bin/env python3
"""
Check Alembic migration status.

Reports:
- Database reachable
- Current Alembic head revision
- Current database revision
- Whether migrations are up to date
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

FAILURES: list[str] = []


def check(message: str, ok: bool, detail: str = "") -> None:
    if ok:
        print(f"  ✓ {message}")
    else:
        print(f"  ✗ {message}")
        if detail:
            print(f"    {detail}")
        FAILURES.append(message)


def main() -> None:
    print("Migration status check")
    print()

    # Check DB reachable
    try:
        from src.shared.db.session import check_db_connection, init_db
        init_db()
        connected = check_db_connection()
        check("Database reachable", connected)
    except Exception as e:
        check("Database reachable", False, str(e))
        print("\nFAIL")
        sys.exit(1)

    # Check Alembic configuration
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory

        alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
        script = ScriptDirectory.from_config(alembic_cfg)
        head = script.get_current_head()
        check("Alembic head revision found", head is not None)
        print(f"  Current head: {head}")
    except Exception as e:
        check("Alembic head revision found", False, str(e))
        print("\nFAIL")
        sys.exit(1)

    # Check current DB revision
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        from alembic.runtime.environment import EnvironmentContext
        from alembic.runtime.migration import MigrationContext
        from sqlalchemy import create_engine
        from src.shared.config.settings import get_settings

        settings = get_settings()
        db_url = settings.database_url
        engine = create_engine(db_url)
        conn = engine.connect()
        mctx = MigrationContext.configure(conn)
        db_rev = mctx.get_current_revision()
        conn.close()
        engine.dispose()

        if db_rev:
            check("Current DB revision found", True)
            print(f"  DB revision: {db_rev}")
        else:
            check("Current DB revision found", False, "No revision — database may be empty")
            db_rev = None
    except Exception as e:
        check("Current DB revision found", False, str(e))
        db_rev = None

    # Compare
    if head and db_rev:
        up_to_date = head == db_rev
        check(f"Migrations up to date ({head} == {db_rev})", up_to_date)
        if not up_to_date:
            check("Run 'python scripts/run_migrations.py' to upgrade", False)
    elif head:
        check("No database revision — run migrations", False)

    print()
    if FAILURES:
        print(f"Migration check: FAIL ({len(FAILURES)} issue(s))")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("Migration check: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
