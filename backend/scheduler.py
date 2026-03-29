import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.config import settings
from backend.database import async_session

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def daily_ingestion_job():
    logger.info("Starting daily ingestion job")
    from backend.ingestion.orchestrator import run_ingestion
    from backend.ai.pipeline import process_new_content
    async with async_session() as db:
        new_items = await run_ingestion(db)
        logger.info("Ingested %d new items, starting AI processing", new_items)
        if new_items > 0:
            processed = await process_new_content(db)
            logger.info("AI processed %d items", processed)

async def run_ingestion_now():
    logger.info("Manual ingestion triggered")
    await daily_ingestion_job()

def start_scheduler():
    parts = settings.ingest_schedule.split()
    if len(parts) == 5:
        trigger = CronTrigger(minute=parts[0], hour=parts[1], day=parts[2], month=parts[3], day_of_week=parts[4])
    else:
        trigger = CronTrigger(hour=6, minute=0)
    scheduler.add_job(daily_ingestion_job, trigger, id="daily_ingest", replace_existing=True)
    scheduler.start()
    logger.info("Scheduler started with schedule: %s", settings.ingest_schedule)

def stop_scheduler():
    scheduler.shutdown(wait=False)
