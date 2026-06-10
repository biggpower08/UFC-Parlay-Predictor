# Historical Fight Backtest Report

## Plain-English Summary
This backtest simulated 5537 historical fights by hiding outcome labels until after model predictions were generated from pre-fight features. Duration is now backtested as one finish/goes-distance model, round reads are separate binary models, and method is scored through the duration-plus-finish-type umbrella.

## Hierarchical Outcome Backtest
| Model | Fights | Accuracy | Balanced Accuracy | Baseline | Improvement | Status |
|---|---:|---:|---:|---:|---:|---|
| fight_duration_model | 3696 | 0.8287 | 0.8282 | 0.5141 | 0.3146 | backtested |
| over_1_5_model | 3683 | 0.7869 | 0.7009 | 0.6964 | 0.0905 | backtested |
| over_2_5_model | 3683 | 0.7993 | 0.7916 | 0.5599 | 0.2394 | backtested |
| ends_before_round_3_model | 3683 | 0.7763 | 0.7503 | 0.6066 | 0.1697 | backtested |
| finish_in_round_1_model | 3683 | 0.8306 | 0.6966 | 0.7613 | 0.0693 | backtested |
| finish_type_model | 1796 | 0.7728 | 0.6162 | 0.632 | 0.1408 | backtested |
| method_umbrella_model | 3696 | 0.7538 | 0.5628 | 0.5141 | 0.2397 | backtested |

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
| fight_duration_model | 3696 | 0.8287 | 0.5141 | 0.3146 | True | backtested |
| finish_model | 3696 | 0.8287 | 0.5141 | 0.3146 | True | backtested |
| goes_distance_model | 3696 | 0.8287 | 0.5141 | 0.3146 | True | backtested |
| method_umbrella_model | 3696 | 0.7538 | 0.5141 | 0.2397 | True | backtested |
| method_model | 3696 | 0.7538 | 0.5141 | 0.2397 | True | backtested |
| over_2_5_model | 3683 | 0.7993 | 0.5599 | 0.2394 | True | backtested |
| strike_volume_model | 1322 | 0.5749 | 0.3623 | 0.2126 | True | backtested |
| ends_before_round_3_model | 3683 | 0.7763 | 0.6066 | 0.1697 | True | backtested |
| finish_type_model | 1796 | 0.7728 | 0.632 | 0.1408 | True | backtested |
| takedown_control_model | 2486 | 0.7285 | 0.5897 | 0.1388 | True | backtested |
| over_1_5_model | 3683 | 0.7869 | 0.6964 | 0.0905 | True | backtested |
| finish_in_round_1_model | 3683 | 0.8306 | 0.7613 | 0.0693 | True | backtested |
| odds_calibration_model | 0 |  |  |  | False | skipped |
| round_phase_model | 0 |  |  |  | False | skipped |
| round_model | 0 |  |  |  | False | skipped |

## Production Readiness Gates
| Model | Production Status | Failed Gates | Public Warning |
|---|---|---|---|
| odds_calibration_model | blocked | model_blocked | This model is blocked until required data quality gates pass. |
| winner_model | high_confidence_only | source_holdout_stable, winner_leakage_audit_passes | Use only as selective model evidence; winner audit gates are not strong enough for production-ready status. |
| fight_duration_model | experimental | interaction_source_holdout_regression, source_holdout_regression, source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |
| over_1_5_model | experimental | source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |
| over_2_5_model | experimental | source_holdout_regression, source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |
| ends_before_round_3_model | experimental | interaction_source_holdout_regression, source_holdout_regression, source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |
| finish_in_round_1_model | experimental | source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |
| finish_type_model | experimental | interaction_source_holdout_regression, source_holdout_regression, source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |
| strike_volume_model | experimental | interaction_source_holdout_regression, source_holdout_regression, source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |
| takedown_control_model | experimental | source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |
| method_umbrella_model | experimental | source_holdout_regression, source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |
| finish_model | experimental | interaction_source_holdout_regression, source_holdout_regression, source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |
| goes_distance_model | experimental | interaction_source_holdout_regression, source_holdout_regression, source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |
| method_model | experimental | source_holdout_regression, source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |
| round_phase_model | experimental | balanced_accuracy_not_dangerously_low, calibration_acceptable, source_holdout_regression, source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |
| round_model | experimental | balanced_accuracy_not_dangerously_low, calibration_acceptable, source_holdout_regression, source_holdout_unstable | Model source-holdout transfer is not stable enough for production candidate use. |

