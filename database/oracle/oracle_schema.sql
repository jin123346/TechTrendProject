-- articles table 생성
CREATE TABLE articles (
    article_id NUMBER NOT NULL,
    source VARCHAR2(255) NOT NULL,
    source_name VARCHAR2(255),
    title CLOB NOT NULL,
    description CLOB,
    original_url VARCHAR2(1000) NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    search_keyword VARCHAR2(100),
    content_hash VARCHAR2(64),
    CONSTRAINT pk_articles PRIMARY KEY (article_id),
    CONSTRAINT uq_article_url UNIQUE (original_url)
);


-- 수집해오는 소스들 관리
CREATE TABLE sources (
    source_id NUMBER NOT NULL,
    source_code VARCHAR2(30) NOT NULL,
    source_name VARCHAR2(255) NOT NULL,
    source_type VARCHAR2(50) NOT NULL,
    base_url VARCHAR2(1000),
    is_active CHAR(1) DEFAULT 'Y' NOT NULL,
    created_at TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,

    CONSTRAINT pk_sources PRIMARY KEY (source_id),
    CONSTRAINT uq_sources_code UNIQUE (source_code),
    CONSTRAINT ck_sources_active CHECK (is_active IN ('Y', 'N'))
);

CREATE SEQUENCE seq_sources
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;


-- pipeline_runs table 생성 실행이력 테이블 
create table pipeline_runs(
    run_id number not null,
    run_code varchar2(100) not null,
    pipeline_name varchar2(100) not null,
    search_keyword varchar2(100) not null,
    
    request_start_num number default 1 not null,
    request_end_num number,
    last_api_start_num number,
    page_size number default 100 not null,

    target_date DATE,
    window_start_at TIMESTAMP,
    window_end_at TIMESTAMP,

    request_count number default 0 not null,
    collected_count number default 0 not null,
    normalized_count number defalut 0 not null,
    inserted_count number default 0 not null,
    duplicate_count number default 0 not null,
    failed_count number default 0 not null,

    request_status varchar2(20) not null,
    stop_reason varchar2(100),

    started_at TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    eror_message CLOB,
    
    constraint pk_pipeline_runs primary key (run_id),
)

-- STOP_REASONS 
-- NO_MORE_ITEMS
-- OLDER_THAN_TARGET_DATE
-- OLDER_THAN_LAST_COLLECTED_AT
-- MAX_START_REACHED
-- MAX_PAGE_REACHED
-- API_ERROR
-- COMPLETED



CREATE TABLE article_collections (
    collection_id NUMBER NOT NULL,
    collection_code VARCHAR2(30) NOT NULL,
    run_id NUMBER NOT NULL,
    article_id NUMBER NOT NULL,
    search_keyword VARCHAR2(100) NOT NULL,
    collected_at TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,

    CONSTRAINT pk_article_collections PRIMARY KEY (collection_id),
    CONSTRAINT uq_article_collections_code UNIQUE (collection_code),
    CONSTRAINT uq_article_collection UNIQUE (
        run_id,
        article_id,
        search_keyword
    ),
    CONSTRAINT fk_collections_run
        FOREIGN KEY (run_id)
        REFERENCES pipeline_runs (run_id),
    CONSTRAINT fk_collections_article
        FOREIGN KEY (article_id)
        REFERENCES articles (article_id)
);

CREATE SEQUENCE seq_article_collections
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;



CREATE TABLE keywords (
    keyword_id NUMBER NOT NULL,
    keyword_name VARCHAR2(255) NOT NULL,
    category VARCHAR2(100),
    created_at TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,

    CONSTRAINT pk_keywords PRIMARY KEY (keyword_id),
    CONSTRAINT uq_keywords_name UNIQUE (keyword_name)
);

CREATE SEQUENCE seq_keywords
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;


CREATE TABLE article_keywords (
    article_id NUMBER NOT NULL,
    keyword_id NUMBER NOT NULL,
    frequency NUMBER DEFAULT 1 NOT NULL,
    relevance_score NUMBER,
    extracted_at TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,

    CONSTRAINT pk_article_keywords
        PRIMARY KEY (article_id, keyword_id),
    CONSTRAINT fk_article_keywords_article
        FOREIGN KEY (article_id)
        REFERENCES articles (article_id),
    CONSTRAINT fk_article_keywords_keyword
        FOREIGN KEY (keyword_id)
        REFERENCES keywords (keyword_id)
);

CREATE TABLE pipeline_logs (
    log_id NUMBER NOT NULL,
    run_id NUMBER NOT NULL,
    log_level VARCHAR2(20) NOT NULL,
    process_step VARCHAR2(100),
    message CLOB NOT NULL,
    article_url VARCHAR2(1000),
    created_at TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,

    CONSTRAINT pk_pipeline_logs PRIMARY KEY (log_id),
    CONSTRAINT fk_pipeline_logs_run
        FOREIGN KEY (run_id)
        REFERENCES pipeline_runs (run_id),
    CONSTRAINT ck_pipeline_logs_level CHECK (
        log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    )
);

CREATE SEQUENCE seq_pipeline_logs
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;