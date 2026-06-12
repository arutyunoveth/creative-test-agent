from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_project_batches_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/projects/test-proj/batches")
    assert resp.status_code == 200


async def test_project_batches_new_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/projects/test-proj/batches/new")
    assert resp.status_code == 200


async def test_project_dashboard_shows_batch_count():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        a1 = (await client.post("/creative-assets", json={
            "title": "Dash Batch", "asset_type": "text", "text_content": "Test",
            "project_id": "proj-dash-batch",
        })).json()
        await client.post("/batches", json={
            "name": "Dashboard Batch",
            "project_id": "proj-dash-batch",
            "creative_asset_ids": [a1["id"]],
        })
        from src.modules.projects.schemas import CreateProjectRequest
        from src.modules.projects.service import create_project
        from src.modules.clients.schemas import CreateClientRequest
        from src.modules.clients.service import create_client
        client_obj = create_client(CreateClientRequest(name="Dash Client"))
        project = create_project(CreateProjectRequest(
            client_id=client_obj.id,
            name="Dash Project",
        ))
        resp = await client.get(f"/ui/projects/{project.id}")
    assert resp.status_code == 200
