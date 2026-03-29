import logging
from datetime import timezone
from email.utils import parsedate_to_datetime
import feedparser
import httpx
from backend.ingestion.base import BaseFetcher, RawContent
from backend.models import Source, SourceType

logger = logging.getLogger(__name__)

class PodcastFetcher(BaseFetcher):
    async def fetch(self, source: Source) -> list[RawContent]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(source.url, timeout=30, follow_redirects=True)
            feed = feedparser.parse(resp.text)
        except Exception:
            logger.exception("Failed to fetch podcast feed: %s", source.url)
            return []

        results: list[RawContent] = []
        for entry in feed.entries:
            published = None
            if hasattr(entry, "published"):
                try:
                    published = parsedate_to_datetime(entry.published)
                except Exception:
                    pass
            if source.last_fetched_at and published:
                cutoff = source.last_fetched_at
                if cutoff.tzinfo is None:
                    cutoff = cutoff.replace(tzinfo=timezone.utc)
                pub_aware = published if published.tzinfo else published.replace(tzinfo=timezone.utc)
                if pub_aware <= cutoff:
                    continue
            results.append(RawContent(title=entry.get("title", "Untitled Episode"), url=entry.get("link", ""), body=entry.get("summary", ""), published_at=published, source_type=SourceType.podcast))
        return results
