#!/usr/bin/env python3
"""
Register all prompt templates in the prompt registry.

Scans src/modules/test_runs/prompts/, computes hashes,
and registers PromptVersion entries.

Usage:
    python scripts/register_prompts.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def main():
    from src.shared.db.session import init_db
    from src.modules.prompt_registry.service import register_prompt

    init_db()

    prompts_dir = Path(__file__).parent.parent / "src" / "modules" / "test_runs" / "prompts"
    if not prompts_dir.is_dir():
        print(f"Prompts directory not found: {prompts_dir}", file=sys.stderr)
        sys.exit(1)

    stage_map = {
        "creative_summary": "creative_summary",
        "audience_simulation": "audience_simulation",
        "brand_safety_review": "brand_safety",
        "brandbook_compliance_review": "brandbook_compliance",
        "rubric_scoring": "rubric_scoring",
        "final_recommendation": "final_recommendation",
    }

    registered = 0
    for stage_name, filename in stage_map.items():
        template_path = prompts_dir / f"{filename}.md"
        if not template_path.is_file():
            print(f"  Warning: template not found: {template_path}")
            continue
        try:
            pv = register_prompt(stage_name, str(template_path))
            print(f"  ✓ {stage_name} → hash={pv.template_hash[:16]}... (v{pv.version})")
            registered += 1
        except Exception as e:
            print(f"  ✗ {stage_name}: {e}")

    print(f"\nRegistered {registered} prompt version(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
