"""backfill elo source for existing ratings

Revision ID: 0004_backfill_elo_source
Revises: 0003_add_elo_status_columns
Create Date: 2026-05-26
"""

from alembic import op

revision = "0004_backfill_elo_source"
down_revision = "0003_add_elo_status_columns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        update fighters
        set elo_source = 'computed'
        where coalesce(elo_fights_count, 0) > 0
           or coalesce(elo, 1000) <> 1000
        """
    )


def downgrade() -> None:
    op.execute(
        """
        update fighters
        set elo_source = 'baseline'
        where coalesce(elo_fights_count, 0) = 0
          and coalesce(elo, 1000) = 1000
        """
    )
