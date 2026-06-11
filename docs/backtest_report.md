# Historical Fight Backtest Report

## Plain-English Summary
This backtest simulated 5537 historical fights by hiding outcome labels until after model predictions were generated from pre-fight features. Duration is now backtested as one finish/goes-distance model, round reads are separate binary models, and method is scored through the duration-plus-finish-type umbrella.

## Hierarchical Outcome Backtest
| Model | Fights | Accuracy | Balanced Accuracy | Baseline | Improvement | Status |
|---|---:|---:|---:|---:|---:|---|
| fight_duration_model | 3327 | 0.8596 | 0.8586 | 0.5191 | 0.3405 | backtested |
| over_1_5_model | 3327 | 0.7947 | 0.7005 | 0.6976 | 0.0971 | backtested |
| over_2_5_model | 3327 | 0.8197 | 0.8082 | 0.5621 | 0.2576 | backtested |
| ends_before_round_3_model | 3327 | 0.7926 | 0.7698 | 0.609 | 0.1836 | backtested |
| finish_in_round_1_model | 3327 | 0.8437 | 0.7041 | 0.7628 | 0.0809 | backtested |
| finish_type_model | 1600 | 0.7956 | 0.7032 | 0.6412 | 0.1544 | backtested |
| method_umbrella_model | 3327 | 0.7923 | 0.6399 | 0.5191 | 0.2732 | backtested |

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
| winner_model | 3327 | 0.9621 | 0.52 | 0.4421 | True | backtested |
| fight_duration_model | 3327 | 0.8596 | 0.5191 | 0.3405 | True | backtested |
| finish_model | 3327 | 0.8596 | 0.5191 | 0.3405 | True | backtested |
| goes_distance_model | 3327 | 0.8596 | 0.5191 | 0.3405 | True | backtested |
| method_umbrella_model | 3327 | 0.7923 | 0.5191 | 0.2732 | True | backtested |
| method_model | 3327 | 0.7923 | 0.5191 | 0.2732 | True | backtested |
| over_2_5_model | 3327 | 0.8197 | 0.5621 | 0.2576 | True | backtested |
| strike_volume_model | 1322 | 0.5749 | 0.3623 | 0.2126 | True | backtested |
| ends_before_round_3_model | 3327 | 0.7926 | 0.609 | 0.1836 | True | backtested |
| finish_type_model | 1600 | 0.7956 | 0.6412 | 0.1544 | True | backtested |
| takedown_control_model | 2486 | 0.7285 | 0.5897 | 0.1388 | True | backtested |
| over_1_5_model | 3327 | 0.7947 | 0.6976 | 0.0971 | True | backtested |
| finish_in_round_1_model | 3327 | 0.8437 | 0.7628 | 0.0809 | True | backtested |
| odds_calibration_model | 0 |  |  |  | False | skipped |
| round_phase_model | 0 |  |  |  | False | skipped |
| round_model | 0 |  |  |  | False | skipped |

## Production Readiness Gates
| Model | Production Status | Failed Gates | Public Warning |
|---|---|---|---|
| odds_calibration_model | blocked | model_blocked | This model is blocked until required data quality gates pass. |
| winner_model | high_confidence_only | source_holdout_stable, winner_leakage_audit_passes | Use only as selective model evidence; winner audit gates are not strong enough for production-ready status. |
| fight_duration_model | production_ready |  | Model passed automated production gates, but fight predictions remain uncertain. |
| over_1_5_model | production_ready |  | Model passed automated production gates, but fight predictions remain uncertain. |
| over_2_5_model | production_ready |  | Model passed automated production gates, but fight predictions remain uncertain. |
| ends_before_round_3_model | production_ready |  | Model passed automated production gates, but fight predictions remain uncertain. |
| finish_in_round_1_model | production_ready |  | Model passed automated production gates, but fight predictions remain uncertain. |
| finish_type_model | experimental | source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |
| strike_volume_model | experimental | interaction_source_holdout_regression, source_holdout_regression, source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |
| takedown_control_model | experimental | source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |
| method_umbrella_model | weak_or_failed_baseline | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, source_holdout_regression, source_holdout_unstable | This model did not beat the chronological baseline and should not be used for user-facing confidence. |
| finish_model | production_ready |  | Model passed automated production gates, but fight predictions remain uncertain. |
| goes_distance_model | production_ready |  | Model passed automated production gates, but fight predictions remain uncertain. |
| method_model | weak_or_failed_baseline | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, source_holdout_regression, source_holdout_unstable | This model did not beat the chronological baseline and should not be used for user-facing confidence. |
| round_phase_model | experimental | balanced_accuracy_not_dangerously_low, calibration_acceptable | Model has not passed enough production-readiness gates for public confidence claims. |
| round_model | experimental | balanced_accuracy_not_dangerously_low, calibration_acceptable | Model has not passed enough production-readiness gates for public confidence claims. |

## Interaction Features Used In Backtest
| Model | Interaction Features | Selection Status |
|---|---:|---|
| odds_calibration_model | 0 | not_run |
| winner_model | 0 | base_features_kept |
| fight_duration_model | 20 | selected |
| over_1_5_model | 10 | selected |
| over_2_5_model | 5 | selected |
| ends_before_round_3_model | 0 | base_features_kept |
| finish_in_round_1_model | 5 | selected |
| finish_type_model | 0 | base_features_kept |
| strike_volume_model | 10 | selected |
| takedown_control_model | 0 | base_features_kept |
| method_umbrella_model | 0 | not_run |
| finish_model | 20 | selected |
| goes_distance_model | 20 | selected |
| method_model | 0 | not_run |
| round_phase_model | 0 | not_run |
| round_model | 0 | not_run |

