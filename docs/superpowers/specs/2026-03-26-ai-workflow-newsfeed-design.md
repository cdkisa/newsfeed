# AI Workflow Newsfeed — Design Spec

## Overview

A web dashboard that aggregates the latest content (blog posts, YouTube videos, podcasts, tweets, newsletters, GitHub activity) from software engineers who share their AI workflows — people like Boris Cherny, Andrej Karpathy, Harrison Chase, and others. AI-powered summarization, tagging, and trending highlights make it easy to stay current.

## Architecture

Two apps in a monorepo:

- **Backend:** FastAPI (Python) — REST API, content ingestion, AI processing, scheduling
- **Frontend:** Vite + React + TypeScript + Tailwind CSS — dashboard and admin UI
- **Database:** PostgreSQL via SQLAlchemy (async), migrations via Alembic
- **LLM:** LiteLLM for pluggable provider support (Claude, OpenAI, Ollama, etc.)

```
newsfeed/
├── backend/
│   ├── api/              # FastAPI routes (public + admin)
│   ├── ingestion/        # Source fetchers (one module per source type)
│   ├── ai/               # LLM processing (summarize, tag, trending)
│   ├── models/           # SQLAlchemy models
│   ├── migrations/       # Alembic migrations
│   └── scheduler/        # APScheduler daily job
├── frontend/
│   ├── src/
│   │   ├── pages/        # Home/Feed, Person Profile, Trending, Admin
│   │   └── components/   # ContentCard, FilterBar, TagCloud, etc.
│   └── ...
└── docker-compose.yml    # PostgreSQL + backend + frontend
```

### Data Flow

1. **Daily job** (APScheduler, default 6 AM) triggers all source fetchers
2. **Fetchers** pull raw content, normalize into a common `RawContent` schema, store in PostgreSQL
3. **AI pipeline** runs on new items: summarize, tag, extract trending topics
4. **API** serves processed content to the React frontend
5. **Dashboard** displays content with filtering, search, and trending highlights

## Content Ingestion

Six source fetchers, each implementing a common interface:

```python
class BaseFetcher:
    async def fetch(self, source: Source) -> list[RawContent]:
        """Fetch new content since last_fetched_at"""
        ...
```

| Fetcher | Method | Key Library |
|---------|--------|-------------|
| Blog/Website | RSS/Atom feed parsing, fallback to HTML scraping | `feedparser`, `BeautifulSoup` |
| YouTube | YouTube Data API v3 (channel videos list) | `google-api-python-client` |
| Podcasts | RSS feed parsing (standard podcast RSS) | `feedparser` |
| Twitter/X | API v2 (user timeline) | `tweepy` or direct REST |
| Newsletters | RSS if available (Substack feeds), fallback to scraping | `feedparser`, `BeautifulSoup` |
| GitHub | REST API (user events, releases) | `PyGithub` or `httpx` |

### Deduplication

Content is deduped by URL (`ContentItem.url` is unique). Cross-posted content (e.g., blog post shared on Twitter) is kept as separate items linked to the same person — the dashboard can group them.

### Error Handling

Each fetcher runs independently. If one fails (e.g., Twitter rate limit), it logs the error and the rest continue. Failed fetches retry on the next daily run.

### YouTube Transcripts

After fetching video metadata via the YouTube Data API, transcripts are pulled via `youtube-transcript-api` for use as summarization input.

## AI Processing Pipeline

Three stages, all using LiteLLM as the provider abstraction.

### Provider Configuration

```
LLM_PROVIDER=anthropic/claude-sonnet-4-20250514
```

LiteLLM wraps 100+ providers behind a single `completion()` call. Switch providers by changing one env var.

### Stage 1 — Summarization

- Each content item gets a 2-3 sentence summary
- Long-form content (articles, podcast transcripts, YouTube transcripts): summarize key takeaways
- Short-form (tweets, GitHub activity): skip summarization, use raw content as-is
- Summaries stored on the `ContentItem` row

### Stage 2 — Tagging

- Each item classified into 1-3 tags from a predefined taxonomy
- Initial tags: "AI Coding Workflows", "Prompt Engineering", "Agent Frameworks", "LLM Tools", "Open Source", "Industry News"
- Taxonomy extensible via admin UI
- Tags stored as a many-to-many relationship (`content_tags` join table)

### Stage 3 — Trending / Highlights

- Runs after all items are processed for the day
- Analyzes the day's content as a batch: most common topics, notable patterns
- Produces a "Today's Highlights" summary (3-5 bullet points) stored in `DailyDigest` table
- Identifies "hot topics" — tags that spiked compared to their rolling average

### Cost Control

- Short content (tweets, GitHub events) skips the LLM when possible
- Batch processing uses the cheapest acceptable model tier
- `processing_status` field prevents reprocessing on retries

## API Design

### Public Endpoints (Dashboard)

