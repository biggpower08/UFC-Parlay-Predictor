# Model Accuracy Report

## Plain-English Summary
Models were evaluated on the newest chronological holdout from normalized historical fight data. Finish and goes-distance are now one fight-duration model with inverse outputs, while method is estimated from duration plus conditional finish type. Metrics are approximate final-test results, not guarantees.

## Hierarchical Fight Outcome Model
- `fight_duration_model` predicts finish probability; `goes_distance_probability` is `1 - finish_probability`.
- `finish_model` and `goes_distance_model` remain as compatibility report entries backed by the same duration model.
- Round reads are separate binary submodels instead of one broad multiclass round-phase model.
- `finish_type_model` is trained only on fights that actually finished.
- `method_umbrella_model` combines `P(decision) = P(goes_distance)` with `P(KO/TKO or submission) = P(finish) * P(type | finish)`.

## Hierarchy Metrics
| Model | Status | Rows | Accuracy | Balanced Accuracy | ROC AUC | Brier | Baseline | Improvement |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| fight_duration_model | evaluated | 3696 | 0.8458 | 0.8451 | 0.9164 | 0.1155 | 0.5141 | 0.3317 |
| over_1_5_model | evaluated | 3683 | 0.7912 | 0.7146 | 0.8402 | 0.1407 | 0.6964 | 0.0948 |
| over_2_5_model | evaluated | 3683 | 0.8034 | 0.796 | 0.8845 | 0.1364 | 0.5599 | 0.2435 |
| ends_before_round_3_model | evaluated | 3683 | 0.7825 | 0.7602 | 0.8605 | 0.1469 | 0.6066 | 0.1759 |
| finish_in_round_1_model | evaluated | 3683 | 0.8374 | 0.7136 | 0.8672 | 0.1169 | 0.7613 | 0.0761 |
| finish_type_model | evaluated | 1796 | 0.7751 | 0.6275 | None | None | 0.632 | 0.1431 |
| method_umbrella_model | evaluated | 3696 | 0.7622 | 0.5873 | None | None | 0.5141 | 0.2481 |

## Method Probability Logic
- Decision probability comes from the duration model's goes-distance output.
- KO/TKO and submission probabilities are conditional on the fight first being projected to finish.
- The combined method output improved over majority baseline on accuracy, but balanced method metrics remain modest, so it is not production-ready.

## Split
- Train: 29347 rows, {'min': '1993-11-12', 'max': '2021-07-10'}
- Validation: 6134 rows, {'min': '2021-07-10', 'max': '2023-11-18'}
- Final test: 5537 rows, {'min': '2023-11-18', 'max': '2026-05-16'}
- Fight-group leakage check: True

## Source Contributions
- All rows by dataset: {'mdabbert_ultimate': 7190, 'ufc_1994_2025': 16674, 'ufc_1994_2026': 8551, 'ufc_fight_forecast': 8231, 'ufc_stats_complete': 8709}
- Train rows by dataset: {'mdabbert_ultimate': 4771, 'ufc_1994_2025': 6176, 'ufc_1994_2026': 6154, 'ufc_fight_forecast': 6062, 'ufc_stats_complete': 6184}
- Validation rows by dataset: {'mdabbert_ultimate': 1209, 'ufc_1994_2025': 1239, 'ufc_1994_2026': 1233, 'ufc_fight_forecast': 1214, 'ufc_stats_complete': 1239}
- Final test rows by dataset: {'mdabbert_ultimate': 1210, 'ufc_1994_2025': 922, 'ufc_1994_2026': 1164, 'ufc_fight_forecast': 955, 'ufc_stats_complete': 1286}

