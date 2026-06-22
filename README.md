# Tech Trend Pipeline

네이버 뉴스, RSS 피드, 개발자 블로그 등 여러 소스에서 기술 관련 콘텐츠를 수집하고, 이를 정제·분석하여 테크 트렌드를 제공하는 데이터 파이프라인 프로젝트입니다.

수집한 기사 데이터는 PostgreSQL에 중복 없이 저장하며, 향후 Airflow, dbt, Kafka, Spark, Vector DB 및 LLM을 활용한 자동화된 트렌드 분석·콘텐츠 발행 플랫폼으로 확장하는 것을 목표로 합니다.

---

## 1. 프로젝트 배경

기술 트렌드를 파악하기 위해서는 뉴스, 기술 블로그, IT 미디어 등 여러 채널을 반복적으로 확인해야 합니다.

하지만 동일한 주제의 기사가 여러 매체에서 중복으로 발행되고, 데이터의 형식과 제공 방식도 소스마다 다르기 때문에 일관된 기준으로 분석하기 어렵습니다.

이 프로젝트는 다음 문제를 해결하기 위해 시작했습니다.

- 여러 데이터 소스에 흩어진 기술 콘텐츠 자동 수집
- 데이터 소스별로 다른 응답 형식 표준화
- 동일 기사 중복 저장 방지
- 날짜별·키워드별 기술 트렌드 분석
- 데이터 파이프라인 실패 기록 및 재처리
- 분석 결과를 기반으로 한 콘텐츠 생성 및 발행 자동화

---

## 2. 현재 개발 범위

현재는 전체 프로젝트 중 첫 번째 MVP를 개발하고 있습니다.

### MVP 목표

> 네이버 뉴스 API에서 기술 관련 기사를 수집하고, 정규화한 데이터를 PostgreSQL에 중복 없이 저장한다.

현재 구현 대상은 다음과 같습니다.

- 네이버 뉴스 API 연동
- 검색 키워드 기반 기사 수집
- HTML 태그 및 특수문자 제거
- 기사 데이터 공통 형식 변환
- PostgreSQL 테이블 자동 생성
- 기사 URL 기반 중복 저장 방지
- 수집 결과 및 오류 로그 기록

---

## 3. 전체 아키텍처

### 현재 MVP 아키텍처

```text
Naver News API
       ↓
Python Collector
       ↓
Data Normalizer
       ↓
PostgreSQL
```

### 향후 확장 아키텍처

```text
Naver News API / RSS / Tech Blogs
                ↓
           Airflow DAG
                ↓
         Python Collectors
                ↓
             Kafka
                ↓
   Spark Structured Streaming
                ↓
      Object Storage / Parquet
                ↓
        PostgreSQL + dbt
                ↓
      Keyword Data Mart
                ↓
      Dashboard / Vector DB
                ↓
          LLM + Blog API
```

---

## 4. 주요 기능

### 4.1 뉴스 데이터 수집

네이버 뉴스 검색 API를 사용하여 지정한 검색어에 대한 최신 뉴스를 수집합니다.

수집 항목은 다음과 같습니다.

| 항목             | 설명                      |
| ---------------- | ------------------------- |
| `source`         | 데이터 수집 소스          |
| `source_name`    | 기사 제공 매체            |
| `title`          | 기사 제목                 |
| `description`    | 기사 요약                 |
| `original_url`   | 원문 기사 URL             |
| `published_at`   | 기사 발행 시각            |
| `collected_at`   | 데이터 수집 시각          |
| `search_keyword` | 뉴스 검색에 사용한 키워드 |
| `content_hash`   | 콘텐츠 중복 확인용 해시   |

### 4.2 데이터 정규화

수집 소스마다 다른 데이터 형식을 하나의 공통 기사 스키마로 변환합니다.

네이버 뉴스 API 응답에 포함된 `<b>` 태그와 HTML 특수문자를 제거하고, 발행일 형식을 PostgreSQL에서 사용할 수 있는 날짜 형식으로 변환합니다.

### 4.3 중복 데이터 방지

동일한 수집 작업을 여러 번 실행해도 같은 기사가 중복 저장되지 않도록 처리합니다.

현재는 `original_url` 컬럼에 `UNIQUE` 제약조건을 설정하고, PostgreSQL의 `ON CONFLICT DO NOTHING` 구문을 사용합니다.