## Interaction Features Used In Backtest
| Model | Interaction Features | Selection Status |
|---|---:|---|
| odds_calibration_model | 0 | not_run |
| winner_model | 0 | base_features_kept |
| fight_duration_model | 5 | selected |
| over_1_5_model | 0 | base_features_kept |
| over_2_5_model | 0 | base_features_kept |
| ends_before_round_3_model | 10 | selected |
| finish_in_round_1_model | 0 | base_features_kept |
| finish_type_model | 5 | selected |
| strike_volume_model | 10 | selected |
| takedown_control_model | 0 | base_features_kept |
| method_umbrella_model | 0 | not_run |
| finish_model | 5 | selected |
| goes_distance_model | 5 | selected |
| method_model | 0 | not_run |
| round_phase_model | 0 | not_run |
| round_model | 0 | not_run |

## Models Not Run
- `odds_calibration_model`: Trusted pre-fight odds snapshots are not available.

## Best Predictions
- Ihor Potieria vs Rodolfo Bellato (fight_duration_model): predicted `1` with confidence 0.9761.
- Ihor Potieria vs Rodolfo Bellato (fight_duration_model): predicted `1` with confidence 0.9761.
- Ihor Potieria vs Rodolfo Bellato (fight_duration_model): predicted `1` with confidence 0.9761.
- Ihor Potieria vs Rodolfo Bellato (fight_duration_model): predicted `1` with confidence 0.9761.
- Azamat Bekoev vs Yousri Belgaroui (fight_duration_model): predicted `1` with confidence 0.9761.

## Worst Misses
- Blake Bilder vs JeongYeong Lee (finish_in_round_1_model): predicted `0.0` with confidence 0.9833.
- Blake Bilder vs JeongYeong Lee (finish_in_round_1_model): predicted `0.0` with confidence 0.9833.
- Blake Bilder vs JeongYeong Lee (finish_in_round_1_model): predicted `0.0` with confidence 0.9833.
- Alice Ardelean vs Melissa Martinez (finish_in_round_1_model): predicted `0.0` with confidence 0.9833.
- Aleksandre Topuria vs Colby Thicknesse (finish_in_round_1_model): predicted `0.0` with confidence 0.9833.

## Prop Examples
- Chad Anheliger vs Jose Johnson: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Joanderson Brito vs Jonathan Pearce: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Myktybek Orolbai vs Uros Medic: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Joanderson Brito vs Jonathan Pearce: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Chad Anheliger vs Jose Johnson: fighter 1 over 50 sig strikes=True, fighter 2 1+ takedown=True.

