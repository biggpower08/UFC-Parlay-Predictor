# Historical Fight Backtest Report

## Plain-English Summary
This backtest simulated 5537 historical fights by hiding outcome labels until after model predictions were generated from pre-fight features. Duration is now backtested as one finish/goes-distance model, round reads are separate binary models, and method is scored through the duration-plus-finish-type umbrella.

## Hierarchical Outcome Backtest
| Model | Fights | Accuracy | Balanced Accuracy | Baseline | Improvement | Status |
|---|---:|---:|---:|---:|---:|---|
| fight_duration_model | 3696 | 0.8287 | 0.8297 | 0.5141 | 0.3146 | backtested |
| over_1_5_model | 3683 | 0.7385 | 0.6758 | 0.6964 | 0.0421 | backtested |
| over_2_5_model | 3683 | 0.7942 | 0.79 | 0.5599 | 0.2343 | backtested |
| ends_before_round_3_model | 3683 | 0.7719 | 0.7611 | 0.6066 | 0.1653 | backtested |
| finish_in_round_1_model | 3683 | 0.6516 | 0.6127 | 0.7613 | -0.1097 | weak_or_failed_baseline |
| finish_type_model | 1796 | 0.559 | 0.44 | 0.632 | -0.073 | weak_or_failed_baseline |
| method_umbrella_model | 3696 | 0.6545 | 0.4621 | 0.5141 | 0.1404 | backtested |

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
| winner_model | 3327 | 0.9092 | 0.52 | 0.3892 | True | backtested |
| fight_duration_model | 3696 | 0.8287 | 0.5141 | 0.3146 | True | backtested |
| finish_model | 3696 | 0.8287 | 0.5141 | 0.3146 | True | backtested |
| goes_distance_model | 3696 | 0.8287 | 0.5141 | 0.3146 | True | backtested |
| over_2_5_model | 3683 | 0.7942 | 0.5599 | 0.2343 | True | backtested |
| ends_before_round_3_model | 3683 | 0.7719 | 0.6066 | 0.1653 | True | backtested |
| method_umbrella_model | 3696 | 0.6545 | 0.5141 | 0.1404 | True | backtested |
| method_model | 3696 | 0.6545 | 0.5141 | 0.1404 | True | backtested |
| strike_volume_model | 1322 | 0.438 | 0.3623 | 0.0757 | True | backtested |
| over_1_5_model | 3683 | 0.7385 | 0.6964 | 0.0421 | True | backtested |
| takedown_control_model | 2486 | 0.5973 | 0.5897 | 0.0076 | True | backtested |
| finish_type_model | 1796 | 0.559 | 0.632 | -0.073 | False | weak_or_failed_baseline |
| finish_in_round_1_model | 3683 | 0.6516 | 0.7613 | -0.1097 | False | weak_or_failed_baseline |
| odds_calibration_model | 0 |  |  |  | False | skipped |
| round_phase_model | 0 |  |  |  | False | skipped |
| round_model | 0 |  |  |  | False | skipped |

## Production Readiness Gates
| Model | Production Status | Failed Gates | Public Warning |
|---|---|---|---|
| odds_calibration_model | blocked | model_blocked | This model is blocked until required data quality gates pass. |
| winner_model | high_confidence_only | source_holdout_stable, winner_leakage_audit_passes | Use only as selective model evidence; winner audit gates are not strong enough for production-ready status. |
| fight_duration_model | production_candidate | source_holdout_not_run | Model is promising but still has failed production gates. |
| over_1_5_model | experimental | source_holdout_not_run | Model has not passed enough production-readiness gates for public confidence claims. |
| over_2_5_model | production_candidate | source_holdout_not_run | Model is promising but still has failed production gates. |
| ends_before_round_3_model | production_candidate | source_holdout_not_run | Model is promising but still has failed production gates. |
| finish_in_round_1_model | weak_or_failed_baseline | beats_chronological_baseline, calibration_acceptable, source_holdout_not_run | This model did not beat the chronological baseline and should not be used for user-facing confidence. |
| finish_type_model | weak_or_failed_baseline | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, source_holdout_not_run | This model did not beat the chronological baseline and should not be used for user-facing confidence. |
| strike_volume_model | experimental | balanced_accuracy_not_dangerously_low, calibration_acceptable, high_confidence_not_tiny_sample_noise, source_holdout_not_run | Model has not passed enough production-readiness gates for public confidence claims. |
| takedown_control_model | experimental | calibration_acceptable, source_holdout_not_run | Model has not passed enough production-readiness gates for public confidence claims. |
| method_umbrella_model | experimental | source_holdout_not_run | Model has not passed enough production-readiness gates for public confidence claims. |
| finish_model | production_candidate | source_holdout_not_run | Model is promising but still has failed production gates. |
| goes_distance_model | production_candidate | source_holdout_not_run | Model is promising but still has failed production gates. |
| method_model | experimental | source_holdout_not_run | Model has not passed enough production-readiness gates for public confidence claims. |
| round_phase_model | experimental | balanced_accuracy_not_dangerously_low, calibration_acceptable, source_holdout_not_run | Model has not passed enough production-readiness gates for public confidence claims. |
| round_model | experimental | balanced_accuracy_not_dangerously_low, calibration_acceptable, source_holdout_not_run | Model has not passed enough production-readiness gates for public confidence claims. |

