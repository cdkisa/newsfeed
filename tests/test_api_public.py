import pytest
from datetime import date
from httpx import ASGITransport, AsyncClient

from backend.main import app
from backend.models import Person, Source, ContentItem, Tag, DailyDigest, SourceType, ProcessingStatus


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def seed_data(db):
    person = Person(name="Boris Cherny", avatar_url="https://example.com/boris.jpg")
    db.add(person)
    await db.flush()
    source = Source(person_id=person.id, type=SourceType.blog, url="https://boris.com/feed")
    db.add(source)
    await db.flush()
    tag = Tag(name="AI Coding Workflows", slug="ai-coding-workflows")
    db.add(tag)
    await db.flush()
    item = ContentItem(
        source_id=source.id, person_id=person.id,
        title="My AI Workflow", url="https://boris.com/ai-workflow",
        summary="Boris shares his AI coding setup.",
        source_type=SourceType.blog, processing_status=ProcessingStatus.completed,
    )
    item.tags.append(tag)
    db.add(item)
    digest = DailyDigest(
        date=date(2026, 3, 26),
        highlights="- Boris shared his workflow\n- New tools released",
        hot_topics=[{"tag": "ai-coding-workflows", "count": 3, "trend": "up"}],
    )
    db.add(digest)
    await db.commit()
    return {"person": person, "source": source, "item": item, "tag": tag, "digest": digest}


@pytest.mark.asyncio
async def test_get_content_list(client, seed_data):
    resp = await client.get("/api/content")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "My AI Workflow"


@pytest.mark.asyncio
async def test_get_content_by_id(client, seed_data):
    item_id = seed_data["item"].id
    resp = await client.get(f"/api/content/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "My AI Workflow"


@pytest.mark.asyncio
async def test_get_people(client, seed_data):
    resp = await client.get("/api/people")
    assert resp.status_code == 200
    people = resp.json()
    assert len(people) == 1
    assert people[0]["name"] == "Boris Cherny"
    assert people[0]["source_count"] == 1


@pytest.mark.asyncio
async def test_get_person_content(client, seed_data):
    pid = seed_data["person"].id
    resp = await client.get(f"/api/people/{pid}/content")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_get_tags(client, seed_data):
    resp = await client.get("/api/tags")
    assert resp.status_code == 200
    tags = resp.json()
    assert len(tags) == 1
    assert tags[0]["slug"] == "ai-coding-workflows"
    assert tags[0]["count"] == 1


@pytest.mark.asyncio
async def test_get_tag_content(client, seed_data):
    resp = await client.get("/api/tags/ai-coding-workflows/content")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_get_digest_today(client, seed_data):
    resp = await client.get("/api/digest/today")
    assert resp.status_code == 200
    data = resp.json()
    assert "Boris" in data["highlights"]


@pytest.mark.asyncio
async def test_get_digest_history(client, seed_data):
    resp = await client.get("/api/digest/history")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
