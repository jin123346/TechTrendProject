import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import Base
from app.domain.enums import (
    ArticleFetchStatus,
    FetchJobStatus,
    FetchRequestType,
    LogLevel,
    PipelineRequestStatus,
    PipelineRequestType,
    PipelineRunStatus,
    SourceType,
)
from app.infrastructure.database import models  # noqa: F401
from app.infrastructure.database.models import (
    Article,
    ArticleCollection,
    ContentFetchJob,
    PipelineLog,
    PipelineRun,
    PipelineRunRequest,
    SearchKeyword,
    Source,
)


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    with Session(engine) as db:
        yield db


def seed_core_graph(session: Session) -> tuple[Source, SearchKeyword, PipelineRunRequest, PipelineRun, Article]:
    source = Source(
        source_code="NAVER_NEWS",
        source_name="Naver News",
        source_type=SourceType.API,
        base_url="https://openapi.naver.com",
    )
    keyword = SearchKeyword(keyword="데이터 파이프라인", normalized_keyword="데이터 파이프라인")
    session.add_all([source, keyword])
    session.flush()

    request = PipelineRunRequest(
        pipeline_code="NEWS_DISCOVERY",
        request_type=PipelineRequestType.MANUAL,
        source_id=source.source_id,
        keyword_id=keyword.keyword_id,
        request_status=PipelineRequestStatus.REQUESTED,
    )
    session.add(request)
    session.flush()

    run = PipelineRun(
        request_id=request.request_id,
        run_number=1,
        run_status=PipelineRunStatus.RUNNING,
    )
    article = Article(
        source_id=source.source_id,
        external_article_id="naver-1",
        title="Pipeline article",
        original_url="https://example.com/article?a=1",
        normalized_url="https://example.com/article?a=1",
        url_hash="a" * 64,
        current_fetch_status=ArticleFetchStatus.DISCOVERED,
    )
    session.add_all([run, article])
    session.flush()
    return source, keyword, request, run, article


def test_core_tables_are_registered() -> None:
    expected_tables = {
        "sources",
        "search_keywords",
        "pipeline_run_requests",
        "pipeline_runs",
        "pipeline_logs",
        "articles",
        "article_collections",
        "content_fetch_jobs",
    }

    assert expected_tables.issubset(Base.metadata.tables.keys())


def test_pipeline_request_to_run_relationship(session: Session) -> None:
    _source, _keyword, request, run, _article = seed_core_graph(session)
    session.commit()

    saved_request = session.get(PipelineRunRequest, request.request_id)

    assert saved_request is not None
    assert saved_request.runs[0].run_id == run.run_id


def test_article_collection_tracks_run_article_and_keyword(session: Session) -> None:
    _source, keyword, _request, run, article = seed_core_graph(session)
    collection = ArticleCollection(
        run_id=run.run_id,
        article_id=article.article_id,
        keyword_id=keyword.keyword_id,
        search_rank=1,
        discovered_title="Discovered title",
    )
    session.add(collection)
    session.commit()

    saved = session.get(ArticleCollection, collection.collection_id)

    assert saved is not None
    assert saved.run.run_id == run.run_id
    assert saved.article.article_id == article.article_id
    assert saved.keyword.keyword_id == keyword.keyword_id


def test_unique_url_hash_prevents_duplicate_articles(session: Session) -> None:
    source, _keyword, _request, _run, _article = seed_core_graph(session)
    duplicate = Article(
        source_id=source.source_id,
        external_article_id="naver-2",
        title="Duplicate",
        original_url="https://example.com/duplicate",
        url_hash="a" * 64,
    )
    session.add(duplicate)

    with pytest.raises(IntegrityError):
        session.commit()


def test_content_fetch_job_attempt_is_unique_per_article(session: Session) -> None:
    _source, _keyword, _request, run, article = seed_core_graph(session)
    session.add_all(
        [
            ContentFetchJob(
                article_id=article.article_id,
                run_id=run.run_id,
                attempt_number=1,
                request_type=FetchRequestType.AUTO,
                fetch_status=FetchJobStatus.PENDING,
            ),
            ContentFetchJob(
                article_id=article.article_id,
                run_id=run.run_id,
                attempt_number=1,
                request_type=FetchRequestType.RETRY,
                fetch_status=FetchJobStatus.PENDING,
            ),
        ]
    )

    with pytest.raises(IntegrityError):
        session.commit()


def test_pipeline_log_references_run(session: Session) -> None:
    _source, _keyword, _request, run, _article = seed_core_graph(session)
    log = PipelineLog(
        run_id=run.run_id,
        log_level=LogLevel.INFO,
        pipeline_step="DISCOVERY",
        message="started",
    )
    session.add(log)
    session.commit()

    saved = session.get(PipelineLog, log.log_id)

    assert saved is not None
    assert saved.run.run_id == run.run_id
