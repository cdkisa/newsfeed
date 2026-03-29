# AI Workflow Newsfeed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a web dashboard that aggregates and AI-processes content from thought leaders sharing AI engineering workflows.

**Architecture:** Python FastAPI backend handles content ingestion (6 source types), AI processing (summarization, tagging, trending via LiteLLM), and serves a REST API. React + Vite + TypeScript frontend displays a filterable feed, person profiles, trending highlights, and an admin UI. PostgreSQL stores everything.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, APScheduler, LiteLLM, feedparser, BeautifulSoup4, httpx | React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, React Router | PostgreSQL 16, Docker Compose

**Spec:** `docs/superpowers/specs/2026-03-26-ai-workflow-newsfeed-design.md`

---

## File Structure

```
newsfeed/
├── backend/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app, lifespan, CORS
│   ├── config.py                   # Pydantic Settings (env vars)
│   ├── database.py                 # Async engine, session factory
│   ├── models.py                   # All SQLAlchemy ORM models
│   ├── schemas.py                  # Pydantic request/response schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                 # get_db, require_admin_key dependencies
│   │   ├── public.py               # Public endpoints (content, people, tags, digest)
│   │   └── admin.py                # Admin endpoints (CRUD people/sources/tags, trigger)
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── base.py                 # BaseFetcher ABC, RawContent dataclass
│   │   ├── blog.py                 # Blog/RSS fetcher
│   │   ├── youtube.py              # YouTube fetcher
│   │   ├── podcast.py              # Podcast fetcher
│   │   ├── twitter.py              # Twitter/X fetcher
│   │   ├── newsletter.py           # Newsletter/Substack fetcher
│   │   ├── github_fetcher.py       # GitHub fetcher (avoid shadowing stdlib)
│   │   └── orchestrator.py         # Runs all fetchers, dedupes, stores
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── llm.py                  # LiteLLM completion wrapper
│   │   ├── summarizer.py           # Stage 1: summarization
│   │   ├── tagger.py               # Stage 2: tagging
│   │   └── trending.py             # Stage 3: daily digest + hot topics
│   └── scheduler.py                # APScheduler setup + job definitions
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Fixtures: async db, test client, factories
│   ├── test_models.py              # Model creation + constraints
│   ├── test_api_admin.py           # Admin CRUD endpoints
│   ├── test_api_public.py          # Public read endpoints
│   ├── test_ingestion_blog.py      # Blog fetcher
│   ├── test_ingestion_youtube.py   # YouTube fetcher
│   ├── test_ingestion_podcast.py   # Podcast fetcher
│   ├── test_ingestion_twitter.py   # Twitter fetcher
│   ├── test_ingestion_newsletter.py# Newsletter fetcher
│   ├── test_ingestion_github.py    # GitHub fetcher
│   ├── test_orchestrator.py        # Orchestrator
│   ├── test_ai_summarizer.py       # Summarizer
│   ├── test_ai_tagger.py           # Tagger
│   └── test_ai_trending.py         # Trending/digest
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
├── pyproject.toml
├── Dockerfile
├── .env.example
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/
│       │   └── client.ts            # Typed fetch wrapper for backend API
│       ├── hooks/
│       │   └── useApi.ts            # TanStack Query hooks
│       ├── types/
│       │   └── index.ts             # TypeScript types matching backend schemas
│       ├── pages/
│       │   ├── FeedPage.tsx
│       │   ├── PersonPage.tsx
│       │   ├── TrendingPage.tsx
│       │   └── AdminPage.tsx
│       └── components/
│           ├── Layout.tsx
│           ├── ContentCard.tsx
│           ├── FilterBar.tsx
│           ├── TagCloud.tsx
│           └── SourceIcon.tsx
└── docker-compose.yml
```

---

## Task 1: Project Scaffolding

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/__init__.py`
- Create: `.env.example`
- Create: `docker-compose.yml`
- Create: `backend/Dockerfile`

- [ ] **Step 1: Create backend pyproject.toml**

```toml
# backend/pyproject.toml
[project]
name = "newsfeed-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlalchemy[asyncio]>=2.0.36",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pydantic-settings>=2.6.0",
    "litellm>=1.55.0",
    "feedparser>=6.0.11",
    "beautifulsoup4>=4.12.3",
    "httpx>=0.28.0",
    "google-api-python-client>=2.157.0",
    "youtube-transcript-api>=0.6.3",
    "tweepy>=4.14.0",
    "apscheduler>=3.10.4",
    "python-slugify>=8.0.4",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.28.0",
    "aiosqlite>=0.20.0",
]

[build-system]
requires = ["setuptools>=75.0"]
build-backend = "setuptools.backends._legacy:_Backend"
```

- [ ] **Step 2: Create backend/__init__.py**

```python
# backend/__init__.py
```

Empty init file.

- [ ] **Step 3: Create .env.example**

```bash
# .env.example
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/newsfeed
LLM_PROVIDER=anthropic/claude-sonnet-4-20250514
LLM_API_KEY=your-llm-api-key
ADMIN_API_KEY=change-me-in-production
YOUTUBE_API_KEY=your-youtube-api-key
TWITTER_BEARER_TOKEN=your-twitter-bearer-token
GITHUB_TOKEN=your-github-token
INGEST_SCHEDULE=0 6 * * *
```

- [ ] **Step 4: Create docker-compose.yml**

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: newsfeed
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
    volumes:
      - ./backend:/app/backend

  frontend:
    build:
      context: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/src:/app/src
    depends_on:
      - backend

volumes:
  pgdata:
```

- [ ] **Step 5: Create backend/Dockerfile**

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY backend/pyproject.toml .
RUN pip install --no-cache-dir .

COPY backend/ ./backend/

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml backend/__init__.py .env.example docker-compose.yml backend/Dockerfile
git commit -m "chore: project scaffolding with deps, Docker Compose, env template"
```

---

## Task 2: Configuration & Database Connection

**Files:**
- Create: `backend/config.py`
- Create: `backend/database.py`

- [ ] **Step 1: Create backend/config.py**

```python
# backend/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/newsfeed"
    llm_provider: str = "anthropic/claude-sonnet-4-20250514"
    llm_api_key: str = ""
    admin_api_key: str = "change-me-in-production"
    youtube_api_key: str = ""
    twitter_bearer_token: str = ""
    github_token: str = ""
    ingest_schedule: str = "0 6 * * *"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
```

- [ ] **Step 2: Create backend/database.py**

```python
# backend/database.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

- [ ] **Step 3: Commit**

```bash
git add backend/config.py backend/database.py
git commit -m "feat: add config (pydantic-settings) and async database connection"
```

---

## Task 3: Database Models

**Files:**
- Create: `backend/models.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write failing model tests**

```python
# tests/__init__.py
```

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.models import Base


@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
```

```python
# tests/test_models.py
import pytest
from sqlalchemy import select

from backend.models import Person, Source, ContentItem, Tag, DailyDigest, SourceType, ProcessingStatus


@pytest.mark.asyncio
async def test_create_person(db):
    person = Person(name="Boris Cherny")
    db.add(person)
    await db.commit()
    result = await db.execute(select(Person).where(Person.name == "Boris Cherny"))
    assert result.scalar_one().name == "Boris Cherny"


@pytest.mark.asyncio
async def test_create_source_linked_to_person(db):
    person = Person(name="Andrej Karpathy")
    db.add(person)
    await db.flush()
    source = Source(person_id=person.id, type=SourceType.youtube, url="https://youtube.com/@karpathy")
    db.add(source)
    await db.commit()
    result = await db.execute(select(Source).where(Source.person_id == person.id))
    src = result.scalar_one()
    assert src.type == SourceType.youtube
    assert src.active is True


@pytest.mark.asyncio
async def test_content_item_unique_url(db):
    person = Person(name="Test")
    db.add(person)
    await db.flush()
    source = Source(person_id=person.id, type=SourceType.blog, url="https://example.com/feed")
    db.add(source)
    await db.flush()
    item1 = ContentItem(
        source_id=source.id, person_id=person.id, title="Post 1",
        url="https://example.com/post-1", source_type=SourceType.blog,
        processing_status=ProcessingStatus.pending,
    )
    db.add(item1)
    await db.commit()
    item2 = ContentItem(
        source_id=source.id, person_id=person.id, title="Duplicate",
        url="https://example.com/post-1", source_type=SourceType.blog,
        processing_status=ProcessingStatus.pending,
    )
    db.add(item2)
    with pytest.raises(Exception):
        await db.commit()


@pytest.mark.asyncio
async def test_content_item_tags(db):
    person = Person(name="Test")
    db.add(person)
    await db.flush()
    source = Source(person_id=person.id, type=SourceType.blog, url="https://example.com/feed")
    db.add(source)
    await db.flush()
    tag = Tag(name="AI Coding Workflows", slug="ai-coding-workflows")
    db.add(tag)
    await db.flush()
    item = ContentItem(
        source_id=source.id, person_id=person.id, title="Post",
        url="https://example.com/post", source_type=SourceType.blog,
        processing_status=ProcessingStatus.pending,
    )
    item.tags.append(tag)
    db.add(item)
    await db.commit()
    result = await db.execute(select(ContentItem).where(ContentItem.url == "https://example.com/post"))
    loaded = result.scalar_one()
    await db.refresh(loaded, ["tags"])
    assert len(loaded.tags) == 1
    assert loaded.tags[0].slug == "ai-coding-workflows"


@pytest.mark.asyncio
async def test_daily_digest(db):
    digest = DailyDigest(
        date="2026-03-26",
        highlights="- Topic A trending\n- Topic B emerging",
        hot_topics=[{"tag": "ai-coding", "count": 5, "trend": "up"}],
    )
    db.add(digest)
    await db.commit()
    result = await db.execute(select(DailyDigest))
    d = result.scalar_one()
    assert d.hot_topics[0]["tag"] == "ai-coding"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && pip install -e ".[dev]" && cd .. && python -m pytest tests/test_models.py -v`
Expected: FAIL — `backend.models` does not exist yet.

- [ ] **Step 3: Implement models**

