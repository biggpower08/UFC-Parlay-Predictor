# Odds Timestamp Audit

## Plain-English Summary
No local odds files were found. Download or place raw Kaggle odds files locally before auditing.

## Decision
- Status: blocked_no_files
- Odds calibration model: blocked
- Files found: 0
- Rows audited: 0
- Missing snapshot timestamp rows: 0
- Missing event date rows: 0
- Snapshot-after-event rows: 0
- Timezone ambiguous files: 0
- Moneyline rows detected: 0
- Method prop rows detected: 0

## Safe Modes
- research_only: allowed_for_manual_review
- opening_odds_model: blocked
- 24h_prefight_model: blocked
- closing_line_model: blocked_or_manual_review_only
- production_odds_model: blocked

## Files
- No files found.

## Leakage Rules
- `snapshot_timestamp` must be before the prediction cutoff.
- Prediction cutoff must be before fight/event start.
- Rows without trusted timestamps cannot train production odds models.
- Closing odds are only safe for closing-line mode.
- Odds snapshots should be append-only and preserve collection history.