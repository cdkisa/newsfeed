from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify

from backend.api.deps import get_db, require_admin_key
from backend.models import Person, Source, Tag
from backend.schemas import (
    PersonCreate, PersonUpdate, PersonOut,
    SourceCreate, SourceOut,
    TagCreate, TagOut,
    IngestTriggerOut,
)

router = APIRouter(dependencies=[Depends(require_admin_key)])


@router.post("/people", response_model=PersonOut, status_code=201)
async def create_person(body: PersonCreate, db: AsyncSession = Depends(get_db)):
    person = Person(**body.model_dump())
    db.add(person)
    await db.commit()
    await db.refresh(person, ["sources"])
    return PersonOut(
        id=person.id, name=person.name, avatar_url=person.avatar_url,
        bio=person.bio, source_count=len(person.sources), created_at=person.created_at,
    )


@router.put("/people/{person_id}", response_model=PersonOut)
async def update_person(person_id: int, body: PersonUpdate, db: AsyncSession = Depends(get_db)):
    person = await db.get(Person, person_id)
    if not person:
        raise HTTPException(404, "Person not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(person, field, value)
    await db.commit()
    await db.refresh(person, ["sources"])
    return PersonOut(
        id=person.id, name=person.name, avatar_url=person.avatar_url,
        bio=person.bio, source_count=len(person.sources), created_at=person.created_at,
    )


@router.delete("/people/{person_id}", status_code=204)
async def delete_person(person_id: int, db: AsyncSession = Depends(get_db)):
    person = await db.get(Person, person_id)
    if not person:
        raise HTTPException(404, "Person not found")
    await db.delete(person)
    await db.commit()


@router.get("/people/{person_id}/sources", response_model=list[SourceOut])
async def list_sources(person_id: int, db: AsyncSession = Depends(get_db)):
    person = await db.get(Person, person_id)
    if not person:
        raise HTTPException(404, "Person not found")
    result = await db.execute(select(Source).where(Source.person_id == person_id))
    return result.scalars().all()


@router.post("/people/{person_id}/sources", response_model=SourceOut, status_code=201)
async def add_source(person_id: int, body: SourceCreate, db: AsyncSession = Depends(get_db)):
    person = await db.get(Person, person_id)
    if not person:
        raise HTTPException(404, "Person not found")
    source = Source(person_id=person_id, **body.model_dump())
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@router.delete("/sources/{source_id}", status_code=204)
async def delete_source(source_id: int, db: AsyncSession = Depends(get_db)):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(404, "Source not found")
    await db.delete(source)
    await db.commit()


@router.post("/tags", response_model=TagOut, status_code=201)
async def create_tag(body: TagCreate, db: AsyncSession = Depends(get_db)):
    slug = slugify(body.name)
    existing = await db.execute(select(Tag).where(Tag.slug == slug))
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Tag already exists")
    tag = Tag(name=body.name, slug=slug)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


@router.post("/ingest/trigger", response_model=IngestTriggerOut)
async def trigger_ingest():
    import logging
    logger = logging.getLogger(__name__)
    try:
        from backend.scheduler import run_ingestion_now
        await run_ingestion_now()
        return IngestTriggerOut(status="started", message="Ingestion triggered")
    except Exception as e:
        logger.exception("Ingestion trigger failed")
        return IngestTriggerOut(status="error", message=str(e))
