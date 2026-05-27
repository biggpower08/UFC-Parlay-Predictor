"""sync observability columns

Revision ID: 0008_sync_observability
Revises: 0007_elo_history_version
Create Date: 2026-05-27
"""

from alembic import op

revision = "0008_sync_observability"
down_revision = "0007_elo_history_version"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("alter table sync_runs add column if not exists inserted_count integer default 0")
    op.execute("alter table sync_runs add column if not exists updated_count integer default 0")
    op.execute("alter table sync_runs add column if not exists skipped_count integer default 0")
    op.execute("alter table sync_runs add column if not exists failed_count integer default 0")
    op.execute("alter table sync_locks add column if not exists metadata jsonb")


def downgrade() -> None:
    op.execute("alter table sync_locks drop column if exists metadata")
    op.execute("alter table sync_runs drop column if exists failed_count")
    op.execute("alter table sync_runs drop column if exists skipped_count")
    op.execute("alter table sync_runs drop column if exists updated_count")
    op.execute("alter table sync_runs drop column if exists inserted_count")
