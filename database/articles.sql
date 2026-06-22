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
