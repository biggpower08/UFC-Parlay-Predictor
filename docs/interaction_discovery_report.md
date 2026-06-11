# Interaction Discovery Report

## Plain-English Summary
Candidate interactions are generated from safe pre-fight feature groups, selected on validation only, and then evaluated on the final chronological holdout.

## How Interaction Discovery Works
- Features are grouped by meaning, such as physical, experience, striking, grappling, finishing, division/context, and opponent weakness.
- Candidate interactions are generated programmatically from safe pre-fight features.
- Candidates are rejected for low coverage, low variance, forbidden inputs, or candidate-cap overflow.
- Selection uses train/validation data only. Final-test rows are not used to choose interactions.
- Selected interactions are included only when validation balanced performance improves without a large log-loss regression.

## Model Summary
| Model | Candidates | Accepted | Selected | Enough Tested | Selection Status | Base Validation | Interaction Validation |
|---|---:|---:|---:|---|---|---|---|
| winner_model | 240 | 80 | 0 | True | base_features_kept | 0.9986 | None |
| fight_duration_model | 240 | 80 | 20 | True | selected | 0.8832 | 0.8864 |
| over_1_5_model | 240 | 80 | 10 | True | selected | 0.7631 | 0.7711 |
| over_2_5_model | 240 | 80 | 5 | True | selected | 0.8246 | 0.8307 |
| ends_before_round_3_model | 240 | 80 | 0 | True | base_features_kept | 0.801 | None |
| finish_in_round_1_model | 240 | 80 | 5 | True | selected | 0.7855 | 0.7903 |
| finish_type_model | 240 | 80 | 0 | True | base_features_kept | 0.7572 | None |
| method_umbrella_model | 0 | 0 | 0 | None | not_run_composite_model | None | None |
| strike_volume_model | 240 | 80 | 10 | True | selected | 0.6567 | 0.6714 |
| takedown_control_model | 240 | 80 | 0 | True | base_features_kept | 0.7266 | None |
| finish_model | 240 | 80 | 20 | True | selected | 0.8832 | 0.8864 |
| goes_distance_model | 240 | 80 | 20 | True | selected | 0.8832 | 0.8864 |
| method_model | 0 | 0 | 0 | None | not_run_composite_model | None | None |
| round_phase_model | 0 | 0 | 0 | None | not_run_composite_summary | None | None |
| round_model | 0 | 0 | 0 | None | not_run_composite_summary | None | None |
| strike_volume_regression | 0 | 0 | 0 | None | not_run | None | None |
| odds_calibration_model | 0 | 0 | 0 | None | not_run | None | None |

## Candidate Counts By Type
### winner_model
- pairwise_products: 96
- ratios: 0
- absolute_differences: 0
- squared_clipped_log_transforms: 0
- fighter_strength_vs_opponent_weakness: 108
- context_division_interactions: 36
### fight_duration_model
- pairwise_products: 96
- ratios: 0
- absolute_differences: 0
- squared_clipped_log_transforms: 0
- fighter_strength_vs_opponent_weakness: 108
- context_division_interactions: 36
### over_1_5_model
- pairwise_products: 96
- ratios: 0
- absolute_differences: 0
- squared_clipped_log_transforms: 0
- fighter_strength_vs_opponent_weakness: 108
- context_division_interactions: 36
### over_2_5_model
- pairwise_products: 96
- ratios: 0
- absolute_differences: 0
- squared_clipped_log_transforms: 0
- fighter_strength_vs_opponent_weakness: 108
- context_division_interactions: 36
### ends_before_round_3_model
- pairwise_products: 96
- ratios: 0
- absolute_differences: 0
- squared_clipped_log_transforms: 0
- fighter_strength_vs_opponent_weakness: 108
- context_division_interactions: 36
### finish_in_round_1_model
- pairwise_products: 96
- ratios: 0
- absolute_differences: 0
- squared_clipped_log_transforms: 0
- fighter_strength_vs_opponent_weakness: 108
- context_division_interactions: 36
### finish_type_model
- pairwise_products: 96
- ratios: 0
- absolute_differences: 0
- squared_clipped_log_transforms: 0
- fighter_strength_vs_opponent_weakness: 108
- context_division_interactions: 36
### method_umbrella_model
- No interaction candidates were generated.
### strike_volume_model
- pairwise_products: 96
- ratios: 0
- absolute_differences: 0
- squared_clipped_log_transforms: 0
- fighter_strength_vs_opponent_weakness: 108
- context_division_interactions: 36
### takedown_control_model
- pairwise_products: 96
- ratios: 0
- absolute_differences: 0
- squared_clipped_log_transforms: 0
- fighter_strength_vs_opponent_weakness: 108
- context_division_interactions: 36
### finish_model
- pairwise_products: 96
- ratios: 0
- absolute_differences: 0
- squared_clipped_log_transforms: 0
- fighter_strength_vs_opponent_weakness: 108
- context_division_interactions: 36
### goes_distance_model
- pairwise_products: 96
- ratios: 0
- absolute_differences: 0
- squared_clipped_log_transforms: 0
- fighter_strength_vs_opponent_weakness: 108
- context_division_interactions: 36
### method_model
- No interaction candidates were generated.
### round_phase_model
- No interaction candidates were generated.
### round_model
- No interaction candidates were generated.
### strike_volume_regression
- No interaction candidates were generated.
### odds_calibration_model
- No interaction candidates were generated.

