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
| fight_duration_model | 0.8285 | 0.8596 | 0.0311 | 3696 -> 3327 | production_candidate | 20 / 240 | high | needs_review | row filtering or split changed |
| finish_model | 0.8285 | 0.8596 | 0.0311 | 3696 -> 3327 | production_candidate | 20 / 240 | high | needs_review | row filtering or split changed |
| goes_distance_model | 0.8285 | 0.8596 | 0.0311 | 3696 -> 3327 | production_candidate | 20 / 240 | high | needs_review | row filtering or split changed |
| over_1_5_model | 0.7907 | 0.7947 | 0.004 | 3683 -> 3327 | production_candidate | 10 / 240 | high | needs_review | row filtering or split changed |
| over_2_5_model | 0.8086 | 0.8197 | 0.0111 | 3683 -> 3327 | production_candidate | 5 / 240 | high | needs_review | row filtering or split changed |
| ends_before_round_3_model | 0.7934 | 0.7926 | -0.0008 | 3683 -> 3327 | production_candidate | 0 / 240 | high | needs_review | row filtering or split changed |
| finish_in_round_1_model | 0.8298 | 0.8437 | 0.0139 | 3683 -> 3327 | production_candidate | 5 / 240 | high | needs_review | row filtering or split changed |
| finish_type_model | 0.7812 | 0.7956 | 0.0144 | 1796 -> 1600 | experimental | 0 / 240 | high | needs_review | row filtering or split changed |
| method_umbrella_model | 0.7484 | 0.5191 | -0.2293 | 3696 -> 3327 | weak_or_failed_baseline | 0 / 0 | high | needs_review | row filtering or split changed |
| strike_volume_model | 0.5825 | 0.5749 | -0.0076 | 1322 -> 1322 | experimental | 10 / 240 | high | needs_review | feature schema expanded by 21 fields and 10 validation-selected interactions were used |
| takedown_control_model | 0.7385 | 0.7285 | -0.01 | 2486 -> 2486 | experimental | 0 / 240 | medium | needs_review | feature schema expanded by 21 fields; base features kept |
| odds_calibration_model | None | None | None | 0 -> 0 | blocked | 0 / 0 | high | blocked | feature schema expanded by 21 fields; base features kept |

## Source-Holdout Readiness
| Model | Source-Holdout Status | Worst Source | Worst Metric | Drop | Production Status |
|---|---|---|---:|---:|---|
| winner_model | needs_review | ufc_1994_2026 | 0.8222 | 0.1399 | high_confidence_only |
| fight_duration_model | stable | ufc_1994_2026 | 0.7826 | 0.077 | production_candidate |
| finish_model | stable | ufc_1994_2026 | 0.7826 | 0.077 | production_candidate |
| goes_distance_model | stable | ufc_1994_2026 | 0.7826 | 0.077 | production_candidate |
| over_1_5_model | stable | ufc_1994_2026 | 0.7715 | 0.0232 | production_candidate |
| over_2_5_model | stable | ufc_1994_2026 | 0.7534 | 0.0663 | production_candidate |
| ends_before_round_3_model | stable | ufc_1994_2026 | 0.7552 | 0.0374 | production_candidate |
| finish_in_round_1_model | stable | ufc_1994_2026 | 0.817 | 0.0267 | production_candidate |
| finish_type_model | needs_review | ufc_1994_2025 | 0.8512 | -0.0556 | experimental |
| method_umbrella_model | unstable | ufc_1994_2026 | 0.5155 | 0.0036 | weak_or_failed_baseline |
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
