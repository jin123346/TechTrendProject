import pytest

from app.application.services.json_utils import merge_options
from app.application.services.pipeline_execution_service import MockRunResult, PipelineExecutionService
from app.application.services.pipeline_request_service import PipelineRequestService
from app.domain.enums import PipelineRequestStatus, PipelineRequestType, PipelineRunStatus, SourceType
from app.domain.exceptions import (
    CancelNotAllowedError,
    InactiveKeywordError,
    InactiveSourceError,
    InvalidRunResultError,
    PipelineAlreadyRunningError,
    RetryNotAllowedError,
)
from app.infrastructure.database.models import PipelineRun, SearchKeyword, Source


def seed_source_keyword(db_session, *, source_active: bool = True, keyword_active: bool = True):
    source = Source(
        source_code="NAVER_NEWS",
        source_name="Naver News",
        source_type=SourceType.API,
        is_active=source_active,
    )
    keyword = SearchKeyword(keyword="data", normalized_keyword="data", is_active=keyword_active)
    db_session.add_all([source, keyword])
    db_session.commit()
    return source, keyword


def create_request(db_session, request_options=None):
    source, keyword = seed_source_keyword(db_session)
    service = PipelineRequestService(db_session)
    return service.create_request(
        pipeline_code="NEWS_COLLECTION",
        request_type=PipelineRequestType.MANUAL,
        source_id=source.source_id,
        keyword_id=keyword.keyword_id,
        requested_by="tester",
        request_options=request_options
        or {
            "mock_total_count": 10,
            "mock_success_count": 10,
            "mock_failure_count": 0,
            "mock_skipped_count": 0,
            "mock_duplicate_count": 0,
        },
    )


def test_determine_run_status() -> None:
    assert PipelineExecutionService.determine_status(10, 0) == PipelineRunStatus.SUCCESS
    assert PipelineExecutionService.determine_status(8, 1) == PipelineRunStatus.PARTIAL_SUCCESS
    assert PipelineExecutionService.determine_status(0, 2) == PipelineRunStatus.FAILED


def test_validate_result_count_sum() -> None:
    PipelineExecutionService.validate_result_counts(MockRunResult(10, 8, 1, 1, 0))

    with pytest.raises(InvalidRunResultError):
        PipelineExecutionService.validate_result_counts(MockRunResult(10, 8, 1, 0, 0))


def test_merge_options_override_wins() -> None:
    assert merge_options({"mock_success_count": 3, "keep": True}, {"mock_success_count": 5}) == {
        "mock_success_count": 5,
        "keep": True,
    }


def test_create_request_rejects_inactive_source(db_session) -> None:
    source, keyword = seed_source_keyword(db_session, source_active=False)
    service = PipelineRequestService(db_session)

    with pytest.raises(InactiveSourceError):
        service.create_request(
            pipeline_code="NEWS_COLLECTION",
            request_type=PipelineRequestType.MANUAL,
            source_id=source.source_id,
            keyword_id=keyword.keyword_id,
            requested_by="tester",
            request_options={},
        )


def test_create_request_rejects_inactive_keyword(db_session) -> None:
    source, keyword = seed_source_keyword(db_session, keyword_active=False)
    service = PipelineRequestService(db_session)

    with pytest.raises(InactiveKeywordError):
        service.create_request(
            pipeline_code="NEWS_COLLECTION",
            request_type=PipelineRequestType.MANUAL,
            source_id=source.source_id,
            keyword_id=keyword.keyword_id,
            requested_by="tester",
            request_options={},
        )


def test_execute_request_success_creates_logs(db_session) -> None:
    request = create_request(db_session)
    run = PipelineExecutionService(db_session).execute_request(request.request_id)

    assert run.run_number == 1
    assert run.run_status == PipelineRunStatus.SUCCESS
    assert run.total_count == 10
    assert len(run.logs) >= 5


def test_execute_request_partial_success(db_session) -> None:
    request = create_request(
        db_session,
        {
            "mock_total_count": 10,
            "mock_success_count": 8,
            "mock_failure_count": 1,
            "mock_skipped_count": 1,
            "mock_duplicate_count": 0,
        },
    )

    run = PipelineExecutionService(db_session).execute_request(request.request_id)

    assert run.run_status == PipelineRunStatus.PARTIAL_SUCCESS


def test_retry_creates_next_run_number(db_session) -> None:
    request = create_request(
        db_session,
        {
            "mock_total_count": 10,
            "mock_success_count": 8,
            "mock_failure_count": 1,
            "mock_skipped_count": 1,
            "mock_duplicate_count": 0,
        },
    )
    first_run = PipelineExecutionService(db_session).execute_request(request.request_id)

    retry = PipelineExecutionService(db_session).retry_request(
        request.request_id,
        {
            "mock_total_count": 10,
            "mock_success_count": 10,
            "mock_failure_count": 0,
            "mock_skipped_count": 0,
            "mock_duplicate_count": 0,
        },
    )

    assert first_run.run_status == PipelineRunStatus.PARTIAL_SUCCESS
    assert retry.run_number == 2
    assert retry.run_status == PipelineRunStatus.SUCCESS


def test_success_run_retry_is_rejected(db_session) -> None:
    request = create_request(db_session)
    PipelineExecutionService(db_session).execute_request(request.request_id)

    with pytest.raises(RetryNotAllowedError):
        PipelineExecutionService(db_session).retry_request(request.request_id)


def test_cancel_request(db_session) -> None:
    request = create_request(db_session)
    cancelled = PipelineRequestService(db_session).cancel_request(request.request_id)

    assert cancelled.request_status == PipelineRequestStatus.CANCELLED


def test_cancelled_request_cannot_execute(db_session) -> None:
    request = create_request(db_session)
    PipelineRequestService(db_session).cancel_request(request.request_id)

    with pytest.raises(Exception):
        PipelineExecutionService(db_session).execute_request(request.request_id)


def test_cancel_running_request_is_rejected(db_session) -> None:
    request = create_request(db_session)
    PipelineExecutionService(db_session).execute_request(request.request_id)

    with pytest.raises(CancelNotAllowedError):
        PipelineRequestService(db_session).cancel_request(request.request_id)


def test_running_request_cannot_execute_twice(db_session) -> None:
    request = create_request(db_session)
    db_session.add(
        PipelineRun(
            request_id=request.request_id,
            run_number=1,
            run_status=PipelineRunStatus.RUNNING,
        )
    )
    db_session.commit()

    with pytest.raises(PipelineAlreadyRunningError):
        PipelineExecutionService(db_session).execute_request(request.request_id)
