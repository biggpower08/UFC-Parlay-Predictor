"""add elo status columns

Revision ID: 0003_add_elo_status_columns
Revises: 0002_add_performance_indexes
Create Date: 2026-05-26
"""

from alembic import op

revision = "0003_add_elo_status_columns"
down_revision = "0002_add_performance_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("alter table fighters add column if not exists elo_fights_count integer default 0")
    op.execute("alter table fighters add column if not exists elo_source text default 'baseline'")
    op.execute("create index if not exists idx_fighters_elo_source on fighters (elo_source)")


def downgrade() -> None:
    op.execute("drop index if exists idx_fighters_elo_source")
    op.execute("alter table fighters drop column if exists elo_source")
    op.execute("alter table fighters drop column if exists elo_fights_count")
