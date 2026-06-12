#!/usr/bin/env python3
"""
Local model diagnostic script.

Checks:
  - profile exists
  - provider allowed
  - base_url is local
  - health check works
  - simple prompt returns output
  - structured JSON prompt returns parseable JSON or reports failure

Usage:
    python scripts/check_local_model.py --profile ollama-local
    python scripts/check_local_model.py --profile lmstudio-local
"""

import argparse
import json
import os
import sys
import time

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


def warn(message: str) -> None:
    print(f"  ⚠ {message}")


def main():
    parser = argparse.ArgumentParser(description="Check local model availability")
    parser.add_argument("--profile", required=True, help="Model profile name")
    parser.add_argument("--smoke", action="store_true", help="Run quick smoke test only")
    args = parser.parse_args()

    from src.shared.db.session import init_db
    from src.shared.config.settings import get_settings

    init_db()
    settings = get_settings()

    print("=" * 60)
    print(f"Local model check: {args.profile}")
    print("=" * 60)

    if settings.local_only_mode and not settings.allow_cloud_llm:
        check("Closed-loop mode enabled (local_only=true)", True)

    # Step 1: find profile
    from src.modules.model_profiles.service import list_profiles

    profiles = list_profiles()
    profile = None
    for p in profiles:
        if p.profile_name == args.profile or p.id.startswith(args.profile):
            profile = p
            break

    if profile is None:
        check(f"Profile '{args.profile}' found in DB", False,
              f"Available profiles: {[pp.profile_name for pp in profiles]}")
        sys.exit(1)
    else:
        check(f"Profile '{profile.profile_name}' found", True)

    # Step 2: provider allowed
    from src.modules.model_profiles.service import ALLOWED_PROVIDERS, FORBIDDEN_PROVIDERS

    if profile.provider in FORBIDDEN_PROVIDERS:
        check(f"Provider '{profile.provider}' is not forbidden", False)
        sys.exit(1)
    elif profile.provider in ALLOWED_PROVIDERS:
        check(f"Provider '{profile.provider}' is allowed", True)
    else:
        check(f"Provider '{profile.provider}' recognized", False,
              f"Allowed: {ALLOWED_PROVIDERS}")
        sys.exit(1)

    # Step 3: check base_url
    if profile.provider in ("ollama", "lmstudio"):
        if not profile.base_url:
            check(f"base_url set for {profile.provider}", False)
            sys.exit(1)
        if "localhost" in profile.base_url or "127.0.0.1" in profile.base_url:
            check(f"base_url is local ({profile.base_url})", True)
        else:
            check(f"base_url is local ({profile.base_url})", False,
                  "Local providers should point to localhost")
            sys.exit(1)

    # Step 4: health check
    from src.modules.model_profiles.service import check_profile_health

    try:
        health = check_profile_health(profile.id)
        check(f"Health check reachable={health.reachable}", health.reachable,
              health.detail if not health.reachable else "")
        if health.warnings:
            for w in health.warnings:
                warn(w)
    except Exception as e:
        check("Health check", False, str(e))

    if args.smoke:
        print("\nSmoke mode — skipping prompt test. Use without --smoke for full check.")
        print("=" * 60)
        _summarize_and_exit()

    # Step 5: simple prompt test (if not stub)
    if profile.provider == "stub":
        warn("Stub provider — no real LLM to test. Skipping prompt test.")
    else:
        print("\n[Prompt test] Simple prompt...")
        from src.modules.test_runs.prompts import load_prompt
        from src.shared.llm.ollama import OllamaProvider
        from src.shared.llm.lmstudio import LMStudioProvider

        if profile.provider == "ollama":
            provider = OllamaProvider()
        elif profile.provider == "lmstudio":
            provider = LMStudioProvider()
        else:
            check("Provider implementation available", False, f"No handler for {profile.provider}")
            _summarize_and_exit()

        try:
            start = time.time()
            result = provider.generate("Respond with the word 'ok' and nothing else.")
            latency = (time.time() - start) * 1000
            content = result.get("content", "")
            has_output = bool(content and content.strip())
            check(f"Simple prompt returns output ({len(content)} chars, {latency:.0f}ms)", has_output)
        except Exception as e:
            check("Simple prompt", False, str(e))

        # Step 6: structured JSON prompt
        print("\n[Prompt test] Structured JSON prompt...")
        json_prompt = """Respond ONLY with valid JSON:
{
  "test": "ok",
  "score": 5
}"""
        try:
            start = time.time()
            result = provider.generate(json_prompt)
            latency = (time.time() - start) * 1000
            content = result.get("content", "")

            from src.shared.llm.structured_output.json_extractor import extract_json_candidate
            from src.shared.llm.structured_output.json_repair import repair_json

            parsed = extract_json_candidate(content)
            if parsed is not None:
                check(f"JSON prompt returns parseable JSON ({latency:.0f}ms)", True)
            else:
                repair_result = repair_json(content)
                if repair_result["repaired"]:
                    check(f"JSON prompt repaired successfully ({latency:.0f}ms)", True,
                          f"Steps: {repair_result['repair_steps']}")
                else:
                    check("JSON prompt returns parseable JSON", False,
                          f"Could not parse. Error: {repair_result.get('error', 'unknown')}")
        except Exception as e:
            check("Structured JSON prompt", False, str(e))

    print("=" * 60)
    _summarize_and_exit()


def _summarize_and_exit():
    if FAILURES:
        print(f"Local model check: FAIL ({len(FAILURES)} failure(s))")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("Local model check: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
