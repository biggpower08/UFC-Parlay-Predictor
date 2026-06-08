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
| Model | Candidates | Accepted | Selected | Selection Status | Base Validation | Interaction Validation |
|---|---:|---:|---:|---|---|---|
| winner_model | 240 | 80 | 5 | selected | 0.9288 | 0.9351 |
| fight_duration_model | 240 | 80 | 0 | base_features_kept | 0.8706 | None |
| over_1_5_model | 240 | 80 | 0 | base_features_kept | 0.7245 | None |
| over_2_5_model | 240 | 80 | 0 | base_features_kept | 0.8346 | None |
| ends_before_round_3_model | 240 | 80 | 0 | base_features_kept | 0.7967 | None |
| finish_in_round_1_model | 240 | 80 | 5 | selected | 0.6453 | 0.6586 |
| finish_type_model | 208 | 80 | 10 | selected | 0.4783 | 0.4867 |
| method_umbrella_model | 0 | 0 | 0 | not_run_composite_model | None | None |
| strike_volume_model | 240 | 80 | 5 | selected | 0.4704 | 0.4788 |
| takedown_control_model | 240 | 80 | 0 | base_features_kept | 0.6089 | None |
| finish_model | 240 | 80 | 0 | base_features_kept | 0.8706 | None |
| goes_distance_model | 240 | 80 | 0 | base_features_kept | 0.8706 | None |
| method_model | 0 | 0 | 0 | not_run_composite_model | None | None |
| round_phase_model | 0 | 0 | 0 | not_run_composite_summary | None | None |
| round_model | 0 | 0 | 0 | not_run_composite_summary | None | None |
| strike_volume_regression | 0 | 0 | 0 | not_run | None | None |
| odds_calibration_model | 0 | 0 | 0 | not_run | None | None |

## Selected Interactions
### winner_model
- `int__win_rate_diff_x_finish_rate_diff` (product, groups=('difference', 'difference'))
- `int__win_rate_diff_x_decision_rate_diff` (product, groups=('difference', 'difference'))
- `int__finish_rate_diff_x_decision_rate_diff` (product, groups=('difference', 'difference'))
- `int__abs_win_rate_diff` (abs, groups=('nonlinear',))
- `int__sq_win_rate_diff` (square, groups=('nonlinear',))
### fight_duration_model
- None selected; base features remained stronger or validation support was insufficient.
### over_1_5_model
- None selected; base features remained stronger or validation support was insufficient.
### over_2_5_model
- None selected; base features remained stronger or validation support was insufficient.
### ends_before_round_3_model
- None selected; base features remained stronger or validation support was insufficient.
### finish_in_round_1_model
- `int__win_rate_diff_x_finish_rate_diff` (product, groups=('difference', 'difference'))
- `int__win_rate_diff_x_decision_rate_diff` (product, groups=('difference', 'difference'))
- `int__finish_rate_diff_x_decision_rate_diff` (product, groups=('difference', 'difference'))
- `int__abs_win_rate_diff` (abs, groups=('nonlinear',))
- `int__sq_win_rate_diff` (square, groups=('nonlinear',))
### finish_type_model
- `int__win_rate_diff_x_finish_rate_diff` (product, groups=('difference', 'difference'))
- `int__win_rate_diff_x_decision_rate_diff` (product, groups=('difference', 'difference'))
- `int__finish_rate_diff_x_decision_rate_diff` (product, groups=('difference', 'difference'))
- `int__abs_win_rate_diff` (abs, groups=('nonlinear',))
- `int__sq_win_rate_diff` (square, groups=('nonlinear',))
- `int__abs_finish_rate_diff` (abs, groups=('nonlinear',))
- `int__sq_finish_rate_diff` (square, groups=('nonlinear',))
- `int__abs_decision_rate_diff` (abs, groups=('nonlinear',))
- `int__sq_decision_rate_diff` (square, groups=('nonlinear',))
- `int__a_prior_decisions_x_cross_division_warning` (product, groups=('finishing', 'physical'))
### method_umbrella_model
- None selected; base features remained stronger or validation support was insufficient.
### strike_volume_model
- `int__win_rate_diff_x_finish_rate_diff` (product, groups=('difference', 'difference'))
- `int__win_rate_diff_x_decision_rate_diff` (product, groups=('difference', 'difference'))
- `int__finish_rate_diff_x_decision_rate_diff` (product, groups=('difference', 'difference'))
- `int__abs_win_rate_diff` (abs, groups=('nonlinear',))
- `int__sq_win_rate_diff` (square, groups=('nonlinear',))
### takedown_control_model
- None selected; base features remained stronger or validation support was insufficient.
### finish_model
- None selected; base features remained stronger or validation support was insufficient.
### goes_distance_model
- None selected; base features remained stronger or validation support was insufficient.
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
