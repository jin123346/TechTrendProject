from sqlalchemy import Boolean, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.infrastructure.database.models.mixins import TimestampMixin


class SearchKeyword(TimestampMixin, Base):
    __tablename__ = "search_keywords"
    __table_args__ = (
        Index("ix_search_keywords_is_active", "is_active"),
        Index("ix_search_keywords_normalized_keyword", "normalized_keyword"),
    )

    keyword_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    keyword: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    normalized_keyword: Mapped[str | None] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    requests = relationship("PipelineRunRequest", back_populates="keyword")
    collections = relationship("ArticleCollection", back_populates="keyword")