## Model Ranking
| Model | Status | Test Rows | Main Metric | Baseline | Improvement | Beats Baseline | Notes |
|---|---|---:|---:|---:|---:|---|---|
| winner_model | evaluated | 3327 | 0.9633 | 0.52 | 0.4433 | True |  |
| fight_duration_model | evaluated | 3696 | 0.8458 | 0.5141 | 0.3317 | True |  |
| finish_model | evaluated | 3696 | 0.8458 | 0.5141 | 0.3317 | True | Compatibility output: internally backed by fight_duration_model. |
| goes_distance_model | evaluated | 3696 | 0.8458 | 0.5141 | 0.3317 | True | Compatibility output: goes_distance_probability is derived as 1 - finish_probability. |
| method_umbrella_model | evaluated | 3696 | 0.7622 | 0.5141 | 0.2481 | True | Umbrella method output combines duration probability with conditional finish type probabilities. |
| method_model | evaluated | 3696 | 0.7622 | 0.5141 | 0.2481 | True | Umbrella method output combines duration probability with conditional finish type probabilities.; Compatibility alias backed by method_umbrella_model. |
| over_2_5_model | evaluated | 3683 | 0.8034 | 0.5599 | 0.2435 | True |  |
| round_phase_model | evaluated | 3683 | 0.8034 | 0.5599 | 0.2435 | True | Legacy round_phase_model is replaced by separate binary round-phase submodels. |
| round_model | evaluated | 3683 | 0.8034 | 0.5599 | 0.2435 | True | Legacy round_phase_model is replaced by separate binary round-phase submodels.; Compatibility alias backed by round_phase_model. |
| strike_volume_model | evaluated | 1322 | 0.5734 | 0.3623 | 0.2111 | True |  |
| ends_before_round_3_model | evaluated | 3683 | 0.7825 | 0.6066 | 0.1759 | True |  |
| takedown_control_model | evaluated | 2486 | 0.7409 | 0.5897 | 0.1512 | True |  |
| finish_type_model | evaluated | 1796 | 0.7751 | 0.632 | 0.1431 | True | Conditional model: trained and scored only on fights that actually finished. |
| over_1_5_model | evaluated | 3683 | 0.7912 | 0.6964 | 0.0948 | True |  |
| finish_in_round_1_model | evaluated | 3683 | 0.8374 | 0.7613 | 0.0761 | True |  |
| strike_volume_regression | baseline_only | 1322 | 52.6679 | 50.6327 | -0.0402 | False | Regression model is currently a simple baseline harness; add trained regressors before public use. |
| odds_calibration_model | blocked | 0 |  |  |  | False | Pre-fight odds snapshots are not yet safely matched to outcomes and timestamps. |

