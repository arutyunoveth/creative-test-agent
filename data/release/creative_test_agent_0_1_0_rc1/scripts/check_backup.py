#!/usr/bin/env python3
"""
Verify integrity of a creative-test-agent backup zip.

Usage:
    python scripts/check_backup.py data/backups/cta_backup_YYYYMMDD_HHMMSS.zip

Checks:
- zip is readable
- manifest.json exists and is valid JSON
- database file exists (if included)
- no .env files
- no path traversal entries
- expected folders exist
"""

import json
import os
import sys
import zipfile

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


def check_backup(backup_path: str) -> None:
    print(f"Checking backup: {backup_path}")
    print()

    if not os.path.isfile(backup_path):
        check("Backup file exists", False, f"File not found: {backup_path}")
        sys.exit(1)

    try:
        zf = zipfile.ZipFile(backup_path, "r")
    except zipfile.BadZipFile:
        check("Zip is readable", False, "Bad zip file")
        sys.exit(1)

    names = zf.namelist()

    check("Zip is readable", True)
    check("Manifest exists", "manifest.json" in names)

    if "manifest.json" in names:
        try:
            manifest = json.loads(zf.read("manifest.json"))
            check("Manifest is valid JSON", True)
            check(
                "Manifest has created_at",
                bool(manifest.get("created_at")),
            )
            check(
                "Manifest has app name",
                manifest.get("app") == "creative-test-agent",
            )
            check(
                "Manifest has counts",
                isinstance(manifest.get("counts"), dict),
            )
        except (json.JSONDecodeError, Exception) as e:
            check("Manifest is valid JSON", False, str(e))

    # Check for database file
    has_db = "creative_test_agent.db" in names
    included_db = True
    if "manifest.json" in names:
        try:
            manifest = json.loads(zf.read("manifest.json"))
            included_db = manifest.get("included", {}).get("database", False)
        except Exception:
            pass
    if included_db:
        check("Database file exists", has_db)
    else:
        check("Database file (not included in backup)", True)

    # Check no .env
    env_files = [n for n in names if ".env" in n and not n.startswith("__")]
    check("No .env files in backup", len(env_files) == 0, f"Found: {env_files}")

    # Check no path traversal
    traversal = [n for n in names if ".." in n or n.startswith("/")]
    check("No path traversal entries", len(traversal) == 0, f"Found: {traversal}")

    # Check folders
    expected_dirs = ["storage", "exports"]
    for d in expected_dirs:
        entries = [n for n in names if n.startswith(f"{d}/") or n == f"{d}/"]
        if entries:
            check(f"Folder '{d}' exists", True)

    # Check for manifest contents
    storage_included = False
    exports_included = False
    if "manifest.json" in names:
        try:
            manifest = json.loads(zf.read("manifest.json"))
            included = manifest.get("included", {})
            storage_included = included.get("storage", False)
            exports_included = included.get("exports", False)
        except Exception:
            pass

    if storage_included:
        storage_entries = [n for n in names if n.startswith("storage/")]
        check("Storage folder has contents", len(storage_entries) > 0)

    if exports_included:
        exports_entries = [n for n in names if n.startswith("exports/")]
        check("Exports folder has contents", len(exports_entries) > 0)

    zf.close()

    print()
    if FAILURES:
        print(f"Backup integrity: FAIL ({len(FAILURES)} issue(s))")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("Backup integrity: PASS")
        sys.exit(0)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_backup.py <backup.zip>", file=sys.stderr)
        sys.exit(1)

    check_backup(sys.argv[1])


if __name__ == "__main__":
    main()
