from database.connection import initialize_database,get_connection
from collectors.naver_news import fetch_naver_news,get_query,get_display_count
from processors.nomalizer  import normalize_naver_articles
from database.repositories.articles_repository import save_article_to_database
from dotenv import load_dotenv
import os


load_dotenv()



def main() -> None:
    # 데이터베이스 초기화
    initialize_database()
    DB_TYPE = os.getenv("DB_TYPE", "postgresql").lower()
    
    print("데이터수집 및 전처리 작업을 수행합니다.")
    # 추가할 로직
    # 1. 네이버 뉴스 API를 사용하여 뉴스 데이터를 수집합니다.
    query = get_query()
    display = get_display_count()
    
    articles = fetch_naver_news(query, display)
    print(f"\n{query}에 대한 검색결과 : {len(articles)}건\n")
    
    # 2. 데이터 정규화
    normalized_articles = normalize_naver_articles(articles, query)
    # 3. DB 저장
    
    connection = get_connection()
    inserted_count = save_article_to_database(connection, normalized_articles, DB_TYPE)
    # 4. 결과 출력
    
    print(f"정규화 완료: {len(normalized_articles)}건")
    print(f"신규 저장 완료: {inserted_count}건")


    
    
if __name__ == "__main__":
    main()