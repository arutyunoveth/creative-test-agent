import io

from httpx import ASGITransport, AsyncClient
from src.main import app


async def _upload(content: bytes, filename: str, content_type: str, client, title: str | None = None):
    files = {"file": (filename, content, content_type)}
    data = {}
    if title:
        data["title"] = title
    return await client.post("/creative-assets/upload", files=files, data=data)


async def test_upload_txt_works():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await _upload(b"Hello creative world", "concept.txt", "text/plain", client, title="My Concept")
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My Concept"
    assert data["asset_type"] == "text"
    assert data["extracted_text"] == "Hello creative world"
    assert data["original_filename"] == "concept.txt"
    assert data["mime_type"] == "text/plain"
    assert data["file_size_bytes"] == 20
    assert "id" in data


async def test_upload_md_works():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await _upload(b"# Concept\n\nBig idea here", "brief.md", "text/markdown", client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["asset_type"] == "text"
    assert "# Concept" in data["extracted_text"]


async def test_upload_pdf_works():
    from io import BytesIO
    from pypdf import PdfWriter
    buf = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(72, 72)
    with open("/tmp/test_upload.pdf", "wb") as f:
        writer.write(f)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with open("/tmp/test_upload.pdf", "rb") as f:
            resp = await client.post(
                "/creative-assets/upload",
                files={"file": ("doc.pdf", f, "application/pdf")},
            )
    assert resp.status_code == 201
    data = resp.json()
    assert data["asset_type"] == "pdf"
    assert "id" in data


async def test_upload_png_works():
    from PIL import Image
    buf = io.BytesIO()
    img = Image.new("RGB", (50, 30), color="blue")
    img.save(buf, format="PNG")
    content = buf.getvalue()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await _upload(content, "image.png", "image/png", client, title="Test Image")
    assert resp.status_code == 201
    data = resp.json()
    assert data["asset_type"] == "image"
    assert data["mime_type"] == "image/png"
    assert "warnings" in data["metadata"]


async def test_upload_unsupported_type_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await _upload(b"data", "file.exe", "application/x-msdownload", client)
    assert resp.status_code == 400
    data = resp.json()
    assert "unsupported" in data["error"]["code"]


async def test_upload_empty_file_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await _upload(b"", "empty.txt", "text/plain", client)
    assert resp.status_code == 400
    data = resp.json()
    assert data["error"]["code"] == "empty_file"


async def test_upload_creates_audit_event():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await _upload(b"audit test", "audit.txt", "text/plain", client)
        audit_resp = await client.get("/audit-log")
    assert audit_resp.status_code == 200
    events = audit_resp.json()
    types = [e["event_type"] for e in events]
    assert "creative_file_uploaded" in types
