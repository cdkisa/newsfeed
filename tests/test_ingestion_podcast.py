import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.ingestion.podcast import PodcastFetcher
from backend.models import Source, SourceType

def make_source():
    s = MagicMock(spec=Source)
    s.id = 1; s.person_id = 1; s.type = SourceType.podcast
    s.url = "https://example.com/podcast.xml"; s.last_fetched_at = None; s.active = True
    return s

SAMPLE_PODCAST_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.apple.com/dtds/podcast-1.0.dtd">
  <channel><title>AI Podcast</title>
    <item><title>Episode 42: AI Workflows</title><link>https://example.com/ep42</link>
      <description>We discuss AI workflows with a special guest.</description>
      <enclosure url="https://example.com/ep42.mp3" type="audio/mpeg"/>
      <pubDate>Tue, 24 Mar 2026 08:00:00 GMT</pubDate></item>
  </channel></rss>"""

@pytest.mark.asyncio
async def test_podcast_fetcher():
    fetcher = PodcastFetcher()
    source = make_source()
    with patch("backend.ingestion.podcast.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = AsyncMock()
        mock_resp.text = SAMPLE_PODCAST_FEED
        mock_resp.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_cls.return_value = mock_client
        results = await fetcher.fetch(source)
    assert len(results) == 1
    assert results[0].title == "Episode 42: AI Workflows"
    assert results[0].source_type == SourceType.podcast