## Candidate Counts By Feature-Group Pair
### winner_model
- physical x style: 0
- physical x division: 36
- striking x opponent weakness: 36
- grappling x opponent weakness: 36
- finishing x durability: 36
- pace x age/activity: 36
- scheduled rounds x pace/duration: 6
### fight_duration_model
- physical x style: 0
- physical x division: 36
- striking x opponent weakness: 36
- grappling x opponent weakness: 36
- finishing x durability: 36
- pace x age/activity: 36
- scheduled rounds x pace/duration: 6
### over_1_5_model
- physical x style: 0
- physical x division: 36
- striking x opponent weakness: 36
- grappling x opponent weakness: 36
- finishing x durability: 36
- pace x age/activity: 36
- scheduled rounds x pace/duration: 6
### over_2_5_model
- physical x style: 0
- physical x division: 36
- striking x opponent weakness: 36
- grappling x opponent weakness: 36
- finishing x durability: 36
- pace x age/activity: 36
- scheduled rounds x pace/duration: 6
### ends_before_round_3_model
- physical x style: 0
- physical x division: 36
- striking x opponent weakness: 36
- grappling x opponent weakness: 36
- finishing x durability: 36
- pace x age/activity: 36
- scheduled rounds x pace/duration: 6
### finish_in_round_1_model
- physical x style: 0
- physical x division: 36
- striking x opponent weakness: 36
- grappling x opponent weakness: 36
- finishing x durability: 36
- pace x age/activity: 36
- scheduled rounds x pace/duration: 6
### finish_type_model
- physical x style: 0
- physical x division: 36
- striking x opponent weakness: 36
- grappling x opponent weakness: 36
- finishing x durability: 36
- pace x age/activity: 36
- scheduled rounds x pace/duration: 6
### method_umbrella_model
- No feature-group pair candidates were generated.
### strike_volume_model
- physical x style: 0
- physical x division: 36
- striking x opponent weakness: 36
- grappling x opponent weakness: 36
- finishing x durability: 36
- pace x age/activity: 36
- scheduled rounds x pace/duration: 6
### takedown_control_model
- physical x style: 0
- physical x division: 36
- striking x opponent weakness: 36
- grappling x opponent weakness: 36
- finishing x durability: 36
- pace x age/activity: 36
- scheduled rounds x pace/duration: 6
### finish_model
- physical x style: 0
- physical x division: 36
- striking x opponent weakness: 36
- grappling x opponent weakness: 36
- finishing x durability: 36
- pace x age/activity: 36
- scheduled rounds x pace/duration: 6
### goes_distance_model
- physical x style: 0
- physical x division: 36
- striking x opponent weakness: 36
- grappling x opponent weakness: 36
- finishing x durability: 36
- pace x age/activity: 36
- scheduled rounds x pace/duration: 6
### method_model
- No feature-group pair candidates were generated.
### round_phase_model
- No feature-group pair candidates were generated.
### round_model
- No feature-group pair candidates were generated.
### strike_volume_regression
- No feature-group pair candidates were generated.
### odds_calibration_model
- No feature-group pair candidates were generated.

