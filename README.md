# Tech Trend Pipeline

뉴스, RSS, 기술 블로그에서 콘텐츠를 수집하고 파이프라인 실행 요청, 실행 이력, 로그, 기사 발견 이력, 본문 수집 작업을 단계별로 관리하기 위한 데이터 파이프라인 프로젝트입니다.

현재 저장소는 두 흐름을 함께 가지고 있습니다.

- 신규 FastAPI + SQLAlchemy 기반 파이프라인 애플리케이션: `app/`
- 기존 Naver News 단일 수집 스크립트: `main.py`, `collectors/`, `processors/`, `database/`

## 현재 구현 범위

- FastAPI 애플리케이션 엔트리포인트
- PostgreSQL Docker Compose 실행 환경
- SQLAlchemy 2.x 모델
- Alembic 초기 migration
- 핵심 Enum 및 도메인 예외
- 파이프라인 실행 요청 API
- Mock 파이프라인 실행, 재실행, 취소 API
- 파이프라인 실행 결과 및 로그 조회 API
- SQLite 기반 모델/API/서비스 테스트

아직 실제 뉴스 API 수집, RSS 수집, 본문 크롤링, AI 초안 생성, 발행 API, Worker/Scheduler는 구현하지 않았습니다.

## 빠른 시작

PowerShell 기준:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
docker compose up -d postgres
alembic upgrade head
uvicorn app.main:app --reload
```

기본 PostgreSQL URL:

```text
postgresql+psycopg://techtrend:techtrend@localhost:5432/techtrend
```

`.env`에 `DATABASE_URL`을 설정하면 해당 값이 우선 사용됩니다.

## 테스트

```powershell
pytest
```

현재 테스트 범위:

- SQLAlchemy 모델 관계와 unique 제약
- 실행 결과 상태 결정
- 처리 건수 합계 검증
- 요청 옵션 병합
- 실행 요청 생성/조회
- Mock 실행 성공/부분 성공/실패
- 실행 로그 생성
- 재실행 정책
- 취소 정책
- API 응답 검증

## 주요 문서

- [프로젝트 구조](docs/project-structure.md)
- [데이터 모델](docs/data-model.md)
- [API 사용법](docs/api.md)
- [파이프라인 실행 정책](docs/pipeline-policy.md)
- [개발 및 운영 메모](docs/development.md)
- [기존 수집 스크립트](docs/legacy-collector.md)

## 핵심 API

```text
GET  /health

POST /api/v1/pipeline-requests
GET  /api/v1/pipeline-requests
GET  /api/v1/pipeline-requests/{request_id}
POST /api/v1/pipeline-requests/{request_id}/execute
POST /api/v1/pipeline-requests/{request_id}/retry
POST /api/v1/pipeline-requests/{request_id}/cancel

GET  /api/v1/pipeline-runs
GET  /api/v1/pipeline-runs/{run_id}
GET  /api/v1/pipeline-runs/{run_id}/logs
```

## 다음 단계

1. `SOURCES`, `SEARCH_KEYWORDS` CRUD API 구현
2. Mock Collector 인터페이스 추가
3. 기사 발견 결과를 `ARTICLES`, `ARTICLE_COLLECTIONS`에 저장
4. 본문 수집 작업 생성 및 상태 관리
