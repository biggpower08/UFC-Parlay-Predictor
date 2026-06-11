# Odds Feature Schema

## Plain-English Summary
Odds features are not live yet. This schema describes how odds can be normalized later without leaking future market information into historical predictions.

## Normalized Fields
- `fight_key`
- `event_name`
- `event_date`
- `fighter_a`
- `fighter_b`
- `selection`
- `market_type`
- `bookmaker`
- `region`
- `american_odds`
- `decimal_odds`
- `implied_probability`
- `snapshot_timestamp`
- `source_dataset`
- `source_file`
- `source_row_hash`
- `is_closing_candidate`
- `is_live`
- `timestamp_audit_status`

## Downloaded Daily Odds Column Mapping
- `fight_url` -> candidate fight key / external fight ID.
- `fighter_1`, `fighter_2` -> matchup fighters.
- `odds_1`, `odds_2` -> moneyline decimal odds.
- `f1_ko_odds`, `f2_ko_odds` -> KO/TKO prop decimal odds.
- `f1_sub_odds`, `f2_sub_odds` -> submission prop decimal odds.
- `f1_dec_odds`, `f2_dec_odds` -> decision prop decimal odds.
- `event_date` -> event date.
- `adding_date` -> candidate snapshot timestamp.
- `source` -> bookmaker/source.
- `region` -> market region.

Current status: useful for a research-only normalized preview after row-level timestamp filtering; blocked for production odds modeling.

## Current Normalized Preview
- Preview status: `research_only`.
- Accepted pre-fight raw rows: 140,842.
- Accepted normalized snapshots: 281,608.
- Rejected raw rows: 40,924.
- Normalized moneyline snapshots: 281,608.
- Normalized KO/TKO prop snapshots: 0.
- Normalized submission prop snapshots: 0.
- Normalized decision prop snapshots: 0.
- Full generated CSV stays local under `ufc_predictor/data/processed/training_imports/` and is ignored by Git.
- Small committed preview files live under `ufc_predictor/data/processed/`.

The preview proves a timestamp-safe moneyline subset exists, but it does not make odds features production-ready.

## Feature Families
- Moneyline snapshots.
- Method props: KO/TKO, submission, decision.
- Market availability flags.
- Bookmaker dispersion.
- Movement between trusted pre-fight snapshots.
- Closing-line values only for closing-line mode.

## Excluded Until Proven Safe
- Odds rows without timestamps.
- Post-fight archived odds.
- Closing odds used as early prediction features.
- Any odds source with unclear event date alignment.
- Any odds feature that cannot be reproduced at runtime for the same prediction cutoff.
