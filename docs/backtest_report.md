# Historical Fight Backtest Report

## Plain-English Summary
This backtest simulated 5537 historical fights by hiding outcome labels until after model predictions were generated from pre-fight features. Duration is now backtested as one finish/goes-distance model, round reads are separate binary models, and method is scored through the duration-plus-finish-type umbrella.

## Hierarchical Outcome Backtest
| Model | Fights | Accuracy | Balanced Accuracy | Baseline | Improvement | Status |
|---|---:|---:|---:|---:|---:|---|
| fight_duration_model | 3696 | 0.8285 | 0.8278 | 0.5141 | 0.3144 | backtested |
| over_1_5_model | 3683 | 0.7907 | 0.7183 | 0.6964 | 0.0943 | backtested |
| over_2_5_model | 3683 | 0.8086 | 0.8008 | 0.5599 | 0.2487 | backtested |
| ends_before_round_3_model | 3683 | 0.7934 | 0.7769 | 0.6066 | 0.1868 | backtested |
| finish_in_round_1_model | 3683 | 0.8298 | 0.7086 | 0.7613 | 0.0685 | backtested |
| finish_type_model | 1796 | 0.7812 | 0.6454 | 0.632 | 0.1492 | backtested |
| method_umbrella_model | 3696 | 0.7484 | 0.5836 | 0.5141 | 0.2343 | backtested |

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
| winner_model | 3327 | 0.9585 | 0.52 | 0.4385 | True | backtested |
| fight_duration_model | 3696 | 0.8285 | 0.5141 | 0.3144 | True | backtested |
| finish_model | 3696 | 0.8285 | 0.5141 | 0.3144 | True | backtested |
| goes_distance_model | 3696 | 0.8285 | 0.5141 | 0.3144 | True | backtested |
| over_2_5_model | 3683 | 0.8086 | 0.5599 | 0.2487 | True | backtested |
| method_umbrella_model | 3696 | 0.7484 | 0.5141 | 0.2343 | True | backtested |
| method_model | 3696 | 0.7484 | 0.5141 | 0.2343 | True | backtested |
| strike_volume_model | 1322 | 0.5825 | 0.3623 | 0.2202 | True | backtested |
| ends_before_round_3_model | 3683 | 0.7934 | 0.6066 | 0.1868 | True | backtested |
| finish_type_model | 1796 | 0.7812 | 0.632 | 0.1492 | True | backtested |
| takedown_control_model | 2486 | 0.7385 | 0.5897 | 0.1488 | True | backtested |
| over_1_5_model | 3683 | 0.7907 | 0.6964 | 0.0943 | True | backtested |
| finish_in_round_1_model | 3683 | 0.8298 | 0.7613 | 0.0685 | True | backtested |
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
| fight_duration_model | 0 | base_features_kept |
| over_1_5_model | 0 | base_features_kept |
| over_2_5_model | 0 | base_features_kept |
| ends_before_round_3_model | 0 | base_features_kept |
| finish_in_round_1_model | 0 | base_features_kept |
| finish_type_model | 10 | selected |
| strike_volume_model | 20 | selected |
| takedown_control_model | 0 | base_features_kept |
| method_umbrella_model | 0 | not_run |
| finish_model | 0 | base_features_kept |
| goes_distance_model | 0 | base_features_kept |
| method_model | 0 | not_run |
| round_phase_model | 0 | not_run |
| round_model | 0 | not_run |

## Models Not Run
- `odds_calibration_model`: Trusted pre-fight odds snapshots are not available.

## Best Predictions
- Josh Hokit vs Max Gimenis (fight_duration_model): predicted `1` with confidence 0.9972.
- Josh Hokit vs Max Gimenis (finish_model): predicted `1` with confidence 0.9972.
- Josh Hokit vs Max Gimenis (goes_distance_model): predicted `0` with confidence 0.9972.
- Damian Pinas vs Wes Schultz (fight_duration_model): predicted `1` with confidence 0.9972.
- Damian Pinas vs Wes Schultz (finish_model): predicted `1` with confidence 0.9972.

## Worst Misses
- ChangHo Lee vs Xiao Long (finish_in_round_1_model): predicted `0.0` with confidence 0.9978.
- Angel Pacheco vs Caolan Loughran (finish_in_round_1_model): predicted `0.0` with confidence 0.9977.
- Dione Barbosa vs Ernesta Kareckaite (finish_in_round_1_model): predicted `0.0` with confidence 0.9977.
- ChangHo Lee vs Xiao Long (finish_in_round_1_model): predicted `0.0` with confidence 0.9977.
- Chad Anheliger vs Charalampos Grigoriou (finish_in_round_1_model): predicted `0.0` with confidence 0.9976.

