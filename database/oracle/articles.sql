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
    SEQ_ARTICLES.NEXTVAL,
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
  );
