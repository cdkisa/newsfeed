import logging
from datetime import timezone
import tweepy
from backend.config import settings
from backend.ingestion.base import BaseFetcher, RawContent
from backend.models import Source, SourceType

logger = logging.getLogger(__name__)

class TwitterFetcher(BaseFetcher):
    async def fetch(self, source: Source) -> list[RawContent]:
        if not settings.twitter_bearer_token:
            logger.warning("No Twitter bearer token configured, skipping")
            return []
        try:
            client = tweepy.Client(bearer_token=settings.twitter_bearer_token)
            user_resp = client.get_user(username=source.url)
            if not user_resp.data:
                logger.warning("Twitter user not found: %s", source.url)
                return []
            user_id = user_resp.data.id
            tweets_resp = client.get_users_tweets(user_id, max_results=10, tweet_fields=["created_at"])
        except Exception:
            logger.exception("Failed to fetch tweets for: %s", source.url)
            return []

        if not tweets_resp.data:
            return []

        results: list[RawContent] = []
        for tweet in tweets_resp.data:
            published = tweet.created_at
            if published and published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
            if source.last_fetched_at and published:
                cutoff = source.last_fetched_at
                if cutoff.tzinfo is None:
                    cutoff = cutoff.replace(tzinfo=timezone.utc)
                if published <= cutoff:
                    continue
            truncated = tweet.text[:80] + "..." if len(tweet.text) > 80 else tweet.text
            results.append(RawContent(title=truncated, url=f"https://twitter.com/{source.url}/status/{tweet.id}", body=tweet.text, published_at=published, source_type=SourceType.twitter))
        return results