```python
# backend/models.py
import enum
from datetime import datetime, date

from sqlalchemy import String, Text, Boolean, Enum, ForeignKey, UniqueConstraint, Date, Index, Column, Table, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SourceType(str, enum.Enum):
    blog = "blog"
    youtube = "youtube"
    podcast = "podcast"
    twitter = "twitter"
    newsletter = "newsletter"
    github = "github"


class ProcessingStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


content_tags = Table(
    "content_tags",
    Base.metadata,
    Column("content_id", ForeignKey("content_items.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    bio: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    sources: Mapped[list["Source"]] = relationship(back_populates="person", cascade="all, delete-orphan")
    content_items: Mapped[list["ContentItem"]] = relationship(back_populates="person")


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"))
    type: Mapped[SourceType] = mapped_column(Enum(SourceType))
    url: Mapped[str] = mapped_column(String(500))
    last_fetched_at: Mapped[datetime | None] = mapped_column()
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    person: Mapped["Person"] = relationship(back_populates="sources")
    content_items: Mapped[list["ContentItem"]] = relationship(back_populates="source")


class ContentItem(Base):
    __tablename__ = "content_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"))
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(1000), unique=True)
    body: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType))
    published_at: Mapped[datetime | None] = mapped_column()
    processing_status: Mapped[ProcessingStatus] = mapped_column(Enum(ProcessingStatus), default=ProcessingStatus.pending)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    source: Mapped["Source"] = relationship(back_populates="content_items")
    person: Mapped["Person"] = relationship(back_populates="content_items")
    tags: Mapped[list["Tag"]] = relationship(secondary=content_tags, back_populates="content_items")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    content_items: Mapped[list["ContentItem"]] = relationship(secondary=content_tags, back_populates="tags")


class DailyDigest(Base):
    __tablename__ = "daily_digests"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, unique=True)
    highlights: Mapped[str] = mapped_column(Text)
    hot_topics: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_models.py -v`
Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/models.py tests/
git commit -m "feat: add SQLAlchemy models (Person, Source, ContentItem, Tag, DailyDigest)"
```

---

## Task 4: Alembic Setup & Initial Migration

**Files:**
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/script.py.mako`

- [ ] **Step 1: Initialize Alembic**

Run: `cd C:/Projects/newsfeed && alembic init alembic`

- [ ] **Step 2: Configure alembic.ini**

Edit `alembic.ini` — set the sqlalchemy.url line:

```ini
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/newsfeed
```

- [ ] **Step 3: Configure alembic/env.py for async + our models**

```python
# alembic/env.py
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from backend.config import settings
from backend.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    url = settings.database_url
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = create_async_engine(settings.database_url)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

- [ ] **Step 4: Generate initial migration**

Run: `alembic revision --autogenerate -m "initial schema"`
Expected: Creates a migration file in `alembic/versions/`.

- [ ] **Step 5: Commit**

```bash
git add alembic.ini alembic/
git commit -m "feat: add Alembic setup with initial schema migration"
```

---

## Task 5: Pydantic Schemas

**Files:**
- Create: `backend/schemas.py`

- [ ] **Step 1: Create schemas**

```python
# backend/schemas.py
from datetime import datetime, date
from pydantic import BaseModel

from backend.models import SourceType, ProcessingStatus


# --- Shared ---

