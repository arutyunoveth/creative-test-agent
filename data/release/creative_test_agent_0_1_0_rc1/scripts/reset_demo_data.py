"""
Reset demo data from the Creative Test Agent database.

Deletes all entities tagged with metadata.demo == True.
Safe to run multiple times.

Usage:
    python scripts/reset_demo_data.py
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _is_demo(metadata: dict | None) -> bool:
    return bool(metadata and metadata.get("demo") is True)


def reset_demo_data() -> dict[str, int]:
    """Remove all entities tagged with demo=True from the database.

    Returns a dict with counts of deleted entities per type.
    """
    from src.shared.db.repository import db_session
    from src.modules.brand_profiles.models import BrandProfile
    from src.modules.audience_profiles.models import AudienceProfile
    from src.modules.creative_assets.models import CreativeAsset
    from src.modules.test_rubrics.models import TestRubric
    from src.modules.test_runs.models import TestRun
    from src.modules.report_generator.models import Report
    from src.shared.db.repository import json_loads

    counts = {}

    with db_session() as db:
        # Brand profiles
        brands = db.query(BrandProfile).all()
        demo_brands = [b for b in brands if _is_demo(json_loads(b.metadata_json))]
        for b in demo_brands:
            db.delete(b)
        counts["brand_profiles"] = len(demo_brands)

        # Audience profiles
        profiles = db.query(AudienceProfile).all()
        demo_profiles = [p for p in profiles if _is_demo(json_loads(p.metadata_json))]
        for p in demo_profiles:
            db.delete(p)
        counts["audience_profiles"] = len(demo_profiles)

        # Creative assets
        assets = db.query(CreativeAsset).all()
        demo_assets = [a for a in assets if _is_demo(json_loads(a.metadata_json))]
        for a in demo_assets:
            db.delete(a)
        counts["creative_assets"] = len(demo_assets)

        # Rubrics
        rubrics = db.query(TestRubric).all()
        demo_rubrics = [r for r in rubrics if _is_demo(json_loads(r.metadata_json))]
        for r in demo_rubrics:
            db.delete(r)
        counts["test_rubrics"] = len(demo_rubrics)

        # Test runs (no metadata column, so match by linked demo assets)
        demo_asset_ids = {a.id for a in demo_assets}
        runs = db.query(TestRun).all()
        demo_runs = [r for r in runs if r.creative_asset_id in demo_asset_ids]
        for r in demo_runs:
            # Also delete associated reports
            db.query(Report).filter(Report.test_run_id == r.id).delete()
            db.delete(r)
        counts["test_runs"] = len(demo_runs)

    return counts


def main():
    print("Resetting demo data...")
    counts = reset_demo_data()
    total = sum(counts.values())
    for entity_type, count in counts.items():
        if count:
            print(f"  Deleted {count} {entity_type}")
    if total:
        print(f"\nTotal: {total} demo entities removed.")
    else:
        print("  No demo data found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
