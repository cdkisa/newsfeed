import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


ADMIN_HEADERS = {"X-Admin-Key": "change-me-in-production"}


@pytest.mark.asyncio
async def test_create_person(client):
    resp = await client.post("/api/admin/people", json={"name": "Boris Cherny"}, headers=ADMIN_HEADERS)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Boris Cherny"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_person_no_auth(client):
    resp = await client.post("/api/admin/people", json={"name": "Test"})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_update_person(client):
    resp = await client.post("/api/admin/people", json={"name": "Original"}, headers=ADMIN_HEADERS)
    pid = resp.json()["id"]
    resp = await client.put(f"/api/admin/people/{pid}", json={"name": "Updated"}, headers=ADMIN_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_person(client):
    resp = await client.post("/api/admin/people", json={"name": "ToDelete"}, headers=ADMIN_HEADERS)
    pid = resp.json()["id"]
    resp = await client.delete(f"/api/admin/people/{pid}", headers=ADMIN_HEADERS)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_add_source_to_person(client):
    resp = await client.post("/api/admin/people", json={"name": "Karpathy"}, headers=ADMIN_HEADERS)
    pid = resp.json()["id"]
    resp = await client.post(
        f"/api/admin/people/{pid}/sources",
        json={"type": "youtube", "url": "https://youtube.com/@karpathy"},
        headers=ADMIN_HEADERS,
    )
    assert resp.status_code == 201
    assert resp.json()["type"] == "youtube"


@pytest.mark.asyncio
async def test_delete_source(client):
    resp = await client.post("/api/admin/people", json={"name": "Test"}, headers=ADMIN_HEADERS)
    pid = resp.json()["id"]
    resp = await client.post(
        f"/api/admin/people/{pid}/sources",
        json={"type": "blog", "url": "https://example.com/feed"},
        headers=ADMIN_HEADERS,
    )
    sid = resp.json()["id"]
    resp = await client.delete(f"/api/admin/sources/{sid}", headers=ADMIN_HEADERS)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_create_tag(client):
    resp = await client.post("/api/admin/tags", json={"name": "AI Coding Workflows"}, headers=ADMIN_HEADERS)
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] == "ai-coding-workflows"
