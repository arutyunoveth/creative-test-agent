#!/usr/bin/env python3
"""
Restore creative-test-agent data from a backup zip.

Usage:
    python scripts/restore_data.py data/backups/cta_backup_YYYYMMDD_HHMMSS.zip [--force]

Creates a pre-restore backup automatically.
Refuses to restore if the app appears to be running, unless --force is passed.
"""

import json
import os
import shutil
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _detect_app_running() -> bool:
    try:
        import http.client
        conn = http.client.HTTPConnection("localhost", 8000, timeout=3)
        conn.request("GET", "/health")
        resp = conn.getresponse()
        conn.close()
        return resp.status == 200
    except Exception:
        return False


def restore_backup(backup_path: str, force: bool = False) -> None:
    from src.shared.config.settings import get_settings

    settings = get_settings()

    if not os.path.isfile(backup_path):
        print(f"Backup file not found: {backup_path}", file=sys.stderr)
        sys.exit(1)

    if not force and _detect_app_running():
        print(
            "ERROR: App appears to be running on localhost:8000. "
            "Stop the app first or use --force.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Verify backup structure
    with zipfile.ZipFile(backup_path, "r") as zf:
        names = zf.namelist()
        if "manifest.json" not in names:
            print("ERROR: Backup is missing manifest.json", file=sys.stderr)
            sys.exit(1)
        for name in names:
            if name.startswith(".env") or "/.env" in name:
                print(f"ERROR: Backup contains .env file: {name}", file=sys.stderr)
                sys.exit(1)
            if ".." in name or name.startswith("/"):
                print(f"ERROR: Backup contains path traversal: {name}", file=sys.stderr)
                sys.exit(1)

        manifest = json.loads(zf.read("manifest.json"))
        print(f"Restoring backup from: {os.path.basename(backup_path)}")
        print(f"  Created: {manifest.get('created_at', 'unknown')}")
        print(f"  Entities: {json.dumps(manifest.get('counts', {}), default=str)}")

    # Create pre-restore backup
    print("Creating pre-restore backup...")
    try:
        from scripts.backup_data import create_backup
        backup_root = os.path.abspath(settings.backup_root)
        os.makedirs(backup_root, exist_ok=True)
        pre_restore_path = os.path.join(
            backup_root,
            f"pre_restore_{os.path.basename(backup_path)}",
        )
        create_backup(pre_restore_path)
    except Exception as e:
        print(f"Warning: Could not create pre-restore backup: {e}")

    # Extract backup
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(backup_path, "r") as zf:
            zf.extractall(tmpdir)

        # Restore database
        db_url = settings.database_url
        if db_url.startswith("sqlite:///"):
            db_path = os.path.abspath(db_url.replace("sqlite:///", ""))
            backup_db = os.path.join(tmpdir, "creative_test_agent.db")
            if os.path.isfile(backup_db):
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                shutil.copy2(backup_db, db_path)
                print(f"  Database restored: {db_path}")
            else:
                print("  Warning: No database file in backup")

        # Restore storage
        backup_storage = os.path.join(tmpdir, "storage")
        if os.path.isdir(backup_storage):
            storage_root = os.path.abspath(settings.storage_root)
            shutil.rmtree(storage_root, ignore_errors=True)
            shutil.copytree(backup_storage, storage_root, dirs_exist_ok=True)
            print(f"  Storage restored: {storage_root}")
        else:
            print("  No storage folder in backup")

        # Restore exports
        backup_exports = os.path.join(tmpdir, "exports")
        if os.path.isdir(backup_exports):
            exports_root = os.path.abspath(settings.exports_root)
            shutil.rmtree(exports_root, ignore_errors=True)
            shutil.copytree(backup_exports, exports_root, dirs_exist_ok=True)
            print(f"  Exports restored: {exports_root}")
        else:
            print("  No exports folder in backup")

    print("Restore completed.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/restore_data.py <backup.zip> [--force]", file=sys.stderr)
        sys.exit(1)

    backup_path = sys.argv[1]
    force = "--force" in sys.argv
    restore_backup(backup_path, force)


if __name__ == "__main__":
    main()
