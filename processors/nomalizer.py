import html
import re
from datetime import datetime
from email.utils import parsedate_to_datetime

def clean_html(value: str | None)-> str:
    if not value : 
        return ""
    
    value = re.sub(r"<[^>]+>","",value)
    return html.unescape(value).strip()

def normalize_naver_article(
        item: dict,
        search_keyword: str,
)-> dict:
    published_at = parsedate_to_datetime(item["pubDate"])

    return {
        "source" : "naver_news",
        "source_name": None,
        "title" : clean_html(item.get("title")),
        "description" : clean_html(item.get("description")),
        "original_url" : clean_html(item.get("originallink") or item.get("link")),
        "published_at" : published_at,
        "collected_at" : datetime.now().astimezone(),
        "search_keyword": search_keyword
    }
    
def normalize_naver_articles(items: list[dict], search_keyword:str) -> list[dict]:
    articles = []
    for item in items:
        try:
            article = normalize_naver_article(item, search_keyword)
            articles.append(article)
        except Exception as error:
            print(f"기사 정규화 중 오류 발생: {error}")
            continue
    return articles