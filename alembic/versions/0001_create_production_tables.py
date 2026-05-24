"""create production tables

Revision ID: 0001_create_production_tables
Revises:
Create Date: 2026-05-22
"""

from alembic import op

revision = "0001_create_production_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("create extension if not exists pgcrypto")
    op.execute("create extension if not exists pg_trgm")
    op.execute(
        """
        create table if not exists fighters (
            id uuid primary key default gen_random_uuid(),
            name text not null,
            normalized_name text not null unique,
            nickname text,
            wins integer,
            losses integer,
            draws integer,
            height_cm double precision,
            weight_in_kg double precision,
            reach_in_cm double precision,
            stance text,
            date_of_birth date,
            significant_strikes_landed_per_minute double precision,
            significant_striking_accuracy double precision,
            significant_strikes_absorbed_per_minute double precision,
            significant_strike_defence double precision,
            average_takedowns_landed_per_15_minutes double precision,
            takedown_accuracy double precision,
            takedown_defense double precision,
            average_submissions_attempted_per_15_minutes double precision,
            elo double precision default 1000,
            peak_elo double precision default 1000,
            weight_class text,
            updated_at timestamptz not null default now()
        )
        """
    )
    op.execute("create index if not exists idx_fighters_name_trgm on fighters using gin (normalized_name gin_trgm_ops)")
    op.execute("create index if not exists idx_fighters_nickname on fighters (nickname)")

    op.execute(
        """
        create table if not exists fights (
            id uuid primary key default gen_random_uuid(),
            event text,
            fighter_1 text not null,
            fighter_2 text not null,
            result text,
            method text,
            round text,
            time text,
            source_hash text not null unique,
            created_at timestamptz not null default now()
        )
        """
    )
    op.execute("create index if not exists idx_fights_fighter_1 on fights (fighter_1)")
    op.execute("create index if not exists idx_fights_fighter_2 on fights (fighter_2)")

    op.execute(
        """
        create table if not exists fighter_elo_history (
            id uuid primary key default gen_random_uuid(),
            fighter_name text not null,
            normalized_name text not null,
            elo double precision not null,
            peak_elo double precision not null,
            computed_at timestamptz not null default now()
        )
        """
    )
    op.execute("create index if not exists idx_elo_history_normalized_name on fighter_elo_history (normalized_name)")
    op.execute("create index if not exists idx_elo_history_computed_at on fighter_elo_history (computed_at)")

    op.execute(
        """
        create table if not exists predictions (
            prediction_id uuid primary key default gen_random_uuid(),
            fighter_a text not null,
            fighter_b text not null,
            winner text,
            confidence double precision,
            model text,
            payload_json jsonb not null,
            created_at timestamptz not null default now()
        )
        """
    )

    op.execute(
        """
        create table if not exists feedback (
            prediction_id uuid,
            fighter_a text not null,
            fighter_b text not null,
            predicted_winner text,
            actual_winner text,
            confidence double precision,
            was_correct boolean,
            user_notes text,
            timestamp timestamptz not null default now()
        )
        """
    )
    op.execute("create index if not exists idx_feedback_prediction_id on feedback (prediction_id)")

    op.execute(
        """
        create table if not exists scrape_cache (
            normalized_name text primary key,
            source text,
            url text,
            raw_json jsonb not null,
            confidence double precision default 0,
            fetched_at timestamptz not null default now()
        )
        """
    )


def downgrade() -> None:
    op.execute("drop table if exists scrape_cache")
    op.execute("drop table if exists feedback")
    op.execute("drop table if exists predictions")
    op.execute("drop table if exists fighter_elo_history")
    op.execute("drop table if exists fights")
    op.execute("drop table if exists fighters")
