# Odds Ingestion Plan

## Plain-English Summary
Odds data is being prepared as a future research source, not as a live sportsbook feature. The app should only use odds rows after timestamp checks prove the odds were collected before the prediction cutoff.

## Current Candidate Sources
- `jerzyszocik/ufc-betting-odds-daily-dataset`: timestamped daily odds candidate.
- `mdabbert/ufc-fights-2010-2020-with-betting-odds`: research-only until timestamp safety is proven.
- `mdabbert/ultimate-ufc-dataset`: research-only odds columns until timestamp safety is proven.
- `oliviersportsdata/us-sports-master-historical-closing-odds`: closing-line research only.
- `jasonkwm/ufc-mens-betting-odds-20152020`: research-only unless timestamp safety passes.

## Downloaded Daily Odds Audit
- File: `data/imports/kaggle/ufc_betting_odds_daily/UFC_betting_odds.csv`.
- Rows: 181,766.
- Event date column: `event_date`.
- Snapshot timestamp column: `adding_date`.
- Bookmaker/source column: `source`.
- Region column: `region`.
- Moneyline odds columns: `odds_1`, `odds_2`.
- Method prop columns: `f1_ko_odds`, `f2_ko_odds`, `f1_sub_odds`, `f2_sub_odds`, `f1_dec_odds`, `f2_dec_odds`.
- Current audit status: `blocked_missing_snapshot_timestamps`.
- Reason: 684 rows are missing snapshot timestamps and 40,240 rows have snapshots after the event date.
- Next step: normalize only timestamp-safe rows into a dry-run `odds_snapshots` preview for mapping review.

## Future Normalized Table: odds_snapshots
- `id`
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
- `created_at`

## Processing Rules
- Raw Kaggle files stay local under `data/imports/kaggle/`.
- Normalized odds snapshots should be append-only.
- Do not overwrite old snapshots without preserving collection timestamps.
- Do not train odds models until timestamp audit passes.
- Do not show fake sportsbook odds in the app.
