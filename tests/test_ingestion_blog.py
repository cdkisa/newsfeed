import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from backend.ingestion.base import RawContent
from backend.ingestion.blog import BlogFetcher
from backend.models import Source, SourceType

def make_source():
    s = MagicMock(spec=Source)
    s.id = 1
    s.person_id = 1
    s.type = SourceType.blog
    s.url = "https://example.com/feed.xml"
    s.last_fetched_at = None
    s.active = True
    return s

SAMPLE_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Blog</title>
    <item>
      <title>My AI Workflow</title>
      <link>https://example.com/ai-workflow</link>
      <description>A deep dive into my AI workflow.</description>
      <pubDate>Wed, 25 Mar 2026 12:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""

@pytest.mark.asyncio
async def test_blog_fetcher_parses_rss():
    fetcher = BlogFetcher()
    source = make_source()
    with patch("backend.ingestion.blog.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = AsyncMock()
        mock_resp.text = SAMPLE_FEED
        mock_resp.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_client
        results = await fetcher.fetch(source)
    assert len(results) == 1
    assert results[0].title == "My AI Workflow"
    assert results[0].url == "https://example.com/ai-workflow"
    assert isinstance(results[0], RawContent)

@pytest.mark.asyncio
async def test_blog_fetcher_filters_by_last_fetched():
    fetcher = BlogFetcher()
    source = make_source()
    source.last_fetched_at = datetime(2026, 3, 26)
    with patch("backend.ingestion.blog.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = AsyncMock()
        mock_resp.text = SAMPLE_FEED
        mock_resp.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_client
        results = await fetcher.fetch(source)
    assert len(results) == 0
