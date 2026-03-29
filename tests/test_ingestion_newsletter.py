import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.ingestion.newsletter import NewsletterFetcher
from backend.models import Source, SourceType

def make_source():
    s = MagicMock(spec=Source)
    s.id = 1; s.person_id = 1; s.type = SourceType.newsletter
    s.url = "https://example.substack.com/feed"; s.last_fetched_at = None; s.active = True
    return s

SAMPLE_SUBSTACK_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>AI Weekly</title>
    <item><title>Issue 10: The Rise of AI Agents</title>
      <link>https://example.substack.com/p/issue-10</link>
      <description>This week we cover the rise of autonomous AI agents.</description>
      <pubDate>Mon, 23 Mar 2026 09:00:00 GMT</pubDate></item>
  </channel></rss>"""

@pytest.mark.asyncio
async def test_newsletter_fetcher():
    fetcher = NewsletterFetcher()
    source = make_source()
    with patch("backend.ingestion.newsletter.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = AsyncMock()
        mock_resp.text = SAMPLE_SUBSTACK_FEED
        mock_resp.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_cls.return_value = mock_client
        results = await fetcher.fetch(source)
    assert len(results) == 1
    assert results[0].title == "Issue 10: The Rise of AI Agents"
    assert results[0].source_type == SourceType.newsletter
