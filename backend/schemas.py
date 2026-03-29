from datetime import datetime, date
from pydantic import BaseModel

from backend.models import SourceType, ProcessingStatus


class TagOut(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


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


class TagCreate(BaseModel):
    name: str


class TagWithCount(BaseModel):
    id: int
    name: str
    slug: str
    count: int = 0

    model_config = {"from_attributes": True}


class DailyDigestOut(BaseModel):
    id: int
    date: date
    highlights: str
    hot_topics: list[dict]
    created_at: datetime

    model_config = {"from_attributes": True}


class IngestTriggerOut(BaseModel):
    status: str
    message: str