## Prop Examples
- Chad Anheliger vs Jose Johnson: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Joanderson Brito vs Jonathan Pearce: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Myktybek Orolbai vs Uros Medic: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Joanderson Brito vs Jonathan Pearce: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Chad Anheliger vs Jose Johnson: fighter 1 over 50 sig strikes=True, fighter 2 1+ takedown=True.

## Segment Performance
### winner_model
- weight_class:Bantamweight: {'rows': 146, 'accuracy': 0.9589, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.916, 'unstable_sample_warning': False}
- weight_class:Featherweight: {'rows': 147, 'accuracy': 0.966, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.9225, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 102, 'accuracy': 0.9608, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.9011, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 88, 'accuracy': 0.9659, 'unstable_sample_warning': True}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.863, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 85, 'accuracy': 0.9882, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.9474, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 163, 'accuracy': 0.9632, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.9257, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 161, 'accuracy': 0.9565, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.9172, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 143, 'accuracy': 0.979, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.9394, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 53, 'accuracy': 0.9245, 'unstable_sample_warning': True}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.9778, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 60, 'accuracy': 0.9833, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.963, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 81, 'accuracy': 0.963, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.9296, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 106, 'accuracy': 1.0, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 1.0, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 1.0, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 1.0, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 63, 'accuracy': 1.0, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 125, 'accuracy': 1.0, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 113, 'accuracy': 1.0, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 108, 'accuracy': 1.0, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 1.0, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 1.0, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 1.0, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8801, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.9654, 'unstable_sample_warning': False}
### fight_duration_model
- weight_class:Bantamweight: {'rows': 185, 'accuracy': 0.8054, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8779, 'unstable_sample_warning': False}
- weight_class:Featherweight: {'rows': 191, 'accuracy': 0.8063, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7907, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 129, 'accuracy': 0.7984, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8242, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 125, 'accuracy': 0.744, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.863, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 110, 'accuracy': 0.8545, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8289, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 210, 'accuracy': 0.7571, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8378, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 213, 'accuracy': 0.7887, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8552, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.7584, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7879, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 68, 'accuracy': 0.8235, 'unstable_sample_warning': True}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 73, 'accuracy': 0.7671, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8704, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 101, 'accuracy': 0.8218, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.9159, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8981, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8767, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.9273, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.8615, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.8968, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.8707, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.8349, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.8649, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.9184, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.9016, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 341, 'accuracy': 0.8328, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.828, 'unstable_sample_warning': False}
### over_1_5_model
- weight_class:Bantamweight: {'rows': 184, 'accuracy': 0.8533, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.855, 'unstable_sample_warning': False}
- weight_class:Featherweight: {'rows': 189, 'accuracy': 0.7249, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7674, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 128, 'accuracy': 0.7422, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8132, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 124, 'accuracy': 0.7016, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.7671, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 109, 'accuracy': 0.6697, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.6974, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 207, 'accuracy': 0.7633, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8041, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 212, 'accuracy': 0.684, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.7172, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.7978, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7652, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 67, 'accuracy': 0.791, 'unstable_sample_warning': True}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 72, 'accuracy': 0.8472, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.9259, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 100, 'accuracy': 0.92, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.9155, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.8785, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8519, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8219, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.7538, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.7937, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.7414, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.8073, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.7838, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.9592, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.9016, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 338, 'accuracy': 0.7929, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.7904, 'unstable_sample_warning': False}
### over_2_5_model
- weight_class:Bantamweight: {'rows': 184, 'accuracy': 0.837, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8779, 'unstable_sample_warning': False}
- weight_class:Featherweight: {'rows': 189, 'accuracy': 0.7566, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7597, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 128, 'accuracy': 0.7188, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.7582, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 124, 'accuracy': 0.7823, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.8219, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 109, 'accuracy': 0.7706, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8421, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 207, 'accuracy': 0.7343, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7568, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 212, 'accuracy': 0.8019, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8276, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.7528, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7197, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 67, 'accuracy': 0.791, 'unstable_sample_warning': True}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 72, 'accuracy': 0.8056, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8704, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 100, 'accuracy': 0.86, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8873, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.9159, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8519, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8767, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.9091, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.8308, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.8175, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.8621, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.7982, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.8108, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.9184, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.918, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8609, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.8033, 'unstable_sample_warning': False}
### ends_before_round_3_model
- weight_class:Bantamweight: {'rows': 184, 'accuracy': 0.8315, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8473, 'unstable_sample_warning': False}
- weight_class:Featherweight: {'rows': 189, 'accuracy': 0.7037, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7364, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 128, 'accuracy': 0.6797, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.7143, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 124, 'accuracy': 0.7903, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.8493, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 109, 'accuracy': 0.7431, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8289, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 207, 'accuracy': 0.7343, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7568, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 212, 'accuracy': 0.7689, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8276, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.7528, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7576, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 67, 'accuracy': 0.7463, 'unstable_sample_warning': True}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.7778, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 72, 'accuracy': 0.7639, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8704, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 100, 'accuracy': 0.86, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8873, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.8692, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8056, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8493, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.9273, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.8333, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.8017, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.8073, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.7838, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.9388, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.8689, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8314, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.7895, 'unstable_sample_warning': False}
### finish_in_round_1_model
- weight_class:Bantamweight: {'rows': 184, 'accuracy': 0.8913, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.9237, 'unstable_sample_warning': False}
- weight_class:Featherweight: {'rows': 189, 'accuracy': 0.7937, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.8217, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 128, 'accuracy': 0.8125, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8242, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 124, 'accuracy': 0.7581, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.8082, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 109, 'accuracy': 0.6881, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.6711, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 207, 'accuracy': 0.8116, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8446, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 212, 'accuracy': 0.7642, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.7379, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.7865, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7955, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 67, 'accuracy': 0.8955, 'unstable_sample_warning': True}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.9111, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 72, 'accuracy': 0.8472, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.9259, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 100, 'accuracy': 0.97, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.9577, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.9252, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8611, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8767, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.8182, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.7385, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.8333, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.7931, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.8073, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.8919, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.9592, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.9508, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8432, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.8284, 'unstable_sample_warning': False}
### finish_type_model
- weight_class:Bantamweight: {'rows': 56, 'accuracy': 0.625, 'unstable_sample_warning': True}
- weight_class:Bantamweight Bout: {'rows': 42, 'accuracy': 0.7381, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 106, 'accuracy': 0.7925, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 71, 'accuracy': 0.7746, 'unstable_sample_warning': True}
- weight_class:Flyweight: {'rows': 64, 'accuracy': 0.8125, 'unstable_sample_warning': True}
- weight_class:Flyweight Bout: {'rows': 42, 'accuracy': 0.8571, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 63, 'accuracy': 0.8095, 'unstable_sample_warning': True}
- weight_class:Heavyweight Bout: {'rows': 37, 'accuracy': 0.7297, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 77, 'accuracy': 0.7662, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight Bout: {'rows': 49, 'accuracy': 0.7959, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 114, 'accuracy': 0.7193, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 75, 'accuracy': 0.7333, 'unstable_sample_warning': True}
- weight_class:Middleweight: {'rows': 126, 'accuracy': 0.7381, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 87, 'accuracy': 0.7931, 'unstable_sample_warning': True}
- weight_class:Welterweight: {'rows': 97, 'accuracy': 0.8247, 'unstable_sample_warning': True}
- weight_class:Welterweight Bout: {'rows': 76, 'accuracy': 0.7763, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 33, 'accuracy': 0.5455, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 35, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 58, 'accuracy': 0.8793, 'unstable_sample_warning': True}
- weight_class:flyweight: {'rows': 33, 'accuracy': 0.9091, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 40, 'accuracy': 0.85, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 60, 'accuracy': 0.75, 'unstable_sample_warning': True}
- weight_class:middleweight: {'rows': 67, 'accuracy': 0.8507, 'unstable_sample_warning': True}
- weight_class:welterweight: {'rows': 62, 'accuracy': 0.871, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 197, 'accuracy': 0.6751, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 1599, 'accuracy': 0.7942, 'unstable_sample_warning': False}
### strike_volume_model
- weight_class:Bantamweight: {'rows': 43, 'accuracy': 0.3023, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 46, 'accuracy': 0.3696, 'unstable_sample_warning': True}
- weight_class:Flyweight: {'rows': 30, 'accuracy': 0.4, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 44, 'accuracy': 0.4773, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 49, 'accuracy': 0.3469, 'unstable_sample_warning': True}
- weight_class:Middleweight: {'rows': 59, 'accuracy': 0.5085, 'unstable_sample_warning': True}
- weight_class:Welterweight: {'rows': 39, 'accuracy': 0.5128, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.7196, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.6296, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.6575, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.7091, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.7077, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.6429, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.6121, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.5872, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.7297, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.6122, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.6066, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 95, 'accuracy': 0.3895, 'unstable_sample_warning': True}
- enough_fighter_history: {'rows': 1227, 'accuracy': 0.5974, 'unstable_sample_warning': False}
### takedown_control_model
- weight_class:Bantamweight: {'rows': 43, 'accuracy': 0.5116, 'unstable_sample_warning': True}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.7634, 'unstable_sample_warning': False}
- weight_class:Featherweight: {'rows': 46, 'accuracy': 0.6522, 'unstable_sample_warning': True}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7287, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 30, 'accuracy': 0.6, 'unstable_sample_warning': True}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.7692, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 44, 'accuracy': 0.6591, 'unstable_sample_warning': True}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.8493, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.9079, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 49, 'accuracy': 0.551, 'unstable_sample_warning': True}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7703, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 59, 'accuracy': 0.6102, 'unstable_sample_warning': True}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.7793, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 39, 'accuracy': 0.5385, 'unstable_sample_warning': True}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7576, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.7556, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.7963, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.6761, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.8131, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.7315, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.7945, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.7455, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.8923, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.6746, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.7414, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.7339, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.7027, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.7959, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.6885, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 291, 'accuracy': 0.8316, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 2195, 'accuracy': 0.7262, 'unstable_sample_warning': False}
### method_umbrella_model
- weight_class:Bantamweight: {'rows': 185, 'accuracy': 0.7676, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8626, 'unstable_sample_warning': False}
- weight_class:Featherweight: {'rows': 191, 'accuracy': 0.712, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7364, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 129, 'accuracy': 0.7132, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.7912, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 125, 'accuracy': 0.616, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.726, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 110, 'accuracy': 0.7182, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.75, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 210, 'accuracy': 0.6714, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7162, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 213, 'accuracy': 0.6385, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.7241, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.6573, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7045, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 68, 'accuracy': 0.75, 'unstable_sample_warning': True}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.7333, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 73, 'accuracy': 0.7671, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8704, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 101, 'accuracy': 0.7624, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8028, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.8692, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8241, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8493, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.7818, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.7692, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.8016, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.7672, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.7798, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.8378, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.9184, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.8361, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 341, 'accuracy': 0.6862, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.7547, 'unstable_sample_warning': False}
### finish_model
- weight_class:Bantamweight: {'rows': 185, 'accuracy': 0.8054, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8779, 'unstable_sample_warning': False}
- weight_class:Featherweight: {'rows': 191, 'accuracy': 0.8063, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7907, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 129, 'accuracy': 0.7984, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8242, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 125, 'accuracy': 0.744, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.863, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 110, 'accuracy': 0.8545, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8289, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 210, 'accuracy': 0.7571, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8378, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 213, 'accuracy': 0.7887, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8552, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.7584, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7879, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 68, 'accuracy': 0.8235, 'unstable_sample_warning': True}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 73, 'accuracy': 0.7671, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8704, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 101, 'accuracy': 0.8218, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.9159, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8981, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8767, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.9273, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.8615, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.8968, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.8707, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.8349, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.8649, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.9184, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.9016, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 341, 'accuracy': 0.8328, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.828, 'unstable_sample_warning': False}
### goes_distance_model
- weight_class:Bantamweight: {'rows': 185, 'accuracy': 0.8054, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8779, 'unstable_sample_warning': False}
- weight_class:Featherweight: {'rows': 191, 'accuracy': 0.8063, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7907, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 129, 'accuracy': 0.7984, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8242, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 125, 'accuracy': 0.744, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.863, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 110, 'accuracy': 0.8545, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8289, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 210, 'accuracy': 0.7571, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8378, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 213, 'accuracy': 0.7887, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8552, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.7584, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7879, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 68, 'accuracy': 0.8235, 'unstable_sample_warning': True}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 73, 'accuracy': 0.7671, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8704, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 101, 'accuracy': 0.8218, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.9159, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8981, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8767, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.9273, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.8615, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.8968, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.8707, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.8349, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.8649, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.9184, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.9016, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 341, 'accuracy': 0.8328, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.828, 'unstable_sample_warning': False}
### method_model
- weight_class:Bantamweight: {'rows': 185, 'accuracy': 0.7676, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8626, 'unstable_sample_warning': False}
- weight_class:Featherweight: {'rows': 191, 'accuracy': 0.712, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7364, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 129, 'accuracy': 0.7132, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.7912, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 125, 'accuracy': 0.616, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.726, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 110, 'accuracy': 0.7182, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.75, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 210, 'accuracy': 0.6714, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7162, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 213, 'accuracy': 0.6385, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.7241, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.6573, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7045, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 68, 'accuracy': 0.75, 'unstable_sample_warning': True}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.7333, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 73, 'accuracy': 0.7671, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8704, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 101, 'accuracy': 0.7624, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8028, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.8692, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8241, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8493, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.7818, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.7692, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.8016, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.7672, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.7798, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.8378, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.9184, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.8361, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 341, 'accuracy': 0.6862, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.7547, 'unstable_sample_warning': False}

## Next Steps
- Improve safe winner-model orientation before backtesting winner probabilities.
- Add trusted pre-fight odds timestamps before odds calibration.
- Keep weak models out of production-ready status until they beat baseline.