## Rejection Counts
### winner_model
- calibration_got_worse: 0
- high_correlation: 0
- leakage_risk: 0
- low_variance: 0
- missingness: 2
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 238
### fight_duration_model
- calibration_got_worse: 0
- high_correlation: 0
- leakage_risk: 0
- low_variance: 0
- missingness: 2
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 218
### over_1_5_model
- calibration_got_worse: 0
- high_correlation: 0
- leakage_risk: 0
- low_variance: 0
- missingness: 2
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 228
### over_2_5_model
- calibration_got_worse: 0
- high_correlation: 0
- leakage_risk: 0
- low_variance: 0
- missingness: 2
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 233
### ends_before_round_3_model
- calibration_got_worse: 0
- high_correlation: 0
- leakage_risk: 0
- low_variance: 0
- missingness: 2
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 238
### finish_in_round_1_model
- calibration_got_worse: 0
- high_correlation: 0
- leakage_risk: 0
- low_variance: 0
- missingness: 2
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 233
### finish_type_model
- calibration_got_worse: 0
- high_correlation: 0
- leakage_risk: 0
- low_variance: 0
- missingness: 2
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 238
### method_umbrella_model
- No rejection counts were recorded.
### strike_volume_model
- calibration_got_worse: 0
- high_correlation: 0
- leakage_risk: 0
- low_variance: 0
- missingness: 2
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 228
### takedown_control_model
- calibration_got_worse: 0
- high_correlation: 0
- leakage_risk: 0
- low_variance: 0
- missingness: 2
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 238
### finish_model
- calibration_got_worse: 0
- high_correlation: 0
- leakage_risk: 0
- low_variance: 0
- missingness: 2
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 218
### goes_distance_model
- calibration_got_worse: 0
- high_correlation: 0
- leakage_risk: 0
- low_variance: 0
- missingness: 2
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 218
### method_model
- No rejection counts were recorded.
### round_phase_model
- No rejection counts were recorded.
### round_model
- No rejection counts were recorded.
### strike_volume_regression
- No rejection counts were recorded.
### odds_calibration_model
- No rejection counts were recorded.

