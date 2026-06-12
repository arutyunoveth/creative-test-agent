"""
Demo batch campaign runner.

Creates a NovaBank A/B/C campaign batch and runs all items in stub mode.

Usage:
    python scripts/run_demo_batch.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.shared.db.session import init_db, reset_engine
from sqlalchemy.pool import StaticPool


def main():
    print("=" * 60)
    print("  NovaBank Campaign Batch Demo")
    print("=" * 60)

    reset_engine(
        url="sqlite:///./data/creative_test_agent.db",
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    init_db()

    from src.modules.creative_assets.schemas import CreateCreativeAssetRequest
    from src.modules.creative_assets.service import create_asset
    from src.modules.audience_profiles.schemas import CreateAudienceProfileRequest
    from src.modules.audience_profiles.service import create_profile as create_audience
    from src.modules.brand_profiles.schemas import CreateBrandProfileRequest
    from src.modules.brand_profiles.service import create_profile as create_brand
    from src.modules.projects.service import create_project
    from src.modules.projects.schemas import CreateProjectRequest
    from src.modules.batches.schemas import CreateBatchRequest
    from src.modules.batches.service import create_batch, queue_batch, run_all_items
    from src.modules.clients.service import create_client
    from src.modules.clients.schemas import CreateClientRequest

    client = create_client(CreateClientRequest(name="NovaBank Demo", industry="Finance"))
    project = create_project(CreateProjectRequest(
        client_id=client.id,
        name="NovaBank Summer Campaign",
        description="Demo campaign batch with A/B/C variants",
        status="active",
    ))

    brand = create_brand(CreateBrandProfileRequest(
        name="NovaBank",
        project_id=project.id,
    ))

    audience_a = create_audience(CreateAudienceProfileRequest(
        name="Young Professionals",
        segment_name="young_professionals",
        project_id=project.id,
    ))
    audience_b = create_audience(CreateAudienceProfileRequest(
        name="Students",
        segment_name="students",
        project_id=project.id,
    ))

    assets = []
    variants = [
        ("NovaBank Variant A", "Welcome to the future of banking with NovaBank. Simple, secure, smart."),
        ("NovaBank Variant B", "NovaBank: Your money, your terms. Banking reimagined for you."),
        ("NovaBank Variant C (Risky)", "Forget everything you know about banking. NovaBank changes the rules."),
    ]
    for title, text in variants:
        asset = create_asset(CreateCreativeAssetRequest(
            title=title,
            asset_type="text",
            text_content=text,
            project_id=project.id,
        ))
        assets.append(asset)

    asset_ids = [a.id for a in assets]
    audience_ids = [audience_a.id, audience_b.id]

    batch = create_batch(CreateBatchRequest(
        project_id=project.id,
        name="NovaBank A/B/C Campaign Batch",
        description="Automated demo batch testing 3 creative variants",
        creative_asset_ids=asset_ids,
        audience_profile_ids=audience_ids,
        brand_profile_id=brand.id,
        input_context={"campaign": "NovaBank Summer", "batch_demo": True},
    ))

    print(f"\nBatch created: {batch.id}")
    print(f"  Name: {batch.name}")
    print(f"  Project: {project.name} ({project.id[:8]}...)")
    print(f"  Assets: {len(asset_ids)} variants")
    print(f"  Audiences: {len(audience_ids)} segments")

    queued = queue_batch(batch.id)
    print(f"\nBatch queued: {queued.status}")
    print(f"  Items created: {len(asset_ids)}")

    count = run_all_items(batch.id)
    print(f"\nBatch run complete: {count} items processed")

    from src.modules.batches.summary import build_batch_summary
    summary = build_batch_summary(batch.id)
    print(f"  Status: {summary.get('status')}")
    print(f"  Completed: {summary.get('completed_items')}/{summary.get('total_items')}")
    print(f"  Average score: {summary.get('average_score')}")
    print(f"  Best creative: {summary.get('best_creative_asset_id', 'N/A')[:16]}...")

    print("\n✓ Demo batch complete.")
    print("\nYou can now:")
    print("  1. Start the server: uvicorn src.main:app --reload")
    print("  2. Open http://localhost:8000/")
    print("  3. Go to Batches to see the NovaBank campaign batch")
    print("  4. Open the project workspace for campaign summary")


if __name__ == "__main__":
    main()
