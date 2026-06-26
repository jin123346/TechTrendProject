from sqlalchemy import Boolean, CheckConstraint, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.enums import SourceType
from app.infrastructure.database.models.mixins import TimestampMixin


class Source(TimestampMixin, Base):
    __tablename__ = "sources"
    __table_args__ = (
        CheckConstraint(
            "source_type in ('API', 'RSS', 'BLOG', 'WEB')",
            name="ck_sources_source_type",
        ),
        Index("ix_sources_source_type", "source_type"),
        Index("ix_sources_is_active", "is_active"),
    )

    source_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    source_name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(String(20), nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(1000))
    config_json: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    requests = relationship("PipelineRunRequest", back_populates="source")
    articles = relationship("Article", back_populates="source")
