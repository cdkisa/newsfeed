import asyncio
from slugify import slugify
from sqlalchemy import select
from backend.database import async_session, engine
from backend.models import Base, Tag

INITIAL_TAGS = [
    "AI Coding Workflows",
    "Prompt Engineering",
    "Agent Frameworks",
    "LLM Tools",
    "Open Source",
    "Industry News",
]

async def seed_tags():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as db:
        for name in INITIAL_TAGS:
            slug = slugify(name)
            existing = await db.execute(select(Tag).where(Tag.slug == slug))
            if not existing.scalar_one_or_none():
                db.add(Tag(name=name, slug=slug))
                print(f"  Created tag: {name}")
            else:
                print(f"  Tag exists: {name}")
        await db.commit()
    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_tags())
