#!/usr/bin/env python3
"""
Run Alembic migrations to upgrade to the latest revision.

Usage:
    python scripts/run_migrations.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def main() -> None:
    from alembic.config import Config
    from alembic import command

    print("Running migrations...")

    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))

    try:
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully.")
    except Exception as e:
        print(f"Migration failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
