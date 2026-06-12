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


async def test_image_asset_can_be_analyzed_in_stub_mode():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        upload_resp = await _upload_image(client)
    assert upload_resp.status_code == 201
    asset_id = upload_resp.json()["id"]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        analyze_resp = await client.post(f"/creative-assets/{asset_id}/analyze-visual")
    assert analyze_resp.status_code == 200
    data = analyze_resp.json()
    assert "metadata" in data
    va = data["metadata"].get("visual_analysis", {})
    assert va.get("provider") == "stub"
    assert "vision_stub_mode" in va.get("warnings", [])


async def test_non_image_asset_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/creative-assets",
            json={"title": "Text", "asset_type": "text", "text_content": "Hello"},
        )
    assert create_resp.status_code == 201
    asset_id = create_resp.json()["id"]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        analyze_resp = await client.post(f"/creative-assets/{asset_id}/analyze-visual")
    assert analyze_resp.status_code == 400
    assert "image" in analyze_resp.json()["detail"].lower()


async def test_missing_asset_returns_404():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/creative-assets/nonexistent/analyze-visual")
    assert resp.status_code == 404


async def test_metadata_updated_with_visual_analysis():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        upload_resp = await _upload_image(client)
    asset_id = upload_resp.json()["id"]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        analyze_resp = await client.post(f"/creative-assets/{asset_id}/analyze-visual")
    assert analyze_resp.status_code == 200
    data = analyze_resp.json()
    assert "visual_analysis" in data["metadata"]
    assert data["metadata"]["visual_analysis"]["provider"] == "stub"


async def test_extracted_text_updated_when_detected_text_present():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        upload_resp = await _upload_image(client)
    asset_id = upload_resp.json()["id"]
    assert upload_resp.json().get("extracted_text") in (None, "")

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        analyze_resp = await client.post(f"/creative-assets/{asset_id}/analyze-visual")
    assert analyze_resp.status_code == 200
    data = analyze_resp.json()
    assert data["metadata"]["visual_analysis"]["provider"] == "stub"


async def test_audit_events_written():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        upload_resp = await _upload_image(client)
    asset_id = upload_resp.json()["id"]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(f"/creative-assets/{asset_id}/analyze-visual")
        audit_resp = await client.get("/audit-log")
    assert audit_resp.status_code == 200
    events = audit_resp.json()
    event_types = [e["event_type"] for e in events]
    assert "visual_analysis_requested" in event_types
    assert "visual_analysis_completed" in event_types


async def test_endpoint_does_not_require_ocr_or_vlm_runtime():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        upload_resp = await _upload_image(client)
    asset_id = upload_resp.json()["id"]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        analyze_resp = await client.post(f"/creative-assets/{asset_id}/analyze-visual")
    assert analyze_resp.status_code == 200
    assert analyze_resp.json()["metadata"]["visual_analysis"]["provider"] == "stub"