## Selected Interactions
### winner_model
- None selected; base features remained stronger or validation support was insufficient.
### fight_duration_model
- `int__fighter_1_striker_score_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_striker_score_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_striker_score_x_strike_absorption_weakness_diff` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_striker_score_x_fighter_1_low_activity_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_striker_score_x_fighter_2_low_activity_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_striker_score_x_low_activity_weakness_diff` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_strike_absorption_weakness_diff` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_fighter_1_low_activity_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_fighter_2_low_activity_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_low_activity_weakness_diff` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_strike_absorption_weakness_diff` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_fighter_1_low_activity_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_fighter_2_low_activity_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_low_activity_weakness_diff` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_high_volume_striker_score_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_high_volume_striker_score_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
### over_1_5_model
- `int__fighter_1_striker_score_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.008, final-test impact=-0.0174, source-holdout impact=0.0232, runtime=training_schema_computable, importance=0.008)
- `int__fighter_1_striker_score_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.008, final-test impact=-0.0174, source-holdout impact=0.0232, runtime=training_schema_computable, importance=0.008)
- `int__fighter_1_striker_score_x_strike_absorption_weakness_diff` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.008, final-test impact=-0.0174, source-holdout impact=0.0232, runtime=training_schema_computable, importance=0.008)
- `int__fighter_1_striker_score_x_fighter_1_low_activity_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.008, final-test impact=-0.0174, source-holdout impact=0.0232, runtime=training_schema_computable, importance=0.008)
- `int__fighter_1_striker_score_x_fighter_2_low_activity_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.008, final-test impact=-0.0174, source-holdout impact=0.0232, runtime=training_schema_computable, importance=0.008)
- `int__fighter_1_striker_score_x_low_activity_weakness_diff` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.008, final-test impact=-0.0174, source-holdout impact=0.0232, runtime=training_schema_computable, importance=0.008)
- `int__fighter_2_striker_score_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.008, final-test impact=-0.0174, source-holdout impact=0.0232, runtime=training_schema_computable, importance=0.008)
- `int__fighter_2_striker_score_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.008, final-test impact=-0.0174, source-holdout impact=0.0232, runtime=training_schema_computable, importance=0.008)
- `int__fighter_2_striker_score_x_strike_absorption_weakness_diff` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.008, final-test impact=-0.0174, source-holdout impact=0.0232, runtime=training_schema_computable, importance=0.008)
- `int__fighter_2_striker_score_x_fighter_1_low_activity_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.008, final-test impact=-0.0174, source-holdout impact=0.0232, runtime=training_schema_computable, importance=0.008)
### over_2_5_model
- `int__fighter_1_striker_score_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0061, final-test impact=-0.0041, source-holdout impact=0.0663, runtime=training_schema_computable, importance=0.0061)
- `int__fighter_1_striker_score_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0061, final-test impact=-0.0041, source-holdout impact=0.0663, runtime=training_schema_computable, importance=0.0061)
- `int__fighter_1_striker_score_x_strike_absorption_weakness_diff` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0061, final-test impact=-0.0041, source-holdout impact=0.0663, runtime=training_schema_computable, importance=0.0061)
- `int__fighter_1_striker_score_x_fighter_1_low_activity_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0061, final-test impact=-0.0041, source-holdout impact=0.0663, runtime=training_schema_computable, importance=0.0061)
- `int__fighter_1_striker_score_x_fighter_2_low_activity_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0061, final-test impact=-0.0041, source-holdout impact=0.0663, runtime=training_schema_computable, importance=0.0061)
### ends_before_round_3_model
- None selected; base features remained stronger or validation support was insufficient.
### finish_in_round_1_model
- `int__fighter_1_striker_score_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0048, final-test impact=-0.0038, source-holdout impact=0.0267, runtime=training_schema_computable, importance=0.0048)
- `int__fighter_1_striker_score_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0048, final-test impact=-0.0038, source-holdout impact=0.0267, runtime=training_schema_computable, importance=0.0048)
- `int__fighter_1_striker_score_x_strike_absorption_weakness_diff` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0048, final-test impact=-0.0038, source-holdout impact=0.0267, runtime=training_schema_computable, importance=0.0048)
- `int__fighter_1_striker_score_x_fighter_1_low_activity_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0048, final-test impact=-0.0038, source-holdout impact=0.0267, runtime=training_schema_computable, importance=0.0048)
- `int__fighter_1_striker_score_x_fighter_2_low_activity_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0048, final-test impact=-0.0038, source-holdout impact=0.0267, runtime=training_schema_computable, importance=0.0048)
### finish_type_model
- None selected; base features remained stronger or validation support was insufficient.
### method_umbrella_model
- None selected; base features remained stronger or validation support was insufficient.
### strike_volume_model
- `int__fighter_1_striker_score_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0147, final-test impact=0.0036, source-holdout impact=0.1594, runtime=training_schema_computable, importance=0.0147)
- `int__fighter_1_striker_score_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0147, final-test impact=0.0036, source-holdout impact=0.1594, runtime=training_schema_computable, importance=0.0147)
- `int__fighter_1_striker_score_x_strike_absorption_weakness_diff` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0147, final-test impact=0.0036, source-holdout impact=0.1594, runtime=training_schema_computable, importance=0.0147)
- `int__fighter_1_striker_score_x_fighter_1_low_activity_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0147, final-test impact=0.0036, source-holdout impact=0.1594, runtime=training_schema_computable, importance=0.0147)
- `int__fighter_1_striker_score_x_fighter_2_low_activity_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0147, final-test impact=0.0036, source-holdout impact=0.1594, runtime=training_schema_computable, importance=0.0147)
- `int__fighter_1_striker_score_x_low_activity_weakness_diff` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0147, final-test impact=0.0036, source-holdout impact=0.1594, runtime=training_schema_computable, importance=0.0147)
- `int__fighter_2_striker_score_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0147, final-test impact=0.0036, source-holdout impact=0.1594, runtime=training_schema_computable, importance=0.0147)
- `int__fighter_2_striker_score_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0147, final-test impact=0.0036, source-holdout impact=0.1594, runtime=training_schema_computable, importance=0.0147)
- `int__fighter_2_striker_score_x_strike_absorption_weakness_diff` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0147, final-test impact=0.0036, source-holdout impact=0.1594, runtime=training_schema_computable, importance=0.0147)
- `int__fighter_2_striker_score_x_fighter_1_low_activity_weakness` (strength_vs_weakness, groups=('striking', 'opponent_weakness'), validation improvement=0.0147, final-test impact=0.0036, source-holdout impact=0.1594, runtime=training_schema_computable, importance=0.0147)
### takedown_control_model
- None selected; base features remained stronger or validation support was insufficient.
### finish_model
- `int__fighter_1_striker_score_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_striker_score_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_striker_score_x_strike_absorption_weakness_diff` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_striker_score_x_fighter_1_low_activity_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_striker_score_x_fighter_2_low_activity_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_striker_score_x_low_activity_weakness_diff` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_strike_absorption_weakness_diff` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_fighter_1_low_activity_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_fighter_2_low_activity_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_low_activity_weakness_diff` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_strike_absorption_weakness_diff` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_fighter_1_low_activity_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_fighter_2_low_activity_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_low_activity_weakness_diff` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_high_volume_striker_score_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_high_volume_striker_score_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
### goes_distance_model
- `int__fighter_1_striker_score_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_striker_score_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_striker_score_x_strike_absorption_weakness_diff` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_striker_score_x_fighter_1_low_activity_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_striker_score_x_fighter_2_low_activity_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_striker_score_x_low_activity_weakness_diff` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_strike_absorption_weakness_diff` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_fighter_1_low_activity_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_fighter_2_low_activity_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_2_striker_score_x_low_activity_weakness_diff` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_strike_absorption_weakness_diff` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_fighter_1_low_activity_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_fighter_2_low_activity_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__striker_score_diff_x_low_activity_weakness_diff` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_high_volume_striker_score_x_fighter_1_strike_absorption_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
- `int__fighter_1_high_volume_striker_score_x_fighter_2_strike_absorption_weakness` (strength_vs_weakness, groups=['striking', 'opponent_weakness'], validation improvement=0.0032, final-test impact=0.0023, source-holdout impact=0.077, runtime=training_schema_computable, importance=0.0032)
### method_model
- None selected; base features remained stronger or validation support was insufficient.
### round_phase_model
- None selected; base features remained stronger or validation support was insufficient.
### round_model
- None selected; base features remained stronger or validation support was insufficient.
### strike_volume_regression
- None selected; base features remained stronger or validation support was insufficient.
### odds_calibration_model
- None selected; base features remained stronger or validation support was insufficient.

