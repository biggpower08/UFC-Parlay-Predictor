# Database Normalization Plan

Supabase remains the production database. Raw Kaggle/GitHub/manual files are local training inputs only and should never be required at runtime.

## Target Internal Tables

- `source_files`: one row per imported raw file, with source type, dataset key, file hash, row count, and import timestamps.
- `source_row_map`: maps raw source row IDs to normalized entities and keeps audit lineage.
- `fighters`: canonical fighter identity.
- `fighter_aliases`: source-specific names, spellings, and IDs.
- `events`: event name, date, location, promotion, source IDs.
- `fights`: canonical fight identity, event link, fighter pair, weight class, scheduled rounds.
- `fight_results`: winner/loser, result, method, finish round/time, no-contest/draw flags.
- `fight_stats`: fight-level significant strikes, takedowns, control, submissions, knockdowns.
- `round_stats`: round-level stats when available.
- `fighter_profiles`: height, reach, stance, DOB, usual division, source profile fields.
- `fighter_snapshots`: time-aware pre-fight features.
- `odds_history`: historical odds snapshots with provider, market, timestamp quality, and pre-fight flags.
- `rankings_history`: rankings and rating snapshots by date/source.
- `scorecards`: judge scorecards and decision artifacts; post-fight labels only.
- `model_training_runs`: model artifacts, metrics, feature schema, data cutoff, leakage status, and limitations.

## Fighter Snapshots

The most important future table is `fighter_snapshots`. It should store the feature state before each fight:

- record before fight
- Elo before fight
- finish rate before fight
- decision rate before fight
- average significant strikes before fight
- average takedowns before fight
- control-time history before fight
- days since last fight
- usual weight class before fight
- source coverage and missingness flags

These rows are what make training and live prediction compatible.

## Source 7

UFCStats live scraping is Source 7 and is intentionally deferred. It should be used later for refresh/cross-checking after local datasets are stable. The deployed app must not depend on live UFCStats scraping, CAPTCHA bypassing, or fragile anti-bot behavior.
