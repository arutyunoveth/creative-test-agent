"""
Release check for Creative Test Agent.

Verifies:
  - pytest command availability
  - check_closed_loop import
  - check_demo_readiness import
  - check_server_readiness import
  - eval cases presence
  - backup script presence
  - client pilot pack builder presence
  - docs presence
  - version endpoint function

Output: "Release check: PASS" or list of failures.
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


def _pytest_available() -> bool:
    import importlib.util
    return importlib.util.find_spec("pytest") is not None


def _check_closed_loop_importable() -> bool:
    from scripts import check_closed_loop
    return hasattr(check_closed_loop, "main")


def _check_demo_readiness_importable() -> bool:
    from scripts import check_demo_readiness
    return hasattr(check_demo_readiness, "main")


def _check_server_readiness_importable() -> bool:
    from scripts import check_server_readiness
    return hasattr(check_server_readiness, "main")


def _eval_cases_present() -> bool:
    for candidate in [os.path.join(PROJECT_ROOT, "data", "eval_cases"), os.path.join(PROJECT_ROOT, "eval_cases")]:
        if os.path.isdir(candidate):
            return any(f.endswith(".json") for f in os.listdir(candidate))
    return False


def _backup_script_present() -> bool:
    return os.path.isfile(os.path.join(PROJECT_ROOT, "scripts", "backup_data.py"))


def _client_pack_builder_present() -> bool:
    return os.path.isfile(os.path.join(PROJECT_ROOT, "scripts", "build_client_pilot_pack.py"))


def _docs_present() -> bool:
    docs_dir = os.path.join(PROJECT_ROOT, "docs")
    if not os.path.isdir(docs_dir):
        return False
    return any(f.endswith(".md") for f in os.listdir(docs_dir))


def _version_endpoint_importable() -> bool:
    from src.shared.version import get_version_info
    info = get_version_info()
    return "version" in info


def _release_manifest_importable() -> bool:
    from scripts import build_release_manifest
    return hasattr(build_release_manifest, "build_manifest")


def _release_notes_exist() -> bool:
    return os.path.isfile(os.path.join(PROJECT_ROOT, "docs", "releases", "0.1.0-rc1.md"))


def _release_bundle_script_exists() -> bool:
    return os.path.isfile(os.path.join(PROJECT_ROOT, "scripts", "build_release_bundle.py"))


def _first_install_guide_exists() -> bool:
    return os.path.isfile(os.path.join(PROJECT_ROOT, "docs", "deployment", "first_server_install_ru.md"))


def _pilot_smoke_script_exists() -> bool:
    return os.path.isfile(os.path.join(PROJECT_ROOT, "scripts", "run_pilot_smoke.py"))


def _demo_meeting_checklist_exists() -> bool:
    return os.path.isfile(os.path.join(PROJECT_ROOT, "docs", "client_pilot", "demo_meeting_checklist_ru.md"))


def _version_is_rc() -> bool:
    from src.shared.version import APP_VERSION
    return APP_VERSION == "0.1.0-rc1"


def _bundle_can_be_built() -> bool:
    from scripts import build_release_bundle
    return hasattr(build_release_bundle, "main")


def run_checks() -> list[dict]:
    CHECKS.clear()
    _check("pytest available", _pytest_available)
    _check("closed loop script importable", _check_closed_loop_importable)
    _check("demo readiness script importable", _check_demo_readiness_importable)
    _check("server readiness script importable", _check_server_readiness_importable)
    _check("eval cases present", _eval_cases_present)
    _check("backup script present", _backup_script_present)
    _check("client pack builder present", _client_pack_builder_present)
    _check("docs present", _docs_present)
    _check("version endpoint importable", _version_endpoint_importable)
    _check("release manifest builder importable", _release_manifest_importable)
    _check("release notes exist", _release_notes_exist)
    _check("release bundle script exists", _release_bundle_script_exists)
    _check("first install guide exists", _first_install_guide_exists)
    _check("pilot smoke script exists", _pilot_smoke_script_exists)
    _check("demo meeting checklist exists", _demo_meeting_checklist_exists)
    _check("version is rc1", _version_is_rc)
    _check("bundle can be built", _bundle_can_be_built)
    return CHECKS


def main():
    results = run_checks()
    failures = [r for r in results if not r["passed"]]
    if failures:
        print("Release check: FAILED")
        for f in failures:
            detail = f" ({f['detail']})" if f["detail"] else ""
            print(f"  - {f['name']}{detail}")
        return 1
    else:
        print("Release check: PASS")
        return 0


if __name__ == "__main__":
    sys.exit(main())
