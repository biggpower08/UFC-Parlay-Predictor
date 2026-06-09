# Historical Fight Backtest Report

## Plain-English Summary
This backtest simulated 5537 historical fights by hiding outcome labels until after model predictions were generated from pre-fight features. Duration is now backtested as one finish/goes-distance model, round reads are separate binary models, and method is scored through the duration-plus-finish-type umbrella.

## Hierarchical Outcome Backtest
| Model | Fights | Accuracy | Balanced Accuracy | Baseline | Improvement | Status |
|---|---:|---:|---:|---:|---:|---|
| fight_duration_model | 3696 | 0.8458 | 0.8451 | 0.5141 | 0.3317 | backtested |
| over_1_5_model | 3683 | 0.7912 | 0.7146 | 0.6964 | 0.0948 | backtested |
| over_2_5_model | 3683 | 0.8034 | 0.796 | 0.5599 | 0.2435 | backtested |
| ends_before_round_3_model | 3683 | 0.7825 | 0.7602 | 0.6066 | 0.1759 | backtested |
| finish_in_round_1_model | 3683 | 0.8374 | 0.7136 | 0.7613 | 0.0761 | backtested |
| finish_type_model | 1796 | 0.7751 | 0.6275 | 0.632 | 0.1431 | backtested |
| method_umbrella_model | 3696 | 0.7622 | 0.5873 | 0.5141 | 0.2481 | backtested |

## Combined Method Logic
- Decision probability is scored from the duration model's goes-distance output.
- KO/TKO and submission are scored as finish probability multiplied by conditional finish-type probability.
- Method is still treated cautiously because finish-type performance remains weak.

## Backtest Setup
- Date range: {'min': '2023-11-18', 'max': '2026-05-16'}
- Data hidden before prediction: combined_sig_strikes, ends_before_round_3_binary, fighter_a_sig_strikes, fighter_a_takedowns, fighter_b_sig_strikes, fighter_b_takedowns, finish_binary, finish_in_round_1_binary, finish_round, finish_time, finish_type_class, goes_distance_binary, grappling_heavy_binary, loser, method, method_class, method_group, over_1_5_binary, over_2_5_binary, result, round_phase_class, takedown_control_bucket, winner
- Models run: winner_model, fight_duration_model, over_1_5_model, over_2_5_model, ends_before_round_3_model, finish_in_round_1_model, finish_type_model, strike_volume_model, takedown_control_model, method_umbrella_model, finish_model, goes_distance_model, method_model, round_phase_model, round_model
- Source rows in train: {'mdabbert_ultimate': 4771, 'ufc_1994_2025': 6176, 'ufc_1994_2026': 6154, 'ufc_fight_forecast': 6062, 'ufc_stats_complete': 6184}
- Source rows in final test: {'mdabbert_ultimate': 1210, 'ufc_1994_2025': 922, 'ufc_1994_2026': 1164, 'ufc_fight_forecast': 955, 'ufc_stats_complete': 1286}

## Overall Ranking
| Model | Fights Tested | Main Metric | Baseline | Improvement | Beats Baseline | Status |
|---|---:|---:|---:|---:|---|---|
| winner_model | 3327 | 0.9633 | 0.52 | 0.4433 | True | backtested |
| fight_duration_model | 3696 | 0.8458 | 0.5141 | 0.3317 | True | backtested |
| finish_model | 3696 | 0.8458 | 0.5141 | 0.3317 | True | backtested |
| goes_distance_model | 3696 | 0.8458 | 0.5141 | 0.3317 | True | backtested |
| method_umbrella_model | 3696 | 0.7622 | 0.5141 | 0.2481 | True | backtested |
| method_model | 3696 | 0.7622 | 0.5141 | 0.2481 | True | backtested |
| over_2_5_model | 3683 | 0.8034 | 0.5599 | 0.2435 | True | backtested |
| strike_volume_model | 1322 | 0.5734 | 0.3623 | 0.2111 | True | backtested |
| ends_before_round_3_model | 3683 | 0.7825 | 0.6066 | 0.1759 | True | backtested |
| takedown_control_model | 2486 | 0.7409 | 0.5897 | 0.1512 | True | backtested |
| finish_type_model | 1796 | 0.7751 | 0.632 | 0.1431 | True | backtested |
| over_1_5_model | 3683 | 0.7912 | 0.6964 | 0.0948 | True | backtested |
| finish_in_round_1_model | 3683 | 0.8374 | 0.7613 | 0.0761 | True | backtested |
| odds_calibration_model | 0 |  |  |  | False | skipped |
| round_phase_model | 0 |  |  |  | False | skipped |
| round_model | 0 |  |  |  | False | skipped |