## Segment Performance
### winner_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.9661}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.9688}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.9549}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.9306}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.9777}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.9656}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.9714}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.9791}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.963}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.9755}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.9624}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.9709}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8764}
### fight_duration_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8676}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.8481}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.843}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.8458}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.8606}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.8471}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.8397}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.8234}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.84}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.8295}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.8627}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.8471}
- low_fighter_history: {'rows': 341, 'accuracy': 0.8328}
### over_1_5_model
- weight_class:bantamweight: {'rows': 422, 'accuracy': 0.872}
- weight_class:featherweight: {'rows': 426, 'accuracy': 0.7793}
- weight_class:flyweight: {'rows': 292, 'accuracy': 0.7774}
- weight_class:heavyweight: {'rows': 252, 'accuracy': 0.7421}
- weight_class:light_heavyweight: {'rows': 250, 'accuracy': 0.68}
- weight_class:lightweight: {'rows': 481, 'accuracy': 0.7942}
- weight_class:middleweight: {'rows': 473, 'accuracy': 0.7188}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7637}
- weight_class:women's_bantamweight: {'rows': 149, 'accuracy': 0.7852}
- weight_class:women's_flyweight: {'rows': 175, 'accuracy': 0.9029}
- weight_class:women's_strawweight: {'rows': 232, 'accuracy': 0.9224}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.7925}
- low_fighter_history: {'rows': 338, 'accuracy': 0.7781}
### over_2_5_model
- weight_class:bantamweight: {'rows': 422, 'accuracy': 0.8791}
- weight_class:featherweight: {'rows': 426, 'accuracy': 0.784}
- weight_class:flyweight: {'rows': 292, 'accuracy': 0.7911}
- weight_class:heavyweight: {'rows': 252, 'accuracy': 0.8095}
- weight_class:light_heavyweight: {'rows': 250, 'accuracy': 0.78}
- weight_class:lightweight: {'rows': 481, 'accuracy': 0.7755}
- weight_class:middleweight: {'rows': 473, 'accuracy': 0.8182}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7399}
- weight_class:women's_bantamweight: {'rows': 149, 'accuracy': 0.7919}
- weight_class:women's_flyweight: {'rows': 175, 'accuracy': 0.8114}
- weight_class:women's_strawweight: {'rows': 232, 'accuracy': 0.8578}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.8006}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8314}
### ends_before_round_3_model
- weight_class:bantamweight: {'rows': 422, 'accuracy': 0.8341}
- weight_class:featherweight: {'rows': 426, 'accuracy': 0.7535}
- weight_class:flyweight: {'rows': 292, 'accuracy': 0.7603}
- weight_class:heavyweight: {'rows': 252, 'accuracy': 0.7817}
- weight_class:light_heavyweight: {'rows': 250, 'accuracy': 0.776}
- weight_class:lightweight: {'rows': 481, 'accuracy': 0.7214}
- weight_class:middleweight: {'rows': 473, 'accuracy': 0.778}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7589}
- weight_class:women's_bantamweight: {'rows': 149, 'accuracy': 0.7785}
- weight_class:women's_flyweight: {'rows': 175, 'accuracy': 0.8514}
- weight_class:women's_strawweight: {'rows': 232, 'accuracy': 0.8621}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.7803}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8047}
### finish_in_round_1_model
- weight_class:bantamweight: {'rows': 422, 'accuracy': 0.9242}
- weight_class:featherweight: {'rows': 426, 'accuracy': 0.8099}
- weight_class:flyweight: {'rows': 292, 'accuracy': 0.8664}
- weight_class:heavyweight: {'rows': 252, 'accuracy': 0.7659}
- weight_class:light_heavyweight: {'rows': 250, 'accuracy': 0.732}
- weight_class:lightweight: {'rows': 481, 'accuracy': 0.8316}
- weight_class:middleweight: {'rows': 473, 'accuracy': 0.7949}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7947}
- weight_class:women's_bantamweight: {'rows': 149, 'accuracy': 0.8926}
- weight_class:women's_flyweight: {'rows': 175, 'accuracy': 0.9029}
- weight_class:women's_strawweight: {'rows': 232, 'accuracy': 0.944}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.8359}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8521}
### finish_type_model
- weight_class:bantamweight: {'rows': 133, 'accuracy': 0.7068}
- weight_class:featherweight: {'rows': 235, 'accuracy': 0.8468}
- weight_class:flyweight: {'rows': 139, 'accuracy': 0.8273}
- weight_class:heavyweight: {'rows': 128, 'accuracy': 0.7891}
- weight_class:light_heavyweight: {'rows': 166, 'accuracy': 0.7771}
- weight_class:lightweight: {'rows': 249, 'accuracy': 0.6988}
- weight_class:middleweight: {'rows': 280, 'accuracy': 0.7393}
- weight_class:welterweight: {'rows': 235, 'accuracy': 0.834}
- weight_class:women's_bantamweight: {'rows': 60, 'accuracy': 0.8}
- weight_class:women's_strawweight: {'rows': 73, 'accuracy': 0.6027}
- enough_fighter_history: {'rows': 1599, 'accuracy': 0.788}
- low_fighter_history: {'rows': 197, 'accuracy': 0.6701}
### method_umbrella_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8227}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.771}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.802}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.7352}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.7371}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.7438}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.7089}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7351}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.7733}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.8125}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.7768}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.7678}
- low_fighter_history: {'rows': 341, 'accuracy': 0.7067}
### strike_volume_model
- weight_class:bantamweight: {'rows': 150, 'accuracy': 0.62}
- weight_class:featherweight: {'rows': 154, 'accuracy': 0.5779}
- weight_class:flyweight: {'rows': 103, 'accuracy': 0.5922}
- weight_class:heavyweight: {'rows': 99, 'accuracy': 0.5758}
- weight_class:light_heavyweight: {'rows': 90, 'accuracy': 0.5667}
- weight_class:lightweight: {'rows': 175, 'accuracy': 0.5257}
- weight_class:middleweight: {'rows': 175, 'accuracy': 0.56}
- weight_class:welterweight: {'rows': 148, 'accuracy': 0.5338}
- weight_class:women's_bantamweight: {'rows': 55, 'accuracy': 0.6364}
- weight_class:women's_flyweight: {'rows': 62, 'accuracy': 0.5968}
- weight_class:women's_strawweight: {'rows': 83, 'accuracy': 0.5904}
- enough_fighter_history: {'rows': 1227, 'accuracy': 0.5852}
- low_fighter_history: {'rows': 95, 'accuracy': 0.4211}
### takedown_control_model
- weight_class:bantamweight: {'rows': 281, 'accuracy': 0.7438}
- weight_class:featherweight: {'rows': 283, 'accuracy': 0.7244}
- weight_class:flyweight: {'rows': 194, 'accuracy': 0.7526}
- weight_class:heavyweight: {'rows': 172, 'accuracy': 0.7616}
- weight_class:light_heavyweight: {'rows': 166, 'accuracy': 0.8855}
- weight_class:lightweight: {'rows': 323, 'accuracy': 0.6904}
- weight_class:middleweight: {'rows': 320, 'accuracy': 0.7312}
- weight_class:welterweight: {'rows': 280, 'accuracy': 0.7607}
- weight_class:women's_bantamweight: {'rows': 100, 'accuracy': 0.69}
- weight_class:women's_flyweight: {'rows': 116, 'accuracy': 0.8103}
- weight_class:women's_strawweight: {'rows': 154, 'accuracy': 0.6623}
- enough_fighter_history: {'rows': 2195, 'accuracy': 0.7253}
- low_fighter_history: {'rows': 291, 'accuracy': 0.8591}
### finish_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8676}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.8481}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.843}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.8458}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.8606}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.8471}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.8397}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.8234}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.84}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.8295}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.8627}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.8471}
- low_fighter_history: {'rows': 341, 'accuracy': 0.8328}
### goes_distance_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8676}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.8481}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.843}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.8458}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.8606}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.8471}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.8397}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.8234}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.84}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.8295}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.8627}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.8471}
- low_fighter_history: {'rows': 341, 'accuracy': 0.8328}
### method_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8227}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.771}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.802}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.7352}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.7371}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.7438}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.7089}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7351}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.7733}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.8125}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.7768}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.7678}
- low_fighter_history: {'rows': 341, 'accuracy': 0.7067}