class TagOut(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


# --- Person ---

class PersonCreate(BaseModel):
    name: str
    avatar_url: str | None = None
    bio: str | None = None


class PersonUpdate(BaseModel):
    name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None


class PersonOut(BaseModel):
    id: int
    name: str
    avatar_url: str | None
    bio: str | None
    source_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Source ---

class SourceCreate(BaseModel):
    type: SourceType
    url: str


class SourceOut(BaseModel):
    id: int
    person_id: int
    type: SourceType
    url: str
    active: bool
    last_fetched_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Content ---

class ContentItemOut(BaseModel):
    id: int
    person_id: int
    person_name: str = ""
    person_avatar_url: str | None = None
    title: str
    url: str
    summary: str | None
    source_type: SourceType
    published_at: datetime | None
    processing_status: ProcessingStatus
    tags: list[TagOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class ContentListOut(BaseModel):
    items: list[ContentItemOut]
    total: int
    page: int
    page_size: int


# --- Tag ---

class TagCreate(BaseModel):
    name: str


class TagWithCount(BaseModel):
    id: int
    name: str
    slug: str
    count: int = 0

    model_config = {"from_attributes": True}


# --- Digest ---

class DailyDigestOut(BaseModel):
    id: int
    date: date
    highlights: str
    hot_topics: list[dict]
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Admin ---

class IngestTriggerOut(BaseModel):
    status: str
    message: str
```

- [ ] **Step 2: Commit**

```bash
git add backend/schemas.py
git commit -m "feat: add Pydantic request/response schemas"
```

---

## Task 6: API Dependencies

**Files:**
- Create: `backend/api/__init__.py`
- Create: `backend/api/deps.py`

- [ ] **Step 1: Create API deps**

```python
# backend/api/__init__.py
```

```python
# backend/api/deps.py
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.database import async_session

api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def require_admin_key(key: str | None = Security(api_key_header)) -> str:
    if not key or key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid admin API key")
    return key
```

- [ ] **Step 2: Commit**

```bash
git add backend/api/
git commit -m "feat: add API dependencies (db session, admin auth)"
```

---

## Task 7: Admin API Endpoints

**Files:**
- Create: `backend/api/admin.py`
- Create: `tests/test_api_admin.py`

- [ ] **Step 1: Write failing admin API tests**

```python
# tests/test_api_admin.py
import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


ADMIN_HEADERS = {"X-Admin-Key": "change-me-in-production"}


@pytest.mark.asyncio
async def test_create_person(client):
    resp = await client.post("/api/admin/people", json={"name": "Boris Cherny"}, headers=ADMIN_HEADERS)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Boris Cherny"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_person_no_auth(client):
    resp = await client.post("/api/admin/people", json={"name": "Test"})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_update_person(client):
    resp = await client.post("/api/admin/people", json={"name": "Original"}, headers=ADMIN_HEADERS)
    pid = resp.json()["id"]
    resp = await client.put(f"/api/admin/people/{pid}", json={"name": "Updated"}, headers=ADMIN_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_person(client):
    resp = await client.post("/api/admin/people", json={"name": "ToDelete"}, headers=ADMIN_HEADERS)
    pid = resp.json()["id"]
    resp = await client.delete(f"/api/admin/people/{pid}", headers=ADMIN_HEADERS)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_add_source_to_person(client):
    resp = await client.post("/api/admin/people", json={"name": "Karpathy"}, headers=ADMIN_HEADERS)
    pid = resp.json()["id"]
    resp = await client.post(
        f"/api/admin/people/{pid}/sources",
        json={"type": "youtube", "url": "https://youtube.com/@karpathy"},
        headers=ADMIN_HEADERS,
    )
    assert resp.status_code == 201
    assert resp.json()["type"] == "youtube"


@pytest.mark.asyncio
async def test_delete_source(client):
    resp = await client.post("/api/admin/people", json={"name": "Test"}, headers=ADMIN_HEADERS)
    pid = resp.json()["id"]
    resp = await client.post(
        f"/api/admin/people/{pid}/sources",
        json={"type": "blog", "url": "https://example.com/feed"},
        headers=ADMIN_HEADERS,
    )
    sid = resp.json()["id"]
    resp = await client.delete(f"/api/admin/sources/{sid}", headers=ADMIN_HEADERS)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_create_tag(client):
    resp = await client.post("/api/admin/tags", json={"name": "AI Coding Workflows"}, headers=ADMIN_HEADERS)
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] == "ai-coding-workflows"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_api_admin.py -v`
Expected: FAIL — `backend.main` has no `app` yet.

- [ ] **Step 3: Create minimal FastAPI app**

```python
# backend/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine
from backend.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables in dev (migrations handle prod)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="AI Workflow Newsfeed", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.api.admin import router as admin_router
from backend.api.public import router as public_router

app.include_router(admin_router, prefix="/api/admin")
app.include_router(public_router, prefix="/api")
```

- [ ] **Step 4: Implement admin router**

```python
# backend/api/admin.py
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
    from backend.scheduler import run_ingestion_now
    await run_ingestion_now()
    return IngestTriggerOut(status="started", message="Ingestion triggered")
```

- [ ] **Step 5: Create stub public router (needed for app import)**

```python
# backend/api/public.py
from fastapi import APIRouter

router = APIRouter()
```

- [ ] **Step 6: Create stub scheduler (needed for admin import)**

```python
# backend/scheduler.py
async def run_ingestion_now():
    pass  # Implemented in Task 16
```

- [ ] **Step 7: Update conftest.py for API tests**

Replace `tests/conftest.py`:

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.models import Base
from backend.api.deps import get_db
from backend.main import app


@pytest.fixture(autouse=True)
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with session_factory() as session:
        yield session

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `python -m pytest tests/test_api_admin.py -v`
Expected: All 7 tests PASS.

- [ ] **Step 9: Commit**

```bash
git add backend/main.py backend/api/ backend/scheduler.py tests/
git commit -m "feat: add admin API (CRUD people, sources, tags) with tests"
```

---

## Task 8: Public API Endpoints

**Files:**
- Modify: `backend/api/public.py`
- Create: `tests/test_api_public.py`

- [ ] **Step 1: Write failing public API tests**

```python
# tests/test_api_public.py
import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app
from backend.models import Person, Source, ContentItem, Tag, DailyDigest, SourceType, ProcessingStatus


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def seed_data(db):
    person = Person(name="Boris Cherny", avatar_url="https://example.com/boris.jpg")
    db.add(person)
    await db.flush()
    source = Source(person_id=person.id, type=SourceType.blog, url="https://boris.com/feed")
    db.add(source)
    await db.flush()
    tag = Tag(name="AI Coding Workflows", slug="ai-coding-workflows")
    db.add(tag)
    await db.flush()
    item = ContentItem(
        source_id=source.id, person_id=person.id,
        title="My AI Workflow", url="https://boris.com/ai-workflow",
        summary="Boris shares his AI coding setup.",
        source_type=SourceType.blog, processing_status=ProcessingStatus.completed,
    )
    item.tags.append(tag)
    db.add(item)
    digest = DailyDigest(
        date="2026-03-26",
        highlights="- Boris shared his workflow\n- New tools released",
        hot_topics=[{"tag": "ai-coding-workflows", "count": 3, "trend": "up"}],
    )
    db.add(digest)
    await db.commit()
    return {"person": person, "source": source, "item": item, "tag": tag, "digest": digest}


@pytest.mark.asyncio
async def test_get_content_list(client, seed_data):
    resp = await client.get("/api/content")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "My AI Workflow"


@pytest.mark.asyncio
async def test_get_content_by_id(client, seed_data):
    item_id = seed_data["item"].id
    resp = await client.get(f"/api/content/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "My AI Workflow"


@pytest.mark.asyncio
async def test_get_people(client, seed_data):
    resp = await client.get("/api/people")
    assert resp.status_code == 200
    people = resp.json()
    assert len(people) == 1
    assert people[0]["name"] == "Boris Cherny"
    assert people[0]["source_count"] == 1


@pytest.mark.asyncio
async def test_get_person_content(client, seed_data):
    pid = seed_data["person"].id
    resp = await client.get(f"/api/people/{pid}/content")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_get_tags(client, seed_data):
    resp = await client.get("/api/tags")
    assert resp.status_code == 200
    tags = resp.json()
    assert len(tags) == 1
    assert tags[0]["slug"] == "ai-coding-workflows"
    assert tags[0]["count"] == 1


@pytest.mark.asyncio
async def test_get_tag_content(client, seed_data):
    resp = await client.get("/api/tags/ai-coding-workflows/content")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_get_digest_today(client, seed_data):
    resp = await client.get("/api/digest/today")
    assert resp.status_code == 200
    data = resp.json()
    assert "Boris" in data["highlights"]


@pytest.mark.asyncio
async def test_get_digest_history(client, seed_data):
    resp = await client.get("/api/digest/history")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_api_public.py -v`
Expected: FAIL — public endpoints not implemented.

- [ ] **Step 3: Implement public router**

```python
# backend/api/public.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_api_public.py -v`
Expected: All 8 tests PASS.

- [ ] **Step 5: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: All tests PASS (models + admin + public).

- [ ] **Step 6: Commit**

```bash
git add backend/api/public.py tests/test_api_public.py
git commit -m "feat: add public API (content, people, tags, digest endpoints) with tests"
```

---

## Task 9: Ingestion Base & Blog Fetcher

**Files:**
- Create: `backend/ingestion/__init__.py`
- Create: `backend/ingestion/base.py`
- Create: `backend/ingestion/blog.py`
- Create: `tests/test_ingestion_blog.py`

- [ ] **Step 1: Write failing blog fetcher test**

```python
# tests/test_ingestion_blog.py
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from backend.ingestion.base import RawContent
from backend.ingestion.blog import BlogFetcher
from backend.models import Source, SourceType


def make_source():
    s = Source.__new__(Source)
    s.id = 1
    s.person_id = 1
    s.type = SourceType.blog
    s.url = "https://example.com/feed.xml"
    s.last_fetched_at = None
    s.active = True
    return s


SAMPLE_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Blog</title>
    <item>
      <title>My AI Workflow</title>
      <link>https://example.com/ai-workflow</link>
      <description>A deep dive into my AI workflow.</description>
      <pubDate>Wed, 25 Mar 2026 12:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""


@pytest.mark.asyncio
async def test_blog_fetcher_parses_rss():
    fetcher = BlogFetcher()
    source = make_source()
    with patch("backend.ingestion.blog.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = AsyncMock()
        mock_resp.text = SAMPLE_FEED
        mock_resp.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_client

        results = await fetcher.fetch(source)

    assert len(results) == 1
    assert results[0].title == "My AI Workflow"
    assert results[0].url == "https://example.com/ai-workflow"
    assert isinstance(results[0], RawContent)


@pytest.mark.asyncio
async def test_blog_fetcher_filters_by_last_fetched():
    fetcher = BlogFetcher()
    source = make_source()
    source.last_fetched_at = datetime(2026, 3, 26)  # After the item's pubDate
    with patch("backend.ingestion.blog.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = AsyncMock()
        mock_resp.text = SAMPLE_FEED
        mock_resp.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_client

        results = await fetcher.fetch(source)

    assert len(results) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_ingestion_blog.py -v`
Expected: FAIL — modules don't exist.

- [ ] **Step 3: Implement base and blog fetcher**

```python
# backend/ingestion/__init__.py
```

```python
# backend/ingestion/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from backend.models import Source, SourceType


@dataclass
class RawContent:
    title: str
    url: str
    body: str | None
    published_at: datetime | None
    source_type: SourceType


class BaseFetcher(ABC):
    @abstractmethod
    async def fetch(self, source: Source) -> list[RawContent]:
        """Fetch new content since source.last_fetched_at."""
        ...
```

```python
# backend/ingestion/blog.py
import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from backend.ingestion.base import BaseFetcher, RawContent
from backend.models import Source, SourceType

logger = logging.getLogger(__name__)


class BlogFetcher(BaseFetcher):
    async def fetch(self, source: Source) -> list[RawContent]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(source.url, timeout=30, follow_redirects=True)
            feed = feedparser.parse(resp.text)
        except Exception:
            logger.exception("Failed to fetch blog feed: %s", source.url)
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

            body = entry.get("summary", "") or entry.get("content", [{}])[0].get("value", "") if hasattr(entry, "content") else entry.get("summary", "")

            results.append(RawContent(
                title=entry.get("title", "Untitled"),
                url=entry.get("link", ""),
                body=body,
                published_at=published,
                source_type=SourceType.blog,
            ))

        return results
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_ingestion_blog.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/ingestion/ tests/test_ingestion_blog.py
git commit -m "feat: add ingestion base interface and blog/RSS fetcher with tests"
```

---

## Task 10: YouTube Fetcher

**Files:**
- Create: `backend/ingestion/youtube.py`
- Create: `tests/test_ingestion_youtube.py`

- [ ] **Step 1: Write failing YouTube fetcher test**

```python
# tests/test_ingestion_youtube.py
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from backend.ingestion.base import RawContent
from backend.ingestion.youtube import YouTubeFetcher
from backend.models import Source, SourceType


def make_source():
    s = Source.__new__(Source)
    s.id = 1
    s.person_id = 1
    s.type = SourceType.youtube
    s.url = "UC_x5XG1OV2P6uZZ5FSM9Ttw"  # channel ID
    s.last_fetched_at = None
    s.active = True
    return s


MOCK_SEARCH_RESPONSE = {
    "items": [
        {
            "id": {"videoId": "abc123"},
            "snippet": {
                "title": "AI Coding Tips",
                "publishedAt": "2026-03-25T10:00:00Z",
                "description": "Tips for AI coding workflows.",
            },
        }
    ]
}


@pytest.mark.asyncio
async def test_youtube_fetcher():
    fetcher = YouTubeFetcher()
    source = make_source()

    mock_service = MagicMock()
    mock_search = MagicMock()
    mock_list = MagicMock()
    mock_list.execute.return_value = MOCK_SEARCH_RESPONSE
    mock_search.list.return_value = mock_list
    mock_service.search.return_value = mock_search

    with patch("backend.ingestion.youtube.build", return_value=mock_service):
        with patch("backend.ingestion.youtube.YouTubeTranscriptApi") as mock_yt_api:
            mock_yt_api.get_transcript.return_value = [
                {"text": "Hello everyone."},
                {"text": "Today we talk about AI."},
            ]
            results = await fetcher.fetch(source)

    assert len(results) == 1
    assert results[0].title == "AI Coding Tips"
    assert results[0].url == "https://www.youtube.com/watch?v=abc123"
    assert "Hello everyone" in results[0].body
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_ingestion_youtube.py -v`
Expected: FAIL — module doesn't exist.

- [ ] **Step 3: Implement YouTube fetcher**

```python
# backend/ingestion/youtube.py
import logging
from datetime import datetime, timezone

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

from backend.config import settings
from backend.ingestion.base import BaseFetcher, RawContent
from backend.models import Source, SourceType

logger = logging.getLogger(__name__)


class YouTubeFetcher(BaseFetcher):
    async def fetch(self, source: Source) -> list[RawContent]:
        try:
            service = build("youtube", "v3", developerKey=settings.youtube_api_key)
            request = service.search().list(
                channelId=source.url,
                part="snippet",
                order="date",
                maxResults=10,
                type="video",
            )
            response = request.execute()
        except Exception:
            logger.exception("Failed to fetch YouTube channel: %s", source.url)
            return []

        results: list[RawContent] = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            published = datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00"))

            if source.last_fetched_at:
                cutoff = source.last_fetched_at
                if cutoff.tzinfo is None:
                    cutoff = cutoff.replace(tzinfo=timezone.utc)
                if published <= cutoff:
                    continue

            transcript_text = ""
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = " ".join(entry["text"] for entry in transcript)
            except Exception:
                logger.debug("No transcript for video %s", video_id)

            body = transcript_text or snippet.get("description", "")

            results.append(RawContent(
                title=snippet["title"],
                url=f"https://www.youtube.com/watch?v={video_id}",
                body=body,
                published_at=published,
                source_type=SourceType.youtube,
            ))

        return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_ingestion_youtube.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/ingestion/youtube.py tests/test_ingestion_youtube.py
git commit -m "feat: add YouTube fetcher with transcript support and tests"
```

---

## Task 11: Podcast Fetcher

**Files:**
- Create: `backend/ingestion/podcast.py`
- Create: `tests/test_ingestion_podcast.py`

- [ ] **Step 1: Write failing podcast fetcher test**

```python
# tests/test_ingestion_podcast.py
import pytest
from unittest.mock import AsyncMock, patch

from backend.ingestion.base import RawContent
from backend.ingestion.podcast import PodcastFetcher
from backend.models import Source, SourceType


def make_source():
    s = Source.__new__(Source)
    s.id = 1
    s.person_id = 1
    s.type = SourceType.podcast
    s.url = "https://example.com/podcast.xml"
    s.last_fetched_at = None
    s.active = True
    return s


SAMPLE_PODCAST_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.apple.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>AI Podcast</title>
    <item>
      <title>Episode 42: AI Workflows</title>
      <link>https://example.com/ep42</link>
      <description>We discuss AI workflows with a special guest.</description>
      <enclosure url="https://example.com/ep42.mp3" type="audio/mpeg"/>
      <pubDate>Tue, 24 Mar 2026 08:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""


@pytest.mark.asyncio
async def test_podcast_fetcher():
    fetcher = PodcastFetcher()
    source = make_source()
    with patch("backend.ingestion.podcast.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = AsyncMock()
        mock_resp.text = SAMPLE_PODCAST_FEED
        mock_resp.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_cls.return_value = mock_client

        results = await fetcher.fetch(source)

    assert len(results) == 1
    assert results[0].title == "Episode 42: AI Workflows"
    assert results[0].source_type == SourceType.podcast
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_ingestion_podcast.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement podcast fetcher**

```python
# backend/ingestion/podcast.py
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

            results.append(RawContent(
                title=entry.get("title", "Untitled Episode"),
                url=entry.get("link", ""),
                body=entry.get("summary", ""),
                published_at=published,
                source_type=SourceType.podcast,
            ))

        return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_ingestion_podcast.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/ingestion/podcast.py tests/test_ingestion_podcast.py
git commit -m "feat: add podcast RSS fetcher with tests"
```

---

## Task 12: Twitter Fetcher

**Files:**
- Create: `backend/ingestion/twitter.py`
- Create: `tests/test_ingestion_twitter.py`

- [ ] **Step 1: Write failing Twitter fetcher test**

```python
# tests/test_ingestion_twitter.py
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from backend.ingestion.twitter import TwitterFetcher
from backend.models import Source, SourceType


def make_source():
    s = Source.__new__(Source)
    s.id = 1
    s.person_id = 1
    s.type = SourceType.twitter
    s.url = "kaboris"  # Twitter handle
    s.last_fetched_at = None
    s.active = True
    return s


@pytest.mark.asyncio
async def test_twitter_fetcher():
    fetcher = TwitterFetcher()
    source = make_source()

    mock_user = MagicMock()
    mock_user.id = 12345

    mock_tweet = MagicMock()
    mock_tweet.id = 99999
    mock_tweet.text = "Just shipped my new AI coding workflow. Thread below."
    mock_tweet.created_at = datetime(2026, 3, 25, 10, 0, 0, tzinfo=timezone.utc)

    mock_response = MagicMock()
    mock_response.data = [mock_tweet]

    with patch("backend.ingestion.twitter.tweepy.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.get_user.return_value = MagicMock(data=mock_user)
        mock_client.get_users_tweets.return_value = mock_response
        mock_client_cls.return_value = mock_client

        results = await fetcher.fetch(source)

    assert len(results) == 1
    assert "AI coding workflow" in results[0].title
    assert results[0].source_type == SourceType.twitter
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_ingestion_twitter.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement Twitter fetcher**

```python
# backend/ingestion/twitter.py
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
            tweets_resp = client.get_users_tweets(
                user_id, max_results=10, tweet_fields=["created_at"],
            )
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

            results.append(RawContent(
                title=truncated,
                url=f"https://twitter.com/{source.url}/status/{tweet.id}",
                body=tweet.text,
                published_at=published,
                source_type=SourceType.twitter,
            ))

        return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_ingestion_twitter.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/ingestion/twitter.py tests/test_ingestion_twitter.py
git commit -m "feat: add Twitter/X fetcher with tests"
```

---

## Task 13: Newsletter Fetcher

**Files:**
- Create: `backend/ingestion/newsletter.py`
- Create: `tests/test_ingestion_newsletter.py`

- [ ] **Step 1: Write failing newsletter fetcher test**

```python
# tests/test_ingestion_newsletter.py
import pytest
from unittest.mock import AsyncMock, patch

from backend.ingestion.newsletter import NewsletterFetcher
from backend.models import Source, SourceType


def make_source():
    s = Source.__new__(Source)
    s.id = 1
    s.person_id = 1
    s.type = SourceType.newsletter
    s.url = "https://example.substack.com/feed"
    s.last_fetched_at = None
    s.active = True
    return s


SAMPLE_SUBSTACK_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>AI Weekly</title>
    <item>
      <title>Issue 10: The Rise of AI Agents</title>
      <link>https://example.substack.com/p/issue-10</link>
      <description>This week we cover the rise of autonomous AI agents.</description>
      <pubDate>Mon, 23 Mar 2026 09:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""


@pytest.mark.asyncio
async def test_newsletter_fetcher():
    fetcher = NewsletterFetcher()
    source = make_source()
    with patch("backend.ingestion.newsletter.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = AsyncMock()
        mock_resp.text = SAMPLE_SUBSTACK_FEED
        mock_resp.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_cls.return_value = mock_client

        results = await fetcher.fetch(source)

    assert len(results) == 1
    assert results[0].title == "Issue 10: The Rise of AI Agents"
    assert results[0].source_type == SourceType.newsletter
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_ingestion_newsletter.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement newsletter fetcher**

```python
# backend/ingestion/newsletter.py
import logging
from datetime import timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from backend.ingestion.base import BaseFetcher, RawContent
from backend.models import Source, SourceType

logger = logging.getLogger(__name__)


class NewsletterFetcher(BaseFetcher):
    async def fetch(self, source: Source) -> list[RawContent]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(source.url, timeout=30, follow_redirects=True)
            feed = feedparser.parse(resp.text)
        except Exception:
            logger.exception("Failed to fetch newsletter feed: %s", source.url)
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

            results.append(RawContent(
                title=entry.get("title", "Untitled"),
                url=entry.get("link", ""),
                body=entry.get("summary", ""),
                published_at=published,
                source_type=SourceType.newsletter,
            ))

        return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_ingestion_newsletter.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/ingestion/newsletter.py tests/test_ingestion_newsletter.py
git commit -m "feat: add newsletter/Substack fetcher with tests"
```

---

## Task 14: GitHub Fetcher

**Files:**
- Create: `backend/ingestion/github_fetcher.py`
- Create: `tests/test_ingestion_github.py`

- [ ] **Step 1: Write failing GitHub fetcher test**

```python
# tests/test_ingestion_github.py
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone

from backend.ingestion.github_fetcher import GitHubFetcher
from backend.models import Source, SourceType


def make_source():
    s = Source.__new__(Source)
    s.id = 1
    s.person_id = 1
    s.type = SourceType.github
    s.url = "karpathy"  # GitHub username
    s.last_fetched_at = None
    s.active = True
    return s


MOCK_EVENTS = [
    {
        "type": "CreateEvent",
        "repo": {"name": "karpathy/nanoGPT"},
        "payload": {"ref_type": "repository", "description": "Simplest GPT training"},
        "created_at": "2026-03-25T10:00:00Z",
    },
    {
        "type": "PushEvent",
        "repo": {"name": "karpathy/minbpe"},
        "payload": {"commits": [{"message": "Add tokenizer benchmarks"}]},
        "created_at": "2026-03-24T08:00:00Z",
    },
]


@pytest.mark.asyncio
async def test_github_fetcher():
    fetcher = GitHubFetcher()
    source = make_source()

    with patch("backend.ingestion.github_fetcher.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(return_value=MOCK_EVENTS)
        mock_resp.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_cls.return_value = mock_client

        results = await fetcher.fetch(source)

    assert len(results) == 2
    assert "nanoGPT" in results[0].title
    assert results[0].source_type == SourceType.github
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_ingestion_github.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement GitHub fetcher**

```python
# backend/ingestion/github_fetcher.py
import logging
from datetime import datetime, timezone

import httpx

from backend.config import settings
from backend.ingestion.base import BaseFetcher, RawContent
from backend.models import Source, SourceType

logger = logging.getLogger(__name__)

EVENT_TYPES_OF_INTEREST = {"CreateEvent", "PushEvent", "ReleaseEvent", "PublicEvent"}


class GitHubFetcher(BaseFetcher):
    async def fetch(self, source: Source) -> list[RawContent]:
        username = source.url
        headers = {"Accept": "application/vnd.github.v3+json"}
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"https://api.github.com/users/{username}/events/public",
                    headers=headers, timeout=30,
                )
                events = await resp.json()
        except Exception:
            logger.exception("Failed to fetch GitHub events for: %s", username)
            return []

        results: list[RawContent] = []
        for event in events:
            if event["type"] not in EVENT_TYPES_OF_INTEREST:
                continue

            created_at = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))

            if source.last_fetched_at:
                cutoff = source.last_fetched_at
                if cutoff.tzinfo is None:
                    cutoff = cutoff.replace(tzinfo=timezone.utc)
                if created_at <= cutoff:
                    continue

            repo_name = event["repo"]["name"]
            event_type = event["type"]
            title = f"[{event_type}] {repo_name}"
            body = _describe_event(event)

            results.append(RawContent(
                title=title,
                url=f"https://github.com/{repo_name}",
                body=body,
                published_at=created_at,
                source_type=SourceType.github,
            ))

        return results


def _describe_event(event: dict) -> str:
    event_type = event["type"]
    payload = event.get("payload", {})
    repo = event["repo"]["name"]

    if event_type == "CreateEvent":
        ref_type = payload.get("ref_type", "")
        desc = payload.get("description", "") or ""
        return f"Created {ref_type} {repo}. {desc}".strip()
    elif event_type == "PushEvent":
        commits = payload.get("commits", [])
        messages = [c.get("message", "") for c in commits[:5]]
        return f"Pushed to {repo}: " + "; ".join(messages)
    elif event_type == "ReleaseEvent":
        release = payload.get("release", {})
        tag = release.get("tag_name", "")
        name = release.get("name", "")
        return f"Released {tag} ({name}) in {repo}"
    else:
        return f"{event_type} on {repo}"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_ingestion_github.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/ingestion/github_fetcher.py tests/test_ingestion_github.py
git commit -m "feat: add GitHub events fetcher with tests"
```

---

## Task 15: Ingestion Orchestrator

**Files:**
- Create: `backend/ingestion/orchestrator.py`
- Create: `tests/test_orchestrator.py`

- [ ] **Step 1: Write failing orchestrator test**

```python
# tests/test_orchestrator.py
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone

from backend.ingestion.base import RawContent
from backend.ingestion.orchestrator import run_ingestion
from backend.models import Person, Source, ContentItem, SourceType


@pytest.mark.asyncio
async def test_orchestrator_stores_content(db):
    person = Person(name="Test Person")
    db.add(person)
    await db.flush()
    source = Source(person_id=person.id, type=SourceType.blog, url="https://example.com/feed")
    db.add(source)
    await db.commit()

    mock_content = [
        RawContent(
            title="Test Post", url="https://example.com/test-post",
            body="Content body here.", published_at=datetime(2026, 3, 25, tzinfo=timezone.utc),
            source_type=SourceType.blog,
        )
    ]

    with patch("backend.ingestion.orchestrator.FETCHER_MAP") as mock_map:
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch.return_value = mock_content
        mock_map.get.return_value = mock_fetcher
        mock_map.__contains__ = lambda self, key: True
        mock_map.__getitem__ = lambda self, key: mock_fetcher

        await run_ingestion(db)

    from sqlalchemy import select
    result = await db.execute(select(ContentItem))
    items = result.scalars().all()
    assert len(items) == 1
    assert items[0].title == "Test Post"
    assert items[0].url == "https://example.com/test-post"


@pytest.mark.asyncio
async def test_orchestrator_deduplicates(db):
    person = Person(name="Test Person")
    db.add(person)
    await db.flush()
    source = Source(person_id=person.id, type=SourceType.blog, url="https://example.com/feed")
    db.add(source)
    await db.flush()
    existing = ContentItem(
        source_id=source.id, person_id=person.id, title="Existing",
        url="https://example.com/test-post", source_type=SourceType.blog,
    )
    db.add(existing)
    await db.commit()

    mock_content = [
        RawContent(
            title="Test Post", url="https://example.com/test-post",
            body="Duplicate", published_at=None, source_type=SourceType.blog,
        )
    ]

    with patch("backend.ingestion.orchestrator.FETCHER_MAP") as mock_map:
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch.return_value = mock_content
        mock_map.get.return_value = mock_fetcher
        mock_map.__contains__ = lambda self, key: True
        mock_map.__getitem__ = lambda self, key: mock_fetcher

        await run_ingestion(db)

    from sqlalchemy import select, func
    count = (await db.execute(select(func.count(ContentItem.id)))).scalar()
    assert count == 1  # No duplicate added
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_orchestrator.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement orchestrator**

```python
# backend/ingestion/orchestrator.py
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
            existing = await db.execute(
                select(ContentItem).where(ContentItem.url == raw.url)
            )
            if existing.scalar_one_or_none():
                continue

            item = ContentItem(
                source_id=source.id,
                person_id=source.person_id,
                title=raw.title,
                url=raw.url,
                body=raw.body,
                source_type=raw.source_type,
                published_at=raw.published_at,
                processing_status=ProcessingStatus.pending,
            )
            db.add(item)
            total_new += 1

        source.last_fetched_at = datetime.now(timezone.utc)

    await db.commit()
    logger.info("Ingestion complete: %d new items", total_new)
    return total_new
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_orchestrator.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/ingestion/orchestrator.py tests/test_orchestrator.py
git commit -m "feat: add ingestion orchestrator with dedup and tests"
```

---

## Task 16: AI — LLM Wrapper & Summarizer

**Files:**
- Create: `backend/ai/__init__.py`
- Create: `backend/ai/llm.py`
- Create: `backend/ai/summarizer.py`
- Create: `tests/test_ai_summarizer.py`

- [ ] **Step 1: Write failing summarizer test**

```python
# tests/test_ai_summarizer.py
import pytest
from unittest.mock import patch, MagicMock

from backend.ai.summarizer import summarize_content
from backend.models import ContentItem, SourceType, ProcessingStatus


def make_item(source_type=SourceType.blog, body="A long article about AI workflows..."):
    item = ContentItem.__new__(ContentItem)
    item.id = 1
    item.title = "My AI Workflow"
    item.body = body
    item.source_type = source_type
    item.processing_status = ProcessingStatus.pending
    item.summary = None
    return item


@pytest.mark.asyncio
async def test_summarize_long_content():
    item = make_item()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Boris describes his AI coding setup using Claude and Cursor."))]

    with patch("backend.ai.llm.litellm.acompletion", return_value=mock_response) as mock_llm:
        result = await summarize_content(item)

    assert result == "Boris describes his AI coding setup using Claude and Cursor."
    mock_llm.assert_called_once()


@pytest.mark.asyncio
async def test_skip_summarize_short_content():
    item = make_item(source_type=SourceType.twitter, body="Just shipped v2!")
    result = await summarize_content(item)
    assert result == "Just shipped v2!"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_ai_summarizer.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement LLM wrapper and summarizer**

```python
# backend/ai/__init__.py
```

```python
# backend/ai/llm.py
import litellm

from backend.config import settings


async def complete(prompt: str, system: str = "") -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = await litellm.acompletion(
        model=settings.llm_provider,
        messages=messages,
        api_key=settings.llm_api_key,
    )
    return response.choices[0].message.content
```

```python
# backend/ai/summarizer.py
from backend.ai.llm import complete
from backend.models import ContentItem, SourceType

SHORT_FORM_TYPES = {SourceType.twitter, SourceType.github}
SHORT_BODY_THRESHOLD = 200


async def summarize_content(item: ContentItem) -> str:
    body = item.body or ""

    if item.source_type in SHORT_FORM_TYPES or len(body) < SHORT_BODY_THRESHOLD:
        return body

    prompt = (
        f"Summarize the following content in 2-3 concise sentences. "
        f"Focus on the key takeaways.\n\n"
        f"Title: {item.title}\n\n"
        f"Content:\n{body[:8000]}"
    )

    return await complete(
        prompt=prompt,
        system="You are a concise technical summarizer for software engineering content.",
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_ai_summarizer.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/ai/ tests/test_ai_summarizer.py
git commit -m "feat: add LLM wrapper (LiteLLM) and content summarizer with tests"
```

---

## Task 17: AI — Tagger

**Files:**
- Create: `backend/ai/tagger.py`
- Create: `tests/test_ai_tagger.py`

- [ ] **Step 1: Write failing tagger test**

```python
# tests/test_ai_tagger.py
import pytest
from unittest.mock import patch, MagicMock

from backend.ai.tagger import tag_content
from backend.models import ContentItem, Tag, SourceType, ProcessingStatus


def make_item():
    item = ContentItem.__new__(ContentItem)
    item.id = 1
    item.title = "Building AI Agents with LangChain"
    item.body = "A guide to building autonomous AI agents using LangChain framework."
    item.summary = "Guide to building AI agents with LangChain."
    item.source_type = SourceType.blog
    item.processing_status = ProcessingStatus.pending
    return item


@pytest.mark.asyncio
async def test_tag_content(db):
    tag1 = Tag(name="Agent Frameworks", slug="agent-frameworks")
    tag2 = Tag(name="AI Coding Workflows", slug="ai-coding-workflows")
    tag3 = Tag(name="LLM Tools", slug="llm-tools")
    db.add_all([tag1, tag2, tag3])
    await db.commit()

    item = make_item()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="agent-frameworks, llm-tools"))]

    with patch("backend.ai.llm.litellm.acompletion", return_value=mock_response):
        tags = await tag_content(item, db)

    slugs = [t.slug for t in tags]
    assert "agent-frameworks" in slugs
    assert "llm-tools" in slugs
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_ai_tagger.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement tagger**

```python
# backend/ai/tagger.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_ai_tagger.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/ai/tagger.py tests/test_ai_tagger.py
git commit -m "feat: add AI content tagger with tests"
```

---

## Task 18: AI — Trending & Daily Digest

**Files:**
- Create: `backend/ai/trending.py`
- Create: `tests/test_ai_trending.py`

- [ ] **Step 1: Write failing trending test**

```python
# tests/test_ai_trending.py
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime, timezone

from backend.ai.trending import generate_daily_digest
from backend.models import Person, Source, ContentItem, Tag, DailyDigest, SourceType, ProcessingStatus, content_tags


@pytest.mark.asyncio
async def test_generate_daily_digest(db):
    person = Person(name="Test")
    db.add(person)
    await db.flush()
    source = Source(person_id=person.id, type=SourceType.blog, url="https://example.com/feed")
    db.add(source)
    await db.flush()
    tag = Tag(name="AI Coding Workflows", slug="ai-coding-workflows")
    db.add(tag)
    await db.flush()

    item1 = ContentItem(
        source_id=source.id, person_id=person.id, title="Post 1",
        url="https://example.com/1", summary="Summary 1",
        source_type=SourceType.blog, processing_status=ProcessingStatus.completed,
        created_at=datetime.now(timezone.utc),
    )
    item1.tags.append(tag)
    item2 = ContentItem(
        source_id=source.id, person_id=person.id, title="Post 2",
        url="https://example.com/2", summary="Summary 2",
        source_type=SourceType.blog, processing_status=ProcessingStatus.completed,
        created_at=datetime.now(timezone.utc),
    )
    item2.tags.append(tag)
    db.add_all([item1, item2])
    await db.commit()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(
        content="- AI coding workflows dominated today\n- Two posts about AI-assisted development"
    ))]

    with patch("backend.ai.llm.litellm.acompletion", return_value=mock_response):
        digest = await generate_daily_digest(db, target_date=date.today())

    assert digest is not None
    assert "AI coding" in digest.highlights
    assert len(digest.hot_topics) >= 1
    assert digest.hot_topics[0]["tag"] == "ai-coding-workflows"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_ai_trending.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement trending/digest**

```python
# backend/ai/trending.py
import logging
from collections import Counter
from datetime import date, datetime, timezone, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.ai.llm import complete
from backend.models import ContentItem, Tag, DailyDigest, ProcessingStatus, content_tags

logger = logging.getLogger(__name__)


async def generate_daily_digest(db: AsyncSession, target_date: date | None = None) -> DailyDigest | None:
    target_date = target_date or date.today()

    start = datetime(target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc)
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

    # Count tags
    tag_counter: Counter[str] = Counter()
    for item in items:
        for tag in item.tags:
            tag_counter[tag.slug] += 1

    hot_topics = [
        {"tag": slug, "count": count, "trend": "up"}
        for slug, count in tag_counter.most_common(10)
    ]

    # Generate highlights via LLM
    summaries = "\n".join(
        f"- {item.title}: {item.summary or '(no summary)'}" for item in items[:20]
    )

    highlights = await complete(
        prompt=(
            f"Based on today's content from AI/software engineering thought leaders, "
            f"write 3-5 bullet points highlighting the most notable themes and insights.\n\n"
            f"Today's content:\n{summaries}"
        ),
        system="You write concise daily digest highlights for a tech newsfeed.",
    )

    # Upsert digest
    existing = await db.execute(
        select(DailyDigest).where(DailyDigest.date == target_date)
    )
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_ai_trending.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/ai/trending.py tests/test_ai_trending.py
git commit -m "feat: add daily digest and trending topic generation with tests"
```

---

## Task 19: AI Processing Pipeline Integration

**Files:**
- Create: `backend/ai/pipeline.py`

- [ ] **Step 1: Implement the full AI pipeline that runs after ingestion**

```python
# backend/ai/pipeline.py
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/ai/pipeline.py
git commit -m "feat: add AI processing pipeline (summarize → tag → digest)"
```

---

## Task 20: Scheduler

**Files:**
- Modify: `backend/scheduler.py`

- [ ] **Step 1: Implement scheduler with APScheduler**

```python
# backend/scheduler.py
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
        trigger = CronTrigger(
            minute=parts[0], hour=parts[1], day=parts[2],
            month=parts[3], day_of_week=parts[4],
        )
    else:
        trigger = CronTrigger(hour=6, minute=0)

    scheduler.add_job(daily_ingestion_job, trigger, id="daily_ingest", replace_existing=True)
    scheduler.start()
    logger.info("Scheduler started with schedule: %s", settings.ingest_schedule)


def stop_scheduler():
    scheduler.shutdown(wait=False)
```

- [ ] **Step 2: Wire scheduler into FastAPI lifespan**

Update `backend/main.py` — replace the lifespan function:

```python
# backend/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine
from backend.models import Base
from backend.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="AI Workflow Newsfeed", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.api.admin import router as admin_router
from backend.api.public import router as public_router

app.include_router(admin_router, prefix="/api/admin")
app.include_router(public_router, prefix="/api")
```

- [ ] **Step 3: Run all backend tests**

Run: `python -m pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 4: Commit**

```bash
git add backend/scheduler.py backend/main.py
git commit -m "feat: add APScheduler with daily ingestion job and manual trigger"
```

---

## Task 21: Frontend Scaffolding

**Files:**
- Create: `frontend/` (via Vite scaffold)
- Modify: `frontend/package.json` (add deps)
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/postcss.config.js`

- [ ] **Step 1: Scaffold Vite React TypeScript project**

Run:
```bash
cd C:/Projects/newsfeed
npm create vite@latest frontend -- --template react-ts
```

- [ ] **Step 2: Install dependencies**

Run:
```bash
cd C:/Projects/newsfeed/frontend
npm install
npm install @tanstack/react-query react-router-dom
npm install -D tailwindcss @tailwindcss/vite
```

- [ ] **Step 3: Configure Tailwind**

Replace `frontend/src/index.css`:

```css
@import "tailwindcss";
```

Add Tailwind plugin to `frontend/vite.config.ts`:

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

- [ ] **Step 4: Clean up default files**

Delete `frontend/src/App.css` and `frontend/src/assets/`. Replace `frontend/src/App.tsx` with a minimal shell:

```tsx
// frontend/src/App.tsx
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import FeedPage from './pages/FeedPage'
import PersonPage from './pages/PersonPage'
import TrendingPage from './pages/TrendingPage'
import AdminPage from './pages/AdminPage'
import Layout from './components/Layout'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<FeedPage />} />
            <Route path="/people/:id" element={<PersonPage />} />
            <Route path="/trending" element={<TrendingPage />} />
            <Route path="/admin" element={<AdminPage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
```

- [ ] **Step 5: Create Layout component**

```tsx
// frontend/src/components/Layout.tsx
import { Link, useLocation } from 'react-router-dom'
import { ReactNode } from 'react'

const NAV_ITEMS = [
  { path: '/', label: 'Feed' },
  { path: '/trending', label: 'Trending' },
  { path: '/admin', label: 'Admin' },
]

export default function Layout({ children }: { children: ReactNode }) {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-8">
          <Link to="/" className="text-xl font-bold text-gray-900">
            AI Newsfeed
          </Link>
          <div className="flex gap-4">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`text-sm font-medium ${
                  location.pathname === item.path
                    ? 'text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </nav>
      <main className="max-w-6xl mx-auto px-4 py-6">{children}</main>
    </div>
  )
}
```

- [ ] **Step 6: Create stub pages**

```tsx
// frontend/src/pages/FeedPage.tsx
export default function FeedPage() {
  return <div>Feed Page — coming soon</div>
}
```

```tsx
// frontend/src/pages/PersonPage.tsx
export default function PersonPage() {
  return <div>Person Page — coming soon</div>
}
```

```tsx
// frontend/src/pages/TrendingPage.tsx
export default function TrendingPage() {
  return <div>Trending Page — coming soon</div>
}
```

```tsx
// frontend/src/pages/AdminPage.tsx
export default function AdminPage() {
  return <div>Admin Page — coming soon</div>
}
```

- [ ] **Step 7: Verify frontend builds**

Run: `cd C:/Projects/newsfeed/frontend && npm run build`
Expected: Build succeeds with no errors.

- [ ] **Step 8: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold React frontend with routing, Tailwind, TanStack Query"
```

---

## Task 22: Frontend API Client & Types

**Files:**
- Create: `frontend/src/types/index.ts`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/hooks/useApi.ts`

- [ ] **Step 1: Define TypeScript types**

```typescript
// frontend/src/types/index.ts
export type SourceType = 'blog' | 'youtube' | 'podcast' | 'twitter' | 'newsletter' | 'github'
export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface Tag {
  id: number
  name: string
  slug: string
}

export interface TagWithCount extends Tag {
  count: number
}

export interface Person {
  id: number
  name: string
  avatar_url: string | null
  bio: string | null
  source_count: number
  created_at: string
}

export interface Source {
  id: number
  person_id: number
  type: SourceType
  url: string
  active: boolean
  last_fetched_at: string | null
  created_at: string
}

export interface ContentItem {
  id: number
  person_id: number
  person_name: string
  person_avatar_url: string | null
  title: string
  url: string
  summary: string | null
  source_type: SourceType
  published_at: string | null
  processing_status: ProcessingStatus
  tags: Tag[]
  created_at: string
}

export interface ContentList {
  items: ContentItem[]
  total: number
  page: number
  page_size: number
}

export interface DailyDigest {
  id: number
  date: string
  highlights: string
  hot_topics: { tag: string; count: number; trend: string }[]
  created_at: string
}
```

- [ ] **Step 2: Create API client**

```typescript
// frontend/src/api/client.ts
const BASE_URL = '/api'

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!resp.ok) {
    throw new Error(`API error: ${resp.status} ${resp.statusText}`)
  }
  if (resp.status === 204) return undefined as T
  return resp.json()
}

