from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_brand_profiles_list_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/brand-profiles")
    assert resp.status_code == 200
    assert "Brand Profiles" in resp.text


async def test_new_brand_profile_form_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/brand-profiles/new")
    assert resp.status_code == 200
    assert "New Brand Profile" in resp.text


async def test_brand_profile_can_be_created():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/ui/brand-profiles",
            data={"name": "Test Brand UI", "tone_of_voice": "Professional"},
            follow_redirects=True,
        )
    assert resp.status_code == 200
    assert "Test Brand UI" in resp.text


async def test_audience_profiles_list_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/audience-profiles")
    assert resp.status_code == 200
    assert "Audience Profiles" in resp.text


async def test_new_audience_profile_form_loads():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ui/audience-profiles/new")
    assert resp.status_code == 200
    assert "New Audience Profile" in resp.text


async def test_audience_profile_can_be_created():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/ui/audience-profiles",
            data={"name": "Test Audience UI", "segment_description": "Young professionals"},
            follow_redirects=True,
        )
    assert resp.status_code == 200
    assert "Test Audience UI" in resp.text
