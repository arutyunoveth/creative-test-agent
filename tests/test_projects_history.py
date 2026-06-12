from httpx import ASGITransport, AsyncClient
from src.main import app
from src.modules.projects.history import get_project_history
from src.shared.db.repository import db_session
from src.modules.creative_assets.models import CreativeAsset
from src.modules.test_runs.models import TestRun
from src.modules.report_generator.models import Report
from src.modules.audit_log.models import AuditEvent
import uuid


async def test_project_history_aggregates_entities():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create client and project
        c_resp = await client.post("/ui/clients", data={"name": "History Client"}, follow_redirects=False)
        c_id = c_resp.headers.get("location").split("/")[-1]
        p_resp = await client.post("/ui/projects", data={"client_id": c_id, "name": "History Project"}, follow_redirects=False)
        p_id = p_resp.headers.get("location").split("/")[-1]

        # Create a creative asset
        await client.post("/ui/creative-assets", data={"title": "History Asset", "asset_type": "text", "text_content": "Test", "project_id": p_id}, follow_redirects=False)

        # Create a test run (via API)
        from src.modules.creative_assets.service import list_assets
        assets = list_assets()
        asset_id = assets[0].id

        from src.modules.test_runs.schemas import CreateTestRunRequest
        from src.modules.test_runs.service import create_test_run
        run = create_test_run(CreateTestRunRequest(creative_asset_id=asset_id, project_id=p_id))

    # Check history via function
    history = get_project_history(p_id)
    assert len(history) >= 2  # creative asset + test run
    entity_types = {h["entity_type"] for h in history}
    assert "creative_asset" in entity_types
    assert "test_run" in entity_types


async def test_project_history_ui_shows_timeline():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        c_resp = await client.post("/ui/clients", data={"name": "History UI Client"}, follow_redirects=False)
        c_id = c_resp.headers.get("location").split("/")[-1]
        p_resp = await client.post("/ui/projects", data={"client_id": c_id, "name": "History UI Project"}, follow_redirects=False)
        p_id = p_resp.headers.get("location").split("/")[-1]

        await client.post("/ui/creative-assets", data={"title": "Timeline Asset", "asset_type": "text", "text_content": "Test", "project_id": p_id}, follow_redirects=False)

        dash_resp = await client.get(f"/ui/projects/{p_id}")
    assert dash_resp.status_code == 200
    assert "Project History" in dash_resp.text


async def test_project_history_sorts_by_timestamp():
    with db_session() as db:
        # Create project
        from src.modules.projects.models import Project
        from src.modules.clients.models import Client
        client_obj = Client(name="Sort Client", industry="Test")
        db.add(client_obj)
        db.flush()
        proj = Project(client_id=client_obj.id, name="Sort Project")
        db.add(proj)
        db.flush()
        p_id = proj.id

        # Create creative assets with different timestamps
        a1 = CreativeAsset(title="Asset A", asset_type="text", project_id=p_id)
        db.add(a1)
        db.flush()

        a2 = CreativeAsset(title="Asset B", asset_type="text", project_id=p_id)
        db.add(a2)
        db.flush()

    history = get_project_history(p_id)
    assert len(history) >= 2
    # Should be sorted reverse-chronological
    timestamps = [h["timestamp"] for h in history if h["entity_type"] == "creative_asset"]
    if len(timestamps) >= 2:
        assert timestamps[0] >= timestamps[1]


async def test_project_history_includes_creative_assets():
    with db_session() as db:
        from src.modules.projects.models import Project
        from src.modules.clients.models import Client
        client_obj = Client(name="CA Client", industry="Test")
        db.add(client_obj)
        db.flush()
        proj = Project(client_id=client_obj.id, name="CA Project")
        db.add(proj)
        db.flush()
        p_id = proj.id

        ca = CreativeAsset(title="History CA", asset_type="text", project_id=p_id)
        db.add(ca)
        db.flush()

    history = get_project_history(p_id)
    entity_types = {h["entity_type"] for h in history}
    assert "creative_asset" in entity_types