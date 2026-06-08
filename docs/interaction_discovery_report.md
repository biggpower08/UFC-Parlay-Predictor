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
| winner_model | 240 | 80 | 0 | True | base_features_kept | 0.9288 | None |
| fight_duration_model | 240 | 80 | 5 | True | selected | 0.8706 | 0.8745 |
| over_1_5_model | 240 | 80 | 0 | True | base_features_kept | 0.7245 | None |
| over_2_5_model | 240 | 80 | 0 | True | base_features_kept | 0.8346 | None |
| ends_before_round_3_model | 240 | 80 | 0 | True | base_features_kept | 0.7967 | None |
| finish_in_round_1_model | 240 | 80 | 5 | True | selected | 0.6453 | 0.6564 |
| finish_type_model | 208 | 80 | 5 | True | selected | 0.4783 | 0.4875 |
| method_umbrella_model | 0 | 0 | 0 | None | not_run_composite_model | None | None |
| strike_volume_model | 240 | 80 | 5 | True | selected | 0.4704 | 0.4798 |
| takedown_control_model | 240 | 80 | 0 | True | base_features_kept | 0.6089 | None |
| finish_model | 240 | 80 | 5 | True | selected | 0.8706 | 0.8745 |
| goes_distance_model | 240 | 80 | 5 | True | selected | 0.8706 | 0.8745 |
| method_model | 0 | 0 | 0 | None | not_run_composite_model | None | None |
| round_phase_model | 0 | 0 | 0 | None | not_run_composite_summary | None | None |
| round_model | 0 | 0 | 0 | None | not_run_composite_summary | None | None |
| strike_volume_regression | 0 | 0 | 0 | None | not_run | None | None |
| odds_calibration_model | 0 | 0 | 0 | None | not_run | None | None |

