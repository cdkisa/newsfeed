import pytest
from unittest.mock import patch, MagicMock
from backend.ai.tagger import tag_content
from backend.models import ContentItem, Tag, SourceType, ProcessingStatus

def make_item():
    item = MagicMock(spec=ContentItem)
    item.id = 1
    item.title = "Building AI Agents with LangChain"
    item.body = "A guide to building autonomous AI agents using LangChain framework."
    item.summary = "Guide to building AI agents with LangChain."
    item.source_type = SourceType.blog
    item.processing_status = ProcessingStatus.pending
    return item

@pytest.mark.asyncio
async def test_tag_content(db):
    tag1 = Tag(name="Agent Frameworks", slug="agent-frameworks")
    tag2 = Tag(name="AI Coding Workflows", slug="ai-coding-workflows")
    tag3 = Tag(name="LLM Tools", slug="llm-tools")
    db.add_all([tag1, tag2, tag3])
    await db.commit()
    item = make_item()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="agent-frameworks, llm-tools"))]
    with patch("backend.ai.llm.litellm.acompletion", return_value=mock_response):
        tags = await tag_content(item, db)
    slugs = [t.slug for t in tags]
    assert "agent-frameworks" in slugs
    assert "llm-tools" in slugs