export const api = {
  // Public
  getContent: (params?: Record<string, string>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : ''
    return fetchJson<import('../types').ContentList>(`/content${qs}`)
  },
  getContentById: (id: number) =>
    fetchJson<import('../types').ContentItem>(`/content/${id}`),
  getPeople: () =>
    fetchJson<import('../types').Person[]>('/people'),
  getPersonContent: (id: number, params?: Record<string, string>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : ''
    return fetchJson<import('../types').ContentList>(`/people/${id}/content${qs}`)
  },
  getTags: () =>
    fetchJson<import('../types').TagWithCount[]>('/tags'),
  getTagContent: (slug: string, params?: Record<string, string>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : ''
    return fetchJson<import('../types').ContentList>(`/tags/${slug}/content${qs}`)
  },
  getDigestToday: () =>
    fetchJson<import('../types').DailyDigest>('/digest/today'),
  getDigestHistory: () =>
    fetchJson<import('../types').DailyDigest[]>('/digest/history'),

  // Admin
  admin: {
    createPerson: (data: { name: string; avatar_url?: string; bio?: string }, key: string) =>
      fetchJson<import('../types').Person>('/admin/people', {
        method: 'POST', body: JSON.stringify(data),
        headers: { 'X-Admin-Key': key },
      }),
    updatePerson: (id: number, data: Record<string, string>, key: string) =>
      fetchJson<import('../types').Person>(`/admin/people/${id}`, {
        method: 'PUT', body: JSON.stringify(data),
        headers: { 'X-Admin-Key': key },
      }),
    deletePerson: (id: number, key: string) =>
      fetchJson<void>(`/admin/people/${id}`, {
        method: 'DELETE', headers: { 'X-Admin-Key': key },
      }),
    addSource: (personId: number, data: { type: string; url: string }, key: string) =>
      fetchJson<import('../types').Source>(`/admin/people/${personId}/sources`, {
        method: 'POST', body: JSON.stringify(data),
        headers: { 'X-Admin-Key': key },
      }),
    deleteSource: (id: number, key: string) =>
      fetchJson<void>(`/admin/sources/${id}`, {
        method: 'DELETE', headers: { 'X-Admin-Key': key },
      }),
    createTag: (data: { name: string }, key: string) =>
      fetchJson<import('../types').Tag>('/admin/tags', {
        method: 'POST', body: JSON.stringify(data),
        headers: { 'X-Admin-Key': key },
      }),
    triggerIngest: (key: string) =>
      fetchJson<{ status: string; message: string }>('/admin/ingest/trigger', {
        method: 'POST', headers: { 'X-Admin-Key': key },
      }),
  },
}
```

- [ ] **Step 3: Create React Query hooks**

```typescript
// frontend/src/hooks/useApi.ts
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

