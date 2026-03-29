import pytest
from datetime import date
from sqlalchemy import select

from backend.models import Person, Source, ContentItem, Tag, DailyDigest, SourceType, ProcessingStatus


@pytest.mark.asyncio
async def test_create_person(db):
    person = Person(name="Boris Cherny")
    db.add(person)
    await db.commit()
    result = await db.execute(select(Person).where(Person.name == "Boris Cherny"))
    assert result.scalar_one().name == "Boris Cherny"


@pytest.mark.asyncio
async def test_create_source_linked_to_person(db):
    person = Person(name="Andrej Karpathy")
    db.add(person)
    await db.flush()
    source = Source(person_id=person.id, type=SourceType.youtube, url="https://youtube.com/@karpathy")
    db.add(source)
    await db.commit()
    result = await db.execute(select(Source).where(Source.person_id == person.id))
    src = result.scalar_one()
    assert src.type == SourceType.youtube
    assert src.active is True


@pytest.mark.asyncio
async def test_content_item_unique_url(db):
    person = Person(name="Test")
    db.add(person)
    await db.flush()
    source = Source(person_id=person.id, type=SourceType.blog, url="https://example.com/feed")
    db.add(source)
    await db.flush()
    item1 = ContentItem(
        source_id=source.id, person_id=person.id, title="Post 1",
        url="https://example.com/post-1", source_type=SourceType.blog,
        processing_status=ProcessingStatus.pending,
    )
    db.add(item1)
    await db.commit()
    item2 = ContentItem(
        source_id=source.id, person_id=person.id, title="Duplicate",
        url="https://example.com/post-1", source_type=SourceType.blog,
        processing_status=ProcessingStatus.pending,
    )
    db.add(item2)
    with pytest.raises(Exception):
        await db.commit()


@pytest.mark.asyncio
async def test_content_item_tags(db):
    person = Person(name="Test")
    db.add(person)
    await db.flush()
    source = Source(person_id=person.id, type=SourceType.blog, url="https://example.com/feed")
    db.add(source)
    await db.flush()
    tag = Tag(name="AI Coding Workflows", slug="ai-coding-workflows")
    db.add(tag)
    await db.flush()
    item = ContentItem(
        source_id=source.id, person_id=person.id, title="Post",
        url="https://example.com/post", source_type=SourceType.blog,
        processing_status=ProcessingStatus.pending,
    )
    item.tags.append(tag)
    db.add(item)
    await db.commit()
    result = await db.execute(select(ContentItem).where(ContentItem.url == "https://example.com/post"))
    loaded = result.scalar_one()
    await db.refresh(loaded, ["tags"])
    assert len(loaded.tags) == 1
    assert loaded.tags[0].slug == "ai-coding-workflows"


@pytest.mark.asyncio
async def test_daily_digest(db):
    digest = DailyDigest(
        date=date(2026, 3, 26),
        highlights="- Topic A trending\n- Topic B emerging",
        hot_topics=[{"tag": "ai-coding", "count": 5, "trend": "up"}],
    )
    db.add(digest)
    await db.commit()
    result = await db.execute(select(DailyDigest))
    d = result.scalar_one()
    assert d.hot_topics[0]["tag"] == "ai-coding"
