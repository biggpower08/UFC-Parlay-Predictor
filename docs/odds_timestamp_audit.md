# Odds Timestamp Audit

## Plain-English Summary
Odds timestamp safety is not proven, so odds modeling remains blocked.

## Decision
- Status: blocked_missing_snapshot_timestamps
- Odds calibration model: blocked
- Files found: 1
- File size bytes: 29620834
- Rows audited: 181766
- Earliest snapshot timestamp: 2025-07-26T07:05:52.715662+00:00
- Latest snapshot timestamp: 2026-06-10T16:53:27+00:00
- Earliest event date: 2010-03-21T00:00:00+00:00
- Latest event date: 2027-07-02T00:00:00+00:00
- Missing snapshot timestamp rows: 684
- Missing event date rows: 0
- Snapshot-after-event rows: 40240
- Snapshot-before-or-equal-event rows: 140842
- Timezone ambiguous files: 0
- Moneyline rows detected: 181551
- Method prop rows detected: 5376
- Duplicate snapshots: 85044
- Multiple snapshots per fight: 175253

## Safe Modes
- research_only: allowed_for_manual_review
- opening_odds_model: blocked
- 24h_prefight_model: blocked
- closing_line_model: blocked_or_manual_review_only
- production_odds_model: blocked

## Files
- `data\imports\kaggle\ufc_betting_odds_daily\UFC_betting_odds.csv`: audited, rows=181766
  - Columns: fight_url, fighter_1_url, fighter_2_url, fighter_1, fighter_2, odds_1, odds_2, f1_ko_odds, f2_ko_odds, f1_sub_odds, f2_sub_odds, f1_dec_odds, f2_dec_odds, event_date, adding_date, source, region
  - Event date column: event_date
  - Snapshot timestamp column: adding_date
  - Bookmaker/source columns: source
  - Fighter/selection columns: fighter_1_url, fighter_2_url, fighter_1, fighter_2
  - Odds columns: odds_1, odds_2, f1_ko_odds, f2_ko_odds, f1_sub_odds, f2_sub_odds, f1_dec_odds, f2_dec_odds

## Leakage Rules
- `snapshot_timestamp` must be before the prediction cutoff.
- Prediction cutoff must be before fight/event start.
- Rows without trusted timestamps cannot train production odds models.
- Closing odds are only safe for closing-line mode.
- Odds snapshots should be append-only and preserve collection history.

## Normalized Preview Follow-Up
- Normalizer: `scripts/normalize_kaggle_odds_snapshots.py`.
- Preview status: `research_only`.
- Accepted raw rows after row-level timestamp filtering: 140,842.
- Rejected raw rows: 40,924.
- Accepted normalized snapshots: 281,608.
- Normalized markets: moneyline only in the current timestamp-safe preview.
- Full generated CSV: `ufc_predictor/data/processed/training_imports/odds_snapshots_preview.csv` and must not be committed.
- Small committed outputs: `ufc_predictor/data/processed/odds_snapshots_preview.json` and `ufc_predictor/data/processed/odds_snapshots_preview_summary.json`.
- `odds_calibration_model` remains blocked until fight mapping, prediction cutoff policy, and modeling review pass.