export function useContent(params?: Record<string, string>) {
  return useQuery({
    queryKey: ['content', params],
    queryFn: () => api.getContent(params),
  })
}

export function usePeople() {
  return useQuery({
    queryKey: ['people'],
    queryFn: api.getPeople,
  })
}

export function usePersonContent(id: number) {
  return useQuery({
    queryKey: ['personContent', id],
    queryFn: () => api.getPersonContent(id),
  })
}

export function useTags() {
  return useQuery({
    queryKey: ['tags'],
    queryFn: api.getTags,
  })
}

export function useDigestToday() {
  return useQuery({
    queryKey: ['digestToday'],
    queryFn: api.getDigestToday,
    retry: false,
  })
}

export function useDigestHistory() {
  return useQuery({
    queryKey: ['digestHistory'],
    queryFn: api.getDigestHistory,
  })
}
```

- [ ] **Step 4: Verify build**

Run: `cd C:/Projects/newsfeed/frontend && npm run build`
Expected: Build succeeds.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/types/ frontend/src/api/ frontend/src/hooks/
git commit -m "feat: add TypeScript types, API client, and React Query hooks"
```

---

## Task 23: Frontend — SourceIcon & ContentCard Components

**Files:**
- Create: `frontend/src/components/SourceIcon.tsx`
- Create: `frontend/src/components/ContentCard.tsx`

