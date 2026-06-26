from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import LogLevel, PipelineRunStatus


class PipelineLogResponse(BaseModel):
    log_id: int
    run_id: int
    log_level: LogLevel
    pipeline_step: str | None
    message: str
    detail: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class PipelineRunRequestSummary(BaseModel):
    request_id: int
    pipeline_code: str
    source_id: int | None
    keyword_id: int | None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class PipelineRunResponse(BaseModel):
    run_id: int
    request_id: int
    run_number: int
    run_status: PipelineRunStatus
    started_at: datetime | None
    finished_at: datetime | None
    total_count: int
    success_count: int
    failure_count: int
    skipped_count: int
    duplicate_count: int
    error_code: str | None
    error_message: str | None
    execution_options: dict[str, Any] = Field(default_factory=dict)
    worker_id: str | None
    request: PipelineRunRequestSummary | None = None
    logs: list[PipelineLogResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class PipelineRunListResponse(BaseModel):
    items: list[PipelineRunResponse]
    page: int
    page_size: int
    total: int
