from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.api.v1.schemas.common import clamp_page_size
from app.api.v1.schemas.pipeline_runs import (
    PipelineLogResponse,
    PipelineRunListResponse,
    PipelineRunRequestSummary,
    PipelineRunResponse,
)
from app.application.services.json_utils import load_json
from app.domain.enums import PipelineRunStatus
from app.domain.exceptions import PipelineRunNotFoundError
from app.infrastructure.database.models import PipelineLog, PipelineRun
from app.infrastructure.database.repositories.pipeline_run_repository import PipelineRunRepository

router = APIRouter(prefix="/api/v1/pipeline-runs", tags=["pipeline-runs"])


@router.get("", response_model=PipelineRunListResponse)
def list_pipeline_runs(
    request_id: int | None = None,
    pipeline_code: str | None = None,
    run_status: PipelineRunStatus | None = None,
    source_id: int | None = None,
    keyword_id: int | None = None,
    started_from: datetime | None = None,
    started_to: datetime | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db_session),
) -> PipelineRunListResponse:
    page_size = clamp_page_size(page_size)
    repository = PipelineRunRepository(db)
    items, total = repository.list(
        request_id=request_id,
        pipeline_code=pipeline_code,
        run_status=run_status,
        source_id=source_id,
        keyword_id=keyword_id,
        started_from=started_from,
        started_to=started_to,
        page=page,
        page_size=page_size,
    )
    return PipelineRunListResponse(
        items=[run_response(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{run_id}", response_model=PipelineRunResponse)
def get_pipeline_run(run_id: int, db: Session = Depends(get_db_session)) -> PipelineRunResponse:
    repository = PipelineRunRepository(db)
    run = repository.get_with_logs(run_id)
    if run is None:
        raise PipelineRunNotFoundError(f"Pipeline run {run_id} was not found.")
    run.logs.sort(key=lambda log: log.created_at)
    return run_response(run)


@router.get("/{run_id}/logs", response_model=list[PipelineLogResponse])
def get_pipeline_run_logs(run_id: int, db: Session = Depends(get_db_session)) -> list[PipelineLogResponse]:
    repository = PipelineRunRepository(db)
    if repository.get(run_id) is None:
        raise PipelineRunNotFoundError(f"Pipeline run {run_id} was not found.")
    return [log_response(log) for log in repository.list_logs(run_id)]


def run_response(run: PipelineRun) -> PipelineRunResponse:
    request_summary = None
    if getattr(run, "request", None) is not None:
        request_summary = PipelineRunRequestSummary(
            request_id=run.request.request_id,
            pipeline_code=run.request.pipeline_code,
            source_id=run.request.source_id,
            keyword_id=run.request.keyword_id,
        )
    return PipelineRunResponse(
        run_id=run.run_id,
        request_id=run.request_id,
        run_number=run.run_number,
        run_status=run.run_status,
        started_at=run.started_at,
        finished_at=run.finished_at,
        total_count=run.total_count,
        success_count=run.success_count,
        failure_count=run.failure_count,
        skipped_count=run.skipped_count,
        duplicate_count=run.duplicate_count,
        error_code=run.error_code,
        error_message=run.error_message,
        execution_options=load_json(run.execution_options_json),
        worker_id=run.worker_id,
        request=request_summary,
        logs=[log_response(log) for log in getattr(run, "logs", [])],
    )


def log_response(log: PipelineLog) -> PipelineLogResponse:
    return PipelineLogResponse(
        log_id=log.log_id,
        run_id=log.run_id,
        log_level=log.log_level,
        pipeline_step=log.pipeline_step,
        message=log.message,
        detail=load_json(log.detail_json),
        created_at=log.created_at,
    )
