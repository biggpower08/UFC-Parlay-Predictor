# Odds Leakage Audit

## Plain-English Summary
Odds data is powerful but risky because archived odds may be closing lines or post-fight records. Until timestamps prove odds were collected before the prediction cutoff, odds-aware models remain blocked.

## Hard Rules
- `snapshot_timestamp` must be trusted.
- `snapshot_timestamp` must be less than or equal to the prediction cutoff.
- The prediction cutoff must be before the fight or event start.
- Rows without trusted timestamps cannot train production odds models.
- Closing odds can only train closing-line mode.
- Historical backtests must simulate a prediction cutoff.
- `odds_calibration_model` cannot be `production_ready` until timestamp audit passes and model review is complete.

## Current Status
- `ufc_betting_odds_daily` is a timestamped candidate, not approved production data.
- `odds_calibration_model` remains blocked.
- The audit script writes `ufc_predictor/data/processed/odds_timestamp_audit.json` and `docs/odds_timestamp_audit.md`.

## Failure Cases
- Missing collection timestamp: blocked.
- Missing event/fight date: blocked.
- Snapshot timestamp after event/fight date: blocked.
- Ambiguous timezone: research-only.
- Closing-only odds: closing-line research only.
