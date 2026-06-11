"""
Optional demo runner.

Seeds demo data and prints instructions for starting the UI.

Usage:
    python scripts/run_demo.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.seed_demo_data import seed_demo_data


def main():
    print("=" * 60)
    print("  Creative Test Agent — Demo Pilot")
    print("=" * 60)

    seeded = seed_demo_data()

    if seeded:
        print("\n✓ Demo data seeded successfully.")
    else:
        print("\n• Demo data already exists (seed is idempotent).")

    print()
    print("To start the application:")
    print()
    print("  uvicorn src.main:app --reload")
    print()
    print("Then open:")
    print()
    print("  http://localhost:8000/")
    print()
    print("Demo flow:")
    print("  1. Open Dashboard — confirm closed-loop banner")
    print("  2. Go to Creative Assets — see 3 demo variants")
    print("  3. Go to Brand Profiles — see NovaBank")
    print("  4. Go to Audience Profiles — see 3 segments")
    print("  5. Create a test run for any variant")
    print("  6. Run analysis")
    print("  7. View report")
    print("  8. Create more test runs")
    print("  9. Compare variants")
    print(" 10. Open client-facing HTML export")
    print()
    print("Default mode: stub (no local LLM required).")
    print("To use a local model, set CTA_LLM_PROVIDER=ollama|lmstudio in .env")


if __name__ == "__main__":
    main()
