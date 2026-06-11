# Elo Leakage Audit

## Plain-English Summary
Historical Elo features are generated from pre-fight snapshots. Same-event rows use the pre-event Elo snapshot, and unsafe current/latest Elo backfills are intentionally not run.

## Decision
- Status: passed
- Feature mode: strict_pre_event_prefight
- Same-event policy: all same-event rows use pre-event Elo
- Runtime policy: future live predictions may use current computed Elo; historical training/backtests may not

## Ablation Results
| Variant | Status | Accuracy | Balanced Accuracy | ROC AUC | Brier | Baseline | Improvement | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Unsafe current/latest Elo | blocked_not_run |  |  |  |  |  |  | Using current/latest Elo on historical rows would intentionally leak future fights into the past. |
| Strict pre-fight Elo | evaluated | 0.9606 | 0.9604 | 0.9892 | 0.0272 | 0.52 | 0.4406 | Used for historical training/backtests. |
| No Elo features | evaluated | 0.9585 | 0.9588 | 0.9901 | 0.027 | 0.52 | 0.4385 | Shows whether Elo is helping without leakage. |

## Passed Checks
- pre_fight_elo_features_generated
- same_event_pre_event_cutoff
- post_fight_elo_features_excluded
- unsafe_current_elo_historical_variant_blocked

## Failed Checks
- None

## Notes
- Historical rows do not use current/latest Elo snapshots.
- Same-card fights are treated as pre-event predictions by default.
- Public Elo methodology was not added to the website.