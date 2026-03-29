import enum
from datetime import datetime, date

from sqlalchemy import String, Text, Boolean, Enum, ForeignKey, Date, Column, Table, JSON
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
