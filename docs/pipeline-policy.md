# 파이프라인 실행 정책

## Mock 실행 단계

이번 단계에서는 실제 외부 뉴스 API를 호출하지 않습니다. 개발용 실행 API는 다음 Mock 단계를 로그로 남깁니다.

```text
REQUEST_VALIDATION
MOCK_COLLECTION
RESULT_AGGREGATION
COMPLETED
```

## 실행 상태 결정

```text
failure_count = 0
-> SUCCESS

success_count > 0 and failure_count > 0
-> PARTIAL_SUCCESS

success_count = 0 and failure_count > 0
-> FAILED
```

처리 건수는 다음 조건을 만족해야 합니다.

```text
total_count = success_count + failure_count + skipped_count + duplicate_count
```

## 재실행 정책

- 기존 `PIPELINE_RUNS`는 수정하지 않습니다.
- 재실행할 때마다 새 `PIPELINE_RUNS`를 생성합니다.
- `run_number`는 기존 최대값 + 1입니다.
- `FAILED`, `PARTIAL_SUCCESS` 실행만 재실행할 수 있습니다.
- `request_options_override`는 기존 요청 옵션 위에 얕은 병합으로 덮어씁니다.

## 취소 정책

- `REQUESTED`, `ACCEPTED` 상태만 취소 대상입니다.
- 이미 실행 이력이 있는 요청은 현재 단계에서 취소하지 않습니다.
- 실행 중 작업을 강제 종료하는 기능은 아직 없습니다.

## 동시성 처리

실행 생성 시 repository에서 요청 레코드를 `SELECT FOR UPDATE`로 잠그도록 구성했습니다. SQLite 테스트 환경에서는 무시되지만 PostgreSQL에서는 같은 요청의 동시 실행 번호 계산을 보호합니다.

최종 방어선으로 `PIPELINE_RUNS(request_id, run_number)` unique 제약조건을 사용합니다.