- [ ] **Step 1: Create SourceIcon**

```tsx
// frontend/src/components/SourceIcon.tsx
import type { SourceType } from '../types'

const ICONS: Record<SourceType, string> = {
  blog: '📝',
  youtube: '▶️',
  podcast: '🎙️',
  twitter: '🐦',
  newsletter: '📬',
  github: '🐙',
}

const LABELS: Record<SourceType, string> = {
  blog: 'Blog',
  youtube: 'YouTube',
  podcast: 'Podcast',
  twitter: 'Twitter',
  newsletter: 'Newsletter',
  github: 'GitHub',
}

export default function SourceIcon({ type }: { type: SourceType }) {
  return (
    <span title={LABELS[type]} className="text-sm">
      {ICONS[type]} {LABELS[type]}
    </span>
  )
}
```

- [ ] **Step 2: Create ContentCard**

```tsx
// frontend/src/components/ContentCard.tsx
import { useState } from 'react'
import { Link } from 'react-router-dom'
import type { ContentItem } from '../types'
import SourceIcon from './SourceIcon'

export default function ContentCard({ item }: { item: ContentItem }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-sm transition-shadow">
      <div className="flex items-start gap-3">
        {item.person_avatar_url && (
          <img
            src={item.person_avatar_url}
            alt={item.person_name}
            className="w-10 h-10 rounded-full flex-shrink-0"
          />
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
            <Link
              to={`/people/${item.person_id}`}
              className="font-medium text-gray-700 hover:text-blue-600"
            >
              {item.person_name}
            </Link>
            <span>·</span>
            <SourceIcon type={item.source_type} />
            {item.published_at && (
              <>
                <span>·</span>
                <span>{new Date(item.published_at).toLocaleDateString()}</span>
              </>
            )}
          </div>

          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-base font-semibold text-gray-900 hover:text-blue-600 block mb-1"
          >
            {item.title}
          </a>

          {item.summary && (
            <p className={`text-sm text-gray-600 ${expanded ? '' : 'line-clamp-2'}`}>
              {item.summary}
            </p>
          )}

          {item.summary && item.summary.length > 150 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-xs text-blue-600 mt-1 hover:underline"
            >
              {expanded ? 'Show less' : 'Read more'}
            </button>
          )}

          {item.tags.length > 0 && (
            <div className="flex gap-1.5 mt-2 flex-wrap">
              {item.tags.map((tag) => (
                <span
                  key={tag.id}
                  className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full"
                >
                  {tag.name}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Verify build**

Run: `cd C:/Projects/newsfeed/frontend && npm run build`
Expected: Build succeeds.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/SourceIcon.tsx frontend/src/components/ContentCard.tsx
git commit -m "feat: add SourceIcon and ContentCard components"
```

