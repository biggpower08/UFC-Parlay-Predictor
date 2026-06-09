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
- Kaan Ofli vs Mairon Santos (fight_duration_model): predicted `1` with confidence 0.9975.
- Brendson Ribeiro vs Zhang Mingyang (fight_duration_model): predicted `1` with confidence 0.9974.
- Brendson Ribeiro vs Zhang Mingyang (fight_duration_model): predicted `1` with confidence 0.9973.
- Brendson Ribeiro vs Zhang Mingyang (fight_duration_model): predicted `1` with confidence 0.9973.

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
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.9661, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 37, 'accuracy': 0.9189, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.9688, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.9549, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.9306, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.9777, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.9656, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.9714, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.9791, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.963, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.9755, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.9624, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8764, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.9709, 'unstable_sample_warning': False}
### fight_duration_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8676, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.8409, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.8481, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.843, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.8458, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.8606, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.8471, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.8397, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.8234, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.84, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.8295, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.8627, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 341, 'accuracy': 0.8328, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.8471, 'unstable_sample_warning': False}
### over_1_5_model
- weight_class:bantamweight: {'rows': 422, 'accuracy': 0.872, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.9545, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 426, 'accuracy': 0.7793, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 292, 'accuracy': 0.7774, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 252, 'accuracy': 0.7421, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 250, 'accuracy': 0.68, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 481, 'accuracy': 0.7942, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 473, 'accuracy': 0.7188, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7637, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 149, 'accuracy': 0.7852, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 175, 'accuracy': 0.9029, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 232, 'accuracy': 0.9224, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 338, 'accuracy': 0.7781, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.7925, 'unstable_sample_warning': False}
### over_2_5_model
- weight_class:bantamweight: {'rows': 422, 'accuracy': 0.8791, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.7727, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 426, 'accuracy': 0.784, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 292, 'accuracy': 0.7911, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 252, 'accuracy': 0.8095, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 250, 'accuracy': 0.78, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 481, 'accuracy': 0.7755, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 473, 'accuracy': 0.8182, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7399, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 149, 'accuracy': 0.7919, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 175, 'accuracy': 0.8114, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 232, 'accuracy': 0.8578, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8314, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.8006, 'unstable_sample_warning': False}
### ends_before_round_3_model
- weight_class:bantamweight: {'rows': 422, 'accuracy': 0.8341, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.8409, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 426, 'accuracy': 0.7535, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 292, 'accuracy': 0.7603, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 252, 'accuracy': 0.7817, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 250, 'accuracy': 0.776, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 481, 'accuracy': 0.7214, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 473, 'accuracy': 0.778, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7589, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 149, 'accuracy': 0.7785, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 175, 'accuracy': 0.8514, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 232, 'accuracy': 0.8621, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8047, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.7803, 'unstable_sample_warning': False}
### finish_in_round_1_model
- weight_class:bantamweight: {'rows': 422, 'accuracy': 0.9242, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.9091, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 426, 'accuracy': 0.8099, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 292, 'accuracy': 0.8664, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 252, 'accuracy': 0.7659, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 250, 'accuracy': 0.732, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 481, 'accuracy': 0.8316, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 473, 'accuracy': 0.7949, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7947, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 149, 'accuracy': 0.8926, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 175, 'accuracy': 0.9029, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 232, 'accuracy': 0.944, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8521, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.8359, 'unstable_sample_warning': False}
### finish_type_model
- weight_class:bantamweight: {'rows': 133, 'accuracy': 0.7068, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 235, 'accuracy': 0.8468, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 139, 'accuracy': 0.8273, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 128, 'accuracy': 0.7891, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 166, 'accuracy': 0.7771, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 249, 'accuracy': 0.6988, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 280, 'accuracy': 0.7393, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 235, 'accuracy': 0.834, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 60, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 47, 'accuracy': 0.8723, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 73, 'accuracy': 0.6027, 'unstable_sample_warning': True}
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
- weight_class:bantamweight: {'rows': 281, 'accuracy': 0.7438, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 30, 'accuracy': 0.6333, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 283, 'accuracy': 0.7244, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 194, 'accuracy': 0.7526, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 172, 'accuracy': 0.7616, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 166, 'accuracy': 0.8855, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 323, 'accuracy': 0.6904, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 320, 'accuracy': 0.7312, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 280, 'accuracy': 0.7607, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 100, 'accuracy': 0.69, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 116, 'accuracy': 0.8103, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 154, 'accuracy': 0.6623, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 291, 'accuracy': 0.8591, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 2195, 'accuracy': 0.7253, 'unstable_sample_warning': False}
### method_umbrella_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8227, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.8409, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.771, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.802, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.7352, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.7371, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.7438, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.7089, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7351, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.7733, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.8125, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.7768, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 341, 'accuracy': 0.7067, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.7678, 'unstable_sample_warning': False}
### finish_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8676, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.8409, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.8481, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.843, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.8458, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.8606, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.8471, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.8397, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.8234, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.84, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.8295, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.8627, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 341, 'accuracy': 0.8328, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.8471, 'unstable_sample_warning': False}
### goes_distance_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8676, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.8409, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.8481, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.843, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.8458, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.8606, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.8471, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.8397, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.8234, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.84, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.8295, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.8627, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 341, 'accuracy': 0.8328, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.8471, 'unstable_sample_warning': False}
### method_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8227, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.8409, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.771, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.802, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.7352, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.7371, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.7438, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.7089, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7351, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.7733, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.8125, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.7768, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 341, 'accuracy': 0.7067, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.7678, 'unstable_sample_warning': False}

## Next Steps
- Improve safe winner-model orientation before backtesting winner probabilities.
- Add trusted pre-fight odds timestamps before odds calibration.
- Keep weak models out of production-ready status until they beat baseline.
