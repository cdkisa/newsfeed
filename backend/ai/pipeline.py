import logging
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.ai.summarizer import summarize_content
from backend.ai.tagger import tag_content
from backend.ai.trending import generate_daily_digest
from backend.models import ContentItem, ProcessingStatus

logger = logging.getLogger(__name__)

async def process_new_content(db: AsyncSession) -> int:
    result = await db.execute(
        select(ContentItem).where(ContentItem.processing_status == ProcessingStatus.pending)
    )
    items = result.scalars().all()
    processed = 0
    for item in items:
        item.processing_status = ProcessingStatus.processing
        await db.commit()
        try:
            item.summary = await summarize_content(item)
            tags = await tag_content(item, db)
            item.tags = tags
            item.processing_status = ProcessingStatus.completed
            processed += 1
        except Exception:
            logger.exception("Failed to process content item %d", item.id)
            item.processing_status = ProcessingStatus.failed
        await db.commit()

    if processed > 0:
        await generate_daily_digest(db, target_date=date.today())
    logger.info("AI pipeline complete: %d/%d items processed", processed, len(items))
    return processed
