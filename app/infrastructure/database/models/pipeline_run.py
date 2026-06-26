from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.enums import PipelineRunStatus
from app.infrastructure.database.models.mixins import TimestampMixin


class PipelineRun(TimestampMixin, Base):
    __tablename__ = "pipeline_runs"
    __table_args__ = (
        UniqueConstraint("request_id", "run_number", name="uq_pipeline_runs_request_run_number"),
        CheckConstraint(
            "run_status in ('PENDING', 'RUNNING', 'SUCCESS', 'PARTIAL_SUCCESS', 'FAILED', 'CANCELLED')",
            name="ck_pipeline_runs_status",
        ),
        CheckConstraint(
            "total_count >= 0 and success_count >= 0 and failure_count >= 0 "
            "and skipped_count >= 0 and duplicate_count >= 0",
            name="ck_pipeline_runs_counts_non_negative",
        ),
        Index("ix_pipeline_runs_status", "run_status"),
        Index("ix_pipeline_runs_started_at", "started_at"),
    )

    run_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("pipeline_run_requests.request_id", ondelete="RESTRICT"), nullable=False)
    run_number: Mapped[int] = mapped_column(nullable=False)
    run_status: Mapped[PipelineRunStatus] = mapped_column(
        String(30),
        default=PipelineRunStatus.PENDING,
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    total_count: Mapped[int] = mapped_column(default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(default=0, nullable=False)
    failure_count: Mapped[int] = mapped_column(default=0, nullable=False)
    skipped_count: Mapped[int] = mapped_column(default=0, nullable=False)
    duplicate_count: Mapped[int] = mapped_column(default=0, nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)
    execution_options_json: Mapped[str | None] = mapped_column(Text)
    worker_id: Mapped[str | None] = mapped_column(String(100))

    request = relationship("PipelineRunRequest", back_populates="runs")
    logs = relationship("PipelineLog", back_populates="run")
    collections = relationship("ArticleCollection", back_populates="run")
    fetch_jobs = relationship("ContentFetchJob", back_populates="run")
