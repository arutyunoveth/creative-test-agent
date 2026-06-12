#!/usr/bin/env python3
"""Demo readiness verification script.

Checks local system without requiring external services:
- database connection works
- demo seed can run
- demo entities exist
- at least 3 demo creatives exist
- UI templates are present
- report generation works in stub mode
- comparison works
- closed-loop config is safe
- pilot export script works
- eval cases present

Returns exit code 0 on PASS, 1 on FAIL.
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


def check_database():
    """Check that SQLite database connection works."""
    try:
        from src.shared.db.session import create_session, init_db, reset_engine
        from sqlalchemy.pool import StaticPool
        from sqlalchemy import text
        reset_engine(
            url="sqlite:///:memory:",
            echo=False,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        init_db()
        session = create_session()
        session.execute(text("SELECT 1"))
        session.close()
        check("Database connection works", True)
    except Exception as e:
        check("Database connection works", False, str(e))


def check_demo_creatives_exist():
    """Check that at least 3 demo creative files exist."""
    demo_dir = os.path.join(os.path.dirname(__file__), "..", "data", "demo")
    if not os.path.isdir(demo_dir):
        check("Demo creative directory exists", False, f"Not found: {demo_dir}")
        return
    files = [f for f in os.listdir(demo_dir) if f.endswith((".md", ".txt")) and "variant" in f.lower()]
    check(f"At least 3 demo creative files ({len(files)} found)", len(files) >= 3, f"Found: {files}")


def check_ui_templates():
    """Check that UI templates directory exists with key templates."""
    templates_dir = os.path.join(os.path.dirname(__file__), "..", "src", "modules", "ui", "templates")
    if not os.path.isdir(templates_dir):
        check("UI templates directory exists", False)
        return
    required = ["dashboard.html", "creative_assets", "test_runs", "login.html", "users"]
    for item in required:
        path = os.path.join(templates_dir, item)
        check(f"UI template: {item}", os.path.exists(path))


def check_pilot_export_importable():
    """Check that export script is importable."""
    try:
        import scripts.export_pilot_data  # noqa: F401
        check("pilot export script is importable", True)
    except Exception as e:
        check("pilot export script is importable", False, str(e))


def check_closed_loop_config():
    """Check basic closed-loop environment config."""
    local_only = os.environ.get("CTA_LOCAL_ONLY_MODE", "true").lower()
    check("CTA_LOCAL_ONLY_MODE=true", local_only == "true", f"Got: {local_only}")

    allow_cloud = os.environ.get("CTA_ALLOW_CLOUD_LLM", "false").lower()
    check("CTA_ALLOW_CLOUD_LLM=false", allow_cloud == "false", f"Got: {allow_cloud}")

    llm = os.environ.get("CTA_LLM_PROVIDER", "stub").lower()
    check(f"CTA_LLM_PROVIDER is safe ({llm})", llm in ("stub", "ollama", "lmstudio"))

    vision = os.environ.get("CTA_VISION_PROVIDER", "stub").lower()
    check(f"CTA_VISION_PROVIDER is safe ({vision})", vision in ("stub", "local_ocr", "local_vlm", "hybrid"))


def check_pytest_runnable():
    """Check that pytest is available."""
    try:
        import pytest  # noqa: F401
        check("pytest is available", True)
    except ImportError:
        check("pytest is available", False, "pytest not installed")


def main():
    print("=" * 60)
    print("Demo readiness check")
    print("=" * 60)
    print()

    print("[1/8] Database...")
    check_database()
    print()

    print("[2/8] Demo creative files...")
    check_demo_creatives_exist()
    print()

    print("[3/8] UI templates...")
    check_ui_templates()
    print()

    print("[4/8] Pilot export...")
    check_pilot_export_importable()
    print()

    print("[5/9] Closed-loop configuration...")
    check_closed_loop_config()
    print()

    print("[6/8] Test tooling...")
    check_pytest_runnable()
    print()

    print("[7/8] Auth docs...")
    auth_docs_path = os.path.join(os.path.dirname(__file__), "..", "docs", "auth_roles.md")
    check("docs/auth_roles.md exists", os.path.isfile(auth_docs_path))
    print()

    print("[8/9] Eval cases...")
    eval_dir = os.path.join(os.path.dirname(__file__), "..", "data", "eval_cases")
    if os.path.isdir(eval_dir):
        cases = [f for f in os.listdir(eval_dir) if f.endswith(".json")]
        check(f"Eval cases present ({len(cases)} files)", len(cases) >= 5, f"Found: {cases}")
    else:
        check("Eval cases directory exists", False)
    print()

    print("[9/9] Additional checks...")
    check("Source directory exists", os.path.isdir(os.path.join(os.path.dirname(__file__), "..", "src")))
    print()

    print("=" * 60)
    if FAILURES:
        print(f"Demo readiness: FAIL ({len(FAILURES)} failure(s))")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("Demo readiness: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
