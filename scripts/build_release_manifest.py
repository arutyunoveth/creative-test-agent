"""
Build release manifest for Creative Test Agent.

Output:
    data/release/release_manifest.json
"""

import json
import os
import sys
from datetime import datetime, timezone

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from src.shared.version import APP_NAME, APP_VERSION, APP_STAGE, BUILD_CHANNEL


def _count_docs() -> int:
    docs_dir = os.path.join(PROJECT_ROOT, "docs")
    if not os.path.isdir(docs_dir):
        return 0
    count = 0
    for root, _dirs, files in os.walk(docs_dir):
        for f in files:
            if f.endswith(".md"):
                count += 1
    return count


def _count_eval_cases() -> int:
    for candidate in [os.path.join(PROJECT_ROOT, "data", "eval_cases"), os.path.join(PROJECT_ROOT, "eval_cases")]:
        if os.path.isdir(candidate):
            return len([f for f in os.listdir(candidate) if f.endswith(".json")])
    return 0


def _prompt_templates_hash() -> str:
    prompts_dir = os.path.join(PROJECT_ROOT, "config", "prompts")
    if not os.path.isdir(prompts_dir):
        return "missing"
    import hashlib
    h = hashlib.sha256()
    for root, _dirs, files in sorted(os.walk(prompts_dir)):
        for f in sorted(files):
            path = os.path.join(root, f)
            try:
                with open(path, "rb") as fh:
                    h.update(fh.read())
            except OSError:
                pass
    return h.hexdigest()[:16]


def _count_model_profiles() -> int:
    profiles_dir = os.path.join(PROJECT_ROOT, "config", "model_profiles")
    if not os.path.isdir(profiles_dir):
        return 0
    return len([f for f in os.listdir(profiles_dir) if f.endswith(".json")])


def _client_pack_exists() -> bool:
    return os.path.isfile(os.path.join(PROJECT_ROOT, "data", "client_pilot_pack.zip"))


def _server_docs_exist() -> bool:
    for item in ["docs/deployment_guide.md", "docs/server_ops.md", "README.md"]:
        if os.path.isfile(os.path.join(PROJECT_ROOT, item)):
            return True
    return False


def _check_no_cloud_sdks() -> list[str]:
    """Check for prohibited SDK imports."""
    findings = []
    src_dir = os.path.join(PROJECT_ROOT, "src")
    prohibited = ["openai", "anthropic", "google.generativeai", "perplexity"]
    for root, _dirs, files in os.walk(src_dir):
        for f in files:
            if not f.endswith(".py"):
                continue
            path = os.path.join(root, f)
            try:
                with open(path) as fh:
                    content = fh.read()
                    for pkg in prohibited:
                        if f"import {pkg}" in content or f"from {pkg}" in content:
                            findings.append(f"{os.path.relpath(path, PROJECT_ROOT)} imports {pkg}")
            except OSError:
                pass
    return findings


def build_manifest() -> dict:
    no_cloud = _check_no_cloud_sdks()
    manifest = {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "stage": APP_STAGE,
        "build_channel": BUILD_CHANNEL,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "docs": _count_docs(),
            "eval_cases": _count_eval_cases(),
            "model_profiles": _count_model_profiles(),
        },
        "checks": {
            "no_cloud_sdks": len(no_cloud) == 0,
            "client_pack_exists": _client_pack_exists(),
            "server_docs_exist": _server_docs_exist(),
        },
        "policy": {
            "local_only": True,
            "cloud_llm": False,
            "cloud_storage": False,
            "external_apis": False,
        },
    }
    if no_cloud:
        manifest["cloud_sdk_violations"] = no_cloud
    return manifest


def main():
    manifest = build_manifest()
    output_dir = os.path.join(PROJECT_ROOT, "data", "release")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "release_manifest.json")
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Release manifest written to: {output_path}")
    print(f"  Version: {manifest['version']} ({manifest['stage']})")
    print(f"  Docs: {manifest['counts']['docs']}")
    print(f"  Eval cases: {manifest['counts']['eval_cases']}")
    print(f"  Model profiles: {manifest['counts']['model_profiles']}")
    print(f"  No cloud SDKs: {manifest['checks']['no_cloud_sdks']}")
    print(f"  Client pack: {'exists' if manifest['checks']['client_pack_exists'] else 'missing'}")
    print(f"  Server docs: {'exist' if manifest['checks']['server_docs_exist'] else 'missing'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