## Models Not Run
- `odds_calibration_model`: Trusted pre-fight odds snapshots are not available.

## Best Predictions
- Ivana Petrovic vs Jamey-Lyn Horth (finish_in_round_1_model): predicted `0` with confidence 0.985.
- Ivana Petrovic vs Jamey-Lyn Horth (finish_in_round_1_model): predicted `0` with confidence 0.985.
- Quang Le vs Xiao Long (finish_in_round_1_model): predicted `0` with confidence 0.9845.
- Bruno Lopes vs Magomed Gadzhiyasulov (finish_in_round_1_model): predicted `0` with confidence 0.9845.
- Ivan Erslan vs Navajo Stirling (finish_in_round_1_model): predicted `0` with confidence 0.9845.

## Worst Misses
- Jarno Errens vs Youssef Zalal (finish_in_round_1_model): predicted `0` with confidence 0.9839.
- Jamey-Lyn Horth vs Tereza Bleda (finish_in_round_1_model): predicted `0` with confidence 0.9839.
- Carlos Vera vs Josias Musasa (finish_in_round_1_model): predicted `0` with confidence 0.9835.
- Bolaji Oki vs Chris Duncan (finish_in_round_1_model): predicted `0` with confidence 0.9834.
- Austin Bashi vs John Yannis (finish_in_round_1_model): predicted `0` with confidence 0.9832.

## Prop Examples
- Chad Anheliger vs Jose Johnson: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Joanderson Brito vs Jonathan Pearce: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Myktybek Orolbai vs Uros Medic: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Joanderson Brito vs Jonathan Pearce: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Chad Anheliger vs Jose Johnson: fighter 1 over 50 sig strikes=True, fighter 2 1+ takedown=True.

## Segment Performance
### winner_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 37, 'accuracy': 0.0, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.0, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 267, 'accuracy': 0.0, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.0, 'unstable_sample_warning': False}
### fight_duration_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 37, 'accuracy': 0.0, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.0, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 267, 'accuracy': 0.0, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.0, 'unstable_sample_warning': False}
### over_1_5_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 37, 'accuracy': 0.0, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.0, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 267, 'accuracy': 0.0, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.0, 'unstable_sample_warning': False}
### over_2_5_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 37, 'accuracy': 0.0, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.0, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 267, 'accuracy': 0.0, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.0, 'unstable_sample_warning': False}
### ends_before_round_3_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 37, 'accuracy': 0.0, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.0, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 267, 'accuracy': 0.0, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.0, 'unstable_sample_warning': False}
### finish_in_round_1_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 37, 'accuracy': 0.0, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.0, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 267, 'accuracy': 0.0, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.0, 'unstable_sample_warning': False}
### finish_type_model
- weight_class:bantamweight: {'rows': 120, 'accuracy': 0.775, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 211, 'accuracy': 0.8341, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 124, 'accuracy': 0.8387, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 111, 'accuracy': 0.7928, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 146, 'accuracy': 0.8425, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 217, 'accuracy': 0.7373, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 245, 'accuracy': 0.7796, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 217, 'accuracy': 0.8203, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 54, 'accuracy': 0.7778, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 41, 'accuracy': 0.9756, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 65, 'accuracy': 0.5846, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 154, 'accuracy': 0.7013, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 1446, 'accuracy': 0.8057, 'unstable_sample_warning': False}
### strike_volume_model
- weight_class:bantamweight: {'rows': 150, 'accuracy': 0.6, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 154, 'accuracy': 0.5909, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 103, 'accuracy': 0.6019, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 99, 'accuracy': 0.5859, 'unstable_sample_warning': True}
- weight_class:light_heavyweight: {'rows': 90, 'accuracy': 0.6778, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 175, 'accuracy': 0.5314, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 175, 'accuracy': 0.5429, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 148, 'accuracy': 0.5135, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 55, 'accuracy': 0.6364, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 62, 'accuracy': 0.5968, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 83, 'accuracy': 0.5542, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 95, 'accuracy': 0.4211, 'unstable_sample_warning': True}
- enough_fighter_history: {'rows': 1227, 'accuracy': 0.5868, 'unstable_sample_warning': False}
### takedown_control_model
- weight_class:bantamweight: {'rows': 281, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 30, 'accuracy': 0.0, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 283, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 194, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 172, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 166, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 323, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 320, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 280, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 100, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 116, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 154, 'accuracy': 0.0, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 291, 'accuracy': 0.0, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 2195, 'accuracy': 0.0, 'unstable_sample_warning': False}
### method_umbrella_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.859, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 37, 'accuracy': 0.8919, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.7839, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.8045, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.7685, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.7812, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.7729, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.7661, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.7624, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.7778, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.8528, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.8028, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8127, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.7905, 'unstable_sample_warning': False}
### finish_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 37, 'accuracy': 0.0, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.0, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 267, 'accuracy': 0.0, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.0, 'unstable_sample_warning': False}
### goes_distance_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 37, 'accuracy': 0.0, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.0, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.0, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 267, 'accuracy': 0.0, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.0, 'unstable_sample_warning': False}
### method_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.859, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 37, 'accuracy': 0.8919, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.7839, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.8045, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.7685, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.7812, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.7729, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.7661, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.7624, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.7778, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.8528, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.8028, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8127, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.7905, 'unstable_sample_warning': False}

## Next Steps
- Improve safe winner-model orientation before backtesting winner probabilities.
- Add trusted pre-fight odds timestamps before odds calibration.
- Keep weak models out of production-ready status until they beat baseline.
