# Metric Jump Audit

## Plain-English Summary
Metric jumps mostly came from feature and interaction changes, not row-count changes. Source-holdout remains the main production-readiness blocker.

## Row, Split, and Label Checks
- Previous report ref: `a955ca9`
- Fight rows: 49355 -> 49355
- Feature count: 136 -> 157 (+21)
- Date range changed: False
- Row count changed: False
- Train rows: 29347
- Validation rows: 6134
- Final test rows: 5537
- Calibration status: basic_probability_scores_only

## Leakage Audit Result
- Style features are derived from accumulated fighter history before each fight row is added to history.
- Opponent-weakness features are also derived from accumulated prior history.
- Interaction discovery excludes forbidden target/result/current-fight columns and records that final test is not used for selection.
- `--calibrate` is currently reported as `basic_probability_scores_only`; it is not true validation-only calibration yet.

## Model Metric Changes
| Model | Old Metric | New Metric | Delta | Test Rows | Status | Interactions | Risk | Verdict | Likely Reason |
|---|---:|---:|---:|---|---|---:|---|---|---|
| winner_model | 0.9585 | 0.9621 | 0.0036 | 3327 -> 3327 | high_confidence_only | 0 / 240 | medium | needs_review | feature schema expanded by 21 fields; base features kept |
| fight_duration_model | 0.8285 | 0.8287 | 0.0002 | 3696 -> 3696 | experimental | 5 / 240 | high | needs_review | feature schema expanded by 21 fields and 5 validation-selected interactions were used |
| finish_model | 0.8285 | 0.8287 | 0.0002 | 3696 -> 3696 | experimental | 5 / 240 | high | needs_review | feature schema expanded by 21 fields and 5 validation-selected interactions were used |
| goes_distance_model | 0.8285 | 0.8287 | 0.0002 | 3696 -> 3696 | experimental | 5 / 240 | high | needs_review | feature schema expanded by 21 fields and 5 validation-selected interactions were used |
| over_1_5_model | 0.7907 | 0.7869 | -0.0038 | 3683 -> 3683 | experimental | 0 / 240 | medium | needs_review | feature schema expanded by 21 fields; base features kept |
| over_2_5_model | 0.8086 | 0.7993 | -0.0093 | 3683 -> 3683 | experimental | 0 / 240 | high | needs_review | feature schema expanded by 21 fields; base features kept |
| ends_before_round_3_model | 0.7934 | 0.7763 | -0.0171 | 3683 -> 3683 | experimental | 10 / 240 | high | needs_review | feature schema expanded by 21 fields and 10 validation-selected interactions were used |
| finish_in_round_1_model | 0.8298 | 0.8306 | 0.0008 | 3683 -> 3683 | experimental | 0 / 240 | medium | needs_review | feature schema expanded by 21 fields; base features kept |
| finish_type_model | 0.7812 | 0.7728 | -0.0084 | 1796 -> 1796 | experimental | 5 / 240 | high | needs_review | feature schema expanded by 21 fields and 5 validation-selected interactions were used |
| method_umbrella_model | 0.7484 | 0.7538 | 0.0054 | 3696 -> 3696 | experimental | 0 / 0 | high | needs_review | feature schema expanded by 21 fields; base features kept |
| strike_volume_model | 0.5825 | 0.5749 | -0.0076 | 1322 -> 1322 | experimental | 10 / 240 | high | needs_review | feature schema expanded by 21 fields and 10 validation-selected interactions were used |
| takedown_control_model | 0.7385 | 0.7285 | -0.01 | 2486 -> 2486 | experimental | 0 / 240 | medium | needs_review | feature schema expanded by 21 fields; base features kept |
| odds_calibration_model | None | None | None | 0 -> 0 | blocked | 0 / 0 | high | blocked | feature schema expanded by 21 fields; base features kept |

## Source-Holdout Readiness
| Model | Source-Holdout Status | Worst Source | Worst Metric | Drop | Production Status |
|---|---|---|---:|---:|---|
| winner_model | needs_review | ufc_1994_2026 | 0.8222 | 0.1399 | high_confidence_only |
| fight_duration_model | unstable | ufc_stats_complete | 0.5762 | 0.2525 | experimental |
| finish_model | unstable | ufc_stats_complete | 0.5762 | 0.2525 | experimental |
| goes_distance_model | unstable | ufc_stats_complete | 0.5762 | 0.2525 | experimental |
| over_1_5_model | needs_review | ufc_stats_complete | 0.6399 | 0.147 | experimental |
| over_2_5_model | unstable | ufc_stats_complete | 0.5873 | 0.212 | experimental |
| ends_before_round_3_model | unstable | ufc_stats_complete | 0.5873 | 0.189 | experimental |
| finish_in_round_1_model | needs_review | ufc_stats_complete | 0.7175 | 0.1131 | experimental |
| finish_type_model | unstable | ufc_stats_complete | 0.4813 | 0.2915 | experimental |
| method_umbrella_model | unstable | ufc_stats_complete | 0.4183 | 0.3355 | experimental |
| strike_volume_model | unstable | ufc_stats_complete | 0.4155 | 0.1594 | experimental |
| takedown_control_model | needs_review | ufc_stats_complete | 0.6343 | 0.0942 | experimental |
| odds_calibration_model | not_run |  |  |  | blocked |

Most non-winner candidates now have source-holdout results. Several were downgraded because transfer to the weakest source was unstable.

## Production Decision
- Do not package artifacts from this audit alone.
- Keep `winner_model` as `high_confidence_only`.
- Keep odds calibration blocked.
- Keep downgraded non-winner models experimental until source-holdout stabilizes.
- Treat `finish_in_round_1_model` and `takedown_control_model` cautiously because their source-holdout status is still `needs_review` or worse.
