import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import Source, ContentItem, SourceType, ProcessingStatus
from backend.ingestion.base import BaseFetcher, RawContent
from backend.ingestion.blog import BlogFetcher
from backend.ingestion.youtube import YouTubeFetcher
from backend.ingestion.podcast import PodcastFetcher
from backend.ingestion.twitter import TwitterFetcher
from backend.ingestion.newsletter import NewsletterFetcher
from backend.ingestion.github_fetcher import GitHubFetcher

logger = logging.getLogger(__name__)

FETCHER_MAP: dict[SourceType, BaseFetcher] = {
    SourceType.blog: BlogFetcher(),
    SourceType.youtube: YouTubeFetcher(),
    SourceType.podcast: PodcastFetcher(),
    SourceType.twitter: TwitterFetcher(),
    SourceType.newsletter: NewsletterFetcher(),
    SourceType.github: GitHubFetcher(),
}

async def run_ingestion(db: AsyncSession) -> int:
    result = await db.execute(select(Source).where(Source.active == True))
    sources = result.scalars().all()
    total_new = 0
    for source in sources:
        fetcher = FETCHER_MAP.get(source.type)
        if not fetcher:
            logger.warning("No fetcher for source type: %s", source.type)
            continue
        try:
            raw_items = await fetcher.fetch(source)
        except Exception:
            logger.exception("Fetcher failed for source %s (id=%d)", source.url, source.id)
            continue
        for raw in raw_items:
            existing = await db.execute(select(ContentItem).where(ContentItem.url == raw.url))
            if existing.scalar_one_or_none():
                continue
            published_at = raw.published_at.replace(tzinfo=None) if raw.published_at and raw.published_at.tzinfo else raw.published_at
            item = ContentItem(source_id=source.id, person_id=source.person_id, title=raw.title, url=raw.url, body=raw.body, source_type=raw.source_type, published_at=published_at, processing_status=ProcessingStatus.pending)
            db.add(item)
            total_new += 1
        source.last_fetched_at = datetime.utcnow()
    await db.commit()
    logger.info("Ingestion complete: %d new items", total_new)
    return total_new
