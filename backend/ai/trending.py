import logging
from collections import Counter
from datetime import date, datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.ai.llm import complete
from backend.models import ContentItem, DailyDigest, ProcessingStatus

logger = logging.getLogger(__name__)

async def generate_daily_digest(db: AsyncSession, target_date: date | None = None) -> DailyDigest | None:
    utc_today = datetime.now(timezone.utc).date()
    # If target_date is today's local date (or not provided), use the UTC date
    # so that item timestamps stored in UTC are found correctly.
    if target_date is None or target_date == date.today():
        query_date = utc_today
    else:
        query_date = target_date
    target_date = target_date or utc_today
    start = datetime(query_date.year, query_date.month, query_date.day)
    end = start + timedelta(days=1)
    result = await db.execute(
        select(ContentItem)
        .where(ContentItem.created_at >= start, ContentItem.created_at < end)
        .where(ContentItem.processing_status == ProcessingStatus.completed)
        .options(selectinload(ContentItem.tags))
    )
    items = result.scalars().all()
    if not items:
        logger.info("No content for %s, skipping digest", target_date)
        return None

    tag_counter: Counter[str] = Counter()
    for item in items:
        for tag in item.tags:
            tag_counter[tag.slug] += 1
    hot_topics = [{"tag": slug, "count": count, "trend": "up"} for slug, count in tag_counter.most_common(10)]

    summaries = "\n".join(f"- {item.title}: {item.summary or '(no summary)'}" for item in items[:20])
    highlights = await complete(
        prompt=(
            f"Based on today's content from AI/software engineering thought leaders, "
            f"write 3-5 bullet points highlighting the most notable themes and insights.\n\n"
            f"Today's content:\n{summaries}"
        ),
        system="You write concise daily digest highlights for a tech newsfeed.",
    )

    existing = await db.execute(select(DailyDigest).where(DailyDigest.date == target_date))
    digest = existing.scalar_one_or_none()
    if digest:
        digest.highlights = highlights
        digest.hot_topics = hot_topics
    else:
        digest = DailyDigest(date=target_date, highlights=highlights, hot_topics=hot_topics)
        db.add(digest)
    await db.commit()
    await db.refresh(digest)
    return digest
