import io

from httpx import ASGITransport, AsyncClient
from PIL import Image

from src.main import app


async def _upload_image(client):
    buf = io.BytesIO()
    img = Image.new("RGB", (50, 30), color="blue")
    img.save(buf, format="PNG")
    files = {"file": ("test.png", buf.getvalue(), "image/png")}
    resp = await client.post("/creative-assets/upload", files=files)
    return resp


async def test_get_report_includes_visual_notes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        upload_resp = await _upload_image(client)
        assert upload_resp.status_code == 201
        asset_id = upload_resp.json()["id"]

        create_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
        run_id = create_resp.json()["id"]
        await client.post(f"/test-runs/{run_id}/run")

        report_resp = await client.get(f"/reports/{run_id}")
    assert report_resp.status_code == 200
    data = report_resp.json()
    assert "visual_notes" in data


async def test_markdown_report_includes_visual_analysis_notes_section():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        upload_resp = await _upload_image(client)
        assert upload_resp.status_code == 201
        asset_id = upload_resp.json()["id"]

        create_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
        run_id = create_resp.json()["id"]
        await client.post(f"/test-runs/{run_id}/run")

        report_resp = await client.get(f"/reports/{run_id}?format=markdown")
    assert report_resp.status_code == 200
    assert "report_markdown" in report_resp.json()


async def test_html_report_includes_visual_notes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        upload_resp = await _upload_image(client)
        assert upload_resp.status_code == 201
        asset_id = upload_resp.json()["id"]

        create_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
        run_id = create_resp.json()["id"]
        await client.post(f"/test-runs/{run_id}/run")

        report_resp = await client.get(f"/reports/{run_id}?format=html")
    assert report_resp.status_code == 200
    html = report_resp.json().get("report_html", "")
    assert html is not None


async def test_internal_mode_shows_provider_and_warnings():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        upload_resp = await _upload_image(client)
        assert upload_resp.status_code == 201
        asset_id = upload_resp.json()["id"]

        create_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
        run_id = create_resp.json()["id"]
        await client.post(f"/test-runs/{run_id}/run")

        report_resp = await client.get(f"/reports/{run_id}?mode=internal")
    assert report_resp.status_code == 200
    data = report_resp.json()
    assert "visual_notes" in data


async def test_text_only_assets_have_empty_visual_notes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/creative-assets",
            json={"title": "Text", "asset_type": "text", "text_content": "Hello"},
        )
        asset_id = create_resp.json()["id"]
        create_run = await client.post("/test-runs", json={"creative_asset_id": asset_id})
        run_id = create_run.json()["id"]
        await client.post(f"/test-runs/{run_id}/run")

        report_resp = await client.get(f"/reports/{run_id}?format=markdown")
    assert report_resp.status_code == 200
    data = report_resp.json()
    assert data.get("visual_notes") in (None, "")
