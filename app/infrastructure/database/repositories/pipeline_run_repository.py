from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.domain.enums import PipelineRunStatus
from app.infrastructure.database.models import PipelineLog, PipelineRun, PipelineRunRequest


class PipelineRunRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, run: PipelineRun) -> PipelineRun:
        self.db.add(run)
        self.db.flush()
        return run

    def add_log(self, log: PipelineLog) -> PipelineLog:
        self.db.add(log)
        self.db.flush()
        return log

    def get(self, run_id: int) -> PipelineRun | None:
        return self.db.get(PipelineRun, run_id)

    def get_with_logs(self, run_id: int) -> PipelineRun | None:
        stmt = (
            select(PipelineRun)
            .options(selectinload(PipelineRun.logs), selectinload(PipelineRun.request))
            .where(PipelineRun.run_id == run_id)
        )
        return self.db.scalars(stmt).first()

    def list_logs(self, run_id: int) -> list[PipelineLog]:
        stmt = select(PipelineLog).where(PipelineLog.run_id == run_id).order_by(PipelineLog.created_at.asc())
        return list(self.db.scalars(stmt).all())

    def has_running_run(self, request_id: int) -> bool:
        stmt = select(PipelineRun.run_id).where(
            PipelineRun.request_id == request_id,
            PipelineRun.run_status == PipelineRunStatus.RUNNING,
        )
        return self.db.scalars(stmt).first() is not None

    def next_run_number(self, request_id: int) -> int:
        current = self.db.scalar(
            select(func.max(PipelineRun.run_number)).where(PipelineRun.request_id == request_id)
        )
        return int(current or 0) + 1

    def latest_run(self, request_id: int) -> PipelineRun | None:
        stmt = (
            select(PipelineRun)
            .where(PipelineRun.request_id == request_id)
            .order_by(PipelineRun.run_number.desc())
            .limit(1)
        )
        return self.db.scalars(stmt).first()

    def list(
        self,
        *,
        request_id: int | None = None,
        pipeline_code: str | None = None,
        run_status: PipelineRunStatus | None = None,
        source_id: int | None = None,
        keyword_id: int | None = None,
        started_from: datetime | None = None,
        started_to: datetime | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[PipelineRun], int]:
        stmt = self._filtered_query(
            request_id=request_id,
            pipeline_code=pipeline_code,
            run_status=run_status,
            source_id=source_id,
            keyword_id=keyword_id,
            started_from=started_from,
            started_to=started_to,
        )
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        rows = self.db.scalars(
            stmt.order_by(PipelineRun.started_at.desc().nullslast(), PipelineRun.run_id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        return list(rows), total

    def _filtered_query(
        self,
        *,
        request_id: int | None,
        pipeline_code: str | None,
        run_status: PipelineRunStatus | None,
        source_id: int | None,
        keyword_id: int | None,
        started_from: datetime | None,
        started_to: datetime | None,
    ) -> Select[tuple[PipelineRun]]:
        stmt = select(PipelineRun).join(PipelineRunRequest)
        if request_id is not None:
            stmt = stmt.where(PipelineRun.request_id == request_id)
        if pipeline_code:
            stmt = stmt.where(PipelineRunRequest.pipeline_code == pipeline_code)
        if run_status:
            stmt = stmt.where(PipelineRun.run_status == run_status)
        if source_id is not None:
            stmt = stmt.where(PipelineRunRequest.source_id == source_id)
        if keyword_id is not None:
            stmt = stmt.where(PipelineRunRequest.keyword_id == keyword_id)
        if started_from:
            stmt = stmt.where(PipelineRun.started_at >= started_from)
        if started_to:
            stmt = stmt.where(PipelineRun.started_at <= started_to)
        return stmt
