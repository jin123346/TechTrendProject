from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.enums import PipelineRequestStatus, PipelineRequestType
from app.infrastructure.database.models.mixins import TimestampMixin, utc_now


class PipelineRunRequest(TimestampMixin, Base):
    __tablename__ = "pipeline_run_requests"
    __table_args__ = (
        CheckConstraint(
            "request_type in ('MANUAL', 'SCHEDULED', 'RETRY', 'API')",
            name="ck_pipeline_run_requests_type",
        ),
        CheckConstraint(
            "request_status in ('REQUESTED', 'ACCEPTED', 'REJECTED', 'CANCELLED')",
            name="ck_pipeline_run_requests_status",
        ),
        Index("ix_pipeline_run_requests_status", "request_status"),
        Index("ix_pipeline_run_requests_requested_at", "requested_at"),
    )

    request_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pipeline_code: Mapped[str] = mapped_column(String(100), nullable=False)
    request_type: Mapped[PipelineRequestType] = mapped_column(String(30), nullable=False)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.source_id", ondelete="RESTRICT"))
    keyword_id: Mapped[int | None] = mapped_column(ForeignKey("search_keywords.keyword_id", ondelete="RESTRICT"))
    requested_by: Mapped[str | None] = mapped_column(String(100))
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    request_options_json: Mapped[str | None] = mapped_column(Text)
    request_status: Mapped[PipelineRequestStatus] = mapped_column(
        String(30),
        default=PipelineRequestStatus.REQUESTED,
        nullable=False,
    )

    source = relationship("Source", back_populates="requests")
    keyword = relationship("SearchKeyword", back_populates="requests")
    runs = relationship("PipelineRun", back_populates="request")
