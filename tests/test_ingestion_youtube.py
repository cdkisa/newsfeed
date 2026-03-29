import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from backend.ingestion.youtube import YouTubeFetcher
from backend.models import Source, SourceType

def make_source():
    s = MagicMock(spec=Source)
    s.id = 1; s.person_id = 1; s.type = SourceType.youtube
    s.url = "UC_x5XG1OV2P6uZZ5FSM9Ttw"; s.last_fetched_at = None; s.active = True
    return s

MOCK_SEARCH_RESPONSE = {"items": [{"id": {"videoId": "abc123"}, "snippet": {"title": "AI Coding Tips", "publishedAt": "2026-03-25T10:00:00Z", "description": "Tips for AI coding workflows."}}]}

@pytest.mark.asyncio
async def test_youtube_fetcher():
    fetcher = YouTubeFetcher()
    source = make_source()
    mock_service = MagicMock()
    mock_search = MagicMock()
    mock_list = MagicMock()
    mock_list.execute.return_value = MOCK_SEARCH_RESPONSE
    mock_search.list.return_value = mock_list
    mock_service.search.return_value = mock_search
    with patch("backend.ingestion.youtube.build", return_value=mock_service):
        with patch("backend.ingestion.youtube.YouTubeTranscriptApi") as mock_yt_api:
            mock_yt_api.get_transcript.return_value = [{"text": "Hello everyone."}, {"text": "Today we talk about AI."}]
            results = await fetcher.fetch(source)
    assert len(results) == 1
    assert results[0].title == "AI Coding Tips"
    assert results[0].url == "https://www.youtube.com/watch?v=abc123"
    assert "Hello everyone" in results[0].body
