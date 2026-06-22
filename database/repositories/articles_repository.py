


POSTGRES_INSERT_ARTICLES_QUERY = """ 
    insert into articles(
        source,
        source_name,
        title,
        description,
        original_url,
        published_at,
        collected_at,
        search_keyword
    )
    values(
        %(source)s,
        %(source_name)s,
        %(title)s,
        %(description)s,
        %(original_url)s,
        %(published_at)s,
        %(collected_at)s,
        %(search_keyword)s,
    )
    on conflict(original_url)
    do nothing;
"""

ORACLE_INSERT_ARTICLES_QUERY = """
    insert into articles(
        article_id,
        article_code,
        source,
        source_name,
        title,
        description,
        original_url,
        published_at,
        collected_at,
        search_keyword
    )
    values(
        seq_articles.nextval,
        'ART-' || LPAD(seq_articles.currval, 8, '0'),
        :source,
        :source_name,
        :title,
        :description,
        :original_url,
        :published_at,
        :collected_at,
        :search_keyword
    )
"""

def save_article_to_database(connection, articles:list[dict], db_type:str) -> int:
    query = ""
    if db_type == "postgresql":
        query = POSTGRES_INSERT_ARTICLES_QUERY
    elif db_type == "oracle":
        query = ORACLE_INSERT_ARTICLES_QUERY
    else:
        raise ValueError(f"지원되지 않는 DB_TYPE: {db_type}")
    
    insert_count=0
    try:

        with connection.cursor() as cursor:
            for article in articles:
                cursor.execute(query, article)
                if cursor.rowcount > 0:
                    insert_count += cursor.rowcount
        connection.commit()
        print(f"{insert_count}건의 기사가 데이터베이스에 저장되었습니다.")      
    except Exception as error:
        connection.rollback()
        print(f"데이터베이스 저장 중 오류 발생: {error}")
        raise
    
    return insert_count
      
