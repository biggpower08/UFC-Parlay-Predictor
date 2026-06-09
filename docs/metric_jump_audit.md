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
| winner_model | 0.9585 | 0.9633 | 0.0048 | 3327 -> 3327 | high_confidence_only | 0 / 240 | medium | needs_review | feature schema expanded by 21 fields; base features kept |
| fight_duration_model | 0.8285 | 0.8458 | 0.0173 | 3696 -> 3696 | production_candidate | 10 / 240 | medium | needs_review | feature schema expanded by 21 fields and 10 validation-selected interactions were used |
| finish_model | 0.8285 | 0.8458 | 0.0173 | 3696 -> 3696 | production_candidate | 10 / 240 | medium | needs_review | feature schema expanded by 21 fields and 10 validation-selected interactions were used |
| goes_distance_model | 0.8285 | 0.8458 | 0.0173 | 3696 -> 3696 | production_candidate | 10 / 240 | medium | needs_review | feature schema expanded by 21 fields and 10 validation-selected interactions were used |
| over_1_5_model | 0.7907 | 0.7912 | 0.0005 | 3683 -> 3683 | production_candidate | 5 / 240 | medium | needs_review | feature schema expanded by 21 fields and 5 validation-selected interactions were used |
| over_2_5_model | 0.8086 | 0.8034 | -0.0052 | 3683 -> 3683 | production_candidate | 0 / 240 | medium | needs_review | feature schema expanded by 21 fields; base features kept |
| ends_before_round_3_model | 0.7934 | 0.7825 | -0.0109 | 3683 -> 3683 | production_candidate | 5 / 240 | medium | needs_review | feature schema expanded by 21 fields and 5 validation-selected interactions were used |
| finish_in_round_1_model | 0.8298 | 0.8374 | 0.0076 | 3683 -> 3683 | production_candidate | 0 / 240 | medium | needs_review | feature schema expanded by 21 fields; base features kept |
| finish_type_model | 0.7812 | 0.7751 | -0.0061 | 1796 -> 1796 | experimental | 5 / 240 | medium | needs_review | feature schema expanded by 21 fields and 5 validation-selected interactions were used |
| method_umbrella_model | 0.7484 | 0.7622 | 0.0138 | 3696 -> 3696 | experimental | 0 / 0 | medium | needs_review | feature schema expanded by 21 fields; base features kept |
| strike_volume_model | 0.5825 | 0.5734 | -0.0091 | 1322 -> 1322 | experimental | 20 / 240 | medium | needs_review | feature schema expanded by 21 fields and 20 validation-selected interactions were used |
| takedown_control_model | 0.7385 | 0.7409 | 0.0024 | 2486 -> 2486 | production_candidate | 0 / 240 | medium | needs_review | feature schema expanded by 21 fields; base features kept |
| odds_calibration_model | None | None | None | 0 -> 0 | blocked | 0 / 0 | high | blocked | feature schema expanded by 21 fields; base features kept |

## Source-Holdout Readiness
Non-winner production candidates still carry `source_holdout_not_run`. That means they may remain candidates for internal validation, but they must not become `production_ready` until source-holdout validation is implemented and passes.

## Production Decision
- Do not package artifacts from this audit alone.
- Keep `winner_model` as `high_confidence_only`.
- Keep odds calibration blocked.
- Treat `finish_in_round_1_model` and `takedown_control_model` cautiously until source-holdout confirms the metric gains.