## Selective Prediction / High-Confidence Performance
| Model | Best Threshold | Rows | Coverage | Accuracy | Balanced Accuracy | Avg Confidence | Calibration Gap | 80%+ Accuracy? | 95%+ Balanced? |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| winner_model | >=80% | 3084 | 92.7 | 0.9883 | 0.9883 | 0.9832 | -0.0051 | True | True |
| fight_duration_model | >=80% | 2481 | 67.13 | 0.9206 | 0.9206 | 0.9487 | 0.0281 | True | False |
| over_1_5_model | >=80% | 2271 | 61.66 | 0.8956 | 0.7951 | 0.9237 | 0.0281 | True | False |
| over_2_5_model | >=80% | 2199 | 59.71 | 0.9122 | 0.902 | 0.9273 | 0.0151 | True | False |
| ends_before_round_3_model | >=80% | 2134 | 57.94 | 0.8978 | 0.8656 | 0.9249 | 0.027 | True | False |
| finish_in_round_1_model | >=80% | 2670 | 72.5 | 0.915 | 0.7814 | 0.9429 | 0.0279 | True | False |
| finish_type_model | >=80% | 1302 | 72.49 | 0.8702 | 0.7314 | 0.961 | 0.0908 | True | False |
| method_umbrella_model | >=80% | 2053 | 55.55 | 0.906 | 0.7037 | 0.9431 | 0.0371 | True | False |
| strike_volume_model | >=80% | 495 | 37.44 | 0.7374 | 0.701 | 0.9222 | 0.1848 | False | False |
| takedown_control_model | >=80% | 1124 | 45.21 | 0.8701 | 0.7732 | 0.909 | 0.0389 | True | False |
| finish_model | >=80% | 2481 | 67.13 | 0.9206 | 0.9206 | 0.9487 | 0.0281 | True | False |
| goes_distance_model | >=80% | 2481 | 67.13 | 0.9206 | 0.9206 | 0.9487 | 0.0281 | True | False |
| method_model | >=80% | 2053 | 55.55 | 0.906 | 0.7037 | 0.9431 | 0.0371 | True | False |
| round_phase_model | >=80% | 2199 | 59.71 | 0.9122 | 0.902 | 0.9273 | 0.0151 | True | False |
| round_model | >=80% | 2199 | 59.71 | 0.9122 | 0.902 | 0.9273 | 0.0151 | True | False |
| strike_volume_regression |  |  |  |  |  |  |  | False | False |
| odds_calibration_model |  |  |  |  |  |  |  | False | False |

