# API 사용법

## Health Check

```text
GET /health
```

## 파이프라인 실행 요청

```text
POST /api/v1/pipeline-requests
GET  /api/v1/pipeline-requests
GET  /api/v1/pipeline-requests/{request_id}
POST /api/v1/pipeline-requests/{request_id}/execute
POST /api/v1/pipeline-requests/{request_id}/retry
POST /api/v1/pipeline-requests/{request_id}/cancel
```

요청 생성 예시:

```json
{
  "pipeline_code": "NEWS_COLLECTION",
  "request_type": "MANUAL",
  "source_id": 1,
  "keyword_id": 2,
  "requested_by": "admin",
  "request_options": {
    "mock_total_count": 10,
    "mock_success_count": 8,
    "mock_failure_count": 1,
    "mock_skipped_count": 1,
    "mock_duplicate_count": 0
  }
}
```

요청 생성 API는 `PIPELINE_RUN_REQUESTS`만 생성합니다. 실제 실행은 `/execute` 또는 향후 Worker/Scheduler가 담당합니다.

## 파이프라인 실행 결과

```text
GET /api/v1/pipeline-runs
GET /api/v1/pipeline-runs/{run_id}
GET /api/v1/pipeline-runs/{run_id}/logs
```

## 재실행 요청 예시

```json
{
  "request_options_override": {
    "mock_total_count": 10,
    "mock_success_count": 10,
    "mock_failure_count": 0,
    "mock_skipped_count": 0,
    "mock_duplicate_count": 0
  }
}
```
