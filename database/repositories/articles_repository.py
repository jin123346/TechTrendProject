


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
    insert into ARTICLES(
        ARTICLE_ID,
        SOURCE_ID,
        PUBLISHER_NAME,
        TITLE,
        SEARCH_SNIPPET,
        ORIGINAL_URL,
        ORIGINAL_URL_HASH,
        PUBLISHED_AT,
        FIRST_COLLECTED_AT,
        LAST_SEEN_AT
    )
    select
        SEQ_ARTICLES.nextval,
        s.SOURCE_ID,
        :source_name,
        :title,
        :description,
        :original_url,
        RAWTOHEX(STANDARD_HASH(:original_url, 'SHA256')),
        :published_at,
        :collected_at,
        :collected_at
    from SOURCES s
    where LOWER(s.SOURCE_CODE) = LOWER(:source)
      and not exists (
          select 1
          from ARTICLES a
          where a.ORIGINAL_URL_HASH = RAWTOHEX(STANDARD_HASH(:original_url, 'SHA256'))
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
      
