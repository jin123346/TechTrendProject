# 개발 및 운영 메모

## 로컬 실행

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

## 아직 구현하지 않은 범위

- 실제 Naver News API를 신규 파이프라인 서비스에 연결
- RSS Collector
- 기술 블로그 Collector
- 기사 저장 및 `ARTICLE_COLLECTIONS` 생성 서비스
- 본문 수집기와 `CONTENT_FETCH_JOBS` 실행
- 콘텐츠 프로젝트, 키워드 분석, 초안 생성, 발행
- 운영용 Worker/Scheduler
- Celery, Kafka, Airflow
- 관리자 프론트엔드

## 다음 단계

1. `SOURCES`, `SEARCH_KEYWORDS` CRUD API 구현
2. Mock Collector 인터페이스 추가
3. 기사 발견 결과를 `ARTICLES`, `ARTICLE_COLLECTIONS`에 저장
4. 본문 수집 작업 생성 및 상태 관리
