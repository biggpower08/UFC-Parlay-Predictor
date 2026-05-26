"""add sync and ranking tables

Revision ID: 0005_add_sync_and_ranking_tables
Revises: 0004_backfill_elo_source
Create Date: 2026-05-26
"""

from alembic import op

revision = "0005_add_sync_and_ranking_tables"
down_revision = "0004_backfill_elo_source"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        create table if not exists events (
            id uuid primary key default gen_random_uuid(),
            name text not null,
            normalized_name text not null unique,
            event_date date,
            location text,
            source text not null default 'ufcstats',
            source_url text,
            source_hash text unique,
            scraped_at timestamptz,
            created_at timestamptz not null default now(),
            updated_at timestamptz not null default now()
        )
        """
    )
    op.execute("create index if not exists idx_events_source_hash on events (source_hash)")
    op.execute("create index if not exists idx_events_event_date on events (event_date)")

    op.execute("alter table fights add column if not exists event_date date")
    op.execute("alter table fights add column if not exists weight_class text")
    op.execute("alter table fights add column if not exists source text default 'local_csv'")
    op.execute("alter table fights add column if not exists source_url text")
    op.execute("alter table fights add column if not exists scraped_at timestamptz")
    op.execute("create index if not exists idx_fights_weight_class on fights (weight_class)")

    op.execute(
        """
        create table if not exists fighter_rankings (
            id uuid primary key default gen_random_uuid(),
            fighter_name text not null,
            normalized_name text not null,
            ranking_type text not null,
            weight_class text,
            rank integer not null,
            elo double precision not null,
            peak_elo double precision,
            fights_count integer default 0,
            wins integer default 0,
            losses integer default 0,
            generated_at timestamptz not null default now(),
            source text not null default 'elo_v1',
            unique (normalized_name, ranking_type, weight_class, source)
        )
        """
    )
    op.execute("create index if not exists idx_rankings_type_rank on fighter_rankings (ranking_type, rank)")
    op.execute("create index if not exists idx_rankings_weight_class on fighter_rankings (weight_class)")

    op.execute(
        """
        create table if not exists fighter_weight_class_history (
            id uuid primary key default gen_random_uuid(),
            fighter_name text not null,
            normalized_name text not null,
            weight_class text not null,
            fights_count integer default 0,
            first_seen date,
            last_seen date,
            inferred_from_fights boolean not null default true,
            confidence double precision default 0,
            generated_at timestamptz not null default now(),
            unique (normalized_name, weight_class)
        )
        """
    )
    op.execute("create index if not exists idx_weight_history_name on fighter_weight_class_history (normalized_name)")

    op.execute(
        """
        create table if not exists sync_runs (
            id uuid primary key default gen_random_uuid(),
            source text not null,
            status text not null,
            started_at timestamptz not null default now(),
            finished_at timestamptz,
            dry_run boolean not null default false,
            events_seen integer default 0,
            fights_seen integer default 0,
            fighters_seen integer default 0,
            message text
        )
        """
    )

    op.execute(
        """
        create table if not exists scraper_sources (
            source text primary key,
            base_url text not null,
            enabled boolean not null default true,
            last_success_at timestamptz,
            last_error text,
            updated_at timestamptz not null default now()
        )
        """
    )


def downgrade() -> None:
    op.execute("drop table if exists scraper_sources")
    op.execute("drop table if exists sync_runs")
    op.execute("drop table if exists fighter_weight_class_history")
    op.execute("drop table if exists fighter_rankings")
    op.execute("drop index if exists idx_fights_weight_class")
    op.execute("alter table fights drop column if exists scraped_at")
    op.execute("alter table fights drop column if exists source_url")
    op.execute("alter table fights drop column if exists source")
    op.execute("alter table fights drop column if exists weight_class")
    op.execute("alter table fights drop column if exists event_date")
    op.execute("drop table if exists events")
