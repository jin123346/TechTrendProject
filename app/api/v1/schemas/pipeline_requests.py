from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.schemas.pipeline_runs import PipelineRunResponse
from app.domain.enums import PipelineRequestStatus, PipelineRequestType


class PipelineRequestCreate(BaseModel):
    pipeline_code: str = Field(min_length=1, max_length=100, examples=["NEWS_COLLECTION"])
    request_type: PipelineRequestType
    source_id: int | None = None
    keyword_id: int | None = None
    requested_by: str | None = Field(default=None, max_length=100)
    request_options: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(use_enum_values=True)


class PipelineRetryRequest(BaseModel):
    request_options_override: dict[str, Any] = Field(default_factory=dict)


class PipelineRequestResponse(BaseModel):
    request_id: int
    pipeline_code: str
    request_type: PipelineRequestType
    request_status: PipelineRequestStatus
    source_id: int | None
    keyword_id: int | None
    requested_by: str | None
    requested_at: datetime
    request_options: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class PipelineRequestDetailResponse(PipelineRequestResponse):
    runs: list[PipelineRunResponse] = Field(default_factory=list)


class PipelineRequestListResponse(BaseModel):
    items: list[PipelineRequestResponse]
    page: int
    page_size: int
    total: int