## Base Vs Interaction Comparison
| Model | Base Final Balanced | Interaction Final Balanced | Final Impact | Base Validation Balanced | Interaction Validation Balanced | High-Confidence Accuracy | High-Confidence Coverage | Source Holdout |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| winner_model | 0.9622 | None | None | 0.9986 | None | 0.9891 | 93.75 | needs_review |
| fight_duration_model | 0.8563 | 0.8586 | 0.0023 | 0.8832 | 0.8864 | 0.9659 | 56.42 | stable |
| over_1_5_model | 0.7179 | 0.7005 | -0.0174 | 0.7631 | 0.7711 | 0.9178 | 55.21 | stable |
| over_2_5_model | 0.8123 | 0.8082 | -0.0041 | 0.8246 | 0.8307 | 0.9444 | 49.17 | stable |
| ends_before_round_3_model | 0.7698 | None | None | 0.801 | None | 0.9384 | 47.34 | stable |
| finish_in_round_1_model | 0.7079 | 0.7041 | -0.0038 | 0.7855 | 0.7903 | 0.9311 | 68.92 | stable |
| finish_type_model | 0.7032 | None | None | 0.7572 | None | 0.9348 | 68.06 | needs_review |
| method_umbrella_model | None | None | None | None | None | 0.5191 | 100.0 | unstable |
| strike_volume_model | 0.5562 | 0.5598 | 0.0036 | 0.6567 | 0.6714 | 0.7644 | 30.18 | unstable |
| takedown_control_model | 0.6893 | None | None | 0.7266 | None | 0.8697 | 39.5 | needs_review |
| finish_model | 0.8563 | 0.8586 | 0.0023 | 0.8832 | 0.8864 | 0.9659 | 56.42 | stable |
| goes_distance_model | 0.8563 | 0.8586 | 0.0023 | 0.8832 | 0.8864 | 0.9659 | 56.42 | stable |
| method_model | None | None | None | None | None | 0.5191 | 100.0 | unstable |
| round_phase_model | None | None | None | None | None | 0.9444 | 49.17 | stable |
| round_model | None | None | None | None | None | 0.9444 | 49.17 | stable |
| strike_volume_regression | None | None | None | None | None | None | None | not_run |
| odds_calibration_model | None | None | None | None | None | None | None | not_run |

