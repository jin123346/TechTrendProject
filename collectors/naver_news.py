import os 

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

def get_query() -> str:
    query = input("검색할 기술 키워드를 입력하세요 : ").strip()

    if not query:
        raise ValueError("검색 키워드를 입력해야 합니다.")

    return query


def get_display_count() -> int:
    raw_value = input("조회할 기사 수를 입력하세요 (1~100, 기본 10): ").strip()

    if not raw_value:
        return 10

    try:
        display = int(raw_value)
    except ValueError as error:
        raise ValueError("조회 건수는 숫자로 입력해야 합니다.") from error

    if not 1 <= display <= 100:
        raise ValueError("조회 건수는 1~100 사이로 입력해야 합니다.")

    return display


def fetch_naver_news(query: str, display: int = 10) -> list[dict]:
    url = "https://openapi.naver.com/v1/search/news.json"

    headers = {
        "X-Naver-Client-Id" : CLIENT_ID,
        "X-Naver-Client-Secret" : CLIENT_SECRET
    }


    params= {
        "query" : query,
        "display" : display,
        "sort" : "date",
    }


    response = requests.get(
        url,
        headers= headers,
        params = params,
        timeout = 10,
    )

    response.raise_for_status()

    return response.json().get("items",[])

# if __name__=="__main__":
#     articles = fetch_naver_news("인공지능",10)

#     for article in articles:
#         print(article)
