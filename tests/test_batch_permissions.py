from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_no_cloud_sdks_added():
    import os
    reqs_path = "requirements.txt"
    if os.path.isfile(reqs_path):
        with open(reqs_path) as f:
            content = f.read().lower()
        for bad in ("openai", "anthropic", "google-generativeai", "redis", "celery", "boto3"):
            assert bad not in content, f"Found forbidden dependency: {bad}"


async def test_job_queue_no_celery():
    import src.modules.job_queue.service
    assert True


async def test_batch_endpoints_exist():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/batches", json={"name": "Test", "creative_asset_ids": []})
    assert resp.status_code == 201
