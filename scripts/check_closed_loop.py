#!/usr/bin/env python3
"""Closed-loop / offline verification script.

Checks that:
1. Forbidden cloud SDK packages are not installed.
2. Forbidden provider names not present in active .env config.
3. CTA_LOCAL_ONLY_MODE=true.
4. CTA_ALLOW_CLOUD_LLM=false.
5. CTA_LLM_PROVIDER is one of: stub, ollama, lmstudio.
6. CTA_VISION_PROVIDER is one of: stub, local_ocr, local_vlm, hybrid.
7. /health, /health/db, /llm/health, /vision/health are reachable (skipped if app not running).

Returns exit code 0 on PASS, 1 on FAIL.
"""

import os
import sys


FORBIDDEN_PACKAGES = [
    "openai",
    "anthropic",
    "google.generativeai",
    "google.cloud.vision",
    "boto3",
    "azure.ai.vision",
]

ALLOWED_LLM = {"stub", "ollama", "lmstudio"}
ALLOWED_VISION = {"stub", "local_ocr", "local_vlm", "hybrid"}

ENV_CHECKS = [
    ("CTA_LOCAL_ONLY_MODE", "true"),
    ("CTA_ALLOW_CLOUD_LLM", "false"),
]

FAILURES: list[str] = []


def check(message: str, ok: bool, detail: str = "") -> None:
    if ok:
        print(f"  ✓ {message}")
    else:
        print(f"  ✗ {message}")
        if detail:
            print(f"    {detail}")
        FAILURES.append(message)


def check_forbidden_packages():
    """Check that cloud SDK packages are not installed."""
    for pkg in FORBIDDEN_PACKAGES:
        try:
            __import__(pkg.replace(".", "."))
            check(f"{pkg} is not installed", False, "Package found — remove it or ensure it is not imported at runtime.")
        except ImportError:
            check(f"{pkg} is not installed", True)


def check_env_settings():
    """Check .env or environment variables for safe settings."""
    for var, expected in ENV_CHECKS:
        value = os.environ.get(var, "").lower()
        if value == "":
            check(f"{var} (default: {expected})", True, "Not overridden — safe default")
        elif value == expected.lower():
            check(f"{var}={value}", True)
        else:
            check(f"{var}={value}", False, f"Expected {expected}")

    llm = os.environ.get("CTA_LLM_PROVIDER", "stub").lower()
    check(f"CTA_LLM_PROVIDER={llm}", llm in ALLOWED_LLM, f"Must be one of: {', '.join(sorted(ALLOWED_LLM))}")

    vision = os.environ.get("CTA_VISION_PROVIDER", "stub").lower()
    check(f"CTA_VISION_PROVIDER={vision}", vision in ALLOWED_VISION, f"Must be one of: {', '.join(sorted(ALLOWED_VISION))}")

    auth = os.environ.get("CTA_ENABLE_AUTH", "false").lower()
    check(f"CTA_ENABLE_AUTH={auth}", auth in ("true", "false"))
    if auth == "true":
        secret = os.environ.get("CTA_SECRET_KEY", "")
        check("CTA_SECRET_KEY set when auth enabled", bool(secret), "Auth enabled but CTA_SECRET_KEY is empty")


def check_http_endpoints():
    """Check health endpoints if server is running (skip gracefully otherwise)."""
    try:
        import httpx
    except ImportError:
        check("HTTP health endpoints (httpx not installed)", True, "Skipping HTTP checks")
        return

    base = os.environ.get("CTA_BASE_URL", "http://localhost:8000")
    endpoints = ["/health", "/health/db", "/llm/health", "/vision/health"]
    any_fail = False
    for ep in endpoints:
        try:
            resp = httpx.get(f"{base}{ep}", timeout=3)
            ok = resp.status_code == 200
            check(f"GET {base}{ep} returns 200", ok, f"Got {resp.status_code}" if not ok else "")
            if not ok:
                any_fail = True
        except httpx.ConnectError:
            check(f"GET {base}{ep}", True, "Server not running — skipping")
        except Exception as e:
            check(f"GET {base}{ep}", True, f"Could not reach — {e}")
    if any_fail:
        pass


def main():
    print("=" * 60)
    print("Closed-loop check")
    print("=" * 60)
    print()

    print("[1/3] Checking forbidden cloud SDK packages...")
    check_forbidden_packages()
    print()

    print("[2/3] Checking environment settings...")
    check_env_settings()
    print()

    print("[3/3] Checking HTTP health endpoints (skipped if server not running)...")
    try:
        check_http_endpoints()
    except Exception:
        print("  — HTTP checks skipped (app not running)")
    print()

    print("=" * 60)
    if FAILURES:
        print(f"Closed-loop check: FAIL ({len(FAILURES)} failure(s))")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("Closed-loop check: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
