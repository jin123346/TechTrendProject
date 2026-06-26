from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.enums import ArticleFetchStatus
from app.infrastructure.database.models.mixins import TimestampMixin


class Article(TimestampMixin, Base):
    __tablename__ = "articles"
    __table_args__ = (
        CheckConstraint(
            "current_fetch_status in ('DISCOVERED', 'FETCH_PENDING', 'FETCHING', 'FETCHED', 'FETCH_FAILED')",
            name="ck_articles_current_fetch_status",
        ),
        Index("ix_articles_source_id", "source_id"),
        Index("ix_articles_published_at", "published_at"),
        Index("ix_articles_current_fetch_status", "current_fetch_status"),
        Index("ix_articles_source_external_id", "source_id", "external_article_id", unique=True),
        Index("ix_articles_url_hash", "url_hash", unique=True),
    )

    article_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.source_id", ondelete="RESTRICT"), nullable=False)
    external_article_id: Mapped[str | None] = mapped_column(String(300))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_url: Mapped[str | None] = mapped_column(Text)
    canonical_url: Mapped[str | None] = mapped_column(Text)
    url_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(String(300))
    publisher: Mapped[str | None] = mapped_column(String(300))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    current_fetch_status: Mapped[ArticleFetchStatus] = mapped_column(
        String(30),
        default=ArticleFetchStatus.DISCOVERED,
        nullable=False,
    )
    latest_fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    latest_content_hash: Mapped[str | None] = mapped_column(String(64))

    source = relationship("Source", back_populates="articles")
    collections = relationship("ArticleCollection", back_populates="article")
    fetch_jobs = relationship("ContentFetchJob", back_populates="article")
