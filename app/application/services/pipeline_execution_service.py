import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.services.json_utils import JsonDict, dump_json, load_json, merge_options
from app.domain.enums import LogLevel, PipelineRequestStatus, PipelineRunStatus
from app.domain.exceptions import (
    InvalidRequestStatusError,
    InvalidRunResultError,
    PipelineAlreadyRunningError,
    PipelineRequestNotFoundError,
    RetryNotAllowedError,
)
from app.infrastructure.database.models import PipelineLog, PipelineRun
from app.infrastructure.database.repositories.pipeline_request_repository import PipelineRequestRepository
from app.infrastructure.database.repositories.pipeline_run_repository import PipelineRunRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MockRunResult:
    total_count: int
    success_count: int
    failure_count: int
    skipped_count: int
    duplicate_count: int


class PipelineExecutionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.requests = PipelineRequestRepository(db)
        self.runs = PipelineRunRepository(db)

    def execute_request(self, request_id: int, options_override: JsonDict | None = None) -> PipelineRun:
        request = self.requests.get_for_update(request_id)
        if request is None:
            raise PipelineRequestNotFoundError(f"Pipeline request {request_id} was not found.")
        self._validate_executable_request(request.request_status)
        if self.runs.has_running_run(request_id):
            raise PipelineAlreadyRunningError(f"Pipeline request {request_id} already has a running run.")

        options = merge_options(load_json(request.request_options_json), options_override)
        run = self._create_running_run(request.request_id, options)
        request.request_status = PipelineRequestStatus.ACCEPTED
        self.db.commit()

        return self._perform_mock_run(run.run_id, options)

    def retry_request(self, request_id: int, options_override: JsonDict | None = None) -> PipelineRun:
        request = self.requests.get_for_update(request_id)
        if request is None:
            raise PipelineRequestNotFoundError(f"Pipeline request {request_id} was not found.")
        latest_run = self.runs.latest_run(request_id)
        if latest_run is None or latest_run.run_status not in {
            PipelineRunStatus.FAILED,
            PipelineRunStatus.PARTIAL_SUCCESS,
        }:
            raise RetryNotAllowedError("Only FAILED or PARTIAL_SUCCESS runs can be retried.")
        if self.runs.has_running_run(request_id):
            raise PipelineAlreadyRunningError(f"Pipeline request {request_id} already has a running run.")

        options = merge_options(load_json(request.request_options_json), options_override)
        run = self._create_running_run(request.request_id, options)
        self._log(
            run.run_id,
            LogLevel.INFO,
            "REQUEST_VALIDATION",
            "재실행을 시작했습니다.",
            {"previous_run_id": latest_run.run_id, "options_override": options_override or {}},
        )
        self.db.commit()

        return self._perform_mock_run(run.run_id, options)

    def _create_running_run(self, request_id: int, options: JsonDict) -> PipelineRun:
        run = PipelineRun(
            request_id=request_id,
            run_number=self.runs.next_run_number(request_id),
            run_status=PipelineRunStatus.RUNNING,
            started_at=self._now(),
            execution_options_json=dump_json(options),
        )
        try:
            return self.runs.add(run)
        except IntegrityError as error:
            self.db.rollback()
            raise PipelineAlreadyRunningError("A duplicate run number was created concurrently.") from error

    def _perform_mock_run(self, run_id: int, options: JsonDict) -> PipelineRun:
        run = self.runs.get(run_id)
        if run is None:
            raise RuntimeError(f"Created pipeline run {run_id} disappeared.")

        try:
            self._log(run.run_id, LogLevel.INFO, "REQUEST_VALIDATION", "실행 요청 검증을 시작했습니다.")
            self._log(run.run_id, LogLevel.INFO, "REQUEST_VALIDATION", "실행 요청 검증이 완료되었습니다.")
            self._log(run.run_id, LogLevel.INFO, "MOCK_COLLECTION", "Mock 데이터 수집을 시작했습니다.")

            result = self.build_mock_result(options)
            if result.failure_count > 0:
                self._log(
                    run.run_id,
                    LogLevel.WARNING,
                    "MOCK_COLLECTION",
                    "일부 데이터 처리에 실패했습니다.",
                    {"failure_count": result.failure_count},
                )

            self._log(
                run.run_id,
                LogLevel.INFO,
                "RESULT_AGGREGATION",
                "처리 결과 집계가 완료되었습니다.",
                self._result_detail(result),
            )
            self._finish_run(run, result)
            self._log(run.run_id, LogLevel.INFO, "COMPLETED", "파이프라인 실행이 완료되었습니다.", self._result_detail(result))
            self.db.commit()
            logger.info("Pipeline run completed", extra={"run_id": run.run_id, "status": run.run_status})
            return run
        except Exception as error:
            self.db.rollback()
            failed_run = self.runs.get(run_id)
            if failed_run is not None:
                failed_run.run_status = PipelineRunStatus.FAILED
                failed_run.finished_at = self._now()
                failed_run.error_code = type(error).__name__
                failed_run.error_message = str(error)
                self._log(
                    failed_run.run_id,
                    LogLevel.ERROR,
                    "FAILED",
                    "파이프라인 실행 중 오류가 발생했습니다.",
                    {"error_type": type(error).__name__, "error_message": str(error)},
                )
                self.db.commit()
            raise

    def _finish_run(self, run: PipelineRun, result: MockRunResult) -> None:
        status = self.determine_status(result.success_count, result.failure_count)
        run.total_count = result.total_count
        run.success_count = result.success_count
        run.failure_count = result.failure_count
        run.skipped_count = result.skipped_count
        run.duplicate_count = result.duplicate_count
        run.run_status = status
        run.finished_at = self._now()

    def _validate_executable_request(self, status: PipelineRequestStatus | str) -> None:
        if status not in {PipelineRequestStatus.REQUESTED, PipelineRequestStatus.ACCEPTED}:
            raise InvalidRequestStatusError(f"Request status {status} cannot be executed.")

    def _log(
        self,
        run_id: int,
        level: LogLevel,
        step: str,
        message: str,
        detail: JsonDict | None = None,
    ) -> None:
        logger.log(
            logging.WARNING if level == LogLevel.WARNING else logging.INFO,
            "%s - %s",
            step,
            message,
            extra={"run_id": run_id, "detail": detail or {}},
        )
        self.runs.add_log(
            PipelineLog(
                run_id=run_id,
                log_level=level,
                pipeline_step=step,
                message=message,
                detail_json=dump_json(detail),
            )
        )

    @classmethod
    def build_mock_result(cls, options: JsonDict | None) -> MockRunResult:
        options = options or {}
        result = MockRunResult(
            total_count=cls._int_option(options, "mock_total_count", 10),
            success_count=cls._int_option(options, "mock_success_count", 10),
            failure_count=cls._int_option(options, "mock_failure_count", 0),
            skipped_count=cls._int_option(options, "mock_skipped_count", 0),
            duplicate_count=cls._int_option(options, "mock_duplicate_count", 0),
        )
        cls.validate_result_counts(result)
        return result

    @staticmethod
    def validate_result_counts(result: MockRunResult) -> None:
        values = [
            result.total_count,
            result.success_count,
            result.failure_count,
            result.skipped_count,
            result.duplicate_count,
        ]
        if any(value < 0 for value in values):
            raise InvalidRunResultError("Run result counts cannot be negative.")
        expected_total = result.success_count + result.failure_count + result.skipped_count + result.duplicate_count
        if result.total_count != expected_total:
            raise InvalidRunResultError("TOTAL_COUNT must equal success + failure + skipped + duplicate.")

    @staticmethod
    def determine_status(success_count: int, failure_count: int) -> PipelineRunStatus:
        if failure_count == 0:
            return PipelineRunStatus.SUCCESS
        if success_count > 0 and failure_count > 0:
            return PipelineRunStatus.PARTIAL_SUCCESS
        if success_count == 0 and failure_count > 0:
            return PipelineRunStatus.FAILED
        return PipelineRunStatus.SUCCESS

    @staticmethod
    def _int_option(options: dict[str, Any], key: str, default: int) -> int:
        value = options.get(key, default)
        if not isinstance(value, int):
            raise InvalidRunResultError(f"{key} must be an integer.")
        return value

    @staticmethod
    def _result_detail(result: MockRunResult) -> JsonDict:
        return {
            "total_count": result.total_count,
            "success_count": result.success_count,
            "failure_count": result.failure_count,
            "skipped_count": result.skipped_count,
            "duplicate_count": result.duplicate_count,
        }

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)
