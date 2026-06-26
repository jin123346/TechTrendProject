from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.infrastructure.database.models.mixins import utc_now


class ArticleCollection(Base):
    __tablename__ = "article_collections"
    __table_args__ = (
        UniqueConstraint("run_id", "article_id", "keyword_id", name="uq_article_collections_run_article_keyword"),
        Index("ix_article_collections_run_id", "run_id"),
        Index("ix_article_collections_keyword_id", "keyword_id"),
        Index("ix_article_collections_discovered_at", "discovered_at"),
    )

    collection_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("pipeline_runs.run_id", ondelete="RESTRICT"), nullable=False)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.article_id", ondelete="RESTRICT"), nullable=False)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("search_keywords.keyword_id", ondelete="RESTRICT"), nullable=False)
    search_rank: Mapped[int | None] = mapped_column()
    discovered_title: Mapped[str | None] = mapped_column(Text)
    discovered_summary: Mapped[str | None] = mapped_column(Text)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    raw_response_json: Mapped[str | None] = mapped_column(Text)

    run = relationship("PipelineRun", back_populates="collections")
    article = relationship("Article", back_populates="collections")
    keyword = relationship("SearchKeyword", back_populates="collections")
