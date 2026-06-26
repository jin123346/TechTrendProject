from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.enums import FetchJobStatus, FetchRequestType
from app.infrastructure.database.models.mixins import TimestampMixin


class ContentFetchJob(TimestampMixin, Base):
    __tablename__ = "content_fetch_jobs"
    __table_args__ = (
        UniqueConstraint("article_id", "attempt_number", name="uq_content_fetch_jobs_article_attempt"),
        CheckConstraint(
            "fetch_status in ('PENDING', 'RUNNING', 'SUCCESS', 'FAILED', 'SKIPPED')",
            name="ck_content_fetch_jobs_status",
        ),
        CheckConstraint(
            "request_type in ('AUTO', 'MANUAL', 'RETRY', 'REFRESH')",
            name="ck_content_fetch_jobs_request_type",
        ),
        CheckConstraint("retry_count >= 0", name="ck_content_fetch_jobs_retry_count"),
        Index("ix_content_fetch_jobs_status", "fetch_status"),
        Index("ix_content_fetch_jobs_article_id", "article_id"),
        Index("ix_content_fetch_jobs_run_id", "run_id"),
    )

    fetch_job_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.article_id", ondelete="RESTRICT"), nullable=False)
    run_id: Mapped[int | None] = mapped_column(ForeignKey("pipeline_runs.run_id", ondelete="RESTRICT"))
    attempt_number: Mapped[int] = mapped_column(nullable=False)
    request_type: Mapped[FetchRequestType] = mapped_column(String(30), default=FetchRequestType.AUTO, nullable=False)
    fetch_status: Mapped[FetchJobStatus] = mapped_column(String(30), default=FetchJobStatus.PENDING, nullable=False)
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    http_status_code: Mapped[int | None] = mapped_column()
    retry_count: Mapped[int] = mapped_column(default=0, nullable=False)
    error_type: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)
    raw_html: Mapped[str | None] = mapped_column(Text)
    clean_content: Mapped[str | None] = mapped_column(Text)
    content_length: Mapped[int | None] = mapped_column()
    content_hash: Mapped[str | None] = mapped_column(String(64))
    fetcher_version: Mapped[str | None] = mapped_column(String(100))

    article = relationship("Article", back_populates="fetch_jobs")
    run = relationship("PipelineRun", back_populates="fetch_jobs")