## Segment Performance
### winner_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.9634, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 37, 'accuracy': 0.9189, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.9635, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.9511, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.9352, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.9777, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.9702, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.9594, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.9765, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.963, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.9816, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.9624, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8839, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.969, 'unstable_sample_warning': False}
### fight_duration_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8629, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.8636, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.8084, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.8328, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.8261, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.8327, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.8409, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.8207, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7995, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.82, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.8068, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.8541, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 341, 'accuracy': 0.824, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.8292, 'unstable_sample_warning': False}
### over_1_5_model
- weight_class:bantamweight: {'rows': 422, 'accuracy': 0.8744, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 1.0, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 426, 'accuracy': 0.7676, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 292, 'accuracy': 0.7842, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 252, 'accuracy': 0.7222, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 250, 'accuracy': 0.7, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 481, 'accuracy': 0.7963, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 473, 'accuracy': 0.704, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7566, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 149, 'accuracy': 0.7584, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 175, 'accuracy': 0.8971, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 232, 'accuracy': 0.9052, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 338, 'accuracy': 0.7929, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.7862, 'unstable_sample_warning': False}
### over_2_5_model
- weight_class:bantamweight: {'rows': 422, 'accuracy': 0.8791, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.7955, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 426, 'accuracy': 0.7746, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 292, 'accuracy': 0.7877, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 252, 'accuracy': 0.8294, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 250, 'accuracy': 0.76, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 481, 'accuracy': 0.7817, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 473, 'accuracy': 0.8161, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7279, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 149, 'accuracy': 0.7651, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 175, 'accuracy': 0.7943, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 232, 'accuracy': 0.8578, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8343, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.7958, 'unstable_sample_warning': False}
### ends_before_round_3_model
- weight_class:bantamweight: {'rows': 422, 'accuracy': 0.8365, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.9091, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 426, 'accuracy': 0.7324, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 292, 'accuracy': 0.7432, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 252, 'accuracy': 0.7738, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 250, 'accuracy': 0.764, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 481, 'accuracy': 0.7277, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 473, 'accuracy': 0.7653, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7566, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 149, 'accuracy': 0.7651, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 175, 'accuracy': 0.8514, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 232, 'accuracy': 0.8664, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 338, 'accuracy': 0.7959, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.7743, 'unstable_sample_warning': False}
### finish_in_round_1_model
- weight_class:bantamweight: {'rows': 422, 'accuracy': 0.9194, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.9091, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 426, 'accuracy': 0.7911, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 292, 'accuracy': 0.8699, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 252, 'accuracy': 0.7778, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 250, 'accuracy': 0.704, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 481, 'accuracy': 0.8191, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 473, 'accuracy': 0.7653, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7995, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 149, 'accuracy': 0.8993, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 175, 'accuracy': 0.9086, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 232, 'accuracy': 0.9612, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8521, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.8284, 'unstable_sample_warning': False}
### finish_type_model
- weight_class:bantamweight: {'rows': 133, 'accuracy': 0.6992, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 235, 'accuracy': 0.8596, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 139, 'accuracy': 0.8201, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 128, 'accuracy': 0.7656, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 166, 'accuracy': 0.8012, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 249, 'accuracy': 0.7108, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 280, 'accuracy': 0.7429, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 235, 'accuracy': 0.8085, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 60, 'accuracy': 0.7333, 'unstable_sample_warning': True}
- weight_class:women's_flyweight: {'rows': 47, 'accuracy': 0.8936, 'unstable_sample_warning': True}
- weight_class:women's_strawweight: {'rows': 73, 'accuracy': 0.6164, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 197, 'accuracy': 0.6599, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 1599, 'accuracy': 0.7867, 'unstable_sample_warning': False}
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
- weight_class:bantamweight: {'rows': 281, 'accuracy': 0.6975, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 30, 'accuracy': 0.6333, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 283, 'accuracy': 0.7208, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 194, 'accuracy': 0.732, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 172, 'accuracy': 0.7384, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 166, 'accuracy': 0.8855, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 323, 'accuracy': 0.6873, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 320, 'accuracy': 0.7469, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 280, 'accuracy': 0.7357, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 100, 'accuracy': 0.68, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 116, 'accuracy': 0.7759, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 154, 'accuracy': 0.6688, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 291, 'accuracy': 0.8522, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 2195, 'accuracy': 0.7121, 'unstable_sample_warning': False}
### method_umbrella_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8298, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.8636, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.743, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.7747, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.7233, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.7291, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.7417, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.7068, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7303, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.76, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.7898, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.7897, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 341, 'accuracy': 0.7038, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.7589, 'unstable_sample_warning': False}
### finish_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8629, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.8636, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.8084, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.8328, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.8261, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.8327, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.8409, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.8207, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7995, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.82, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.8068, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.8541, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 341, 'accuracy': 0.824, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.8292, 'unstable_sample_warning': False}
### goes_distance_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8629, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.8636, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.8084, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.8328, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.8261, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.8327, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.8409, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.8207, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7995, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.82, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.8068, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.8541, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 341, 'accuracy': 0.824, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.8292, 'unstable_sample_warning': False}
### method_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8298, 'unstable_sample_warning': False}
- weight_class:catch_weight: {'rows': 44, 'accuracy': 0.8636, 'unstable_sample_warning': True}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.743, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.7747, 'unstable_sample_warning': False}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.7233, 'unstable_sample_warning': False}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.7291, 'unstable_sample_warning': False}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.7417, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.7068, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7303, 'unstable_sample_warning': False}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.76, 'unstable_sample_warning': False}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.7898, 'unstable_sample_warning': False}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.7897, 'unstable_sample_warning': False}
- low_fighter_history: {'rows': 341, 'accuracy': 0.7038, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.7589, 'unstable_sample_warning': False}

## Next Steps
- Improve safe winner-model orientation before backtesting winner probabilities.
- Add trusted pre-fight odds timestamps before odds calibration.
- Keep weak models out of production-ready status until they beat baseline.
