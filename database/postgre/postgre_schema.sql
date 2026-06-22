-- article table 생성
create table if not exists articles(
    article_id bigserial primary key,
    source varchar(255) not null,
    source_name varchar(255),
    title text not null,
    description text,
    original_url text not null,
    published_at timestamptz,
    collected_at timestamptz not null default current_timestamp,
    search_keyword varchar(100),
    content_hash varchar(64),
    constraint uq_article_url unique (original_url)
);