## Safety Checks
### winner_model
- selection_uses_validation_only: True
- final_test_used_for_selection: False
- forbidden_target_columns_excluded: True
- selected_interactions_runtime_computable: True
- source_holdout_regression_blocks_production: True
### fight_duration_model
- selection_uses_validation_only: True
- final_test_used_for_selection: False
- forbidden_target_columns_excluded: True
- selected_interactions_runtime_computable: True
- source_holdout_regression_blocks_production: True
### over_1_5_model
- selection_uses_validation_only: True
- final_test_used_for_selection: False
- forbidden_target_columns_excluded: True
- selected_interactions_runtime_computable: True
- source_holdout_regression_blocks_production: True
### over_2_5_model
- selection_uses_validation_only: True
- final_test_used_for_selection: False
- forbidden_target_columns_excluded: True
- selected_interactions_runtime_computable: True
- source_holdout_regression_blocks_production: True
### ends_before_round_3_model
- selection_uses_validation_only: True
- final_test_used_for_selection: False
- forbidden_target_columns_excluded: True
- selected_interactions_runtime_computable: True
- source_holdout_regression_blocks_production: True
### finish_in_round_1_model
- selection_uses_validation_only: True
- final_test_used_for_selection: False
- forbidden_target_columns_excluded: True
- selected_interactions_runtime_computable: True
- source_holdout_regression_blocks_production: True
### finish_type_model
- selection_uses_validation_only: True
- final_test_used_for_selection: False
- forbidden_target_columns_excluded: True
- selected_interactions_runtime_computable: True
- source_holdout_regression_blocks_production: True
### method_umbrella_model
- No interaction safety checks were recorded.
### strike_volume_model
- selection_uses_validation_only: True
- final_test_used_for_selection: False
- forbidden_target_columns_excluded: True
- selected_interactions_runtime_computable: True
- source_holdout_regression_blocks_production: True
### takedown_control_model
- selection_uses_validation_only: True
- final_test_used_for_selection: False
- forbidden_target_columns_excluded: True
- selected_interactions_runtime_computable: True
- source_holdout_regression_blocks_production: True
### finish_model
- selection_uses_validation_only: True
- final_test_used_for_selection: False
- forbidden_target_columns_excluded: True
- selected_interactions_runtime_computable: True
- source_holdout_regression_blocks_production: True
### goes_distance_model
- selection_uses_validation_only: True
- final_test_used_for_selection: False
- forbidden_target_columns_excluded: True
- selected_interactions_runtime_computable: True
- source_holdout_regression_blocks_production: True
### method_model
- No interaction safety checks were recorded.
### round_phase_model
- No interaction safety checks were recorded.
### round_model
- No interaction safety checks were recorded.
### strike_volume_regression
- No interaction safety checks were recorded.
### odds_calibration_model
- No interaction safety checks were recorded.