## Production Readiness Gates
| Model | Production Status | Failed Gates | Public Warning |
|---|---|---|---|
| odds_calibration_model | blocked | model_blocked | This model is blocked until required data quality gates pass. |
| winner_model | high_confidence_only | source_holdout_stable, winner_leakage_audit_passes | Use only as selective model evidence; winner audit gates are not strong enough for production-ready status. |
| fight_duration_model | production_candidate | source_holdout_not_run | Model is promising but still has failed production gates. |
| over_1_5_model | production_candidate | source_holdout_not_run | Model is promising but still has failed production gates. |
| over_2_5_model | production_candidate | source_holdout_not_run | Model is promising but still has failed production gates. |
| ends_before_round_3_model | production_candidate | source_holdout_not_run | Model is promising but still has failed production gates. |
| finish_in_round_1_model | production_candidate | source_holdout_not_run | Model is promising but still has failed production gates. |
| finish_type_model | experimental | source_holdout_not_run | Model has not passed enough production-readiness gates for public confidence claims. |
| strike_volume_model | experimental | calibration_acceptable, source_holdout_not_run | Model has not passed enough production-readiness gates for public confidence claims. |
| takedown_control_model | production_candidate | source_holdout_not_run | Model is promising but still has failed production gates. |
| method_umbrella_model | experimental | source_holdout_not_run | Model has not passed enough production-readiness gates for public confidence claims. |
| finish_model | production_candidate | source_holdout_not_run | Model is promising but still has failed production gates. |
| goes_distance_model | production_candidate | source_holdout_not_run | Model is promising but still has failed production gates. |
| method_model | experimental | source_holdout_not_run | Model has not passed enough production-readiness gates for public confidence claims. |
| round_phase_model | experimental | balanced_accuracy_not_dangerously_low, calibration_acceptable, source_holdout_not_run | Model has not passed enough production-readiness gates for public confidence claims. |
| round_model | experimental | balanced_accuracy_not_dangerously_low, calibration_acceptable, source_holdout_not_run | Model has not passed enough production-readiness gates for public confidence claims. |

## Interaction Features Used In Backtest
| Model | Interaction Features | Selection Status |
|---|---:|---|
| odds_calibration_model | 0 | not_run |
| winner_model | 0 | base_features_kept |
| fight_duration_model | 10 | selected |
| over_1_5_model | 5 | selected |
| over_2_5_model | 0 | base_features_kept |
| ends_before_round_3_model | 5 | selected |
| finish_in_round_1_model | 0 | base_features_kept |
| finish_type_model | 5 | selected |
| strike_volume_model | 20 | selected |
| takedown_control_model | 0 | base_features_kept |
| method_umbrella_model | 0 | not_run |
| finish_model | 10 | selected |
| goes_distance_model | 10 | selected |
| method_model | 0 | not_run |
| round_phase_model | 0 | not_run |
| round_model | 0 | not_run |

## Models Not Run
- `odds_calibration_model`: Trusted pre-fight odds snapshots are not available.

## Best Predictions
- Ozzy Diaz vs Zhang Mingyang (fight_duration_model): predicted `1` with confidence 0.9976.
- Ozzy Diaz vs Zhang Mingyang (finish_model): predicted `1` with confidence 0.9976.
- Ozzy Diaz vs Zhang Mingyang (goes_distance_model): predicted `0` with confidence 0.9976.
- Kaan Ofli vs Mairon Santos (fight_duration_model): predicted `1` with confidence 0.9975.
- Kaan Ofli vs Mairon Santos (finish_model): predicted `1` with confidence 0.9975.

## Worst Misses
- Angel Pacheco vs Caolan Loughran (finish_in_round_1_model): predicted `0.0` with confidence 0.9981.
- Landon Quinones vs MarQuel Mederos (finish_in_round_1_model): predicted `0.0` with confidence 0.9979.
- Angel Pacheco vs Caolan Loughran (finish_in_round_1_model): predicted `0.0` with confidence 0.9979.
- Angel Pacheco vs Caolan Loughran (finish_in_round_1_model): predicted `0.0` with confidence 0.9979.
- Dione Barbosa vs Ernesta Kareckaite (finish_in_round_1_model): predicted `0.0` with confidence 0.9979.

