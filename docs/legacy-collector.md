# 기존 수집 스크립트

루트의 `main.py`, `collectors/`, `processors/`, `database/`는 이전 단계의 Naver News 수집 스크립트입니다.

이 스크립트는 신규 `app/` 기반 API 구조와 아직 완전히 통합되지는 않았습니다.

## 주요 파일

| 경로 | 역할 |
| --- | --- |
| `main.py` | 기존 수집 프로세스 실행 진입점 |
| `collectors/naver_news.py` | Naver News API 호출 |
| `processors/nomalizer.py` | API 응답 정규화 |
| `database/connection.py` | 기존 DB 연결 및 초기화 |
| `database/repositories/articles_repository.py` | 기존 기사 저장 로직 |

## 실행

```powershell
python main.py
```

## 참고

신규 파이프라인 구조에서는 향후 Collector를 Application Service 또는 Worker에서 호출하도록 통합할 예정입니다.