```sql
INSERT INTO articles (...)
VALUES (...)
ON CONFLICT (original_url)
DO NOTHING;
```

향후에는 URL이 다르지만 내용이 동일하거나 유사한 기사도 탐지할 수 있도록 콘텐츠 해시와 문서 유사도 비교 기능을 추가할 예정입니다.

### 4.4 데이터베이스 자동 초기화

애플리케이션 실행 시 `articles` 테이블이 존재하지 않으면 자동으로 생성합니다.

```sql
CREATE TABLE IF NOT EXISTS articles (
    article_id BIGSERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    source_name VARCHAR(200),
    title TEXT NOT NULL,
    description TEXT,
    original_url TEXT NOT NULL,
    published_at TIMESTAMPTZ,
    collected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    search_keyword VARCHAR(100),
    content_hash VARCHAR(64),
    CONSTRAINT uq_articles_url UNIQUE (original_url)
);
```

---

## 5. 기술 스택

### 현재 사용 기술

| 구분                  | 기술          |
| --------------------- | ------------- |
| Language              | Python 3.10   |
| Database              | PostgreSQL    |
| HTTP Client           | Requests      |
| PostgreSQL Driver     | psycopg 3     |
| Environment Variables | python-dotenv |
| Version Control       | Git, GitHub   |

### 향후 도입 예정

| 구분                   | 기술                           |
| ---------------------- | ------------------------------ |
| Workflow Orchestration | Apache Airflow                 |
| Data Transformation    | dbt                            |
| Message Broker         | Apache Kafka                   |
| Stream Processing      | Apache Spark                   |
| Storage                | Parquet, MinIO 또는 S3         |
| Dashboard              | Streamlit 또는 Apache Superset |
| Vector Database        | Qdrant 또는 Chroma             |
| Content Generation     | LLM API                        |

향후 기술은 실제 데이터 처리량과 기능 요구사항에 따라 단계적으로 도입할 예정입니다.

---

## 6. 프로젝트 구조

```text
techtrendProject/
├── collectors/
│   ├── __init__.py
│   ├── naver_news.py
│   └── rss_collector.py
├── processors/
│   ├── __init__.py
│   ├── normalizer.py
│   └── deduplicator.py
├── database/
│   ├── __init__.py
│   ├── connection.py
│   └── schema.sql
├── logs/
├── tests/
├── .env
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

### 디렉터리 설명

| 경로          | 설명                           |
| ------------- | ------------------------------ |
| `collectors/` | 외부 API 및 RSS 데이터 수집    |
| `processors/` | 텍스트 정제, 표준화, 중복 판별 |
| `database/`   | PostgreSQL 연결 및 스키마 관리 |
| `logs/`       | 수집 및 오류 로그 저장         |
| `tests/`      | 단위 테스트 및 통합 테스트     |
| `main.py`     | 전체 수집 프로세스 실행 진입점 |

---

## 7. 실행 환경 구성

### 7.1 프로젝트 이동

```cmd
cd D:\techtrendProject
```

### 7.2 가상환경 생성

```cmd
python -m venv .venv
```

### 7.3 가상환경 활성화

Windows CMD:

```cmd
.venv\Scripts\activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

가상환경이 활성화되면 명령 프롬프트 앞에 `(.venv)`가 표시됩니다.

```text
(.venv) D:\techtrendProject>
```

### 7.4 패키지 설치

```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

현재 필요한 패키지는 다음과 같습니다.

```text
requests
python-dotenv
psycopg[binary]
```

`requirements.txt`가 아직 없다면 다음 명령어로 직접 설치할 수 있습니다.

```cmd
python -m pip install requests python-dotenv "psycopg[binary]"
```

설치 후 현재 환경의 패키지를 저장합니다.

```cmd
python -m pip freeze > requirements.txt
```

---

## 8. 환경변수 설정

프로젝트 최상위 경로에 `.env` 파일을 생성합니다.

```env
NAVER_CLIENT_ID=네이버_API_클라이언트_ID
NAVER_CLIENT_SECRET=네이버_API_클라이언트_SECRET

DATABASE_URL=postgresql://postgres:비밀번호@localhost:5432/tech_trend
```

예시:

```env
NAVER_CLIENT_ID=example_client_id
NAVER_CLIENT_SECRET=example_client_secret

