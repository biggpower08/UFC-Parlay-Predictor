"""add elo history version column

Revision ID: 0007_elo_history_version
Revises: 0006_productionize_sync_health
Create Date: 2026-05-27
"""

from alembic import op

revision = "0007_elo_history_version"
down_revision = "0006_productionize_sync_health"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("alter table fighter_elo_history add column if not exists elo_version text not null default 'v1'")


def downgrade() -> None:
    op.execute("alter table fighter_elo_history drop column if exists elo_version")