| Endpoint | Description |
|----------|-------------|
| `GET /api/content` | Paginated feed — filters by person, source type, tag, date range. Default: latest first |
| `GET /api/content/{id}` | Single item with full summary, tags, original URL |
| `GET /api/people` | List all followed people with avatar, bio, source count |
| `GET /api/people/{id}/content` | All content from a specific person |
| `GET /api/tags` | All tags with item counts |
| `GET /api/tags/{slug}/content` | Content filtered by tag |
| `GET /api/digest/today` | Today's highlights and trending topics |
| `GET /api/digest/history` | Past daily digests |

### Admin Endpoints

Protected by API key (`ADMIN_API_KEY` env var).

| Endpoint | Description |
|----------|-------------|
| `POST /api/admin/people` | Add a person (name, avatar URL, bio) |
| `PUT /api/admin/people/{id}` | Update a person |
| `DELETE /api/admin/people/{id}` | Remove a person and optionally their content |
| `POST /api/admin/people/{id}/sources` | Add a source (type + URL/handle) to a person |
| `DELETE /api/admin/sources/{id}` | Remove a source |
| `POST /api/admin/tags` | Add a new tag to the taxonomy |
| `POST /api/admin/ingest/trigger` | Manually trigger an ingestion run |

No auth on public endpoints — this is a personal tool.

## Data Model

### Person

| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| name | string | |
| avatar_url | string, nullable | |
| bio | text, nullable | |
| created_at | timestamp | |
| updated_at | timestamp | |

### Source

| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| person_id | FK → Person | |
| type | enum | blog, youtube, podcast, twitter, newsletter, github |
| url | string | Feed URL, channel URL, handle, etc. |
| last_fetched_at | timestamp, nullable | |
| active | bool | Default true |
| created_at | timestamp | |

### ContentItem

| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| source_id | FK → Source | |
| person_id | FK → Person | Denormalized for query convenience |
| title | string | |
| url | string, unique | Dedup key |
| body | text, nullable | Raw content or transcript |
| summary | text, nullable | LLM-generated |
| source_type | enum | Same enum as Source.type |
| published_at | timestamp | |
| processing_status | enum | pending, processing, completed, failed |
| created_at | timestamp | |

Full-text search index on `title` + `summary` using PostgreSQL `tsvector`.

### Tag

| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| name | string | Display name |
| slug | string, unique | URL-safe identifier |
| created_at | timestamp | |

### content_tags (join table)

| Column | Type |
|--------|------|
| content_id | FK → ContentItem |
| tag_id | FK → Tag |

Composite primary key on `(content_id, tag_id)`.

### DailyDigest

| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| date | date, unique | |
| highlights | text | LLM-generated bullet points |
| hot_topics | JSON | List of {tag, count, trend} objects |
| created_at | timestamp | |

## Frontend

React + Vite + TypeScript + Tailwind CSS. State management via TanStack Query (React Query).

### Pages

| Page | Description |
|------|-------------|
| Home / Feed | Chronological feed with summary cards. Sticky filter bar: person, source type, tag, date range. Each card: avatar, title, summary, tags, source icon, date, original link |
| Person Profile | All content from one person grouped by source type. Bio and links at top |
| Trending | Today's highlights at top, hot topics below, tag cloud with relative sizing |
| Admin | Two tabs: People (add/edit/remove people and sources) and Tags (manage taxonomy). "Run Ingestion Now" button |

### Key UI Elements

- **Content card** — compact by default, expandable for full summary. Source type icon (blog, YouTube, podcast, tweet, GitHub, newsletter)
- **Filter bar** — sticky top. Multi-select for people, source types, tags. Date range picker
- **Search** — full-text across titles and summaries (PostgreSQL `tsvector` backed)
- **Responsive** — mobile-friendly, desktop primary

## Infrastructure

### Local Development

`docker-compose.yml` runs PostgreSQL, FastAPI backend (`uvicorn --reload`), and Vite dev server (HMR).

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `LLM_PROVIDER` | LiteLLM model string (e.g., `anthropic/claude-sonnet-4-20250514`) |
| `LLM_API_KEY` | API key for the chosen LLM provider |
| `ADMIN_API_KEY` | Protects admin endpoints |
| `YOUTUBE_API_KEY` | YouTube Data API v3 |
| `TWITTER_BEARER_TOKEN` | Twitter API v2 |
| `GITHUB_TOKEN` | GitHub API (optional, increases rate limits) |
| `INGEST_SCHEDULE` | Cron expression, default `0 6 * * *` (6 AM daily) |

### Scheduler

APScheduler runs inside the FastAPI process. Registers the daily ingestion job on startup. Manual runs via `POST /api/admin/ingest/trigger`.

### Database Migrations

Alembic for schema versioning. Migrations in `backend/migrations/`.

### Production

Not designed up front. Start local with Docker Compose. Deploy when ready to any platform (Railway, Fly.io, VPS) with managed PostgreSQL.
