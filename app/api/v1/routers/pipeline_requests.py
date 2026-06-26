from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.api.v1.schemas.common import clamp_page_size
from app.api.v1.schemas.pipeline_requests import (
    PipelineRequestCreate,
    PipelineRequestDetailResponse,
    PipelineRequestListResponse,
    PipelineRequestResponse,
    PipelineRetryRequest,
)
from app.api.v1.schemas.pipeline_runs import PipelineRunResponse
from app.application.services.json_utils import load_json
from app.application.services.pipeline_execution_service import PipelineExecutionService
from app.application.services.pipeline_request_service import PipelineRequestService
from app.domain.enums import PipelineRequestStatus, PipelineRequestType
from app.infrastructure.database.models import PipelineRunRequest

router = APIRouter(prefix="/api/v1/pipeline-requests", tags=["pipeline-requests"])


@router.post("", response_model=PipelineRequestResponse, status_code=status.HTTP_201_CREATED)
def create_pipeline_request(payload: PipelineRequestCreate, db: Session = Depends(get_db_session)) -> PipelineRequestResponse:
    service = PipelineRequestService(db)
    request = service.create_request(
        pipeline_code=payload.pipeline_code,
        request_type=PipelineRequestType(payload.request_type),
        source_id=payload.source_id,
        keyword_id=payload.keyword_id,
        requested_by=payload.requested_by,
        request_options=payload.request_options,
    )
    return _request_response(request)


@router.get("", response_model=PipelineRequestListResponse)
def list_pipeline_requests(
    pipeline_code: str | None = None,
    request_type: PipelineRequestType | None = None,
    request_status: PipelineRequestStatus | None = None,
    source_id: int | None = None,
    keyword_id: int | None = None,
    requested_from: datetime | None = None,
    requested_to: datetime | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db_session),
) -> PipelineRequestListResponse:
    page_size = clamp_page_size(page_size)
    service = PipelineRequestService(db)
    items, total = service.list_requests(
        pipeline_code=pipeline_code,
        request_type=request_type,
        request_status=request_status,
        source_id=source_id,
        keyword_id=keyword_id,
        requested_from=requested_from,
        requested_to=requested_to,
        page=page,
        page_size=page_size,
    )
    return PipelineRequestListResponse(
        items=[_request_response(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{request_id}", response_model=PipelineRequestDetailResponse)
def get_pipeline_request(request_id: int, db: Session = Depends(get_db_session)) -> PipelineRequestDetailResponse:
    service = PipelineRequestService(db)
    request = service.get_request_detail(request_id)
    response = _request_response(request).model_dump()
    response["runs"] = [_run_response(run) for run in request.runs]
    return PipelineRequestDetailResponse(**response)


@router.post("/{request_id}/execute", response_model=PipelineRunResponse)
def execute_pipeline_request(request_id: int, db: Session = Depends(get_db_session)) -> PipelineRunResponse:
    service = PipelineExecutionService(db)
    run = service.execute_request(request_id)
    return _run_response(run)


@router.post("/{request_id}/retry", response_model=PipelineRunResponse)
def retry_pipeline_request(
    request_id: int,
    payload: PipelineRetryRequest | None = None,
    db: Session = Depends(get_db_session),
) -> PipelineRunResponse:
    service = PipelineExecutionService(db)
    run = service.retry_request(request_id, (payload or PipelineRetryRequest()).request_options_override)
    return _run_response(run)


@router.post("/{request_id}/cancel", response_model=PipelineRequestResponse)
def cancel_pipeline_request(request_id: int, db: Session = Depends(get_db_session)) -> PipelineRequestResponse:
    service = PipelineRequestService(db)
    request = service.cancel_request(request_id)
    return _request_response(request)


def _request_response(request: PipelineRunRequest) -> PipelineRequestResponse:
    return PipelineRequestResponse(
        request_id=request.request_id,
        pipeline_code=request.pipeline_code,
        request_type=request.request_type,
        request_status=request.request_status,
        source_id=request.source_id,
        keyword_id=request.keyword_id,
        requested_by=request.requested_by,
        requested_at=request.requested_at,
        request_options=load_json(request.request_options_json),
    )


def _run_response(run) -> PipelineRunResponse:
    from app.api.v1.routers.pipeline_runs import run_response

    return run_response(run)
