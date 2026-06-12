"""
Verify release install for Creative Test Agent.

Checks:
  - version endpoint import works
  - .env.server.example exists
  - Docker server compose exists
  - migrations directory exists
  - server docs exist
  - release notes exist
  - release manifest exists or can be generated
  - release bundle script imports
  - client pilot pack script imports
  - backup/check scripts import
  - no forbidden cloud SDK packages declared
  - no .env included in release bundle if bundle exists

Output: "Release install verification: PASS" or list of failures.
"""

import os
import sys

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHECKS: list[dict] = []


def _check(name: str, fn) -> None:
    try:
        result = fn()
        CHECKS.append({"name": name, "passed": bool(result), "detail": "" if result else f"{name} failed"})
    except Exception as e:
        CHECKS.append({"name": name, "passed": False, "detail": str(e)})


def _version_endpoint_works() -> bool:
    from src.shared.version import get_version_info
    info = get_version_info()
    return info["version"] == "0.1.0-rc1"


def _env_server_example_exists() -> bool:
    return os.path.isfile(os.path.join(PROJECT_ROOT, ".env.server.example"))


def _docker_server_compose_exists() -> bool:
    return os.path.isfile(os.path.join(PROJECT_ROOT, "docker-compose.server.yml"))


def _migrations_dir_exists() -> bool:
    return os.path.isdir(os.path.join(PROJECT_ROOT, "migrations"))


def _server_docs_exist() -> bool:
    for p in [
        "docs/deployment_guide.md",
        "docs/server_ops.md",
        "docs/deployment/first_server_install_ru.md",
    ]:
        if os.path.isfile(os.path.join(PROJECT_ROOT, p)):
            return True
    return False


def _release_notes_exist() -> bool:
    return os.path.isfile(os.path.join(PROJECT_ROOT, "docs", "releases", "0.1.0-rc1.md"))


def _release_manifest_exists_or_buildable() -> bool:
    manifest_path = os.path.join(PROJECT_ROOT, "data", "release", "release_manifest.json")
    if os.path.isfile(manifest_path):
        return True
    from scripts import build_release_manifest
    return hasattr(build_release_manifest, "build_manifest")


def _release_bundle_script_imports() -> bool:
    from scripts import build_release_bundle
    return hasattr(build_release_bundle, "main")


def _client_pack_script_imports() -> bool:
    from scripts import build_client_pilot_pack
    return hasattr(build_client_pilot_pack, "main")


def _backup_script_imports() -> bool:
    from scripts import backup_data
    return hasattr(backup_data, "main")


def _restore_script_imports() -> bool:
    from scripts import restore_data
    return hasattr(restore_data, "main")


def _check_forbidden_cloud_imports() -> bool:
    """Check for prohibited SDK references in pyproject.toml / requirements.txt"""
    for dep_file in ["pyproject.toml", "requirements.txt"]:
        path = os.path.join(PROJECT_ROOT, dep_file)
        if not os.path.isfile(path):
            continue
        with open(path) as f:
            content = f.read().lower()
        for pkg in ["openai", "anthropic", "google-generativeai", "perplexity"]:
            if pkg in content:
                return False
    return True


def _bundle_excludes_env() -> bool:
    """Check that existing bundle doesn't contain .env"""
    import glob as glob_mod
    bundles = glob_mod.glob(os.path.join(PROJECT_ROOT, "data", "release", "*.zip"))
    if not bundles:
        return True
    import zipfile
    for b in bundles[:1]:
        try:
            with zipfile.ZipFile(b) as zf:
                names = zf.namelist()
                for n in names:
                    if ".env" in n and "example" not in n:
                        return False
        except Exception:
            pass
    return True


def run_checks() -> list[dict]:
    CHECKS.clear()
    _check("version endpoint returns rc1", _version_endpoint_works)
    _check(".env.server.example exists", _env_server_example_exists)
    _check("docker server compose exists", _docker_server_compose_exists)
    _check("migrations directory exists", _migrations_dir_exists)
    _check("server docs exist", _server_docs_exist)
    _check("release notes exist", _release_notes_exist)
    _check("release manifest exists or buildable", _release_manifest_exists_or_buildable)
    _check("release bundle script imports", _release_bundle_script_imports)
    _check("client pack script imports", _client_pack_script_imports)
    _check("backup script imports", _backup_script_imports)
    _check("restore script imports", _restore_script_imports)
    _check("no forbidden cloud SDKs", _check_forbidden_cloud_imports)
    _check("bundle excludes .env", _bundle_excludes_env)
    return CHECKS


def main():
    results = run_checks()
    failures = [r for r in results if not r["passed"]]
    if failures:
        print("Release install verification: FAILED")
        for f in failures:
            detail = f" ({f['detail']})" if f["detail"] else ""
            print(f"  - {f['name']}{detail}")
        return 1
    else:
        print("Release install verification: PASS")
        return 0


if __name__ == "__main__":
    sys.exit(main())
