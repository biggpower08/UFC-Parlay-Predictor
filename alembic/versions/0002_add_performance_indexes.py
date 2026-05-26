"""add performance indexes

Revision ID: 0002_add_performance_indexes
Revises: 0001_create_production_tables
Create Date: 2026-05-25
"""

from alembic import op

revision = "0002_add_performance_indexes"
down_revision = "0001_create_production_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("create extension if not exists pg_trgm")

    op.execute("create index if not exists idx_fighters_normalized_name on fighters (normalized_name)")
    op.execute("create index if not exists idx_fighters_name_lower on fighters (lower(name))")
    op.execute("create index if not exists idx_fighters_nickname_lower on fighters (lower(nickname))")
    op.execute("create index if not exists idx_fighters_name_trgm on fighters using gin (normalized_name gin_trgm_ops)")
    op.execute("create index if not exists idx_fighters_nickname_trgm on fighters using gin (nickname gin_trgm_ops)")
    op.execute("create index if not exists idx_fighters_weight_class on fighters (weight_class)")

    op.execute("create index if not exists idx_fights_fighter_1_event on fights (fighter_1, event)")
    op.execute("create index if not exists idx_fights_fighter_2_event on fights (fighter_2, event)")
    op.execute("create index if not exists idx_fights_event_created_at on fights (event, created_at)")
    op.execute("create index if not exists idx_fights_created_at on fights (created_at)")

    op.execute("create index if not exists idx_predictions_fighter_a_created_at on predictions (fighter_a, created_at)")
    op.execute("create index if not exists idx_predictions_fighter_b_created_at on predictions (fighter_b, created_at)")
    op.execute("create index if not exists idx_predictions_created_at on predictions (created_at)")

    op.execute("create index if not exists idx_elo_history_name_computed_at on fighter_elo_history (normalized_name, computed_at)")
    op.execute("create index if not exists idx_elo_history_fighter_name on fighter_elo_history (fighter_name)")


def downgrade() -> None:
    op.execute("drop index if exists idx_elo_history_fighter_name")
    op.execute("drop index if exists idx_elo_history_name_computed_at")
    op.execute("drop index if exists idx_predictions_created_at")
    op.execute("drop index if exists idx_predictions_fighter_b_created_at")
    op.execute("drop index if exists idx_predictions_fighter_a_created_at")
    op.execute("drop index if exists idx_fights_created_at")
    op.execute("drop index if exists idx_fights_event_created_at")
    op.execute("drop index if exists idx_fights_fighter_2_event")
    op.execute("drop index if exists idx_fights_fighter_1_event")
    op.execute("drop index if exists idx_fighters_weight_class")
    op.execute("drop index if exists idx_fighters_nickname_trgm")
    op.execute("drop index if exists idx_fighters_name_trgm")
    op.execute("drop index if exists idx_fighters_nickname_lower")
    op.execute("drop index if exists idx_fighters_name_lower")
    op.execute("drop index if exists idx_fighters_normalized_name")
