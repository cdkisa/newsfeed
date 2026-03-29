from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.api.deps import get_db
from backend.models import ContentItem, Person, Source, Tag, DailyDigest, SourceType, content_tags
from backend.schemas import ContentItemOut, ContentListOut, PersonOut, TagWithCount, TagOut, DailyDigestOut

router = APIRouter()


@router.get("/content", response_model=ContentListOut)
async def list_content(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    person_id: int | None = None,
    source_type: SourceType | None = None,
    tag_slug: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(ContentItem).options(selectinload(ContentItem.tags), selectinload(ContentItem.person))
    count_query = select(func.count(ContentItem.id))

    if person_id:
        query = query.where(ContentItem.person_id == person_id)
        count_query = count_query.where(ContentItem.person_id == person_id)
    if source_type:
        query = query.where(ContentItem.source_type == source_type)
        count_query = count_query.where(ContentItem.source_type == source_type)
    if tag_slug:
        query = query.join(content_tags).join(Tag).where(Tag.slug == tag_slug)
        count_query = count_query.join(content_tags).join(Tag).where(Tag.slug == tag_slug)
    if search:
        pattern = f"%{search}%"
        query = query.where(ContentItem.title.ilike(pattern) | ContentItem.summary.ilike(pattern))
        count_query = count_query.where(ContentItem.title.ilike(pattern) | ContentItem.summary.ilike(pattern))

    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(desc(ContentItem.published_at), desc(ContentItem.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return ContentListOut(
        items=[
            ContentItemOut(
                id=item.id, person_id=item.person_id,
                person_name=item.person.name if item.person else "",
                person_avatar_url=item.person.avatar_url if item.person else None,
                title=item.title, url=item.url, summary=item.summary,
                source_type=item.source_type, published_at=item.published_at,
                processing_status=item.processing_status,
                tags=[TagOut.model_validate(t) for t in item.tags],
                created_at=item.created_at,
            )
            for item in items
        ],
        total=total, page=page, page_size=page_size,
    )


@router.get("/content/{content_id}", response_model=ContentItemOut)
async def get_content(content_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ContentItem).where(ContentItem.id == content_id)
        .options(selectinload(ContentItem.tags), selectinload(ContentItem.person))
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Content not found")
    return ContentItemOut(
        id=item.id, person_id=item.person_id,
        person_name=item.person.name if item.person else "",
        person_avatar_url=item.person.avatar_url if item.person else None,
        title=item.title, url=item.url, summary=item.summary,
        source_type=item.source_type, published_at=item.published_at,
        processing_status=item.processing_status,
        tags=[TagOut.model_validate(t) for t in item.tags],
        created_at=item.created_at,
    )


@router.get("/people", response_model=list[PersonOut])
async def list_people(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Person).options(selectinload(Person.sources)))
    people = result.scalars().all()
    return [
        PersonOut(
            id=p.id, name=p.name, avatar_url=p.avatar_url, bio=p.bio,
            source_count=len(p.sources), created_at=p.created_at,
        )
        for p in people
    ]


@router.get("/people/{person_id}/content", response_model=ContentListOut)
async def get_person_content(
    person_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    person = await db.get(Person, person_id)
    if not person:
        raise HTTPException(404, "Person not found")
    return await list_content(page=page, page_size=page_size, person_id=person_id, db=db)


@router.get("/tags", response_model=list[TagWithCount])
async def list_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Tag, func.count(content_tags.c.content_id).label("count"))
        .outerjoin(content_tags)
        .group_by(Tag.id)
        .order_by(desc("count"))
    )
    return [
        TagWithCount(id=tag.id, name=tag.name, slug=tag.slug, count=count)
        for tag, count in result.all()
    ]


@router.get("/tags/{slug}/content", response_model=ContentListOut)
async def get_tag_content(
    slug: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    tag = (await db.execute(select(Tag).where(Tag.slug == slug))).scalar_one_or_none()
    if not tag:
        raise HTTPException(404, "Tag not found")
    return await list_content(page=page, page_size=page_size, tag_slug=slug, db=db)


@router.get("/digest/today", response_model=DailyDigestOut)
async def get_digest_today(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DailyDigest).order_by(desc(DailyDigest.date)).limit(1)
    )
    digest = result.scalar_one_or_none()
    if not digest:
        raise HTTPException(404, "No digest available")
    return digest


@router.get("/digest/history", response_model=list[DailyDigestOut])
async def get_digest_history(
    limit: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DailyDigest).order_by(desc(DailyDigest.date)).limit(limit)
    )
    return result.scalars().all()
