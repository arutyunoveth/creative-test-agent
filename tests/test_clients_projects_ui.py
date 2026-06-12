from httpx import ASGITransport, AsyncClient
from src.main import app


async def _create_client(client, name="Test Client"):
    resp = await client.post("/ui/clients", data={"name": name, "industry": "Tech"}, follow_redirects=False)
    return resp


async def _create_project(client, client_id, name="Test Project"):
    resp = await client.post(
        f"/ui/clients/{client_id}/projects/new",
        data={"name": name},
        follow_redirects=False,
    )
    return resp


async def test_clients_list_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/clients")
    assert resp.status_code == 200
    assert "Clients" in resp.text


async def test_new_client_form_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/clients/new")
    assert resp.status_code == 200
    assert "New Client" in resp.text


async def test_client_can_be_created_through_ui():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await _create_client(client, "UI Client Test")
    assert resp.status_code == 303
    assert "/ui/clients/" in resp.headers.get("location", "")


async def test_client_detail_shows_after_creation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await _create_client(client, "Detail Client")
        location = create_resp.headers.get("location")
        detail_resp = await client.get(location, follow_redirects=True)
    assert detail_resp.status_code == 200
    assert "Detail Client" in detail_resp.text


async def test_projects_list_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/projects")
    assert resp.status_code == 200
    assert "Projects" in resp.text


async def test_new_project_form_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/projects/new")
    assert resp.status_code == 200
    assert "New Project" in resp.text


async def test_project_can_be_created_through_ui():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c_resp = await _create_client(client, "Proj Client")
        c_location = c_resp.headers.get("location")
        c_id = c_location.split("/")[-1]
        resp = await client.post(f"/ui/projects", data={"client_id": c_id, "name": "UI Project"}, follow_redirects=False)
    assert resp.status_code == 303
    assert "/ui/projects/" in resp.headers.get("location", "")


async def test_project_detail_shows_after_creation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c_resp = await _create_client(client, "Proj Client 2")
        c_id = c_resp.headers.get("location").split("/")[-1]
        p_resp = await client.post("/ui/projects", data={"client_id": c_id, "name": "Detail Project"}, follow_redirects=False)
        p_location = p_resp.headers.get("location")
        detail_resp = await client.get(p_location, follow_redirects=True)
    assert detail_resp.status_code == 200
    assert "Detail Project" in detail_resp.text


async def test_client_detail_shows_projects():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c_resp = await _create_client(client, "Client With Projects")
        c_id = c_resp.headers.get("location").split("/")[-1]
        await client.post("/ui/projects", data={"client_id": c_id, "name": "Project Alpha"})
        await client.post("/ui/projects", data={"client_id": c_id, "name": "Project Beta"})
        detail_resp = await client.get(f"/ui/clients/{c_id}")
    assert detail_resp.status_code == 200
    assert "Project Alpha" in detail_resp.text
    assert "Project Beta" in detail_resp.text


async def test_projects_dashboard_shows_counts():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c_resp = await _create_client(client, "Dashboard Client")
        c_id = c_resp.headers.get("location").split("/")[-1]
        p_resp = await client.post("/ui/projects", data={"client_id": c_id, "name": "Dashboard Project"}, follow_redirects=False)
        p_id = p_resp.headers.get("location").split("/")[-1]
        dash_resp = await client.get(f"/ui/projects/{p_id}")
    assert dash_resp.status_code == 200
    assert "Dashboard Project" in dash_resp.text
    assert "Creative Assets" in dash_resp.text
    assert "Test Runs" in dash_resp.text


async def test_dashboard_shows_client_project_counts():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await _create_client(client, "Count Client")
        await client.post("/ui/projects", data={"client_id": "dummy", "name": "Count Project"}, follow_redirects=False)
        resp = await client.get("/ui")
    assert resp.status_code == 200
    assert "Clients" in resp.text
    assert "Projects" in resp.text


async def test_nav_links_in_base_template():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui")
    assert resp.status_code == 200
    assert "/ui/clients" in resp.text
    assert "/ui/projects" in resp.text


async def test_project_scoped_test_run_form():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c_resp = await _create_client(client, "TestRun Client")
        c_id = c_resp.headers.get("location").split("/")[-1]
        p_resp = await client.post("/ui/projects", data={"client_id": c_id, "name": "TestRun Project"}, follow_redirects=False)
        p_id = p_resp.headers.get("location").split("/")[-1]
        resp = await client.get(f"/ui/projects/{p_id}/test-runs/new")
    assert resp.status_code == 200
    assert "New Test Run" in resp.text


async def test_project_scoped_compare_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c_resp = await _create_client(client, "Compare Client")
        c_id = c_resp.headers.get("location").split("/")[-1]
        p_resp = await client.post("/ui/projects", data={"client_id": c_id, "name": "Compare Project"}, follow_redirects=False)
        p_id = p_resp.headers.get("location").split("/")[-1]
        resp = await client.get(f"/ui/projects/{p_id}/compare")
    assert resp.status_code == 200
    assert "Compare" in resp.text


async def test_project_reports_page_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c_resp = await _create_client(client, "Reports Client")
        c_id = c_resp.headers.get("location").split("/")[-1]
        p_resp = await client.post("/ui/projects", data={"client_id": c_id, "name": "Reports Project"}, follow_redirects=False)
        p_id = p_resp.headers.get("location").split("/")[-1]
        resp = await client.get(f"/ui/projects/{p_id}/reports")
    assert resp.status_code == 200


async def test_project_exports_page_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c_resp = await _create_client(client, "Exports Client")
        c_id = c_resp.headers.get("location").split("/")[-1]
        p_resp = await client.post("/ui/projects", data={"client_id": c_id, "name": "Exports Project"}, follow_redirects=False)
        p_id = p_resp.headers.get("location").split("/")[-1]
        resp = await client.get(f"/ui/projects/{p_id}/exports")
    assert resp.status_code == 200