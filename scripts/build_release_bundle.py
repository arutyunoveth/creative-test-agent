"""
Build release bundle for Creative Test Agent.

Output:
    data/release/creative_test_agent_<version>/
    data/release/creative_test_agent_<version>.zip

Excludes:
    - .env, .env.server
    - data/db, data/storage, data/exports, data/backups
    - __pycache__, .pytest_cache, .git
    - secrets, local SQLite databases
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime, timezone

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from src.shared.version import APP_NAME, APP_VERSION

INCLUDED_PATHS = [
    "README.md",
    ".env.server.example",
    "docker-compose.server.yml",
    "Dockerfile",
    "Makefile",
    "pyproject.toml",
    "requirements.txt",
    "alembic.ini",
]

INCLUDED_DIRS = [
    "docs",
    "config",
    "scripts",
    "migrations",
    "src",
]

EXCLUDED_PATTERNS = [
    "__pycache__", ".pytest_cache", ".git", ".env",
    ".env.server", ".DS_Store", "*.pyc",
]

EXCLUDED_DIR_PREFIXES = [
    "data/db", "data/storage", "data/exports", "data/backups",
]

LOCAL_ONLY_POLICY = {
    "local_only": True,
    "cloud_llm": False,
    "cloud_storage": False,
    "external_apis": False,
}


def _should_exclude(rel_path: str) -> bool:
    for prefix in EXCLUDED_DIR_PREFIXES:
        if rel_path.startswith(prefix):
            return True
    for pat in EXCLUDED_PATTERNS:
        if pat.startswith("*."):
            if rel_path.endswith(pat[1:]):
                return True
        elif pat in rel_path:
            return True
    return False


def build_bundle() -> str:
    version_slug = APP_VERSION.replace(".", "_").replace("-", "_")
    output_dir = os.path.join(PROJECT_ROOT, "data", "release", f"creative_test_agent_{version_slug}")
    bundle_dir = os.path.abspath(output_dir)

    if os.path.isdir(bundle_dir):
        shutil.rmtree(bundle_dir)
    os.makedirs(bundle_dir, exist_ok=True)

    included_paths: list[str] = []

    for rel_path in INCLUDED_PATHS:
        src = os.path.join(PROJECT_ROOT, rel_path)
        if os.path.isfile(src):
            dst = os.path.join(bundle_dir, rel_path)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            included_paths.append(rel_path)

    for dir_rel in INCLUDED_DIRS:
        src_dir = os.path.join(PROJECT_ROOT, dir_rel)
        if not os.path.isdir(src_dir):
            continue
        for root, dirs, files in os.walk(src_dir):
            rel_root = os.path.relpath(root, PROJECT_ROOT)
            dirs[:] = [d for d in dirs if not _should_exclude(os.path.join(rel_root, d))]
            for f in files:
                rel_path = os.path.join(rel_root, f)
                if _should_exclude(rel_path):
                    continue
                src_path = os.path.join(root, f)
                dst_path = os.path.join(bundle_dir, rel_path)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)
                included_paths.append(rel_path)

    # Copy release manifest if exists
    manifest_src = os.path.join(PROJECT_ROOT, "data", "release", "release_manifest.json")
    if os.path.isfile(manifest_src):
        dst = os.path.join(bundle_dir, "release_manifest.json")
        shutil.copy2(manifest_src, dst)
        included_paths.append("release_manifest.json")

    # Copy client pack if exists
    pack_src = os.path.join(PROJECT_ROOT, "data", "client_pilot_pack.zip")
    if os.path.isfile(pack_src):
        dst = os.path.join(bundle_dir, "client_pilot_pack.zip")
        shutil.copy2(pack_src, dst)
        included_paths.append("client_pilot_pack.zip")

    # Build bundle manifest
    bundle_manifest = {
        "app": APP_NAME,
        "version": APP_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "included_paths": sorted(included_paths),
        "excluded_sensitive_patterns": EXCLUDED_PATTERNS + EXCLUDED_DIR_PREFIXES,
        "local_only": LOCAL_ONLY_POLICY["local_only"],
    }
    manifest_path = os.path.join(bundle_dir, "bundle_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(bundle_manifest, f, indent=2, ensure_ascii=False)

    # Create ZIP
    zip_path = f"{bundle_dir}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(bundle_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                arcname = os.path.relpath(file_path, os.path.dirname(bundle_dir))
                zf.write(file_path, arcname)

    print(f"Release bundle built at: {bundle_dir}")
    print(f"Archive: {zip_path}")
    print(f"Version: {APP_VERSION}")
    print(f"Files included: {len(included_paths)}")
    print(f"Excluded sensitive patterns: {EXCLUDED_PATTERNS + EXCLUDED_DIR_PREFIXES}")

    return bundle_dir


def main():
    build_bundle()
    return 0


if __name__ == "__main__":
    sys.exit(main())
