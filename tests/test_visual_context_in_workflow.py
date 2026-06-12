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


async def test_uploaded_image_stores_visual_analysis_metadata():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        upload_resp = await _upload_image(client)
    assert upload_resp.status_code == 201
    data = upload_resp.json()
    assert data["asset_type"] == "image"
    assert "warnings" in data["metadata"]


async def test_image_asset_test_run_completes_in_stub_mode():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        upload_resp = await _upload_image(client)
        assert upload_resp.status_code == 201
        asset_id = upload_resp.json()["id"]

        create_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
        assert create_resp.status_code == 201
        run_id = create_resp.json()["id"]

        run_resp = await client.post(f"/test-runs/{run_id}/run")
    assert run_resp.status_code == 200
    data = run_resp.json()
    assert data["status"] == "completed"
    assert data["creative_asset_id"] == asset_id


async def test_report_for_image_asset_includes_visual_notes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        upload_resp = await _upload_image(client)
        asset_id = upload_resp.json()["id"]

        create_resp = await client.post("/test-runs", json={"creative_asset_id": asset_id})
        run_id = create_resp.json()["id"]
        await client.post(f"/test-runs/{run_id}/run")

        report_resp = await client.get(f"/reports/{run_id}?format=markdown")
    assert report_resp.status_code == 200
    report_data = report_resp.json()
    assert report_data.get("visual_notes") is not None or "Visual Analysis" in (report_data.get("report_markdown") or "")


async def test_text_only_asset_does_not_produce_noisy_visual_section():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/creative-assets",
            json={"title": "Text Only", "asset_type": "text", "text_content": "Just text"},
        )
        asset_id = create_resp.json()["id"]
        create_run = await client.post("/test-runs", json={"creative_asset_id": asset_id})
        run_id = create_run.json()["id"]
        await client.post(f"/test-runs/{run_id}/run")

        report_resp = await client.get(f"/reports/{run_id}?format=markdown")
    assert report_resp.status_code == 200
    report_data = report_resp.json()
    assert report_data.get("visual_notes") in (None, "")
