from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.enums import LogLevel
from app.infrastructure.database.models.mixins import utc_now


class PipelineLog(Base):
    __tablename__ = "pipeline_logs"
    __table_args__ = (
        CheckConstraint(
            "log_level in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')",
            name="ck_pipeline_logs_level",
        ),
        Index("ix_pipeline_logs_run_id_created_at", "run_id", "created_at"),
        Index("ix_pipeline_logs_log_level", "log_level"),
    )

    log_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("pipeline_runs.run_id", ondelete="RESTRICT"), nullable=False)
    log_level: Mapped[LogLevel] = mapped_column(String(20), default=LogLevel.INFO, nullable=False)
    pipeline_step: Mapped[str | None] = mapped_column(String(100))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    detail_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    run = relationship("PipelineRun", back_populates="logs")