## Summary Judgment
### winner_model
- Enough interactions tested: True
- Coverage gaps: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
- Model improved: False
- Model worsened: False
- Next groups to try: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
### fight_duration_model
- Enough interactions tested: True
- Coverage gaps: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
- Model improved: True
- Model worsened: False
- Next groups to try: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
### over_1_5_model
- Enough interactions tested: True
- Coverage gaps: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
- Model improved: True
- Model worsened: False
- Next groups to try: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
### over_2_5_model
- Enough interactions tested: True
- Coverage gaps: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
- Model improved: True
- Model worsened: False
- Next groups to try: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
### ends_before_round_3_model
- Enough interactions tested: True
- Coverage gaps: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
- Model improved: False
- Model worsened: False
- Next groups to try: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
### finish_in_round_1_model
- Enough interactions tested: True
- Coverage gaps: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
- Model improved: True
- Model worsened: False
- Next groups to try: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
### finish_type_model
- Enough interactions tested: True
- Coverage gaps: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
- Model improved: False
- Model worsened: False
- Next groups to try: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
### method_umbrella_model
- No summary judgment was recorded.
### strike_volume_model
- Enough interactions tested: True
- Coverage gaps: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
- Model improved: True
- Model worsened: False
- Next groups to try: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
### takedown_control_model
- Enough interactions tested: True
- Coverage gaps: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
- Model improved: False
- Model worsened: False
- Next groups to try: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
### finish_model
- Enough interactions tested: True
- Coverage gaps: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
- Model improved: True
- Model worsened: False
- Next groups to try: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
### goes_distance_model
- Enough interactions tested: True
- Coverage gaps: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
- Model improved: True
- Model worsened: False
- Next groups to try: ['ratios', 'absolute_differences', 'squared_clipped_log_transforms', 'physical x style']
### method_model
- No summary judgment was recorded.
### round_phase_model
- No summary judgment was recorded.
### round_model
- No summary judgment was recorded.
### strike_volume_regression
- No summary judgment was recorded.
### odds_calibration_model
- No summary judgment was recorded.

## Rejection Summary
### winner_model
- Pre-selection rejected examples: 25 shown.
- Validation rejected examples: 25 shown.
### fight_duration_model
- Pre-selection rejected examples: 25 shown.
- Validation rejected examples: 25 shown.
### over_1_5_model
- Pre-selection rejected examples: 25 shown.
- Validation rejected examples: 25 shown.
### over_2_5_model
- Pre-selection rejected examples: 25 shown.
- Validation rejected examples: 25 shown.
### ends_before_round_3_model
- Pre-selection rejected examples: 25 shown.
- Validation rejected examples: 25 shown.
### finish_in_round_1_model
- Pre-selection rejected examples: 25 shown.
- Validation rejected examples: 25 shown.
### finish_type_model
- Pre-selection rejected examples: 25 shown.
- Validation rejected examples: 25 shown.
### method_umbrella_model
- Pre-selection rejected examples: 0 shown.
- Validation rejected examples: 0 shown.
### strike_volume_model
- Pre-selection rejected examples: 25 shown.
- Validation rejected examples: 25 shown.
### takedown_control_model
- Pre-selection rejected examples: 25 shown.
- Validation rejected examples: 25 shown.
### finish_model
- Pre-selection rejected examples: 25 shown.
- Validation rejected examples: 25 shown.
### goes_distance_model
- Pre-selection rejected examples: 25 shown.
- Validation rejected examples: 25 shown.
### method_model
- Pre-selection rejected examples: 0 shown.
- Validation rejected examples: 0 shown.
### round_phase_model
- Pre-selection rejected examples: 0 shown.
- Validation rejected examples: 0 shown.
### round_model
- Pre-selection rejected examples: 0 shown.
- Validation rejected examples: 0 shown.
### strike_volume_regression
- Pre-selection rejected examples: 0 shown.
- Validation rejected examples: 0 shown.
### odds_calibration_model
- Pre-selection rejected examples: 0 shown.
- Validation rejected examples: 0 shown.
