from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db_session
from app.core.database import Base
from app.domain.enums import SourceType
from app.infrastructure.database import models  # noqa: F401
from app.infrastructure.database.models import SearchKeyword, Source
from app.main import app


def build_client() -> tuple[TestClient, Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session = Session(engine)

    def override_db():
        yield session

    app.dependency_overrides[get_db_session] = override_db
    return TestClient(app), session


def seed_source_keyword(session: Session, *, source_active: bool = True, keyword_active: bool = True):
    source = Source(
        source_code="NAVER_NEWS",
        source_name="Naver News",
        source_type=SourceType.API,
        is_active=source_active,
    )
    keyword = SearchKeyword(keyword="data", normalized_keyword="data", is_active=keyword_active)
    session.add_all([source, keyword])
    session.commit()
    return source, keyword


def create_request(client: TestClient, source_id: int, keyword_id: int, options=None):
    return client.post(
        "/api/v1/pipeline-requests",
        json={
            "pipeline_code": "NEWS_COLLECTION",
            "request_type": "MANUAL",
            "source_id": source_id,
            "keyword_id": keyword_id,
            "requested_by": "admin",
            "request_options": options
            or {
                "mock_total_count": 10,
                "mock_success_count": 10,
                "mock_failure_count": 0,
                "mock_skipped_count": 0,
                "mock_duplicate_count": 0,
            },
        },
    )


def test_create_list_detail_execute_and_logs() -> None:
    client, session = build_client()
    source, keyword = seed_source_keyword(session)

    created = create_request(client, source.source_id, keyword.keyword_id)
    assert created.status_code == 201
    request_id = created.json()["request_id"]

    listed = client.get("/api/v1/pipeline-requests", params={"pipeline_code": "NEWS_COLLECTION"})
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    executed = client.post(f"/api/v1/pipeline-requests/{request_id}/execute")
    assert executed.status_code == 200
    run_body = executed.json()
    assert run_body["run_status"] == "SUCCESS"
    assert run_body["run_number"] == 1

    detail = client.get(f"/api/v1/pipeline-requests/{request_id}")
    assert detail.status_code == 200
    assert len(detail.json()["runs"]) == 1

    run_id = run_body["run_id"]
    run_detail = client.get(f"/api/v1/pipeline-runs/{run_id}")
    assert run_detail.status_code == 200
    assert len(run_detail.json()["logs"]) >= 5

    logs = client.get(f"/api/v1/pipeline-runs/{run_id}/logs")
    assert logs.status_code == 200
    assert logs.json()[0]["pipeline_step"] == "REQUEST_VALIDATION"

    app.dependency_overrides.clear()
    session.close()


def test_create_request_rejects_missing_source() -> None:
    client, session = build_client()
    _source, keyword = seed_source_keyword(session)

    response = create_request(client, 999, keyword.keyword_id)

    assert response.status_code == 422
    assert response.json()["error_code"] == "INACTIVE_SOURCE"

    app.dependency_overrides.clear()
    session.close()


def test_cancel_and_execute_cancelled_request() -> None:
    client, session = build_client()
    source, keyword = seed_source_keyword(session)
    request_id = create_request(client, source.source_id, keyword.keyword_id).json()["request_id"]

    cancelled = client.post(f"/api/v1/pipeline-requests/{request_id}/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["request_status"] == "CANCELLED"

    executed = client.post(f"/api/v1/pipeline-requests/{request_id}/execute")
    assert executed.status_code == 409

    app.dependency_overrides.clear()
    session.close()


def test_failed_run_can_retry_with_override() -> None:
    client, session = build_client()
    source, keyword = seed_source_keyword(session)
    created = create_request(
        client,
        source.source_id,
        keyword.keyword_id,
        {
            "mock_total_count": 10,
            "mock_success_count": 0,
            "mock_failure_count": 10,
            "mock_skipped_count": 0,
            "mock_duplicate_count": 0,
        },
    )
    request_id = created.json()["request_id"]

    failed = client.post(f"/api/v1/pipeline-requests/{request_id}/execute")
    assert failed.json()["run_status"] == "FAILED"

    retry = client.post(
        f"/api/v1/pipeline-requests/{request_id}/retry",
        json={
            "request_options_override": {
                "mock_total_count": 10,
                "mock_success_count": 10,
                "mock_failure_count": 0,
                "mock_skipped_count": 0,
                "mock_duplicate_count": 0,
            }
        },
    )
    assert retry.status_code == 200
    assert retry.json()["run_number"] == 2
    assert retry.json()["run_status"] == "SUCCESS"

    app.dependency_overrides.clear()
    session.close()
