import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime, timezone
from backend.ai.trending import generate_daily_digest
from backend.models import Person, Source, ContentItem, Tag, SourceType, ProcessingStatus

@pytest.mark.asyncio
async def test_generate_daily_digest(db):
    person = Person(name="Test")
    db.add(person)
    await db.flush()
    source = Source(person_id=person.id, type=SourceType.blog, url="https://example.com/feed")
    db.add(source)
    await db.flush()
    tag = Tag(name="AI Coding Workflows", slug="ai-coding-workflows")
    db.add(tag)
    await db.flush()

    item1 = ContentItem(
        source_id=source.id, person_id=person.id, title="Post 1",
        url="https://example.com/1", summary="Summary 1",
        source_type=SourceType.blog, processing_status=ProcessingStatus.completed,
        created_at=datetime.now(timezone.utc),
    )
    item1.tags.append(tag)
    item2 = ContentItem(
        source_id=source.id, person_id=person.id, title="Post 2",
        url="https://example.com/2", summary="Summary 2",
        source_type=SourceType.blog, processing_status=ProcessingStatus.completed,
        created_at=datetime.now(timezone.utc),
    )
    item2.tags.append(tag)
    db.add_all([item1, item2])
    await db.commit()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(
        content="- AI coding workflows dominated today\n- Two posts about AI-assisted development"
    ))]
    with patch("backend.ai.llm.litellm.acompletion", return_value=mock_response):
        digest = await generate_daily_digest(db, target_date=date.today())

    assert digest is not None
    assert "AI coding" in digest.highlights
    assert len(digest.hot_topics) >= 1
    assert digest.hot_topics[0]["tag"] == "ai-coding-workflows"