## Prop Examples
- Chad Anheliger vs Jose Johnson: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Joanderson Brito vs Jonathan Pearce: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Myktybek Orolbai vs Uros Medic: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Joanderson Brito vs Jonathan Pearce: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Chad Anheliger vs Jose Johnson: fighter 1 over 50 sig strikes=True, fighter 2 1+ takedown=True.

## Segment Performance
### winner_model
- weight_class:bantamweight: {'rows': 252, 'accuracy': 0.9841, 'unstable_sample_warning': False}
- weight_class:bantamweight_bout: {'rows': 131, 'accuracy': 0.9313, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 255, 'accuracy': 0.9843, 'unstable_sample_warning': False}
- weight_class:featherweight_bout: {'rows': 129, 'accuracy': 0.938, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 175, 'accuracy': 0.9771, 'unstable_sample_warning': False}
- weight_class:flyweight_bout: {'rows': 91, 'accuracy': 0.9121, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 143, 'accuracy': 0.965, 'unstable_sample_warning': False}
- weight_class:heavyweight_bout: {'rows': 73, 'accuracy': 0.863, 'unstable_sample_warning': True}
- weight_class:light_heavyweight: {'rows': 148, 'accuracy': 0.9932, 'unstable_sample_warning': False}
- weight_class:light_heavyweight_bout: {'rows': 76, 'accuracy': 0.9474, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 288, 'accuracy': 0.9757, 'unstable_sample_warning': False}
- weight_class:lightweight_bout: {'rows': 148, 'accuracy': 0.9459, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 274, 'accuracy': 0.9891, 'unstable_sample_warning': False}
- weight_class:middleweight_bout: {'rows': 145, 'accuracy': 0.9379, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 251, 'accuracy': 0.988, 'unstable_sample_warning': False}
- weight_class:welterweight_bout: {'rows': 132, 'accuracy': 0.9621, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 90, 'accuracy': 0.9556, 'unstable_sample_warning': True}
- weight_class:women's_bantamweight_bout: {'rows': 45, 'accuracy': 0.9778, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 109, 'accuracy': 0.9908, 'unstable_sample_warning': False}
- weight_class:women's_flyweight_bout: {'rows': 54, 'accuracy': 0.9444, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 142, 'accuracy': 0.9789, 'unstable_sample_warning': False}
- weight_class:women's_strawweight_bout: {'rows': 71, 'accuracy': 0.9296, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8764, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.9709, 'unstable_sample_warning': False}
### fight_duration_model
- weight_class:bantamweight: {'rows': 292, 'accuracy': 0.863, 'unstable_sample_warning': False}
- weight_class:bantamweight_bout: {'rows': 131, 'accuracy': 0.8779, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 30, 'accuracy': 0.8333, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 299, 'accuracy': 0.8595, 'unstable_sample_warning': False}
- weight_class:featherweight_bout: {'rows': 129, 'accuracy': 0.8217, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 202, 'accuracy': 0.8465, 'unstable_sample_warning': False}
- weight_class:flyweight_bout: {'rows': 91, 'accuracy': 0.8352, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 180, 'accuracy': 0.8333, 'unstable_sample_warning': False}
- weight_class:heavyweight_bout: {'rows': 73, 'accuracy': 0.8767, 'unstable_sample_warning': True}
- weight_class:light_heavyweight: {'rows': 175, 'accuracy': 0.8629, 'unstable_sample_warning': False}
- weight_class:light_heavyweight_bout: {'rows': 76, 'accuracy': 0.8553, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 336, 'accuracy': 0.8393, 'unstable_sample_warning': False}
- weight_class:lightweight_bout: {'rows': 148, 'accuracy': 0.8649, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 329, 'accuracy': 0.8359, 'unstable_sample_warning': False}
- weight_class:middleweight_bout: {'rows': 145, 'accuracy': 0.8483, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 287, 'accuracy': 0.8188, 'unstable_sample_warning': False}
- weight_class:welterweight_bout: {'rows': 132, 'accuracy': 0.8333, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 105, 'accuracy': 0.8476, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight_bout: {'rows': 45, 'accuracy': 0.8222, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 122, 'accuracy': 0.8197, 'unstable_sample_warning': False}
- weight_class:women's_flyweight_bout: {'rows': 54, 'accuracy': 0.8519, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 162, 'accuracy': 0.8642, 'unstable_sample_warning': False}
- weight_class:women's_strawweight_bout: {'rows': 71, 'accuracy': 0.8592, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 341, 'accuracy': 0.8328, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.8471, 'unstable_sample_warning': False}
### over_1_5_model
- weight_class:bantamweight: {'rows': 291, 'accuracy': 0.8694, 'unstable_sample_warning': False}
- weight_class:bantamweight_bout: {'rows': 131, 'accuracy': 0.8779, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 30, 'accuracy': 0.9667, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 297, 'accuracy': 0.7744, 'unstable_sample_warning': False}
- weight_class:featherweight_bout: {'rows': 129, 'accuracy': 0.7907, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 201, 'accuracy': 0.7761, 'unstable_sample_warning': False}
- weight_class:flyweight_bout: {'rows': 91, 'accuracy': 0.7802, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 179, 'accuracy': 0.7318, 'unstable_sample_warning': False}
- weight_class:heavyweight_bout: {'rows': 73, 'accuracy': 0.7671, 'unstable_sample_warning': True}
- weight_class:light_heavyweight: {'rows': 174, 'accuracy': 0.6954, 'unstable_sample_warning': False}
- weight_class:light_heavyweight_bout: {'rows': 76, 'accuracy': 0.6447, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 333, 'accuracy': 0.7898, 'unstable_sample_warning': False}
- weight_class:lightweight_bout: {'rows': 148, 'accuracy': 0.8041, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 328, 'accuracy': 0.7287, 'unstable_sample_warning': False}
- weight_class:middleweight_bout: {'rows': 145, 'accuracy': 0.6966, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 287, 'accuracy': 0.7805, 'unstable_sample_warning': False}
- weight_class:welterweight_bout: {'rows': 132, 'accuracy': 0.7273, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 104, 'accuracy': 0.7885, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight_bout: {'rows': 45, 'accuracy': 0.7778, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 121, 'accuracy': 0.8926, 'unstable_sample_warning': False}
- weight_class:women's_flyweight_bout: {'rows': 54, 'accuracy': 0.9259, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 161, 'accuracy': 0.9193, 'unstable_sample_warning': False}
- weight_class:women's_strawweight_bout: {'rows': 71, 'accuracy': 0.9296, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 338, 'accuracy': 0.7781, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.7925, 'unstable_sample_warning': False}
### over_2_5_model
- weight_class:bantamweight: {'rows': 291, 'accuracy': 0.8797, 'unstable_sample_warning': False}
- weight_class:bantamweight_bout: {'rows': 131, 'accuracy': 0.8779, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 30, 'accuracy': 0.7667, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 297, 'accuracy': 0.7811, 'unstable_sample_warning': False}
- weight_class:featherweight_bout: {'rows': 129, 'accuracy': 0.7907, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 201, 'accuracy': 0.796, 'unstable_sample_warning': False}
- weight_class:flyweight_bout: {'rows': 91, 'accuracy': 0.7802, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 179, 'accuracy': 0.8101, 'unstable_sample_warning': False}
- weight_class:heavyweight_bout: {'rows': 73, 'accuracy': 0.8082, 'unstable_sample_warning': True}
- weight_class:light_heavyweight: {'rows': 174, 'accuracy': 0.7759, 'unstable_sample_warning': False}
- weight_class:light_heavyweight_bout: {'rows': 76, 'accuracy': 0.7895, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 333, 'accuracy': 0.7838, 'unstable_sample_warning': False}
- weight_class:lightweight_bout: {'rows': 148, 'accuracy': 0.7568, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 328, 'accuracy': 0.8232, 'unstable_sample_warning': False}
- weight_class:middleweight_bout: {'rows': 145, 'accuracy': 0.8069, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 287, 'accuracy': 0.7631, 'unstable_sample_warning': False}
- weight_class:welterweight_bout: {'rows': 132, 'accuracy': 0.6894, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 104, 'accuracy': 0.7885, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight_bout: {'rows': 45, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 121, 'accuracy': 0.8017, 'unstable_sample_warning': False}
- weight_class:women's_flyweight_bout: {'rows': 54, 'accuracy': 0.8333, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 161, 'accuracy': 0.8696, 'unstable_sample_warning': False}
- weight_class:women's_strawweight_bout: {'rows': 71, 'accuracy': 0.831, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8314, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.8006, 'unstable_sample_warning': False}
### ends_before_round_3_model
- weight_class:bantamweight: {'rows': 291, 'accuracy': 0.8316, 'unstable_sample_warning': False}
- weight_class:bantamweight_bout: {'rows': 131, 'accuracy': 0.8397, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 30, 'accuracy': 0.8333, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 297, 'accuracy': 0.7475, 'unstable_sample_warning': False}
- weight_class:featherweight_bout: {'rows': 129, 'accuracy': 0.7674, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 201, 'accuracy': 0.7761, 'unstable_sample_warning': False}
- weight_class:flyweight_bout: {'rows': 91, 'accuracy': 0.7253, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 179, 'accuracy': 0.7821, 'unstable_sample_warning': False}
- weight_class:heavyweight_bout: {'rows': 73, 'accuracy': 0.7808, 'unstable_sample_warning': True}
- weight_class:light_heavyweight: {'rows': 174, 'accuracy': 0.7874, 'unstable_sample_warning': False}
- weight_class:light_heavyweight_bout: {'rows': 76, 'accuracy': 0.75, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 333, 'accuracy': 0.7177, 'unstable_sample_warning': False}
- weight_class:lightweight_bout: {'rows': 148, 'accuracy': 0.7297, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 328, 'accuracy': 0.7713, 'unstable_sample_warning': False}
- weight_class:middleweight_bout: {'rows': 145, 'accuracy': 0.7931, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 287, 'accuracy': 0.7666, 'unstable_sample_warning': False}
- weight_class:welterweight_bout: {'rows': 132, 'accuracy': 0.7424, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 104, 'accuracy': 0.7692, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight_bout: {'rows': 45, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 121, 'accuracy': 0.843, 'unstable_sample_warning': False}
- weight_class:women's_flyweight_bout: {'rows': 54, 'accuracy': 0.8704, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 161, 'accuracy': 0.8509, 'unstable_sample_warning': False}
- weight_class:women's_strawweight_bout: {'rows': 71, 'accuracy': 0.8873, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8047, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.7803, 'unstable_sample_warning': False}
### finish_in_round_1_model
- weight_class:bantamweight: {'rows': 291, 'accuracy': 0.9244, 'unstable_sample_warning': False}
- weight_class:bantamweight_bout: {'rows': 131, 'accuracy': 0.9237, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 30, 'accuracy': 0.9, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 297, 'accuracy': 0.8081, 'unstable_sample_warning': False}
- weight_class:featherweight_bout: {'rows': 129, 'accuracy': 0.814, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 201, 'accuracy': 0.8657, 'unstable_sample_warning': False}
- weight_class:flyweight_bout: {'rows': 91, 'accuracy': 0.8681, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 179, 'accuracy': 0.7709, 'unstable_sample_warning': False}
- weight_class:heavyweight_bout: {'rows': 73, 'accuracy': 0.7534, 'unstable_sample_warning': True}
- weight_class:light_heavyweight: {'rows': 174, 'accuracy': 0.7356, 'unstable_sample_warning': False}
- weight_class:light_heavyweight_bout: {'rows': 76, 'accuracy': 0.7237, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 333, 'accuracy': 0.8258, 'unstable_sample_warning': False}
- weight_class:lightweight_bout: {'rows': 148, 'accuracy': 0.8446, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 328, 'accuracy': 0.7988, 'unstable_sample_warning': False}
- weight_class:middleweight_bout: {'rows': 145, 'accuracy': 0.7862, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 287, 'accuracy': 0.7909, 'unstable_sample_warning': False}
- weight_class:welterweight_bout: {'rows': 132, 'accuracy': 0.803, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 104, 'accuracy': 0.8846, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight_bout: {'rows': 45, 'accuracy': 0.9111, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 121, 'accuracy': 0.8926, 'unstable_sample_warning': False}
- weight_class:women's_flyweight_bout: {'rows': 54, 'accuracy': 0.9259, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 161, 'accuracy': 0.9441, 'unstable_sample_warning': False}
- weight_class:women's_strawweight_bout: {'rows': 71, 'accuracy': 0.9437, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8521, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.8359, 'unstable_sample_warning': False}
### finish_type_model
- weight_class:bantamweight: {'rows': 91, 'accuracy': 0.7033, 'unstable_sample_warning': True}
- weight_class:bantamweight_bout: {'rows': 42, 'accuracy': 0.7143, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 164, 'accuracy': 0.8598, 'unstable_sample_warning': False}
- weight_class:featherweight_bout: {'rows': 71, 'accuracy': 0.8169, 'unstable_sample_warning': True}
- weight_class:flyweight: {'rows': 97, 'accuracy': 0.8247, 'unstable_sample_warning': True}
- weight_class:flyweight_bout: {'rows': 42, 'accuracy': 0.8333, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 91, 'accuracy': 0.8022, 'unstable_sample_warning': True}
- weight_class:heavyweight_bout: {'rows': 37, 'accuracy': 0.7568, 'unstable_sample_warning': True}
- weight_class:light_heavyweight: {'rows': 117, 'accuracy': 0.7778, 'unstable_sample_warning': False}
- weight_class:light_heavyweight_bout: {'rows': 49, 'accuracy': 0.7755, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 174, 'accuracy': 0.6954, 'unstable_sample_warning': False}
- weight_class:lightweight_bout: {'rows': 75, 'accuracy': 0.7067, 'unstable_sample_warning': True}
- weight_class:middleweight: {'rows': 193, 'accuracy': 0.7306, 'unstable_sample_warning': False}
- weight_class:middleweight_bout: {'rows': 87, 'accuracy': 0.7586, 'unstable_sample_warning': True}
- weight_class:welterweight: {'rows': 159, 'accuracy': 0.8616, 'unstable_sample_warning': False}
- weight_class:welterweight_bout: {'rows': 76, 'accuracy': 0.7763, 'unstable_sample_warning': True}
- weight_class:women's_bantamweight: {'rows': 42, 'accuracy': 0.8095, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 33, 'accuracy': 0.8788, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 51, 'accuracy': 0.549, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 197, 'accuracy': 0.6701, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 1599, 'accuracy': 0.788, 'unstable_sample_warning': False}
### strike_volume_model
- weight_class:bantamweight: {'rows': 150, 'accuracy': 0.62, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 154, 'accuracy': 0.5779, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 103, 'accuracy': 0.5922, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 99, 'accuracy': 0.5758, 'unstable_sample_warning': True}
- weight_class:light_heavyweight: {'rows': 90, 'accuracy': 0.5667, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 175, 'accuracy': 0.5257, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 175, 'accuracy': 0.56, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 148, 'accuracy': 0.5338, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 55, 'accuracy': 0.6364, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 62, 'accuracy': 0.5968, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 83, 'accuracy': 0.5904, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 95, 'accuracy': 0.4211, 'unstable_sample_warning': True}
- enough_fighter_history: {'rows': 1227, 'accuracy': 0.5852, 'unstable_sample_warning': False}
### takedown_control_model
- weight_class:bantamweight: {'rows': 150, 'accuracy': 0.7533, 'unstable_sample_warning': False}
- weight_class:bantamweight_bout: {'rows': 131, 'accuracy': 0.7328, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 154, 'accuracy': 0.7078, 'unstable_sample_warning': False}
- weight_class:featherweight_bout: {'rows': 129, 'accuracy': 0.7442, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 103, 'accuracy': 0.7476, 'unstable_sample_warning': False}
- weight_class:flyweight_bout: {'rows': 91, 'accuracy': 0.7582, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 99, 'accuracy': 0.7475, 'unstable_sample_warning': True}
- weight_class:heavyweight_bout: {'rows': 73, 'accuracy': 0.7808, 'unstable_sample_warning': True}
- weight_class:light_heavyweight: {'rows': 90, 'accuracy': 0.8889, 'unstable_sample_warning': True}
- weight_class:light_heavyweight_bout: {'rows': 76, 'accuracy': 0.8816, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 175, 'accuracy': 0.6571, 'unstable_sample_warning': False}
- weight_class:lightweight_bout: {'rows': 148, 'accuracy': 0.7297, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 175, 'accuracy': 0.6914, 'unstable_sample_warning': False}
- weight_class:middleweight_bout: {'rows': 145, 'accuracy': 0.7793, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 148, 'accuracy': 0.7162, 'unstable_sample_warning': False}
- weight_class:welterweight_bout: {'rows': 132, 'accuracy': 0.8106, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 55, 'accuracy': 0.6727, 'unstable_sample_warning': True}
- weight_class:women's_bantamweight_bout: {'rows': 45, 'accuracy': 0.7111, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 62, 'accuracy': 0.8226, 'unstable_sample_warning': True}
- weight_class:women's_flyweight_bout: {'rows': 54, 'accuracy': 0.7963, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 83, 'accuracy': 0.6265, 'unstable_sample_warning': True}
- weight_class:women's_strawweight_bout: {'rows': 71, 'accuracy': 0.7042, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 291, 'accuracy': 0.8591, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 2195, 'accuracy': 0.7253, 'unstable_sample_warning': False}
### method_umbrella_model
- weight_class:bantamweight: {'rows': 292, 'accuracy': 0.8116, 'unstable_sample_warning': False}
- weight_class:bantamweight_bout: {'rows': 131, 'accuracy': 0.8473, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 30, 'accuracy': 0.8667, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 299, 'accuracy': 0.7759, 'unstable_sample_warning': False}
- weight_class:featherweight_bout: {'rows': 129, 'accuracy': 0.7597, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 202, 'accuracy': 0.802, 'unstable_sample_warning': False}
- weight_class:flyweight_bout: {'rows': 91, 'accuracy': 0.8022, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 180, 'accuracy': 0.7222, 'unstable_sample_warning': False}
- weight_class:heavyweight_bout: {'rows': 73, 'accuracy': 0.7671, 'unstable_sample_warning': True}
- weight_class:light_heavyweight: {'rows': 175, 'accuracy': 0.7257, 'unstable_sample_warning': False}
- weight_class:light_heavyweight_bout: {'rows': 76, 'accuracy': 0.7632, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 336, 'accuracy': 0.7351, 'unstable_sample_warning': False}
- weight_class:lightweight_bout: {'rows': 148, 'accuracy': 0.7635, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 329, 'accuracy': 0.6991, 'unstable_sample_warning': False}
- weight_class:middleweight_bout: {'rows': 145, 'accuracy': 0.731, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 287, 'accuracy': 0.7387, 'unstable_sample_warning': False}
- weight_class:welterweight_bout: {'rows': 132, 'accuracy': 0.7273, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 105, 'accuracy': 0.7714, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight_bout: {'rows': 45, 'accuracy': 0.7778, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 122, 'accuracy': 0.8033, 'unstable_sample_warning': False}
- weight_class:women's_flyweight_bout: {'rows': 54, 'accuracy': 0.8333, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 162, 'accuracy': 0.7716, 'unstable_sample_warning': False}
- weight_class:women's_strawweight_bout: {'rows': 71, 'accuracy': 0.7887, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 341, 'accuracy': 0.7067, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.7678, 'unstable_sample_warning': False}
### finish_model
- weight_class:bantamweight: {'rows': 292, 'accuracy': 0.863, 'unstable_sample_warning': False}
- weight_class:bantamweight_bout: {'rows': 131, 'accuracy': 0.8779, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 30, 'accuracy': 0.8333, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 299, 'accuracy': 0.8595, 'unstable_sample_warning': False}
- weight_class:featherweight_bout: {'rows': 129, 'accuracy': 0.8217, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 202, 'accuracy': 0.8465, 'unstable_sample_warning': False}
- weight_class:flyweight_bout: {'rows': 91, 'accuracy': 0.8352, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 180, 'accuracy': 0.8333, 'unstable_sample_warning': False}
- weight_class:heavyweight_bout: {'rows': 73, 'accuracy': 0.8767, 'unstable_sample_warning': True}
- weight_class:light_heavyweight: {'rows': 175, 'accuracy': 0.8629, 'unstable_sample_warning': False}
- weight_class:light_heavyweight_bout: {'rows': 76, 'accuracy': 0.8553, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 336, 'accuracy': 0.8393, 'unstable_sample_warning': False}
- weight_class:lightweight_bout: {'rows': 148, 'accuracy': 0.8649, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 329, 'accuracy': 0.8359, 'unstable_sample_warning': False}
- weight_class:middleweight_bout: {'rows': 145, 'accuracy': 0.8483, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 287, 'accuracy': 0.8188, 'unstable_sample_warning': False}
- weight_class:welterweight_bout: {'rows': 132, 'accuracy': 0.8333, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 105, 'accuracy': 0.8476, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight_bout: {'rows': 45, 'accuracy': 0.8222, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 122, 'accuracy': 0.8197, 'unstable_sample_warning': False}
- weight_class:women's_flyweight_bout: {'rows': 54, 'accuracy': 0.8519, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 162, 'accuracy': 0.8642, 'unstable_sample_warning': False}
- weight_class:women's_strawweight_bout: {'rows': 71, 'accuracy': 0.8592, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 341, 'accuracy': 0.8328, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.8471, 'unstable_sample_warning': False}
### goes_distance_model
- weight_class:bantamweight: {'rows': 292, 'accuracy': 0.863, 'unstable_sample_warning': False}
- weight_class:bantamweight_bout: {'rows': 131, 'accuracy': 0.8779, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 30, 'accuracy': 0.8333, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 299, 'accuracy': 0.8595, 'unstable_sample_warning': False}
- weight_class:featherweight_bout: {'rows': 129, 'accuracy': 0.8217, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 202, 'accuracy': 0.8465, 'unstable_sample_warning': False}
- weight_class:flyweight_bout: {'rows': 91, 'accuracy': 0.8352, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 180, 'accuracy': 0.8333, 'unstable_sample_warning': False}
- weight_class:heavyweight_bout: {'rows': 73, 'accuracy': 0.8767, 'unstable_sample_warning': True}
- weight_class:light_heavyweight: {'rows': 175, 'accuracy': 0.8629, 'unstable_sample_warning': False}
- weight_class:light_heavyweight_bout: {'rows': 76, 'accuracy': 0.8553, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 336, 'accuracy': 0.8393, 'unstable_sample_warning': False}
- weight_class:lightweight_bout: {'rows': 148, 'accuracy': 0.8649, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 329, 'accuracy': 0.8359, 'unstable_sample_warning': False}
- weight_class:middleweight_bout: {'rows': 145, 'accuracy': 0.8483, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 287, 'accuracy': 0.8188, 'unstable_sample_warning': False}
- weight_class:welterweight_bout: {'rows': 132, 'accuracy': 0.8333, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 105, 'accuracy': 0.8476, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight_bout: {'rows': 45, 'accuracy': 0.8222, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 122, 'accuracy': 0.8197, 'unstable_sample_warning': False}
- weight_class:women's_flyweight_bout: {'rows': 54, 'accuracy': 0.8519, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 162, 'accuracy': 0.8642, 'unstable_sample_warning': False}
- weight_class:women's_strawweight_bout: {'rows': 71, 'accuracy': 0.8592, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 341, 'accuracy': 0.8328, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.8471, 'unstable_sample_warning': False}
### method_model
- weight_class:bantamweight: {'rows': 292, 'accuracy': 0.8116, 'unstable_sample_warning': False}
- weight_class:bantamweight_bout: {'rows': 131, 'accuracy': 0.8473, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 30, 'accuracy': 0.8667, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 299, 'accuracy': 0.7759, 'unstable_sample_warning': False}
- weight_class:featherweight_bout: {'rows': 129, 'accuracy': 0.7597, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 202, 'accuracy': 0.802, 'unstable_sample_warning': False}
- weight_class:flyweight_bout: {'rows': 91, 'accuracy': 0.8022, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 180, 'accuracy': 0.7222, 'unstable_sample_warning': False}
- weight_class:heavyweight_bout: {'rows': 73, 'accuracy': 0.7671, 'unstable_sample_warning': True}
- weight_class:light_heavyweight: {'rows': 175, 'accuracy': 0.7257, 'unstable_sample_warning': False}
- weight_class:light_heavyweight_bout: {'rows': 76, 'accuracy': 0.7632, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 336, 'accuracy': 0.7351, 'unstable_sample_warning': False}
- weight_class:lightweight_bout: {'rows': 148, 'accuracy': 0.7635, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 329, 'accuracy': 0.6991, 'unstable_sample_warning': False}
- weight_class:middleweight_bout: {'rows': 145, 'accuracy': 0.731, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 287, 'accuracy': 0.7387, 'unstable_sample_warning': False}
- weight_class:welterweight_bout: {'rows': 132, 'accuracy': 0.7273, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 105, 'accuracy': 0.7714, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight_bout: {'rows': 45, 'accuracy': 0.7778, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 122, 'accuracy': 0.8033, 'unstable_sample_warning': False}
- weight_class:women's_flyweight_bout: {'rows': 54, 'accuracy': 0.8333, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 162, 'accuracy': 0.7716, 'unstable_sample_warning': False}
- weight_class:women's_strawweight_bout: {'rows': 71, 'accuracy': 0.7887, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 341, 'accuracy': 0.7067, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.7678, 'unstable_sample_warning': False}

## Next Steps
- Improve safe winner-model orientation before backtesting winner probabilities.
- Add trusted pre-fight odds timestamps before odds calibration.
- Keep weak models out of production-ready status until they beat baseline.