## Candidate Counts By Type
### winner_model
- pairwise_products: 225
- ratios: 1
- absolute_differences: 7
- squared_clipped_log_transforms: 7
- fighter_strength_vs_opponent_weakness: 0
- context_division_interactions: 0
### fight_duration_model
- pairwise_products: 171
- ratios: 1
- absolute_differences: 7
- squared_clipped_log_transforms: 7
- fighter_strength_vs_opponent_weakness: 0
- context_division_interactions: 54
### over_1_5_model
- pairwise_products: 96
- ratios: 1
- absolute_differences: 7
- squared_clipped_log_transforms: 7
- fighter_strength_vs_opponent_weakness: 0
- context_division_interactions: 129
### over_2_5_model
- pairwise_products: 96
- ratios: 1
- absolute_differences: 7
- squared_clipped_log_transforms: 7
- fighter_strength_vs_opponent_weakness: 0
- context_division_interactions: 129
### ends_before_round_3_model
- pairwise_products: 96
- ratios: 1
- absolute_differences: 7
- squared_clipped_log_transforms: 7
- fighter_strength_vs_opponent_weakness: 0
- context_division_interactions: 129
### finish_in_round_1_model
- pairwise_products: 96
- ratios: 1
- absolute_differences: 7
- squared_clipped_log_transforms: 7
- fighter_strength_vs_opponent_weakness: 0
- context_division_interactions: 129
### finish_type_model
- pairwise_products: 46
- ratios: 0
- absolute_differences: 7
- squared_clipped_log_transforms: 7
- fighter_strength_vs_opponent_weakness: 0
- context_division_interactions: 148
### method_umbrella_model
- No interaction candidates were generated.
### strike_volume_model
- pairwise_products: 96
- ratios: 0
- absolute_differences: 7
- squared_clipped_log_transforms: 7
- fighter_strength_vs_opponent_weakness: 0
- context_division_interactions: 130
### takedown_control_model
- pairwise_products: 96
- ratios: 0
- absolute_differences: 7
- squared_clipped_log_transforms: 7
- fighter_strength_vs_opponent_weakness: 0
- context_division_interactions: 130
### finish_model
- pairwise_products: 171
- ratios: 1
- absolute_differences: 7
- squared_clipped_log_transforms: 7
- fighter_strength_vs_opponent_weakness: 0
- context_division_interactions: 54
### goes_distance_model
- pairwise_products: 171
- ratios: 1
- absolute_differences: 7
- squared_clipped_log_transforms: 7
- fighter_strength_vs_opponent_weakness: 0
- context_division_interactions: 54
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
- physical × style: 0
- physical × division: 25
- striking × opponent weakness: 0
- grappling × opponent weakness: 0
- finishing × durability: 0
- pace × age/activity: 0
- scheduled rounds × pace/duration: 0
### fight_duration_model
- physical × style: 25
- physical × division: 25
- striking × opponent weakness: 0
- grappling × opponent weakness: 0
- finishing × durability: 0
- pace × age/activity: 0
- scheduled rounds × pace/duration: 0
### over_1_5_model
- physical × style: 0
- physical × division: 0
- striking × opponent weakness: 0
- grappling × opponent weakness: 0
- finishing × durability: 0
- pace × age/activity: 0
- scheduled rounds × pace/duration: 0
### over_2_5_model
- physical × style: 0
- physical × division: 0
- striking × opponent weakness: 0
- grappling × opponent weakness: 0
- finishing × durability: 0
- pace × age/activity: 0
- scheduled rounds × pace/duration: 0
### ends_before_round_3_model
- physical × style: 0
- physical × division: 0
- striking × opponent weakness: 0
- grappling × opponent weakness: 0
- finishing × durability: 0
- pace × age/activity: 0
- scheduled rounds × pace/duration: 0
### finish_in_round_1_model
- physical × style: 0
- physical × division: 0
- striking × opponent weakness: 0
- grappling × opponent weakness: 0
- finishing × durability: 0
- pace × age/activity: 0
- scheduled rounds × pace/duration: 0
### finish_type_model
- physical × style: 25
- physical × division: 0
- striking × opponent weakness: 0
- grappling × opponent weakness: 0
- finishing × durability: 0
- pace × age/activity: 0
- scheduled rounds × pace/duration: 0
### method_umbrella_model
- No feature-group pair candidates were generated.
### strike_volume_model
- physical × style: 0
- physical × division: 25
- striking × opponent weakness: 0
- grappling × opponent weakness: 0
- finishing × durability: 0
- pace × age/activity: 0
- scheduled rounds × pace/duration: 0
### takedown_control_model
- physical × style: 0
- physical × division: 25
- striking × opponent weakness: 0
- grappling × opponent weakness: 0
- finishing × durability: 0
- pace × age/activity: 0
- scheduled rounds × pace/duration: 0
### finish_model
- physical × style: 25
- physical × division: 25
- striking × opponent weakness: 0
- grappling × opponent weakness: 0
- finishing × durability: 0
- pace × age/activity: 0
- scheduled rounds × pace/duration: 0
### goes_distance_model
- physical × style: 25
- physical × division: 25
- striking × opponent weakness: 0
- grappling × opponent weakness: 0
- finishing × durability: 0
- pace × age/activity: 0
- scheduled rounds × pace/duration: 0
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
- high_correlation: 6
- leakage_risk: 0
- low_variance: 103
- missingness: 0
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 106
### fight_duration_model
- calibration_got_worse: 0
- high_correlation: 4
- leakage_risk: 0
- low_variance: 79
- missingness: 0
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 152
### over_1_5_model
- calibration_got_worse: 0
- high_correlation: 1
- leakage_risk: 0
- low_variance: 64
- missingness: 0
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 175
### over_2_5_model
- calibration_got_worse: 0
- high_correlation: 1
- leakage_risk: 0
- low_variance: 64
- missingness: 0
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 175
### ends_before_round_3_model
- calibration_got_worse: 0
- high_correlation: 1
- leakage_risk: 0
- low_variance: 64
- missingness: 0
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 175
### finish_in_round_1_model
- calibration_got_worse: 0
- high_correlation: 1
- leakage_risk: 0
- low_variance: 64
- missingness: 0
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 170
### finish_type_model
- calibration_got_worse: 0
- high_correlation: 1
- leakage_risk: 0
- low_variance: 86
- missingness: 0
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 103
### method_umbrella_model
- No rejection counts were recorded.
### strike_volume_model
- calibration_got_worse: 0
- high_correlation: 4
- leakage_risk: 0
- low_variance: 110
- missingness: 0
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 109
### takedown_control_model
- calibration_got_worse: 0
- high_correlation: 4
- leakage_risk: 0
- low_variance: 110
- missingness: 0
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 114
### finish_model
- calibration_got_worse: 0
- high_correlation: 4
- leakage_risk: 0
- low_variance: 79
- missingness: 0
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 152
### goes_distance_model
- calibration_got_worse: 0
- high_correlation: 4
- leakage_risk: 0
- low_variance: 79
- missingness: 0
- runtime_incompatibility: 0
- source_holdout_got_worse: 0
- validation_did_not_improve: 152
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
- `int__win_rate_diff_x_finish_rate_diff` (product, groups=('difference', 'difference'), validation improvement=0.0039, final-test impact=0.0025, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0039)
- `int__win_rate_diff_x_decision_rate_diff` (product, groups=('difference', 'difference'), validation improvement=0.0039, final-test impact=0.0025, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0039)
- `int__abs_win_rate_diff` (abs, groups=('nonlinear',), validation improvement=0.0039, final-test impact=0.0025, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0039)
- `int__sq_win_rate_diff` (square, groups=('nonlinear',), validation improvement=0.0039, final-test impact=0.0025, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0039)
- `int__abs_finish_rate_diff` (abs, groups=('nonlinear',), validation improvement=0.0039, final-test impact=0.0025, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0039)
### over_1_5_model
- None selected; base features remained stronger or validation support was insufficient.
### over_2_5_model
- None selected; base features remained stronger or validation support was insufficient.
### ends_before_round_3_model
- None selected; base features remained stronger or validation support was insufficient.
### finish_in_round_1_model
- `int__win_rate_diff_x_finish_rate_diff` (product, groups=('difference', 'difference'), validation improvement=0.0111, final-test impact=0.0133, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0111)
- `int__win_rate_diff_x_decision_rate_diff` (product, groups=('difference', 'difference'), validation improvement=0.0111, final-test impact=0.0133, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0111)
- `int__abs_win_rate_diff` (abs, groups=('nonlinear',), validation improvement=0.0111, final-test impact=0.0133, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0111)
- `int__sq_win_rate_diff` (square, groups=('nonlinear',), validation improvement=0.0111, final-test impact=0.0133, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0111)
- `int__abs_finish_rate_diff` (abs, groups=('nonlinear',), validation improvement=0.0111, final-test impact=0.0133, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0111)
### finish_type_model
- `int__win_rate_diff_x_finish_rate_diff` (product, groups=('difference', 'difference'), validation improvement=0.0092, final-test impact=-0.0093, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0092)
- `int__win_rate_diff_x_decision_rate_diff` (product, groups=('difference', 'difference'), validation improvement=0.0092, final-test impact=-0.0093, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0092)
- `int__abs_win_rate_diff` (abs, groups=('nonlinear',), validation improvement=0.0092, final-test impact=-0.0093, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0092)
- `int__sq_win_rate_diff` (square, groups=('nonlinear',), validation improvement=0.0092, final-test impact=-0.0093, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0092)
- `int__abs_finish_rate_diff` (abs, groups=('nonlinear',), validation improvement=0.0092, final-test impact=-0.0093, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0092)
### method_umbrella_model
- None selected; base features remained stronger or validation support was insufficient.
### strike_volume_model
- `int__win_rate_diff_x_finish_rate_diff` (product, groups=('difference', 'difference'), validation improvement=0.0094, final-test impact=0.0102, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0094)
- `int__win_rate_diff_x_decision_rate_diff` (product, groups=('difference', 'difference'), validation improvement=0.0094, final-test impact=0.0102, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0094)
- `int__abs_win_rate_diff` (abs, groups=('nonlinear',), validation improvement=0.0094, final-test impact=0.0102, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0094)
- `int__sq_win_rate_diff` (square, groups=('nonlinear',), validation improvement=0.0094, final-test impact=0.0102, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0094)
- `int__abs_finish_rate_diff` (abs, groups=('nonlinear',), validation improvement=0.0094, final-test impact=0.0102, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0094)
### takedown_control_model
- None selected; base features remained stronger or validation support was insufficient.
### finish_model
- `int__win_rate_diff_x_finish_rate_diff` (product, groups=['difference', 'difference'], validation improvement=0.0039, final-test impact=0.0025, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0039)
- `int__win_rate_diff_x_decision_rate_diff` (product, groups=['difference', 'difference'], validation improvement=0.0039, final-test impact=0.0025, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0039)
- `int__abs_win_rate_diff` (abs, groups=['nonlinear'], validation improvement=0.0039, final-test impact=0.0025, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0039)
- `int__sq_win_rate_diff` (square, groups=['nonlinear'], validation improvement=0.0039, final-test impact=0.0025, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0039)
- `int__abs_finish_rate_diff` (abs, groups=['nonlinear'], validation improvement=0.0039, final-test impact=0.0025, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0039)
### goes_distance_model
- `int__win_rate_diff_x_finish_rate_diff` (product, groups=['difference', 'difference'], validation improvement=0.0039, final-test impact=0.0025, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0039)
- `int__win_rate_diff_x_decision_rate_diff` (product, groups=['difference', 'difference'], validation improvement=0.0039, final-test impact=0.0025, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0039)
- `int__abs_win_rate_diff` (abs, groups=['nonlinear'], validation improvement=0.0039, final-test impact=0.0025, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0039)
- `int__sq_win_rate_diff` (square, groups=['nonlinear'], validation improvement=0.0039, final-test impact=0.0025, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0039)
- `int__abs_finish_rate_diff` (abs, groups=['nonlinear'], validation improvement=0.0039, final-test impact=0.0025, source-holdout impact=not_run, runtime=training_schema_computable, importance=0.0039)
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
| winner_model | 0.9093 | None | None | 0.9288 | None | 0.9722 | 75.65 | not_run |
| fight_duration_model | 0.8297 | 0.8322 | 0.0025 | 0.8706 | 0.8745 | 0.9276 | 51.92 | not_run |
| over_1_5_model | 0.6758 | None | None | 0.7245 | None | 0.9246 | 36.71 | not_run |
| over_2_5_model | 0.79 | None | None | 0.8346 | None | 0.9225 | 43.77 | not_run |
| ends_before_round_3_model | 0.7611 | None | None | 0.7967 | None | 0.9087 | 42.52 | not_run |
| finish_in_round_1_model | 0.6127 | 0.626 | 0.0133 | 0.6453 | 0.6564 | 0.851 | 8.2 | not_run |
| finish_type_model | 0.44 | 0.4307 | -0.0093 | 0.4783 | 0.4875 | 0.5951 | 31.63 | not_run |
| method_umbrella_model | None | None | None | None | None | 0.9137 | 26.95 | not_run |
| strike_volume_model | 0.4356 | 0.4458 | 0.0102 | 0.4704 | 0.4798 | 0.6545 | 4.16 | not_run |
| takedown_control_model | 0.5485 | None | None | 0.6089 | None | 0.7742 | 8.73 | not_run |
| finish_model | 0.8297 | 0.8322 | 0.0025 | 0.8706 | 0.8745 | 0.9276 | 51.92 | not_run |
| goes_distance_model | 0.8297 | 0.8322 | 0.0025 | 0.8706 | 0.8745 | 0.9276 | 51.92 | not_run |
| method_model | None | None | None | None | None | 0.9137 | 26.95 | not_run |
| round_phase_model | None | None | None | None | None | 0.9225 | 43.77 | not_run |
| round_model | None | None | None | None | None | 0.9225 | 43.77 | not_run |
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
- Coverage gaps: ['fighter_strength_vs_opponent_weakness', 'context_division_interactions', 'physical × style', 'striking × opponent weakness', 'grappling × opponent weakness', 'finishing × durability', 'pace × age/activity', 'scheduled rounds × pace/duration']
- Model improved: False
- Model worsened: False
- Next groups to try: ['fighter_strength_vs_opponent_weakness', 'context_division_interactions', 'physical × style', 'striking × opponent weakness', 'grappling × opponent weakness']
### fight_duration_model
- Enough interactions tested: True
- Coverage gaps: ['fighter_strength_vs_opponent_weakness', 'striking × opponent weakness', 'grappling × opponent weakness', 'finishing × durability', 'pace × age/activity', 'scheduled rounds × pace/duration']
- Model improved: True
- Model worsened: False
- Next groups to try: ['fighter_strength_vs_opponent_weakness', 'striking × opponent weakness', 'grappling × opponent weakness', 'finishing × durability', 'pace × age/activity']
### over_1_5_model
- Enough interactions tested: True
- Coverage gaps: ['fighter_strength_vs_opponent_weakness', 'physical × style', 'physical × division', 'striking × opponent weakness', 'grappling × opponent weakness', 'finishing × durability', 'pace × age/activity', 'scheduled rounds × pace/duration']
- Model improved: False
- Model worsened: False
- Next groups to try: ['fighter_strength_vs_opponent_weakness', 'physical × style', 'physical × division', 'striking × opponent weakness', 'grappling × opponent weakness']
### over_2_5_model
- Enough interactions tested: True
- Coverage gaps: ['fighter_strength_vs_opponent_weakness', 'physical × style', 'physical × division', 'striking × opponent weakness', 'grappling × opponent weakness', 'finishing × durability', 'pace × age/activity', 'scheduled rounds × pace/duration']
- Model improved: False
- Model worsened: False
- Next groups to try: ['fighter_strength_vs_opponent_weakness', 'physical × style', 'physical × division', 'striking × opponent weakness', 'grappling × opponent weakness']
### ends_before_round_3_model
- Enough interactions tested: True
- Coverage gaps: ['fighter_strength_vs_opponent_weakness', 'physical × style', 'physical × division', 'striking × opponent weakness', 'grappling × opponent weakness', 'finishing × durability', 'pace × age/activity', 'scheduled rounds × pace/duration']
- Model improved: False
- Model worsened: False
- Next groups to try: ['fighter_strength_vs_opponent_weakness', 'physical × style', 'physical × division', 'striking × opponent weakness', 'grappling × opponent weakness']
### finish_in_round_1_model
- Enough interactions tested: True
- Coverage gaps: ['fighter_strength_vs_opponent_weakness', 'physical × style', 'physical × division', 'striking × opponent weakness', 'grappling × opponent weakness', 'finishing × durability', 'pace × age/activity', 'scheduled rounds × pace/duration']
- Model improved: True
- Model worsened: False
- Next groups to try: ['fighter_strength_vs_opponent_weakness', 'physical × style', 'physical × division', 'striking × opponent weakness', 'grappling × opponent weakness']
### finish_type_model
- Enough interactions tested: True
- Coverage gaps: ['ratios', 'fighter_strength_vs_opponent_weakness', 'physical × division', 'striking × opponent weakness', 'grappling × opponent weakness', 'finishing × durability', 'pace × age/activity', 'scheduled rounds × pace/duration']
- Model improved: True
- Model worsened: False
- Next groups to try: ['ratios', 'fighter_strength_vs_opponent_weakness', 'physical × division', 'striking × opponent weakness', 'grappling × opponent weakness']
### method_umbrella_model
- No summary judgment was recorded.
### strike_volume_model
- Enough interactions tested: True
- Coverage gaps: ['ratios', 'fighter_strength_vs_opponent_weakness', 'physical × style', 'striking × opponent weakness', 'grappling × opponent weakness', 'finishing × durability', 'pace × age/activity', 'scheduled rounds × pace/duration']
- Model improved: True
- Model worsened: False
- Next groups to try: ['ratios', 'fighter_strength_vs_opponent_weakness', 'physical × style', 'striking × opponent weakness', 'grappling × opponent weakness']
### takedown_control_model
- Enough interactions tested: True
- Coverage gaps: ['ratios', 'fighter_strength_vs_opponent_weakness', 'physical × style', 'striking × opponent weakness', 'grappling × opponent weakness', 'finishing × durability', 'pace × age/activity', 'scheduled rounds × pace/duration']
- Model improved: False
- Model worsened: False
- Next groups to try: ['ratios', 'fighter_strength_vs_opponent_weakness', 'physical × style', 'striking × opponent weakness', 'grappling × opponent weakness']
### finish_model
- Enough interactions tested: True
- Coverage gaps: ['fighter_strength_vs_opponent_weakness', 'striking × opponent weakness', 'grappling × opponent weakness', 'finishing × durability', 'pace × age/activity', 'scheduled rounds × pace/duration']
- Model improved: True
- Model worsened: False
- Next groups to try: ['fighter_strength_vs_opponent_weakness', 'striking × opponent weakness', 'grappling × opponent weakness', 'finishing × durability', 'pace × age/activity']
### goes_distance_model
- Enough interactions tested: True
- Coverage gaps: ['fighter_strength_vs_opponent_weakness', 'striking × opponent weakness', 'grappling × opponent weakness', 'finishing × durability', 'pace × age/activity', 'scheduled rounds × pace/duration']
- Model improved: True
- Model worsened: False
- Next groups to try: ['fighter_strength_vs_opponent_weakness', 'striking × opponent weakness', 'grappling × opponent weakness', 'finishing × durability', 'pace × age/activity']
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
