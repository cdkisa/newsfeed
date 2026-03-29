import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone
from backend.ingestion.base import RawContent
from backend.ingestion.orchestrator import run_ingestion
from backend.models import Person, Source, ContentItem, SourceType

@pytest.mark.asyncio
async def test_orchestrator_stores_content(db):
    person = Person(name="Test Person")
    db.add(person)
    await db.flush()
    source = Source(person_id=person.id, type=SourceType.blog, url="https://example.com/feed")
    db.add(source)
    await db.commit()

    mock_content = [RawContent(title="Test Post", url="https://example.com/test-post", body="Content body here.", published_at=datetime(2026, 3, 25, tzinfo=timezone.utc), source_type=SourceType.blog)]

    with patch("backend.ingestion.orchestrator.FETCHER_MAP") as mock_map:
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch.return_value = mock_content
        mock_map.get.return_value = mock_fetcher
        mock_map.__contains__ = lambda self, key: True
        mock_map.__getitem__ = lambda self, key: mock_fetcher
        await run_ingestion(db)

    from sqlalchemy import select
    result = await db.execute(select(ContentItem))
    items = result.scalars().all()
    assert len(items) == 1
    assert items[0].title == "Test Post"

@pytest.mark.asyncio
async def test_orchestrator_deduplicates(db):
    person = Person(name="Test Person")
    db.add(person)
    await db.flush()
    source = Source(person_id=person.id, type=SourceType.blog, url="https://example.com/feed")
    db.add(source)
    await db.flush()
    existing = ContentItem(source_id=source.id, person_id=person.id, title="Existing", url="https://example.com/test-post", source_type=SourceType.blog)
    db.add(existing)
    await db.commit()

    mock_content = [RawContent(title="Test Post", url="https://example.com/test-post", body="Duplicate", published_at=None, source_type=SourceType.blog)]

    with patch("backend.ingestion.orchestrator.FETCHER_MAP") as mock_map:
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch.return_value = mock_content
        mock_map.get.return_value = mock_fetcher
        mock_map.__contains__ = lambda self, key: True
        mock_map.__getitem__ = lambda self, key: mock_fetcher
        await run_ingestion(db)

    from sqlalchemy import select, func
    count = (await db.execute(select(func.count(ContentItem.id)))).scalar()
    assert count == 1