---

## Task 24: Frontend — FilterBar & Feed Page

**Files:**
- Create: `frontend/src/components/FilterBar.tsx`
- Modify: `frontend/src/pages/FeedPage.tsx`

- [ ] **Step 1: Create FilterBar**

```tsx
// frontend/src/components/FilterBar.tsx
import type { Person, TagWithCount, SourceType } from '../types'

const SOURCE_TYPES: { value: SourceType; label: string }[] = [
  { value: 'blog', label: 'Blog' },
  { value: 'youtube', label: 'YouTube' },
  { value: 'podcast', label: 'Podcast' },
  { value: 'twitter', label: 'Twitter' },
  { value: 'newsletter', label: 'Newsletter' },
  { value: 'github', label: 'GitHub' },
]

interface FilterBarProps {
  people: Person[]
  tags: TagWithCount[]
  filters: {
    person_id?: string
    source_type?: string
    tag_slug?: string
    search?: string
  }
  onChange: (filters: Record<string, string>) => void
}

export default function FilterBar({ people, tags, filters, onChange }: FilterBarProps) {
  const update = (key: string, value: string) => {
    const next = { ...filters, [key]: value }
    if (!value) delete next[key]
    onChange(next)
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 flex flex-wrap gap-3 items-center sticky top-14 z-40">
      <input
        type="text"
        placeholder="Search..."
        value={filters.search || ''}
        onChange={(e) => update('search', e.target.value)}
        className="px-3 py-1.5 border border-gray-300 rounded text-sm flex-1 min-w-48"
      />
      <select
        value={filters.person_id || ''}
        onChange={(e) => update('person_id', e.target.value)}
        className="px-3 py-1.5 border border-gray-300 rounded text-sm"
      >
        <option value="">All people</option>
        {people.map((p) => (
          <option key={p.id} value={p.id}>{p.name}</option>
        ))}
      </select>
      <select
        value={filters.source_type || ''}
        onChange={(e) => update('source_type', e.target.value)}
        className="px-3 py-1.5 border border-gray-300 rounded text-sm"
      >
        <option value="">All sources</option>
        {SOURCE_TYPES.map((s) => (
          <option key={s.value} value={s.value}>{s.label}</option>
        ))}
      </select>
      <select
        value={filters.tag_slug || ''}
        onChange={(e) => update('tag_slug', e.target.value)}
        className="px-3 py-1.5 border border-gray-300 rounded text-sm"
      >
        <option value="">All tags</option>
        {tags.map((t) => (
          <option key={t.slug} value={t.slug}>{t.name} ({t.count})</option>
        ))}
      </select>
    </div>
  )
}
```

- [ ] **Step 2: Implement FeedPage**

```tsx
// frontend/src/pages/FeedPage.tsx
import { useState } from 'react'
import { useContent, usePeople, useTags } from '../hooks/useApi'
import ContentCard from '../components/ContentCard'
import FilterBar from '../components/FilterBar'

export default function FeedPage() {
  const [filters, setFilters] = useState<Record<string, string>>({})
  const [page, setPage] = useState(1)

  const params = { ...filters, page: String(page) }
  const { data, isLoading } = useContent(params)
  const { data: people = [] } = usePeople()
  const { data: tags = [] } = useTags()

  return (
    <div className="space-y-4">
      <FilterBar people={people} tags={tags} filters={filters} onChange={(f) => { setFilters(f); setPage(1) }} />

      {isLoading && <p className="text-gray-500 text-sm">Loading...</p>}

      {data && (
        <>
          <p className="text-xs text-gray-500">{data.total} items</p>
          <div className="space-y-3">
            {data.items.map((item) => (
              <ContentCard key={item.id} item={item} />
            ))}
          </div>

          {data.total > data.page_size && (
            <div className="flex justify-center gap-2 pt-4">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 border rounded text-sm disabled:opacity-50"
              >
                Previous
              </button>
              <span className="px-3 py-1 text-sm text-gray-600">
                Page {data.page} of {Math.ceil(data.total / data.page_size)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= Math.ceil(data.total / data.page_size)}
                className="px-3 py-1 border rounded text-sm disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Verify build**

Run: `cd C:/Projects/newsfeed/frontend && npm run build`
Expected: Build succeeds.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/FilterBar.tsx frontend/src/pages/FeedPage.tsx
git commit -m "feat: add FilterBar and FeedPage with pagination"
```

---

## Task 25: Frontend — Person Profile Page

**Files:**
- Modify: `frontend/src/pages/PersonPage.tsx`

- [ ] **Step 1: Implement PersonPage**

```tsx
// frontend/src/pages/PersonPage.tsx
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import ContentCard from '../components/ContentCard'
import type { Person, ContentList } from '../types'

export default function PersonPage() {
  const { id } = useParams<{ id: string }>()
  const personId = Number(id)

  const { data: people } = useQuery({
    queryKey: ['people'],
    queryFn: api.getPeople,
  })
  const person = people?.find((p: Person) => p.id === personId)

  const { data, isLoading } = useQuery({
    queryKey: ['personContent', personId],
    queryFn: () => api.getPersonContent(personId),
    enabled: !!personId,
  })

  if (!person && !isLoading) {
    return <p className="text-gray-500">Person not found.</p>
  }

  return (
    <div className="space-y-6">
      {person && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center gap-4">
            {person.avatar_url && (
              <img src={person.avatar_url} alt={person.name} className="w-16 h-16 rounded-full" />
            )}
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{person.name}</h1>
              {person.bio && <p className="text-gray-600 mt-1">{person.bio}</p>}
              <p className="text-xs text-gray-400 mt-1">{person.source_count} sources</p>
            </div>
          </div>
        </div>
      )}

      {isLoading && <p className="text-gray-500 text-sm">Loading content...</p>}

      {data && (
        <div className="space-y-3">
          {data.items.map((item) => (
            <ContentCard key={item.id} item={item} />
          ))}
          {data.items.length === 0 && (
            <p className="text-gray-500 text-sm">No content yet.</p>
          )}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Verify build**

Run: `cd C:/Projects/newsfeed/frontend && npm run build`
Expected: Build succeeds.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/PersonPage.tsx
git commit -m "feat: add Person Profile page"
```

---

## Task 26: Frontend — Trending Page

**Files:**
- Create: `frontend/src/components/TagCloud.tsx`
- Modify: `frontend/src/pages/TrendingPage.tsx`

- [ ] **Step 1: Create TagCloud**

```tsx
// frontend/src/components/TagCloud.tsx
import type { TagWithCount } from '../types'

export default function TagCloud({ tags }: { tags: TagWithCount[] }) {
  const maxCount = Math.max(...tags.map((t) => t.count), 1)

  return (
    <div className="flex flex-wrap gap-2">
      {tags.map((tag) => {
        const size = 0.75 + (tag.count / maxCount) * 0.75
        return (
          <span
            key={tag.slug}
            className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full cursor-default"
            style={{ fontSize: `${size}rem` }}
          >
            {tag.name} ({tag.count})
          </span>
        )
      })}
    </div>
  )
}
```

- [ ] **Step 2: Implement TrendingPage**

