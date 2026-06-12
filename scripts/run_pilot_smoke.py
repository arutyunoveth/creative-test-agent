"""
Pilot smoke test — verify core user-level flow.

Steps:
  1. Check version.
  2. Check DB.
  3. Load demo profile (via API calls on in-memory DB).
  4. Ensure client/project exist.
  5. Ensure A/B/C creatives exist.
  6. Create or reuse demo batch.
  7. Run batch in stub mode.
  8. Generate batch summary.
  9. Generate report for one item.
  10. Create review from report.
  11. Save review feedback to knowledge.
  12. Create backup.
  13. Build client pilot pack.
  14. Build release manifest.

Uses an in-memory SQLite database — does not touch on-disk data.

Output: "Pilot smoke: PASS"
"""

import os
import sys

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ensure stub mode
os.environ.setdefault("CTA_LLM_PROVIDER", "stub")
os.environ.setdefault("CTA_VISION_PROVIDER", "stub")
os.environ.setdefault("CTA_ENABLE_AUTH", "false")

# Use in-memory DB to avoid affecting on-disk data
from sqlalchemy.pool import StaticPool
from src.shared.db.session import init_db, reset_engine
reset_engine(
    url="sqlite:///:memory:",
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)
init_db()

from src.shared.db.session import check_db_connection
from src.modules.clients.schemas import CreateClientRequest
from src.modules.clients.service import create_client, list_clients
from src.modules.projects.schemas import CreateProjectRequest
from src.modules.projects.service import create_project, list_projects
from src.modules.creative_assets.schemas import CreateCreativeAssetRequest
from src.modules.creative_assets.service import create_asset, list_assets
from src.modules.brand_profiles.schemas import CreateBrandProfileRequest
from src.modules.brand_profiles.service import create_profile as create_brand_profile
from src.modules.batches.schemas import CreateBatchRequest
from src.modules.batches.service import create_batch, list_batches
from src.modules.batches.service import queue_batch, run_all_items
from src.modules.batches.summary import build_batch_summary
from src.modules.report_generator.service import generate_report
from src.modules.reviews.schemas import CreateReviewRequest
from src.modules.reviews.service import create_review
from src.modules.knowledge_base.schemas import CreateKnowledgeItemRequest
from src.modules.knowledge_base.service import create_knowledge_item
from src.shared.version import get_version_info

import logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("pilot_smoke")

failures: list[str] = []


def step(name: str, fn):
    try:
        fn()
        log.info(f"  \u2713 {name}")
    except Exception as e:
        log.info(f"  \u2717 {name}: {e}")
        failures.append(f"{name}: {e}")


def main():
    log.info("Pilot smoke test")
    log.info("=" * 60)

    step("Version check", _test_version)
    step("DB connection", _test_db)
    step("Create client", _test_create_client)
    step("Create project", _test_create_project)
    step("Create brand profile", _test_create_brand_profile)
    step("Create A/B/C creatives", _test_create_creatives)
    step("Create batch", _test_create_batch)
    step("Queue & run batch", _test_run_batch)
    step("Batch summary", _test_summary)
    step("Report generation", _test_report)
    step("Create review", _test_review)
    step("Save to knowledge", _test_knowledge)
    step("Create backup", _test_backup)
    step("Build client pack", _test_client_pack)
    step("Build release manifest", _test_release_manifest)

    log.info("=" * 60)
    if failures:
        log.info(f"Pilot smoke: FAILED \u2014 {len(failures)} step(s) failed")
        for f in failures:
            log.info(f"  - {f}")
        return 1
    else:
        log.info("Pilot smoke: PASS")
        return 0


def _test_version():
    info = get_version_info()
    assert info["version"] == "0.1.0-rc1", f"Expected rc1, got {info['version']}"


def _test_db():
    assert check_db_connection(), "DB not connected"


def _test_create_client():
    client = create_client(CreateClientRequest(
        name="NovaBank Smoke",
        industry="Finance",
    ))
    assert client is not None


def _test_create_project():
    client = list_clients()[0]
    project = create_project(CreateProjectRequest(
        client_id=client.id,
        name="Smoke Campaign",
    ))
    assert project is not None


def _test_create_brand_profile():
    profile = create_brand_profile(CreateBrandProfileRequest(
        name="Smoke Brand Profile",
        tone_of_voice="Professional",
    ))
    assert profile is not None


def _test_create_creatives():
    for i, (title, content) in enumerate([
        ("Variant A", "Safe banking message for smoke test"),
        ("Variant B", "Bold banking message for smoke test"),
        ("Variant C", "Risky banking message for smoke test"),
    ]):
        asset = create_asset(CreateCreativeAssetRequest(
            title=title,
            asset_type="text",
            text_content=content,
        ))
        assert asset is not None
    assert len(list_assets()) == 3


def _test_create_batch():
    project = list_projects()[0]
    assets = list_assets()
    batch = create_batch(CreateBatchRequest(
        name="Smoke Demo Batch",
        project_id=project.id,
        creative_asset_ids=[a.id for a in assets],
        metadata={"smoke_test": "true"},
    ))
    assert batch is not None


def _test_run_batch():
    batch = list_batches()[-1]
    queue_batch(batch.id)
    result = run_all_items(batch.id)
    assert isinstance(result, int) and result > 0, f"Expected > 0 items, got {result}"
    assert result >= 2


def _test_summary():
    batch = list_batches()[-1]
    summary = build_batch_summary(batch.id)
    assert summary["total_items"] > 0, f"Empty summary: {summary}"
    assert "average_score" in summary, f"Missing average_score in: {list(summary.keys())}"


def _test_report():
    from src.shared.db.repository import db_session
    from src.modules.batches.models import BatchRunItem
    batch = list_batches()[-1]
    test_run_id = None
    with db_session() as db:
        item = db.query(BatchRunItem).filter(
            BatchRunItem.batch_run_id == batch.id,
            BatchRunItem.test_run_id.isnot(None),
        ).first()
        if item:
            test_run_id = item.test_run_id
    if test_run_id:
        report = generate_report(test_run_id, report_mode="internal", report_format="json")
        assert report is not None, "Report not generated"


def _test_review():
    assets = list_assets()
    review = create_review(CreateReviewRequest(
        creative_asset_id=assets[0].id,
        reviewer="smoke_test",
        decision="approve",
        rating=85,
        summary="Smoke test review",
    ))
    assert review is not None


def _test_knowledge():
    item = create_knowledge_item(CreateKnowledgeItemRequest(
        source_type="other",
        title="Smoke test insight",
        content="This is a smoke test knowledge item.",
        tags=["smoke_test"],
    ))
    assert item is not None


def _test_backup():
    from scripts.backup_data import main as backup_main
    old_argv = sys.argv
    try:
        sys.argv = ["backup_data"]
        backup_main()
    finally:
        sys.argv = old_argv


def _test_client_pack():
    from scripts.build_client_pilot_pack import build_pack
    out = os.path.join(PROJECT_ROOT, "data", "release", "smoke_client_pack")
    build_pack(out)
    import shutil
    if os.path.isdir(out):
        shutil.rmtree(out)
    zip_path = f"{out}.zip"
    if os.path.isfile(zip_path):
        os.remove(zip_path)


def _test_release_manifest():
    from scripts.build_release_manifest import build_manifest
    manifest = build_manifest()
    assert manifest["version"] == "0.1.0-rc1"


if __name__ == "__main__":
    sys.exit(main())
