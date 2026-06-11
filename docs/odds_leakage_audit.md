# Odds Leakage Audit

## Plain-English Summary
The downloaded UFC daily odds file now has a research-only normalized preview, but odds modeling is still blocked. The safe subset only includes rows where `adding_date` is present and no later than `event_date`; this prevents obvious post-event leakage, but fight mapping and prediction-cutoff review are still required.

## Hard Rules
- `snapshot_timestamp` must be trusted.
- `snapshot_timestamp` must be less than or equal to the prediction cutoff.
- The prediction cutoff must be before the fight or event start.
- Rows without trusted timestamps cannot train production odds models.
- Closing odds can only train closing-line mode.
- Historical backtests must simulate a prediction cutoff.
- `odds_calibration_model` cannot be `production_ready` until timestamp audit, fight mapping, and model review are complete.

## Current Preview Decision
- Source file: `data/imports/kaggle/ufc_betting_odds_daily/UFC_betting_odds.csv`.
- Raw rows: 181,766.
- Accepted pre-fight raw rows: 140,842.
- Rejected raw rows: 40,924.
- Accepted normalized snapshots: 281,608.
- Missing snapshot timestamp rows rejected: 684.
- Post-event snapshot rows rejected: 40,240.
- Duplicate snapshots rejected: 76.
- Normalized markets: moneyline only.
- Status: `research_only`.

## Failure Cases
- Missing collection timestamp: blocked.
- Missing event/fight date: blocked.
- Snapshot timestamp after event/fight date: blocked.
- Ambiguous timezone: research-only.
- Closing-only odds: closing-line research only.

## Still Blocked
- `odds_calibration_model` remains blocked.
- Production odds features remain blocked.
- Method-prop odds modeling remains blocked because no timestamp-safe prop snapshots were normalized in the current preview.
- No odds artifacts should be packaged.
- Raw Kaggle odds data must stay local and uncommitted.

## Next Required Gate
Map `fight_url` / `fight_key_candidate` to normalized fight records, then define strict prediction cutoffs before any odds-aware training.
