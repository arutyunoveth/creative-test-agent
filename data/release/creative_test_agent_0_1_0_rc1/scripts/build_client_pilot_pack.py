"""
Build a client pilot pack: collect documentation, config, and scripts
into a single directory and create a ZIP archive.

Usage:
    python scripts/build_client_pilot_pack.py [output_dir]

Output:
    data/client_pilot_pack/  (directory with unpacked files)
    data/client_pilot_pack.zip  (archive of the same)
"""

import os
import shutil
import sys
import zipfile
from datetime import datetime, timezone

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE_DIRS = {
    "docs/client_pilot": "docs/client_pilot",
    "config/pilot_profiles": "config/pilot_profiles",
    "docs/releases": "docs/releases",
    "docs/deployment": "docs/deployment",
    "docs": "docs",
}

SOURCE_FILES = [
    "scripts/load_pilot_profile.py",
    "scripts/seed_demo_data.py",
    "scripts/check_closed_loop.py",
    "scripts/check_demo_readiness.py",
    "scripts/export_pilot_data.py",
    "scripts/build_release_manifest.py",
    "scripts/release_check.py",
    "scripts/run_demo_batch.py",
    "scripts/run_pilot_smoke.py",
    "scripts/verify_release_install.py",
    "scripts/build_release_bundle.py",
    "Makefile",
]

EXCLUDE_PATTERNS = ["__pycache__", ".DS_Store", "*.pyc"]


def _should_exclude(name: str) -> bool:
    for pat in EXCLUDE_PATTERNS:
        if pat.startswith("*."):
            if name.endswith(pat[1:]):
                return True
        elif pat in name:
            return True
    return False


def _collect_files(source_dir: str, pack_dir: str, subdir: str) -> list[str]:
    copied = []
    src = os.path.join(PROJECT_ROOT, source_dir)
    dst = os.path.join(pack_dir, subdir)
    if not os.path.isdir(src):
        return copied
    os.makedirs(dst, exist_ok=True)
    for entry in os.listdir(src):
        if _should_exclude(entry):
            continue
        src_path = os.path.join(src, entry)
        dst_path = os.path.join(dst, entry)
        if os.path.isfile(src_path):
            shutil.copy2(src_path, dst_path)
            copied.append(os.path.join(subdir, entry))
        elif os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True,
                            ignore=lambda d, files: [f for f in files if _should_exclude(f)])
            for root_dir, _, filenames in os.walk(dst_path):
                for f in filenames:
                    rel = os.path.relpath(os.path.join(root_dir, f), pack_dir)
                    copied.append(rel)
    return copied


def build_pack(output_dir: str | None = None) -> str:
    if output_dir is None:
        output_dir = os.path.join(PROJECT_ROOT, "data", "client_pilot_pack")

    pack_dir = os.path.abspath(output_dir)
    if os.path.isdir(pack_dir):
        shutil.rmtree(pack_dir)
    os.makedirs(pack_dir, exist_ok=True)

    manifest_entries: list[str] = []

    # Copy source directories
    for source_dir, subdir in SOURCE_DIRS.items():
        entries = _collect_files(source_dir, pack_dir, subdir)
        manifest_entries.extend(entries)

    # Copy individual files
    for rel_path in SOURCE_FILES:
        src = os.path.join(PROJECT_ROOT, rel_path)
        if os.path.isfile(src):
            dst = os.path.join(pack_dir, rel_path)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            manifest_entries.append(rel_path)

    # Write manifest
    manifest_path = os.path.join(pack_dir, "manifest.txt")
    with open(manifest_path, "w") as f:
        f.write(f"Client Pilot Pack — generated {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"{'=' * 60}\n")
        for entry in sorted(manifest_entries):
            f.write(f"{entry}\n")

    # Create ZIP
    zip_path = f"{pack_dir}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root_dir, _, filenames in os.walk(pack_dir):
            for filename in filenames:
                file_path = os.path.join(root_dir, filename)
                arcname = os.path.relpath(file_path, os.path.dirname(pack_dir))
                zf.write(file_path, arcname)

    print(f"Client pilot pack built at: {pack_dir}")
    print(f"Archive: {zip_path}")
    print(f"Files included: {len(manifest_entries)}")

    return pack_dir


def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else None
    build_pack(output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
