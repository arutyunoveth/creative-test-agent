from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_enqueue_job():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/jobs", json={
            "job_type": "run_test",
            "entity_type": "test_run",
            "entity_id": "test-123",
            "payload": {"test": True},
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["job_type"] == "run_test"
    assert data["status"] == "queued"
    assert data["payload"]["test"] is True


async def test_get_job():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post("/jobs", json={"job_type": "run_test"})
        job_id = created.json()["id"]
        resp = await client.get(f"/jobs/{job_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == job_id


async def test_list_jobs():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/jobs", json={"job_type": "run_test"})
        resp = await client.get("/jobs")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


async def test_claim_next_job():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/jobs", json={"job_type": "test_type"})
        resp = await client.post("/jobs/claim-next", params={"job_type": "test_type"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "running"


async def test_mark_job_completed():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post("/jobs", json={"job_type": "run_test"})
        job_id = created.json()["id"]
        resp = await client.post(f"/jobs/{job_id}/complete", json={"result": {"ok": True}})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["result"]["ok"] is True


async def test_mark_job_failed():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post("/jobs", json={"job_type": "run_test"})
        job_id = created.json()["id"]
        resp = await client.post(f"/jobs/{job_id}/fail", json={"error_message": "Something went wrong"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "failed"
    assert data["error_message"] == "Something went wrong"


async def test_cancel_queued_job():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post("/jobs", json={"job_type": "run_test"})
        job_id = created.json()["id"]
        resp = await client.post(f"/jobs/{job_id}/cancel")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


async def test_retry_failed_job():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post("/jobs", json={"job_type": "run_test"})
        job_id = created.json()["id"]
        await client.post(f"/jobs/{job_id}/fail", json={"error_message": "error"})
        resp = await client.post(f"/jobs/{job_id}/retry")
    assert resp.status_code == 200
    assert resp.json()["status"] == "queued"
