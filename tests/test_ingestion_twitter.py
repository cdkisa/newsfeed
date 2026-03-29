import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from backend.ingestion.twitter import TwitterFetcher
from backend.models import Source, SourceType

def make_source():
    s = MagicMock(spec=Source)
    s.id = 1; s.person_id = 1; s.type = SourceType.twitter
    s.url = "kaboris"; s.last_fetched_at = None; s.active = True
    return s

@pytest.mark.asyncio
async def test_twitter_fetcher():
    fetcher = TwitterFetcher()
    source = make_source()
    mock_user = MagicMock(); mock_user.id = 12345
    mock_tweet = MagicMock(); mock_tweet.id = 99999
    mock_tweet.text = "Just shipped my new AI coding workflow. Thread below."
    mock_tweet.created_at = datetime(2026, 3, 25, 10, 0, 0, tzinfo=timezone.utc)
    mock_response = MagicMock(); mock_response.data = [mock_tweet]
    with patch("backend.ingestion.twitter.settings") as mock_settings:
        mock_settings.twitter_bearer_token = "fake-bearer-token"
        with patch("backend.ingestion.twitter.tweepy.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get_user.return_value = MagicMock(data=mock_user)
            mock_client.get_users_tweets.return_value = mock_response
            mock_client_cls.return_value = mock_client
            results = await fetcher.fetch(source)
    assert len(results) == 1
    assert "AI coding workflow" in results[0].title
    assert results[0].source_type == SourceType.twitter