```tsx
// frontend/src/pages/TrendingPage.tsx
import { useDigestToday, useDigestHistory, useTags } from '../hooks/useApi'
import TagCloud from '../components/TagCloud'

export default function TrendingPage() {
  const { data: digest, isLoading: digestLoading } = useDigestToday()
  const { data: history } = useDigestHistory()
  const { data: tags = [] } = useTags()

  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Today's Highlights</h2>
        {digestLoading && <p className="text-gray-500 text-sm">Loading...</p>}
        {digest ? (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="prose prose-sm max-w-none whitespace-pre-line">{digest.highlights}</div>

            {digest.hot_topics.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Hot Topics</h3>
                <div className="flex flex-wrap gap-2">
                  {digest.hot_topics.map((topic) => (
                    <span
                      key={topic.tag}
                      className="px-2 py-1 bg-orange-50 text-orange-700 text-xs rounded-full"
                    >
                      {topic.tag} ({topic.count})
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          !digestLoading && <p className="text-gray-500 text-sm">No digest available yet.</p>
        )}
      </section>

      {tags.length > 0 && (
        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Tag Cloud</h2>
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <TagCloud tags={tags} />
          </div>
        </section>
      )}

      {history && history.length > 1 && (
        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Past Digests</h2>
          <div className="space-y-3">
            {history.slice(1).map((d) => (
              <div key={d.id} className="bg-white rounded-lg border border-gray-200 p-4">
                <p className="text-sm font-medium text-gray-700 mb-2">{d.date}</p>
                <p className="text-sm text-gray-600 whitespace-pre-line">{d.highlights}</p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Verify build**

Run: `cd C:/Projects/newsfeed/frontend && npm run build`
Expected: Build succeeds.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/TagCloud.tsx frontend/src/pages/TrendingPage.tsx
git commit -m "feat: add TagCloud component and Trending page"
```

---

## Task 27: Frontend — Admin Page

**Files:**
- Modify: `frontend/src/pages/AdminPage.tsx`

- [ ] **Step 1: Implement AdminPage**

```tsx
// frontend/src/pages/AdminPage.tsx
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import type { Person, SourceType } from '../types'

const SOURCE_TYPES: SourceType[] = ['blog', 'youtube', 'podcast', 'twitter', 'newsletter', 'github']

export default function AdminPage() {
  const [adminKey, setAdminKey] = useState('')
  const [tab, setTab] = useState<'people' | 'tags'>('people')
  const queryClient = useQueryClient()

  if (!adminKey) {
    return (
      <div className="max-w-md mx-auto mt-12">
        <h2 className="text-xl font-bold mb-4">Admin Access</h2>
        <form onSubmit={(e) => { e.preventDefault(); const input = e.currentTarget.elements.namedItem('key') as HTMLInputElement; setAdminKey(input.value) }}>
          <input name="key" type="password" placeholder="Admin API Key" className="w-full px-3 py-2 border rounded mb-3" />
          <button type="submit" className="w-full px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Login</button>
        </form>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex gap-4 items-center">
        <button onClick={() => setTab('people')} className={`text-sm font-medium ${tab === 'people' ? 'text-blue-600 underline' : 'text-gray-600'}`}>People</button>
        <button onClick={() => setTab('tags')} className={`text-sm font-medium ${tab === 'tags' ? 'text-blue-600 underline' : 'text-gray-600'}`}>Tags</button>
        <div className="flex-1" />
        <TriggerIngestButton adminKey={adminKey} />
      </div>

      {tab === 'people' && <PeopleTab adminKey={adminKey} />}
      {tab === 'tags' && <TagsTab adminKey={adminKey} />}
    </div>
  )
}

function TriggerIngestButton({ adminKey }: { adminKey: string }) {
  const mutation = useMutation({ mutationFn: () => api.admin.triggerIngest(adminKey) })
  return (
    <button
      onClick={() => mutation.mutate()}
      disabled={mutation.isPending}
      className="px-3 py-1.5 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50"
    >
      {mutation.isPending ? 'Running...' : 'Run Ingestion Now'}
    </button>
  )
}

function PeopleTab({ adminKey }: { adminKey: string }) {
  const queryClient = useQueryClient()
  const { data: people = [] } = useQuery({ queryKey: ['people'], queryFn: api.getPeople })
  const [name, setName] = useState('')
  const [sourceForm, setSourceForm] = useState<{ personId: number; type: SourceType; url: string } | null>(null)

  const createPerson = useMutation({
    mutationFn: (n: string) => api.admin.createPerson({ name: n }, adminKey),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['people'] }); setName('') },
  })

  const deletePerson = useMutation({
    mutationFn: (id: number) => api.admin.deletePerson(id, adminKey),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['people'] }),
  })

  const addSource = useMutation({
    mutationFn: (data: { personId: number; type: string; url: string }) =>
      api.admin.addSource(data.personId, { type: data.type, url: data.url }, adminKey),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['people'] }); setSourceForm(null) },
  })

  return (
    <div className="space-y-4">
      <form
        onSubmit={(e) => { e.preventDefault(); if (name.trim()) createPerson.mutate(name.trim()) }}
        className="flex gap-2"
      >
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Person name" className="flex-1 px-3 py-2 border rounded text-sm" />
        <button type="submit" className="px-4 py-2 bg-blue-600 text-white text-sm rounded">Add Person</button>
      </form>

      {people.map((p: Person) => (
        <div key={p.id} className="bg-white border rounded-lg p-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="font-medium">{p.name}</p>
              <p className="text-xs text-gray-500">{p.source_count} sources</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setSourceForm({ personId: p.id, type: 'blog', url: '' })}
                className="text-xs text-blue-600 hover:underline"
              >
                + Source
              </button>
              <button onClick={() => deletePerson.mutate(p.id)} className="text-xs text-red-600 hover:underline">Delete</button>
            </div>
          </div>
          {sourceForm?.personId === p.id && (
            <form
              onSubmit={(e) => { e.preventDefault(); addSource.mutate(sourceForm) }}
              className="mt-3 flex gap-2"
            >
              <select
                value={sourceForm.type}
                onChange={(e) => setSourceForm({ ...sourceForm, type: e.target.value as SourceType })}
                className="px-2 py-1 border rounded text-sm"
              >
                {SOURCE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
              <input
                value={sourceForm.url}
                onChange={(e) => setSourceForm({ ...sourceForm, url: e.target.value })}
                placeholder="URL or handle"
                className="flex-1 px-2 py-1 border rounded text-sm"
              />
              <button type="submit" className="px-3 py-1 bg-blue-600 text-white text-sm rounded">Add</button>
              <button type="button" onClick={() => setSourceForm(null)} className="px-3 py-1 border text-sm rounded">Cancel</button>
            </form>
          )}
        </div>
      ))}
    </div>
  )
}

function TagsTab({ adminKey }: { adminKey: string }) {
  const queryClient = useQueryClient()
  const { data: tags = [] } = useQuery({ queryKey: ['tags'], queryFn: api.getTags })
  const [name, setName] = useState('')

  const createTag = useMutation({
    mutationFn: (n: string) => api.admin.createTag({ name: n }, adminKey),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['tags'] }); setName('') },
  })

  return (
    <div className="space-y-4">
      <form
        onSubmit={(e) => { e.preventDefault(); if (name.trim()) createTag.mutate(name.trim()) }}
        className="flex gap-2"
      >
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Tag name" className="flex-1 px-3 py-2 border rounded text-sm" />
        <button type="submit" className="px-4 py-2 bg-blue-600 text-white text-sm rounded">Add Tag</button>
      </form>

      <div className="flex flex-wrap gap-2">
        {tags.map((t) => (
          <span key={t.slug} className="px-3 py-1.5 bg-white border rounded-full text-sm">
            {t.name} ({t.count})
          </span>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verify build**

Run: `cd C:/Projects/newsfeed/frontend && npm run build`
Expected: Build succeeds.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/AdminPage.tsx
git commit -m "feat: add Admin page (people/sources/tags CRUD, ingest trigger)"
```

---

## Task 28: Frontend Dockerfile & Final Docker Compose

**Files:**
- Create: `frontend/Dockerfile`
- Verify: `docker-compose.yml`

- [ ] **Step 1: Create frontend Dockerfile**

```dockerfile
# frontend/Dockerfile
FROM node:20-slim

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

- [ ] **Step 2: Create .env from .env.example**

Run: `cp C:/Projects/newsfeed/.env.example C:/Projects/newsfeed/.env`

Edit `.env` with real API keys as needed for local testing.

- [ ] **Step 3: Test Docker Compose builds**

Run: `cd C:/Projects/newsfeed && docker compose build`
Expected: All three services build successfully.

- [ ] **Step 4: Commit**

```bash
git add frontend/Dockerfile
git commit -m "feat: add frontend Dockerfile, finalize Docker Compose setup"
```

---

## Task 29: Seed Initial Tags

**Files:**
- Create: `backend/seed.py`

- [ ] **Step 1: Create seed script**

```python
# backend/seed.py
import asyncio

from slugify import slugify
from sqlalchemy import select

from backend.database import async_session
from backend.models import Tag

INITIAL_TAGS = [
    "AI Coding Workflows",
    "Prompt Engineering",
    "Agent Frameworks",
    "LLM Tools",
    "Open Source",
    "Industry News",
]


async def seed_tags():
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/seed.py
git commit -m "feat: add seed script for initial tag taxonomy"
```

---

## Task 30: End-to-End Smoke Test

- [ ] **Step 1: Start the stack**

Run: `cd C:/Projects/newsfeed && docker compose up -d`

- [ ] **Step 2: Run Alembic migration**

Run: `cd C:/Projects/newsfeed && alembic upgrade head`

- [ ] **Step 3: Seed tags**

Run: `cd C:/Projects/newsfeed && python -m backend.seed`

- [ ] **Step 4: Verify API health**

Run: `curl http://localhost:8000/api/tags`
Expected: JSON array with 6 seeded tags.

Run: `curl http://localhost:8000/api/people`
Expected: Empty JSON array `[]`.

- [ ] **Step 5: Create a person via admin API**

Run:
```bash
curl -X POST http://localhost:8000/api/admin/people \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: change-me-in-production" \
  -d '{"name": "Andrej Karpathy", "bio": "AI researcher, educator, YouTuber"}'
```
Expected: 201 with person JSON.

- [ ] **Step 6: Verify frontend loads**

Open `http://localhost:5173` in browser.
Expected: AI Newsfeed dashboard loads with navigation, empty feed, working filter bar.

- [ ] **Step 7: Run all backend tests one final time**

Run: `cd C:/Projects/newsfeed && python -m pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 8: Stop stack**

Run: `cd C:/Projects/newsfeed && docker compose down`
