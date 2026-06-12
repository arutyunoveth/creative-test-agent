from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_demo_status_detects_empty_db():
    from src.modules.demo.status import get_demo_status
    status = get_demo_status()
    assert "profile_loaded" in status
    assert "client_exists" in status
    assert "next_recommended_action" in status


async def test_demo_status_returns_expected_keys():
    from src.modules.demo.status import get_demo_status
    status = get_demo_status()
    expected_keys = [
        "profile_loaded", "client_exists", "project_exists",
        "creatives_count", "brandbooks_count", "batch_exists",
        "batch_completed", "reports_count", "reviews_count",
        "knowledge_items_count", "next_recommended_action",
    ]
    for key in expected_keys:
        assert key in status, f"Missing key: {key}"
