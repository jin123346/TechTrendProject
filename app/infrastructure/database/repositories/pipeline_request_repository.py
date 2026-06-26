from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.domain.enums import PipelineRequestStatus, PipelineRequestType
from app.infrastructure.database.models import PipelineRunRequest, SearchKeyword, Source


class PipelineRequestRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_source(self, source_id: int) -> Source | None:
        return self.db.get(Source, source_id)

    def get_keyword(self, keyword_id: int) -> SearchKeyword | None:
        return self.db.get(SearchKeyword, keyword_id)

    def add(self, request: PipelineRunRequest) -> PipelineRunRequest:
        self.db.add(request)
        self.db.flush()
        return request

    def get(self, request_id: int) -> PipelineRunRequest | None:
        return self.db.get(PipelineRunRequest, request_id)

    def get_with_runs(self, request_id: int) -> PipelineRunRequest | None:
        stmt = (
            select(PipelineRunRequest)
            .options(selectinload(PipelineRunRequest.runs))
            .where(PipelineRunRequest.request_id == request_id)
        )
        return self.db.scalars(stmt).first()

    def get_for_update(self, request_id: int) -> PipelineRunRequest | None:
        # PostgreSQL locks the request row while the run number is calculated.
        # SQLite ignores FOR UPDATE in tests; the unique constraint remains the final guard.
        stmt = select(PipelineRunRequest).where(PipelineRunRequest.request_id == request_id).with_for_update()
        return self.db.scalars(stmt).first()

    def list(
        self,
        *,
        pipeline_code: str | None = None,
        request_type: PipelineRequestType | None = None,
        request_status: PipelineRequestStatus | None = None,
        source_id: int | None = None,
        keyword_id: int | None = None,
        requested_from: datetime | None = None,
        requested_to: datetime | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[PipelineRunRequest], int]:
        stmt = self._filtered_query(
            pipeline_code=pipeline_code,
            request_type=request_type,
            request_status=request_status,
            source_id=source_id,
            keyword_id=keyword_id,
            requested_from=requested_from,
            requested_to=requested_to,
        )
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        rows = self.db.scalars(
            stmt.order_by(PipelineRunRequest.requested_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        return list(rows), total

    def _filtered_query(
        self,
        *,
        pipeline_code: str | None,
        request_type: PipelineRequestType | None,
        request_status: PipelineRequestStatus | None,
        source_id: int | None,
        keyword_id: int | None,
        requested_from: datetime | None,
        requested_to: datetime | None,
    ) -> Select[tuple[PipelineRunRequest]]:
        stmt = select(PipelineRunRequest)
        if pipeline_code:
            stmt = stmt.where(PipelineRunRequest.pipeline_code == pipeline_code)
        if request_type:
            stmt = stmt.where(PipelineRunRequest.request_type == request_type)
        if request_status:
            stmt = stmt.where(PipelineRunRequest.request_status == request_status)
        if source_id is not None:
            stmt = stmt.where(PipelineRunRequest.source_id == source_id)
        if keyword_id is not None:
            stmt = stmt.where(PipelineRunRequest.keyword_id == keyword_id)
        if requested_from:
            stmt = stmt.where(PipelineRunRequest.requested_at >= requested_from)
        if requested_to:
            stmt = stmt.where(PipelineRunRequest.requested_at <= requested_to)
        return stmt
