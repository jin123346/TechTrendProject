# 프로젝트 구조

현재 실제 폴더 구조는 다음과 같습니다.

```text
techtrendProject/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── dependencies.py
│   │   └── v1/
│   │       ├── routers/
│   │       │   ├── pipeline_requests.py
│   │       │   └── pipeline_runs.py
│   │       └── schemas/
│   │           ├── common.py
│   │           ├── pipeline_requests.py
│   │           └── pipeline_runs.py
│   ├── application/
│   │   └── services/
│   │       ├── json_utils.py
│   │       ├── pipeline_execution_service.py
│   │       └── pipeline_request_service.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── domain/
│   │   ├── exceptions.py
│   │   └── enums/
│   │       ├── article.py
│   │       ├── common.py
│   │       ├── fetch_job.py
│   │       └── pipeline.py
│   └── infrastructure/
│       └── database/
│           ├── session.py
│           ├── models/
│           │   ├── article.py
│           │   ├── article_collection.py
│           │   ├── content_fetch_job.py
│           │   ├── mixins.py
│           │   ├── pipeline_log.py
│           │   ├── pipeline_run.py
│           │   ├── pipeline_run_request.py
│           │   ├── search_keyword.py
│           │   └── source.py
│           └── repositories/
│               ├── pipeline_request_repository.py
│               └── pipeline_run_repository.py
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 20260625_0001_initial_core_tables.py
├── collectors/
│   └── naver_news.py
├── database/
│   ├── connection.py
│   ├── articles.sql
│   ├── oracle/
│   │   ├── articles.sql
│   │   └── oracle_schema.sql
│   ├── postgre/
│   │   └── postgre_schema.sql
│   └── repositories/
│       └── articles_repository.py
├── processors/
│   └── nomalizer.py
├── tests/
│   ├── conftest.py
│   ├── test_core_models.py
│   ├── test_pipeline_api.py
│   └── test_pipeline_services.py
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
├── main.py
├── DB_정의서.xlsx
└── README.md
```

## 주요 디렉터리 역할

| 경로 | 역할 |
| --- | --- |
| `app/` | 신규 FastAPI 애플리케이션 |
| `app/api/` | HTTP Router, API Schema, 의존성 |
| `app/application/services/` | 비즈니스 흐름과 트랜잭션 경계 |
| `app/domain/` | Enum, 도메인 예외 |
| `app/infrastructure/database/models/` | SQLAlchemy 모델 |
| `app/infrastructure/database/repositories/` | DB 조회/저장/페이지네이션 |
| `alembic/` | DB migration |
| `tests/` | 모델, 서비스, API 테스트 |
| `collectors/`, `processors/`, `database/` | 기존 Naver News 수집 스크립트 계층 |