## Models Not Run
- `odds_calibration_model`: Trusted pre-fight odds snapshots are not available.

## Best Predictions
- Danny Barlow vs Josh Quinlan (fight_duration_model): predicted `1` with confidence 0.9954.
- Danny Barlow vs Josh Quinlan (finish_model): predicted `1` with confidence 0.9954.
- Danny Barlow vs Josh Quinlan (goes_distance_model): predicted `0` with confidence 0.9954.
- Danny Barlow vs Josh Quinlan (fight_duration_model): predicted `1` with confidence 0.9954.
- Danny Barlow vs Josh Quinlan (finish_model): predicted `1` with confidence 0.9954.

## Worst Misses
- Luke Riley vs Michael Aswell Jr. (fight_duration_model): predicted `1` with confidence 0.9951.
- Luke Riley vs Michael Aswell Jr. (finish_model): predicted `1` with confidence 0.9951.
- Luke Riley vs Michael Aswell Jr. (goes_distance_model): predicted `0` with confidence 0.9951.
- Luke Riley vs Michael Aswell Jr. (fight_duration_model): predicted `1` with confidence 0.9951.
- Luke Riley vs Michael Aswell Jr. (finish_model): predicted `1` with confidence 0.9951.

## Prop Examples
- Chad Anheliger vs Jose Johnson: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Joanderson Brito vs Jonathan Pearce: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Myktybek Orolbai vs Uros Medic: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Joanderson Brito vs Jonathan Pearce: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Chad Anheliger vs Jose Johnson: fighter 1 over 50 sig strikes=True, fighter 2 1+ takedown=True.

