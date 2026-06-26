# 데이터 모델

현재 SQLAlchemy와 Alembic으로 구현된 핵심 테이블은 다음과 같습니다.

```text
SOURCES
SEARCH_KEYWORDS
PIPELINE_RUN_REQUESTS
PIPELINE_RUNS
PIPELINE_LOGS
ARTICLES
ARTICLE_COLLECTIONS
CONTENT_FETCH_JOBS
```

## 주요 관계

```text
SOURCES 1:N PIPELINE_RUN_REQUESTS
SOURCES 1:N ARTICLES
SEARCH_KEYWORDS 1:N PIPELINE_RUN_REQUESTS
SEARCH_KEYWORDS 1:N ARTICLE_COLLECTIONS
PIPELINE_RUN_REQUESTS 1:N PIPELINE_RUNS
PIPELINE_RUNS 1:N PIPELINE_LOGS
PIPELINE_RUNS 1:N ARTICLE_COLLECTIONS
PIPELINE_RUNS 1:N CONTENT_FETCH_JOBS
ARTICLES 1:N ARTICLE_COLLECTIONS
ARTICLES 1:N CONTENT_FETCH_JOBS
```

## 주요 제약조건

- `sources.source_code` unique
- `search_keywords.keyword` unique
- `pipeline_runs(request_id, run_number)` unique
- `articles.url_hash` unique
- `articles(source_id, external_article_id)` unique
- `article_collections(run_id, article_id, keyword_id)` unique
- `content_fetch_jobs(article_id, attempt_number)` unique

## Migration

초기 migration:

```text
alembic/versions/20260625_0001_initial_core_tables.py
```

적용:

```powershell
alembic upgrade head
```
