"""productionize sync health

Revision ID: 0006_productionize_sync_health
Revises: 0005_add_sync_and_ranking_tables
Create Date: 2026-05-26
"""

from alembic import op

revision = "0006_productionize_sync_health"
down_revision = "0005_add_sync_and_ranking_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("alter table scraper_sources add column if not exists last_failed_at timestamptz")
    op.execute("alter table scraper_sources add column if not exists challenge_detected boolean not null default false")
    op.execute("alter table scraper_sources add column if not exists consecutive_failures integer not null default 0")
    op.execute("alter table scraper_sources add column if not exists last_status_code integer")
    op.execute("alter table scraper_sources add column if not exists average_fetch_ms double precision")

    op.execute(
        """
        create table if not exists sync_locks (
            lock_name text primary key,
            owner text not null,
            started_at timestamptz not null default now(),
            expires_at timestamptz not null
        )
        """
    )
    op.execute("create index if not exists idx_sync_locks_expires_at on sync_locks (expires_at)")


def downgrade() -> None:
    op.execute("drop table if exists sync_locks")
    op.execute("alter table scraper_sources drop column if exists average_fetch_ms")
    op.execute("alter table scraper_sources drop column if exists last_status_code")
    op.execute("alter table scraper_sources drop column if exists consecutive_failures")
    op.execute("alter table scraper_sources drop column if exists challenge_detected")
    op.execute("alter table scraper_sources drop column if exists last_failed_at")