DATABASE_URL=postgresql://postgres:1234@localhost:5432/tech_trend
```

`.env` 파일에는 API 키와 데이터베이스 비밀번호가 포함되므로 Git 저장소에 업로드하면 안 됩니다.

`.gitignore`에 다음 내용을 추가합니다.

```gitignore
.env
.venv/
__pycache__/
*.pyc
logs/*.log
```

---

## 9. PostgreSQL 데이터베이스 준비

현재 프로그램은 `articles` 테이블이 존재하지 않으면 자동으로 생성하지만, PostgreSQL 데이터베이스 자체는 미리 생성해야 합니다.

PostgreSQL에서 다음 SQL을 실행합니다.

```sql
CREATE DATABASE tech_trend;
```

데이터베이스 생성 후 `.env`의 `DATABASE_URL`이 실제 접속 정보와 일치하는지 확인합니다.

---

## 10. 데이터베이스 초기화

다음 명령어를 실행하면 `database/schema.sql`을 읽어 필요한 테이블을 생성합니다.

```cmd
python database\connection.py
```

정상 실행 결과:

```text
데이터베이스 초기화가 완료되었습니다.
```

테이블이 이미 존재하는 경우에는 기존 테이블을 삭제하거나 다시 생성하지 않습니다.

> `CREATE TABLE IF NOT EXISTS`는 기존 테이블에 새로운 컬럼을 자동으로 추가하지 않습니다. 향후 스키마 변경 관리를 위해 Alembic 도입을 검토할 예정입니다.

---

## 11. 뉴스 수집 실행

네이버 뉴스 API 수집 테스트:

```cmd
python collectors\naver_news.py
```

전체 수집 프로세스 실행:

```cmd
python main.py
```

초기 테스트에서는 하나의 검색 키워드와 소량의 데이터를 사용합니다.

```text
검색 키워드: 인공지능
수집 건수: 10건
정렬 기준: 최신순
```

---

## 12. 데이터 확인

수집된 데이터는 다음 SQL로 확인할 수 있습니다.

```sql
SELECT
    article_id,
    source,
    title,
    original_url,
    published_at,
    collected_at,
    search_keyword
FROM articles
ORDER BY collected_at DESC;
```

날짜와 검색어별 수집 건수는 다음 SQL로 조회합니다.

```sql
SELECT
    DATE(collected_at) AS collected_date,
    source,
    search_keyword,
    COUNT(*) AS article_count
FROM articles
GROUP BY
    DATE(collected_at),
    source,
    search_keyword
ORDER BY collected_date DESC;
```

---

## 13. 중복 저장 테스트

수집기를 동일한 조건으로 두 번 실행합니다.

```cmd
python main.py
python main.py
```

`original_url`이 동일한 기사는 두 번째 실행에서 추가로 저장되지 않아야 합니다.

```sql
SELECT
    original_url,
    COUNT(*) AS duplicate_count
FROM articles
GROUP BY original_url
HAVING COUNT(*) > 1;
```

조회 결과가 없다면 URL 기준 중복 방지가 정상적으로 동작한 것입니다.

---

## 14. 개발 로드맵

### Phase 1. 기본 수집 파이프라인

- [ ] 네이버 뉴스 API 연동
- [ ] 기사 데이터 정규화
- [ ] PostgreSQL 연결
- [ ] `articles` 테이블 자동 생성
- [ ] 기사 데이터 저장
- [ ] URL 기준 중복 방지
- [ ] 수집 성공·실패 로그 기록
- [ ] 기본 테스트 작성

### Phase 2. 수집 소스 확장

- [ ] IT 미디어 RSS 수집
- [ ] 주요 개발자 블로그 수집
- [ ] 수집 소스별 어댑터 구조 적용
- [ ] 공통 기사 스키마 정의
- [ ] Raw JSON 원본 보관
- [ ] 콘텐츠 해시 기반 중복 판별

### Phase 3. 워크플로우 자동화

- [ ] Airflow 환경 구성
- [ ] 뉴스 수집 DAG 작성
- [ ] 증분 수집 적용
- [ ] 실패 작업 재시도
- [ ] Backfill 및 재처리 구현
- [ ] 파이프라인 실행 이력 저장

### Phase 4. 데이터 마트 및 품질 관리

- [ ] 키워드 추출
- [ ] 불용어 처리
- [ ] 일별 키워드 집계
- [ ] 급상승 키워드 계산
- [ ] 매체별 트렌드 분석
- [ ] dbt 모델 구성
- [ ] dbt Test를 활용한 데이터 검증
- [ ] 데이터 Lineage 관리

### Phase 5. 성능 최적화

- [ ] 대용량 테스트 데이터 구성
- [ ] 실행계획 분석
- [ ] 단일·복합 인덱스 비교
- [ ] 조인 방식별 성능 비교
- [ ] 파티셔닝 적용 검토
- [ ] 집계 쿼리 Before & After 측정

### Phase 6. 스트리밍 확장

- [ ] Kafka Producer 구현
- [ ] Kafka Consumer 구현
- [ ] Dead Letter Queue 구성
- [ ] 이벤트 스키마 버전 관리
- [ ] Spark Structured Streaming 연동
- [ ] Parquet 기반 데이터 적재

### Phase 7. 트렌드 콘텐츠 생성

- [ ] Vector DB 구성
- [ ] 기사 Chunking 및 Embedding
- [ ] RAG 검색 파이프라인 구축
- [ ] 출처 기반 트렌드 글 초안 생성
- [ ] 발행 전 검수 기능
- [ ] 블로그 API 연동
- [ ] 게시물 반응 데이터 수집

---

## 15. 프로젝트에서 검증하려는 내용

이 프로젝트는 단순한 뉴스 크롤러 구현이 아니라 다음 데이터 엔지니어링 문제를 직접 해결하는 것을 목표로 합니다.

### 멱등성

동일한 작업을 여러 번 실행해도 같은 데이터가 중복 저장되지 않도록 설계합니다.

### 증분 수집

매번 전체 데이터를 다시 가져오지 않고, 마지막 수집 시점 이후의 데이터만 처리합니다.

### 스키마 표준화

서로 다른 API와 RSS 응답을 공통 데이터 모델로 변환합니다.

### 데이터 품질

필수값 누락, 잘못된 날짜 형식, 중복 URL과 같은 문제를 탐지하고 기록합니다.

### 장애 복구

외부 API 오류나 데이터 형식 변경으로 작업이 실패했을 때 실패 지점부터 다시 처리할 수 있도록 구성합니다.

### 성능 최적화

데이터가 증가하면서 발생하는 조회 및 집계 성능 저하를 실행계획과 인덱스를 기반으로 개선합니다.

---

## 16. 성능 측정 계획

향후 다음 항목을 기준으로 성능 개선 전후를 비교할 예정입니다.

- 전체 실행시간
- 쿼리 실행시간
- 읽은 데이터 블록 수
- 실제 행 수와 예상 행 수
- 인덱스 사용 여부
- 조인 방식
- 데이터 건수별 처리시간
- 일별 집계 마트 적용 전후 성능

실제 운영 데이터와 대용량 부하 테스트 데이터는 명확하게 구분하여 측정할 예정입니다.

---

## 17. 주의사항

- 네이버 API 키를 GitHub에 업로드하지 않습니다.
- 수집 대상 사이트의 이용약관과 robots.txt를 확인합니다.
- 기사 원문 전체를 무단 저장하거나 재배포하지 않습니다.
- 데이터 수집량과 API 호출 제한을 준수합니다.
- 자동 생성 콘텐츠는 출처를 표시하고 발행 전에 검수합니다.
- RAG를 사용하더라도 생성 결과의 정확성을 항상 검증합니다.

---

## 18. 프로젝트 목표

최종적으로 다음 데이터 흐름을 구현하는 것이 목표입니다.

```text
데이터 수집
   ↓
원본 보관
   ↓
정제 및 표준화
   ↓
중복 제거
   ↓
분석용 데이터 모델 구축
   ↓
키워드 및 트렌드 분석
   ↓
대시보드 제공
   ↓
근거 기반 콘텐츠 생성
   ↓
블로그 발행
   ↓
사용자 반응 분석
```

이를 통해 외부 데이터 수집부터 데이터 품질 관리, 분석용 데이터 마트 구축, 성능 최적화, 데이터 활용까지 이어지는 전체 데이터 라이프사이클을 경험하고 기록합니다.

---

## 19. 진행 상태

현재 진행 단계:

```text
Phase 1. 네이버 뉴스 API 수집 및 PostgreSQL 적재
```

다음 구현 목표:

```text
1. PostgreSQL 연결 확인
2. articles 테이블 자동 생성
3. 네이버 뉴스 데이터 정규화
4. 기사 저장 함수 구현
5. 중복 저장 방지 테스트
```
