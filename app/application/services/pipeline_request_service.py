from datetime import datetime

from sqlalchemy.orm import Session

from app.application.services.json_utils import JsonDict, dump_json
from app.domain.enums import PipelineRequestStatus, PipelineRequestType
from app.domain.exceptions import (
    CancelNotAllowedError,
    InactiveKeywordError,
    InactiveSourceError,
    PipelineRequestNotFoundError,
)
from app.infrastructure.database.models import PipelineRunRequest
from app.infrastructure.database.repositories.pipeline_request_repository import PipelineRequestRepository
from app.infrastructure.database.repositories.pipeline_run_repository import PipelineRunRepository


class PipelineRequestService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.requests = PipelineRequestRepository(db)
        self.runs = PipelineRunRepository(db)

    def create_request(
        self,
        *,
        pipeline_code: str,
        request_type: PipelineRequestType,
        source_id: int | None,
        keyword_id: int | None,
        requested_by: str | None,
        request_options: JsonDict | None,
    ) -> PipelineRunRequest:
        if source_id is not None:
            source = self.requests.get_source(source_id)
            if source is None or not source.is_active:
                raise InactiveSourceError(f"Source {source_id} does not exist or is inactive.")
        if keyword_id is not None:
            keyword = self.requests.get_keyword(keyword_id)
            if keyword is None or not keyword.is_active:
                raise InactiveKeywordError(f"Keyword {keyword_id} does not exist or is inactive.")

        request = PipelineRunRequest(
            pipeline_code=pipeline_code,
            request_type=request_type,
            source_id=source_id,
            keyword_id=keyword_id,
            requested_by=requested_by,
            request_options_json=dump_json(request_options),
            request_status=PipelineRequestStatus.REQUESTED,
        )
        self.requests.add(request)
        self.db.commit()
        return request

    def list_requests(
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
        return self.requests.list(
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

    def get_request_detail(self, request_id: int) -> PipelineRunRequest:
        request = self.requests.get_with_runs(request_id)
        if request is None:
            raise PipelineRequestNotFoundError(f"Pipeline request {request_id} was not found.")
        request.runs.sort(key=lambda run: (run.run_number, run.started_at or run.created_at))
        return request

    def cancel_request(self, request_id: int) -> PipelineRunRequest:
        request = self.requests.get_for_update(request_id)
        if request is None:
            raise PipelineRequestNotFoundError(f"Pipeline request {request_id} was not found.")
        if request.request_status not in {PipelineRequestStatus.REQUESTED, PipelineRequestStatus.ACCEPTED}:
            raise CancelNotAllowedError(f"Request status {request.request_status} cannot be cancelled.")
        if self.runs.latest_run(request_id) is not None:
            raise CancelNotAllowedError("A request with execution history cannot be cancelled in this stage.")
        request.request_status = PipelineRequestStatus.CANCELLED
        self.db.commit()
        return request
