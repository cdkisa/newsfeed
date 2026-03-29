import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.ingestion.github_fetcher import GitHubFetcher
from backend.models import Source, SourceType

def make_source():
    s = MagicMock(spec=Source)
    s.id = 1; s.person_id = 1; s.type = SourceType.github
    s.url = "karpathy"; s.last_fetched_at = None; s.active = True
    return s

MOCK_EVENTS = [
    {"type": "CreateEvent", "repo": {"name": "karpathy/nanoGPT"}, "payload": {"ref_type": "repository", "description": "Simplest GPT training"}, "created_at": "2026-03-25T10:00:00Z"},
    {"type": "PushEvent", "repo": {"name": "karpathy/minbpe"}, "payload": {"commits": [{"message": "Add tokenizer benchmarks"}]}, "created_at": "2026-03-24T08:00:00Z"},
]

@pytest.mark.asyncio
async def test_github_fetcher():
    fetcher = GitHubFetcher()
    source = make_source()
    with patch("backend.ingestion.github_fetcher.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = AsyncMock()
        mock_resp.json = MagicMock(return_value=MOCK_EVENTS)
        mock_resp.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_cls.return_value = mock_client
        results = await fetcher.fetch(source)
    assert len(results) == 2
    assert "nanoGPT" in results[0].title
    assert results[0].source_type == SourceType.github