## Interaction Discovery Summary
| Model | Candidates | Accepted | Selected | Selection Status |
|---|---:|---:|---:|---|
| winner_model | 240 | 80 | 0 | base_features_kept |
| fight_duration_model | 240 | 80 | 10 | selected |
| over_1_5_model | 240 | 80 | 5 | selected |
| over_2_5_model | 240 | 80 | 0 | base_features_kept |
| ends_before_round_3_model | 240 | 80 | 5 | selected |
| finish_in_round_1_model | 240 | 80 | 0 | base_features_kept |
| finish_type_model | 240 | 80 | 5 | selected |
| method_umbrella_model | 0 | 0 | 0 | not_run_composite_model |
| strike_volume_model | 240 | 80 | 20 | selected |
| takedown_control_model | 240 | 80 | 0 | base_features_kept |
| finish_model | 240 | 80 | 10 | selected |
| goes_distance_model | 240 | 80 | 10 | selected |
| method_model | 0 | 0 | 0 | not_run_composite_model |
| round_phase_model | 0 | 0 | 0 | not_run_composite_summary |
| round_model | 0 | 0 | 0 | not_run_composite_summary |
| strike_volume_regression | 0 | 0 | 0 | not_run |
| odds_calibration_model | 0 | 0 | 0 | not_run |

## Production Readiness Gates
| Model | Production Status | Passed Gates | Failed Gates | Recommended Use |
|---|---|---|---|---|
| winner_model | high_confidence_only | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, cold_start_low_history_not_dangerously_poor, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists, runtime_parity_passes | source_holdout_stable, winner_leakage_audit_passes | research/high-confidence selective predictions only |
| fight_duration_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| over_1_5_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| over_2_5_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| ends_before_round_3_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| finish_in_round_1_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| finish_type_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | source_holdout_not_run | research only |
| method_umbrella_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | source_holdout_not_run | research only |
| strike_volume_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | calibration_acceptable, source_holdout_not_run | research only |
| takedown_control_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| finish_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| goes_distance_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| method_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | source_holdout_not_run | research only |
| round_phase_model | experimental | beats_chronological_baseline, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, calibration_acceptable, source_holdout_not_run | research only |
| round_model | experimental | beats_chronological_baseline, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, calibration_acceptable, source_holdout_not_run | research only |
| strike_volume_regression | weak_or_failed_baseline | duplicate_mirrored_fight_leakage_prevented, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, high_confidence_not_tiny_sample_noise, source_holdout_not_run | research only |
| odds_calibration_model | blocked |  | model_blocked | not available |
