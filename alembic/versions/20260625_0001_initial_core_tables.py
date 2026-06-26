"""initial core tables

Revision ID: 20260625_0001
Revises:
Create Date: 2026-06-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260625_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("source_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_code", sa.String(length=100), nullable=False),
        sa.Column("source_name", sa.String(length=200), nullable=False),
        sa.Column("source_type", sa.String(length=20), nullable=False),
        sa.Column("base_url", sa.String(length=1000), nullable=True),
        sa.Column("config_json", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("source_type in ('API', 'RSS', 'BLOG', 'WEB')", name="ck_sources_source_type"),
        sa.PrimaryKeyConstraint("source_id"),
        sa.UniqueConstraint("source_code"),
    )
    op.create_index("ix_sources_is_active", "sources", ["is_active"])
    op.create_index("ix_sources_source_type", "sources", ["source_type"])

    op.create_table(
        "search_keywords",
        sa.Column("keyword_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("keyword", sa.String(length=200), nullable=False),
        sa.Column("normalized_keyword", sa.String(length=200), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("keyword_id"),
        sa.UniqueConstraint("keyword"),
    )
    op.create_index("ix_search_keywords_is_active", "search_keywords", ["is_active"])
    op.create_index("ix_search_keywords_normalized_keyword", "search_keywords", ["normalized_keyword"])

    op.create_table(
        "pipeline_run_requests",
        sa.Column("request_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pipeline_code", sa.String(length=100), nullable=False),
        sa.Column("request_type", sa.String(length=30), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("keyword_id", sa.Integer(), nullable=True),
        sa.Column("requested_by", sa.String(length=100), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("request_options_json", sa.Text(), nullable=True),
        sa.Column("request_status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "request_status in ('REQUESTED', 'ACCEPTED', 'REJECTED', 'CANCELLED')",
            name="ck_pipeline_run_requests_status",
        ),
        sa.CheckConstraint(
            "request_type in ('MANUAL', 'SCHEDULED', 'RETRY', 'API')",
            name="ck_pipeline_run_requests_type",
        ),
        sa.ForeignKeyConstraint(["keyword_id"], ["search_keywords.keyword_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.source_id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("request_id"),
    )
    op.create_index("ix_pipeline_run_requests_requested_at", "pipeline_run_requests", ["requested_at"])
    op.create_index("ix_pipeline_run_requests_status", "pipeline_run_requests", ["request_status"])

    op.create_table(
        "articles",
        sa.Column("article_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("external_article_id", sa.String(length=300), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("original_url", sa.Text(), nullable=False),
        sa.Column("normalized_url", sa.Text(), nullable=True),
        sa.Column("canonical_url", sa.Text(), nullable=True),
        sa.Column("url_hash", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("author", sa.String(length=300), nullable=True),
        sa.Column("publisher", sa.String(length=300), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_fetch_status", sa.String(length=30), nullable=False),
        sa.Column("latest_fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("latest_content_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "current_fetch_status in ('DISCOVERED', 'FETCH_PENDING', 'FETCHING', 'FETCHED', 'FETCH_FAILED')",
            name="ck_articles_current_fetch_status",
        ),
        sa.ForeignKeyConstraint(["source_id"], ["sources.source_id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("article_id"),
    )
    op.create_index("ix_articles_current_fetch_status", "articles", ["current_fetch_status"])
    op.create_index("ix_articles_published_at", "articles", ["published_at"])
    op.create_index("ix_articles_source_external_id", "articles", ["source_id", "external_article_id"], unique=True)
    op.create_index("ix_articles_source_id", "articles", ["source_id"])
    op.create_index("ix_articles_url_hash", "articles", ["url_hash"], unique=True)

    op.create_table(
        "pipeline_runs",
        sa.Column("run_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("run_number", sa.Integer(), nullable=False),
        sa.Column("run_status", sa.String(length=30), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_count", sa.Integer(), nullable=False),
        sa.Column("success_count", sa.Integer(), nullable=False),
        sa.Column("failure_count", sa.Integer(), nullable=False),
        sa.Column("skipped_count", sa.Integer(), nullable=False),
        sa.Column("duplicate_count", sa.Integer(), nullable=False),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("execution_options_json", sa.Text(), nullable=True),
        sa.Column("worker_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "run_status in ('PENDING', 'RUNNING', 'SUCCESS', 'PARTIAL_SUCCESS', 'FAILED', 'CANCELLED')",
            name="ck_pipeline_runs_status",
        ),
        sa.CheckConstraint(
            "total_count >= 0 and success_count >= 0 and failure_count >= 0 "
            "and skipped_count >= 0 and duplicate_count >= 0",
            name="ck_pipeline_runs_counts_non_negative",
        ),
        sa.ForeignKeyConstraint(["request_id"], ["pipeline_run_requests.request_id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("run_id"),
        sa.UniqueConstraint("request_id", "run_number", name="uq_pipeline_runs_request_run_number"),
    )
    op.create_index("ix_pipeline_runs_started_at", "pipeline_runs", ["started_at"])
    op.create_index("ix_pipeline_runs_status", "pipeline_runs", ["run_status"])

    op.create_table(
        "pipeline_logs",
        sa.Column("log_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("log_level", sa.String(length=20), nullable=False),
        sa.Column("pipeline_step", sa.String(length=100), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("detail_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "log_level in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')",
            name="ck_pipeline_logs_level",
        ),
        sa.ForeignKeyConstraint(["run_id"], ["pipeline_runs.run_id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("log_id"),
    )
    op.create_index("ix_pipeline_logs_log_level", "pipeline_logs", ["log_level"])
    op.create_index("ix_pipeline_logs_run_id_created_at", "pipeline_logs", ["run_id", "created_at"])

    op.create_table(
        "article_collections",
        sa.Column("collection_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("keyword_id", sa.Integer(), nullable=False),
        sa.Column("search_rank", sa.Integer(), nullable=True),
        sa.Column("discovered_title", sa.Text(), nullable=True),
        sa.Column("discovered_summary", sa.Text(), nullable=True),
        sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_response_json", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["article_id"], ["articles.article_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["keyword_id"], ["search_keywords.keyword_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["run_id"], ["pipeline_runs.run_id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("collection_id"),
        sa.UniqueConstraint("run_id", "article_id", "keyword_id", name="uq_article_collections_run_article_keyword"),
    )
    op.create_index("ix_article_collections_discovered_at", "article_collections", ["discovered_at"])
    op.create_index("ix_article_collections_keyword_id", "article_collections", ["keyword_id"])
    op.create_index("ix_article_collections_run_id", "article_collections", ["run_id"])

    op.create_table(
        "content_fetch_jobs",
        sa.Column("fetch_job_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=True),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("request_type", sa.String(length=30), nullable=False),
        sa.Column("fetch_status", sa.String(length=30), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("http_status_code", sa.Integer(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("error_type", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("raw_html", sa.Text(), nullable=True),
        sa.Column("clean_content", sa.Text(), nullable=True),
        sa.Column("content_length", sa.Integer(), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("fetcher_version", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("retry_count >= 0", name="ck_content_fetch_jobs_retry_count"),
        sa.CheckConstraint(
            "fetch_status in ('PENDING', 'RUNNING', 'SUCCESS', 'FAILED', 'SKIPPED')",
            name="ck_content_fetch_jobs_status",
        ),
        sa.CheckConstraint(
            "request_type in ('AUTO', 'MANUAL', 'RETRY', 'REFRESH')",
            name="ck_content_fetch_jobs_request_type",
        ),
        sa.ForeignKeyConstraint(["article_id"], ["articles.article_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["run_id"], ["pipeline_runs.run_id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("fetch_job_id"),
        sa.UniqueConstraint("article_id", "attempt_number", name="uq_content_fetch_jobs_article_attempt"),
    )
    op.create_index("ix_content_fetch_jobs_article_id", "content_fetch_jobs", ["article_id"])
    op.create_index("ix_content_fetch_jobs_run_id", "content_fetch_jobs", ["run_id"])
    op.create_index("ix_content_fetch_jobs_status", "content_fetch_jobs", ["fetch_status"])


def downgrade() -> None:
    op.drop_index("ix_content_fetch_jobs_status", table_name="content_fetch_jobs")
    op.drop_index("ix_content_fetch_jobs_run_id", table_name="content_fetch_jobs")
    op.drop_index("ix_content_fetch_jobs_article_id", table_name="content_fetch_jobs")
    op.drop_table("content_fetch_jobs")
    op.drop_index("ix_article_collections_run_id", table_name="article_collections")
    op.drop_index("ix_article_collections_keyword_id", table_name="article_collections")
    op.drop_index("ix_article_collections_discovered_at", table_name="article_collections")
    op.drop_table("article_collections")
    op.drop_index("ix_pipeline_logs_run_id_created_at", table_name="pipeline_logs")
    op.drop_index("ix_pipeline_logs_log_level", table_name="pipeline_logs")
    op.drop_table("pipeline_logs")
    op.drop_index("ix_pipeline_runs_status", table_name="pipeline_runs")
    op.drop_index("ix_pipeline_runs_started_at", table_name="pipeline_runs")
    op.drop_table("pipeline_runs")
    op.drop_index("ix_articles_url_hash", table_name="articles")
    op.drop_index("ix_articles_source_id", table_name="articles")
    op.drop_index("ix_articles_source_external_id", table_name="articles")
    op.drop_index("ix_articles_published_at", table_name="articles")
    op.drop_index("ix_articles_current_fetch_status", table_name="articles")
    op.drop_table("articles")
    op.drop_index("ix_pipeline_run_requests_status", table_name="pipeline_run_requests")
    op.drop_index("ix_pipeline_run_requests_requested_at", table_name="pipeline_run_requests")
    op.drop_table("pipeline_run_requests")
    op.drop_index("ix_search_keywords_normalized_keyword", table_name="search_keywords")
    op.drop_index("ix_search_keywords_is_active", table_name="search_keywords")
    op.drop_table("search_keywords")
    op.drop_index("ix_sources_source_type", table_name="sources")
    op.drop_index("ix_sources_is_active", table_name="sources")
    op.drop_table("sources")