## Segment Performance
### winner_model
- weight_class:Bantamweight: {'rows': 146, 'accuracy': 0.9041, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8702, 'unstable_sample_warning': False}
- weight_class:Featherweight: {'rows': 147, 'accuracy': 0.9116, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.8527, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 102, 'accuracy': 0.9314, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8352, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 88, 'accuracy': 0.875, 'unstable_sample_warning': True}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.8493, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 85, 'accuracy': 0.9176, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8684, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 163, 'accuracy': 0.9018, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.9122, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 161, 'accuracy': 0.9379, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8552, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 143, 'accuracy': 0.9091, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.8788, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 53, 'accuracy': 0.9057, 'unstable_sample_warning': True}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.8444, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 60, 'accuracy': 0.9333, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.9444, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 81, 'accuracy': 0.963, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8592, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 106, 'accuracy': 0.934, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.9537, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.9726, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.9455, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 63, 'accuracy': 0.9524, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 125, 'accuracy': 0.976, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 113, 'accuracy': 0.9558, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 108, 'accuracy': 0.9537, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.973, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.9796, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.9508, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8577, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.9137, 'unstable_sample_warning': False}
### fight_duration_model
- weight_class:Bantamweight: {'rows': 292, 'accuracy': 0.839, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8702, 'unstable_sample_warning': False}
- weight_class:Catch Weight: {'rows': 30, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 297, 'accuracy': 0.8451, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.8527, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 202, 'accuracy': 0.8515, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8132, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 175, 'accuracy': 0.7371, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.7534, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 175, 'accuracy': 0.84, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8684, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 335, 'accuracy': 0.8179, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8446, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 323, 'accuracy': 0.8204, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8759, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.784, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7955, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 105, 'accuracy': 0.9143, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.9556, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 122, 'accuracy': 0.8443, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8519, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 162, 'accuracy': 0.7901, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 477, 'accuracy': 0.8721, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3219, 'accuracy': 0.8223, 'unstable_sample_warning': False}
### over_1_5_model
- weight_class:Bantamweight: {'rows': 291, 'accuracy': 0.811, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8092, 'unstable_sample_warning': False}
- weight_class:Catch Weight: {'rows': 30, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 295, 'accuracy': 0.7017, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.6744, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 201, 'accuracy': 0.7413, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.7363, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 174, 'accuracy': 0.7069, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.6986, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 174, 'accuracy': 0.6494, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.6579, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 332, 'accuracy': 0.7259, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7432, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 322, 'accuracy': 0.6832, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.6759, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.7352, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7197, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 104, 'accuracy': 0.7981, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.8222, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 121, 'accuracy': 0.8099, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8148, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 161, 'accuracy': 0.8323, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 474, 'accuracy': 0.7616, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3209, 'accuracy': 0.7351, 'unstable_sample_warning': False}
### over_2_5_model
- weight_class:Bantamweight: {'rows': 291, 'accuracy': 0.8419, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8626, 'unstable_sample_warning': False}
- weight_class:Catch Weight: {'rows': 30, 'accuracy': 0.9333, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 295, 'accuracy': 0.7898, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.8062, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 201, 'accuracy': 0.806, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8132, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 174, 'accuracy': 0.7586, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.726, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 174, 'accuracy': 0.7529, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8026, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 332, 'accuracy': 0.7801, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7905, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 322, 'accuracy': 0.7578, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8138, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.7282, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.697, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 104, 'accuracy': 0.8846, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.8667, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 121, 'accuracy': 0.843, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8889, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 161, 'accuracy': 0.8075, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8732, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 474, 'accuracy': 0.8565, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3209, 'accuracy': 0.785, 'unstable_sample_warning': False}
### ends_before_round_3_model
- weight_class:Bantamweight: {'rows': 291, 'accuracy': 0.8385, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8397, 'unstable_sample_warning': False}
- weight_class:Catch Weight: {'rows': 30, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 295, 'accuracy': 0.7661, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7752, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 201, 'accuracy': 0.7463, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.7582, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 174, 'accuracy': 0.7011, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.7123, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 174, 'accuracy': 0.7356, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.7632, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 332, 'accuracy': 0.7711, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7703, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 322, 'accuracy': 0.736, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.7655, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.7352, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7273, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 104, 'accuracy': 0.8558, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.8667, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 121, 'accuracy': 0.8099, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8148, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 161, 'accuracy': 0.8075, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.831, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 474, 'accuracy': 0.808, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3209, 'accuracy': 0.7666, 'unstable_sample_warning': False}
### finish_in_round_1_model
- weight_class:Bantamweight: {'rows': 291, 'accuracy': 0.7801, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.771, 'unstable_sample_warning': False}
- weight_class:Catch Weight: {'rows': 30, 'accuracy': 0.7333, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 295, 'accuracy': 0.5695, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.5271, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 201, 'accuracy': 0.6219, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.5714, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 174, 'accuracy': 0.6092, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.6712, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 174, 'accuracy': 0.5517, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.5395, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 332, 'accuracy': 0.6446, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.6284, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 322, 'accuracy': 0.5714, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.5517, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.6341, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.5833, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 104, 'accuracy': 0.7212, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.7556, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 121, 'accuracy': 0.7521, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.7593, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 161, 'accuracy': 0.8944, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.9014, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 474, 'accuracy': 0.6519, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3209, 'accuracy': 0.6516, 'unstable_sample_warning': False}
### finish_type_model
- weight_class:Bantamweight: {'rows': 91, 'accuracy': 0.3846, 'unstable_sample_warning': True}
- weight_class:Bantamweight Bout: {'rows': 42, 'accuracy': 0.5, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 164, 'accuracy': 0.5305, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 71, 'accuracy': 0.5775, 'unstable_sample_warning': True}
- weight_class:Flyweight: {'rows': 97, 'accuracy': 0.5258, 'unstable_sample_warning': True}
- weight_class:Flyweight Bout: {'rows': 42, 'accuracy': 0.5238, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 90, 'accuracy': 0.5444, 'unstable_sample_warning': True}
- weight_class:Heavyweight Bout: {'rows': 37, 'accuracy': 0.4865, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 117, 'accuracy': 0.6752, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 49, 'accuracy': 0.7143, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 174, 'accuracy': 0.5517, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 75, 'accuracy': 0.6533, 'unstable_sample_warning': True}
- weight_class:Middleweight: {'rows': 189, 'accuracy': 0.5397, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 87, 'accuracy': 0.5862, 'unstable_sample_warning': True}
- weight_class:Welterweight: {'rows': 159, 'accuracy': 0.6792, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 76, 'accuracy': 0.6711, 'unstable_sample_warning': True}
- weight_class:Women's Bantamweight: {'rows': 42, 'accuracy': 0.4762, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 33, 'accuracy': 0.4545, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 51, 'accuracy': 0.2941, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 272, 'accuracy': 0.5074, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 1524, 'accuracy': 0.5682, 'unstable_sample_warning': False}
### strike_volume_model
- weight_class:Bantamweight: {'rows': 150, 'accuracy': 0.52, 'unstable_sample_warning': False}
- weight_class:Featherweight: {'rows': 152, 'accuracy': 0.5, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 103, 'accuracy': 0.4078, 'unstable_sample_warning': False}
- weight_class:Heavyweight: {'rows': 94, 'accuracy': 0.4149, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 90, 'accuracy': 0.4556, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 174, 'accuracy': 0.3851, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 169, 'accuracy': 0.4142, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 148, 'accuracy': 0.4189, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 55, 'accuracy': 0.4364, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 62, 'accuracy': 0.4516, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 83, 'accuracy': 0.4217, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 231, 'accuracy': 0.4762, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 1091, 'accuracy': 0.4299, 'unstable_sample_warning': False}
### takedown_control_model
- weight_class:Bantamweight: {'rows': 150, 'accuracy': 0.56, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.5649, 'unstable_sample_warning': False}
- weight_class:Featherweight: {'rows': 152, 'accuracy': 0.5592, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.5659, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 103, 'accuracy': 0.5631, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.6154, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 94, 'accuracy': 0.6702, 'unstable_sample_warning': True}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.6849, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 90, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8158, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 174, 'accuracy': 0.523, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.5946, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 169, 'accuracy': 0.6154, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.7034, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 148, 'accuracy': 0.6149, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.697, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 55, 'accuracy': 0.4909, 'unstable_sample_warning': True}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.6, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 62, 'accuracy': 0.4355, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.5926, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 83, 'accuracy': 0.3855, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.5352, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 427, 'accuracy': 0.6206, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 2059, 'accuracy': 0.5925, 'unstable_sample_warning': False}
### method_umbrella_model
- weight_class:Bantamweight: {'rows': 292, 'accuracy': 0.7021, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.7405, 'unstable_sample_warning': False}
- weight_class:Catch Weight: {'rows': 30, 'accuracy': 0.7667, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 297, 'accuracy': 0.6364, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.6434, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 202, 'accuracy': 0.6535, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.6374, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 175, 'accuracy': 0.5657, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.5479, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 175, 'accuracy': 0.68, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.7368, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 335, 'accuracy': 0.6149, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7095, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 323, 'accuracy': 0.5882, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.6552, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.6202, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.6136, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 105, 'accuracy': 0.7333, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.7778, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 122, 'accuracy': 0.7213, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.7222, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 162, 'accuracy': 0.6605, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.6761, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 477, 'accuracy': 0.6373, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3219, 'accuracy': 0.657, 'unstable_sample_warning': False}
### finish_model
- weight_class:Bantamweight: {'rows': 292, 'accuracy': 0.839, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8702, 'unstable_sample_warning': False}
- weight_class:Catch Weight: {'rows': 30, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 297, 'accuracy': 0.8451, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.8527, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 202, 'accuracy': 0.8515, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8132, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 175, 'accuracy': 0.7371, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.7534, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 175, 'accuracy': 0.84, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8684, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 335, 'accuracy': 0.8179, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8446, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 323, 'accuracy': 0.8204, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8759, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.784, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7955, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 105, 'accuracy': 0.9143, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.9556, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 122, 'accuracy': 0.8443, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8519, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 162, 'accuracy': 0.7901, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 477, 'accuracy': 0.8721, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3219, 'accuracy': 0.8223, 'unstable_sample_warning': False}
### goes_distance_model
- weight_class:Bantamweight: {'rows': 292, 'accuracy': 0.839, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8702, 'unstable_sample_warning': False}
- weight_class:Catch Weight: {'rows': 30, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 297, 'accuracy': 0.8451, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.8527, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 202, 'accuracy': 0.8515, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8132, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 175, 'accuracy': 0.7371, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.7534, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 175, 'accuracy': 0.84, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8684, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 335, 'accuracy': 0.8179, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8446, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 323, 'accuracy': 0.8204, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8759, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.784, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7955, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 105, 'accuracy': 0.9143, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.9556, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 122, 'accuracy': 0.8443, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8519, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 162, 'accuracy': 0.7901, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 477, 'accuracy': 0.8721, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3219, 'accuracy': 0.8223, 'unstable_sample_warning': False}
### method_model
- weight_class:Bantamweight: {'rows': 292, 'accuracy': 0.7021, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.7405, 'unstable_sample_warning': False}
- weight_class:Catch Weight: {'rows': 30, 'accuracy': 0.7667, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 297, 'accuracy': 0.6364, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.6434, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 202, 'accuracy': 0.6535, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.6374, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 175, 'accuracy': 0.5657, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.5479, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 175, 'accuracy': 0.68, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.7368, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 335, 'accuracy': 0.6149, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7095, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 323, 'accuracy': 0.5882, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.6552, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.6202, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.6136, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 105, 'accuracy': 0.7333, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.7778, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 122, 'accuracy': 0.7213, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.7222, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 162, 'accuracy': 0.6605, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.6761, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 477, 'accuracy': 0.6373, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3219, 'accuracy': 0.657, 'unstable_sample_warning': False}

## Next Steps
- Improve safe winner-model orientation before backtesting winner probabilities.
- Add trusted pre-fight odds timestamps before odds calibration.
- Keep weak models out of production-ready status until they beat baseline.
