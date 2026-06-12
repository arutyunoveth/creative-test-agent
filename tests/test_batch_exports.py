import os
from httpx import ASGITransport, AsyncClient
from src.main import app


async def _create_asset(client, title="Export Test", text_content="Test"):
    resp = await client.post("/creative-assets", json={
        "title": title, "asset_type": "text", "text_content": text_content,
    })
    return resp.json()


async def _create_batch_with_items(client, name="Export Batch"):
    a1 = await _create_asset(client, title=f"{name} A", text_content="Content A")
    created = await client.post("/batches", json={
        "name": name,
        "creative_asset_ids": [a1["id"]],
    })
    batch_id = created.json()["id"]
    await client.post(f"/batches/{batch_id}/queue")
    await client.post(f"/batches/{batch_id}/run-all")
    return batch_id


async def test_batch_report_markdown():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        batch_id = await _create_batch_with_items(client)
        resp = await client.get(f"/batches/{batch_id}/report?format=markdown")
    assert resp.status_code == 200
    data = resp.json()
    assert data["format"] == "markdown"
    assert "Campaign Batch" in data["report"]


async def test_batch_report_html():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        batch_id = await _create_batch_with_items(client, "HTML Batch")
        resp = await client.get(f"/batches/{batch_id}/report?format=html")
    assert resp.status_code == 200
    data = resp.json()
    assert data["format"] == "html"
    assert "<html>" in data["report"]


async def test_batch_report_json():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        batch_id = await _create_batch_with_items(client, "JSON Batch")
        resp = await client.get(f"/batches/{batch_id}/report?format=json")
    assert resp.status_code == 200
    data = resp.json()
    assert "batch_id" in data


async def test_batch_docx_export():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        batch_id = await _create_batch_with_items(client, "DOCX Batch")
        resp = await client.post(f"/batches/{batch_id}/export/docx")
    if resp.status_code == 200:
        data = resp.json()
        assert "file_path" in data
        if os.path.isfile(data["file_path"]):
            os.remove(data["file_path"])


async def test_batch_pptx_export():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        batch_id = await _create_batch_with_items(client, "PPTX Batch")
        resp = await client.post(f"/batches/{batch_id}/export/pptx")
    if resp.status_code == 200:
        data = resp.json()
        assert "file_path" in data
        if os.path.isfile(data["file_path"]):
            os.remove(data["file_path"])


async def test_batch_pdf_export():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        batch_id = await _create_batch_with_items(client, "PDF Batch")
        resp = await client.post(f"/batches/{batch_id}/export/pdf")
    if resp.status_code == 200:
        data = resp.json()
        assert "file_path" in data
        if os.path.isfile(data["file_path"]):
            os.remove(data["file_path"])
