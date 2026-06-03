"""add fight-by-fight elo history

Revision ID: 0009_elo_fight_history
Revises: 0008_sync_observability
Create Date: 2026-05-30
"""

from alembic import op

revision = "0009_elo_fight_history"
down_revision = "0008_sync_observability"
branch_labels = None
depends_on = None


def upgrade() -> None:
    dialect = op.get_bind().dialect.name
    if dialect == "postgresql":
        op.execute("create extension if not exists pgcrypto")
        op.execute(
            """
            create table if not exists fighter_elo_fight_history (
                id uuid primary key default gen_random_uuid(),
                fighter_name text not null,
                normalized_name text not null,
                opponent_name text not null,
                opponent_normalized_name text,
                event text,
                event_date date,
                fight_id text,
                source_hash text,
                weight_class text,
                result text,
                method text,
                round text,
                elo_before double precision not null,
                elo_after double precision not null,
                elo_change double precision not null,
                opponent_elo_before double precision,
                expected_score double precision,
                elo_version text not null default 'v1',
                order_source text,
                computed_at timestamptz not null default now()
            )
            """
        )
    else:
        op.execute(
            """
            create table if not exists fighter_elo_fight_history (
                id integer primary key autoincrement,
                fighter_name text not null,
                normalized_name text not null,
                opponent_name text not null,
                opponent_normalized_name text,
                event text,
                event_date text,
                fight_id text,
                source_hash text,
                weight_class text,
                result text,
                method text,
                round text,
                elo_before real not null,
                elo_after real not null,
                elo_change real not null,
                opponent_elo_before real,
                expected_score real,
                elo_version text not null default 'v1',
                order_source text,
                computed_at text not null
            )
            """
        )
    op.execute("create index if not exists idx_elo_fight_history_normalized_name on fighter_elo_fight_history (normalized_name)")
    op.execute("create index if not exists idx_elo_fight_history_event_date on fighter_elo_fight_history (event_date)")
    op.execute("create index if not exists idx_elo_fight_history_elo_version on fighter_elo_fight_history (elo_version)")
    op.execute("create index if not exists idx_elo_fight_history_name_date on fighter_elo_fight_history (normalized_name, event_date)")
    op.execute("create index if not exists idx_elo_fight_history_source_hash on fighter_elo_fight_history (source_hash)")


def downgrade() -> None:
    op.execute("drop index if exists idx_elo_fight_history_source_hash")
    op.execute("drop index if exists idx_elo_fight_history_name_date")
    op.execute("drop index if exists idx_elo_fight_history_elo_version")
    op.execute("drop index if exists idx_elo_fight_history_event_date")
    op.execute("drop index if exists idx_elo_fight_history_normalized_name")
    op.execute("drop table if exists fighter_elo_fight_history")
