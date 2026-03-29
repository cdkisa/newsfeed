import pytest
from unittest.mock import patch, MagicMock
from backend.ai.summarizer import summarize_content
from backend.models import ContentItem, SourceType, ProcessingStatus

def make_item(source_type=SourceType.blog, body="A long article about AI workflows that is definitely more than 200 characters. " * 5):
    item = MagicMock(spec=ContentItem)
    item.id = 1
    item.title = "My AI Workflow"
    item.body = body
    item.source_type = source_type
    item.processing_status = ProcessingStatus.pending
    item.summary = None
    return item

@pytest.mark.asyncio
async def test_summarize_long_content():
    item = make_item()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Boris describes his AI coding setup using Claude and Cursor."))]
    with patch("backend.ai.llm.litellm.acompletion", return_value=mock_response) as mock_llm:
        result = await summarize_content(item)
    assert result == "Boris describes his AI coding setup using Claude and Cursor."
    mock_llm.assert_called_once()

@pytest.mark.asyncio
async def test_skip_summarize_short_content():
    item = make_item(source_type=SourceType.twitter, body="Just shipped v2!")
    result = await summarize_content(item)
    assert result == "Just shipped v2!"
