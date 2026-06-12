import io

from httpx import ASGITransport, AsyncClient
from PIL import Image

from src.main import app


async def _upload_image(client, content: bytes, filename: str = "test.png"):
    files = {"file": (filename, content, "image/png")}
    resp = await client.post("/creative-assets/upload", files=files)
    return resp


async def test_image_preview_works_for_uploaded_png():
    buf = io.BytesIO()
    img = Image.new("RGB", (50, 30), color="blue")
    img.save(buf, format="PNG")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        upload_resp = await _upload_image(client, buf.getvalue())
    assert upload_resp.status_code == 201
    asset_id = upload_resp.json()["id"]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        preview_resp = await client.get(f"/creative-assets/{asset_id}/image")
    assert preview_resp.status_code == 200
    assert preview_resp.headers["content-type"] == "image/png"


async def test_image_preview_works_for_uploaded_jpg():
    buf = io.BytesIO()
    img = Image.new("RGB", (50, 30), color="red")
    img.save(buf, format="JPEG")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        upload_resp = await _upload_image(client, buf.getvalue(), "test.jpg")
    assert upload_resp.status_code == 201
    asset_id = upload_resp.json()["id"]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        preview_resp = await client.get(f"/creative-assets/{asset_id}/image")
    assert preview_resp.status_code == 200
    assert "image" in preview_resp.headers["content-type"]


async def test_non_image_asset_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/creative-assets",
            json={"title": "Text Asset", "asset_type": "text", "text_content": "Hello"},
        )
    assert create_resp.status_code == 201
    asset_id = create_resp.json()["id"]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        preview_resp = await client.get(f"/creative-assets/{asset_id}/image")
    assert preview_resp.status_code == 400
    assert "not an image" in preview_resp.json()["detail"].lower()


async def test_missing_asset_returns_404():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/creative-assets/nonexistent-id/image")
    assert resp.status_code == 404


async def test_response_content_type_is_image_type():
    buf = io.BytesIO()
    img = Image.new("RGB", (50, 30), color="green")
    img.save(buf, format="PNG")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        upload_resp = await _upload_image(client, buf.getvalue())
    asset_id = upload_resp.json()["id"]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        preview_resp = await client.get(f"/creative-assets/{asset_id}/image")
    assert preview_resp.status_code == 200
    assert preview_resp.headers["content-type"] == "image/png"
