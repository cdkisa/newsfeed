from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.ai.llm import complete
from backend.models import ContentItem, Tag

async def tag_content(item: ContentItem, db: AsyncSession) -> list[Tag]:
    result = await db.execute(select(Tag))
    all_tags = result.scalars().all()
    if not all_tags:
        return []
    tag_list = ", ".join(f"{t.slug}" for t in all_tags)
    prompt = (
        f"Classify the following content into 1-3 of these tags: {tag_list}\n\n"
        f"Title: {item.title}\n"
        f"Summary: {item.summary or item.body or ''}\n\n"
        f"Return ONLY a comma-separated list of tag slugs. Nothing else."
    )
    response = await complete(
        prompt=prompt,
        system="You are a content classifier. Return only comma-separated tag slugs.",
    )
    selected_slugs = [s.strip() for s in response.strip().split(",")]
    slug_to_tag = {t.slug: t for t in all_tags}
    return [slug_to_tag[slug] for slug in selected_slugs if slug in slug_to_tag]
