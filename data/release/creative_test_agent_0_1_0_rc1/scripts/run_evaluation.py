#!/usr/bin/env python3
"""
Run evaluation against test cases.

Usage:
    python scripts/run_evaluation.py --profile stub
    python scripts/run_evaluation.py --profile ollama-local --smoke
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def main():
    parser = argparse.ArgumentParser(description="Run evaluation against test cases")
    parser.add_argument("--profile", default="stub", help="Model profile name or ID")
    parser.add_argument("--smoke", action="store_true", help="Quick smoke test with fewer cases")
    parser.add_argument("--case", action="append", help="Specific case IDs to run")
    args = parser.parse_args()

    from src.shared.db.session import init_db
    init_db()

    profile_id = None
    if args.profile != "stub":
        from src.modules.model_profiles.service import list_profiles
        profiles = list_profiles()
        for p in profiles:
            if p.profile_name == args.profile or p.id == args.profile:
                profile_id = p.id
                break
        if not profile_id:
            print(f"Profile '{args.profile}' not found. Use stub instead.", file=sys.stderr)

    case_ids = args.case
    if args.smoke:
        case_ids = ["novabank_variant_a", "novabank_variant_c_risky"]

    print(f"Running evaluation (profile={args.profile}, smoke={args.smoke})...")
    from src.modules.evaluations.runner import run_evaluation

    result = run_evaluation(profile_id=profile_id, case_ids=case_ids)

    print(f"  Evaluation run ID: {result['evaluation_run_id']}")
    print(f"  Status: {result['status']}")
    print(f"  Overall score: {result['overall_score']}")

    from src.modules.evaluations.runner import get_evaluation_results
    details = get_evaluation_results(result["evaluation_run_id"])
    if details:
        for r in details.get("results", []):
            status_icon = "✓" if r["status"] == "completed" and not r["failures"] else "✗"
            print(f"  {status_icon} {r['case_id']}: score={r['score']}, passed={r['passed']}/{r['total_checks']}")
            for f in r.get("failures", []):
                print(f"      FAIL: {f}")
            for w in r.get("warnings", []):
                print(f"      WARN: {w}")

    return 0 if result["overall_score"] >= 50 else 1


if __name__ == "__main__":
    sys.exit(main())
