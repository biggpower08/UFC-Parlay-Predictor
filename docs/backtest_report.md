# Historical Fight Backtest Report

## Plain-English Summary
This backtest simulated 5537 historical fights by hiding outcome labels until after model predictions were generated from pre-fight features.

## Backtest Setup
- Date range: {'min': '2023-11-18', 'max': '2026-05-16'}
- Data hidden before prediction: combined_sig_strikes, fighter_a_sig_strikes, fighter_a_takedowns, fighter_b_sig_strikes, fighter_b_takedowns, finish_binary, finish_round, finish_time, goes_distance_binary, grappling_heavy_binary, loser, method, method_class, method_group, result, round_phase_class, takedown_control_bucket, winner
- Models run: winner_model, finish_model, goes_distance_model, method_model, round_phase_model, strike_volume_model, takedown_control_model
- Source rows in train: {'mdabbert_ultimate': 4771, 'ufc_1994_2025': 6176, 'ufc_1994_2026': 6154, 'ufc_fight_forecast': 6062, 'ufc_stats_complete': 6184}
- Source rows in final test: {'mdabbert_ultimate': 1210, 'ufc_1994_2025': 922, 'ufc_1994_2026': 1164, 'ufc_fight_forecast': 955, 'ufc_stats_complete': 1286}

## Overall Ranking
| Model | Fights Tested | Main Metric | Baseline | Improvement | Beats Baseline | Status |
|---|---:|---:|---:|---:|---|---|
| winner_model | 3327 | 0.9092 | 0.52 | 0.3892 | True | backtested |
| finish_model | 3696 | 0.8287 | 0.5141 | 0.3146 | True | backtested |
| goes_distance_model | 3696 | 0.8287 | 0.5141 | 0.3146 | True | backtested |
| method_model | 3696 | 0.6656 | 0.5141 | 0.1515 | True | backtested |
| strike_volume_model | 1322 | 0.438 | 0.3623 | 0.0757 | True | backtested |
| takedown_control_model | 2486 | 0.5973 | 0.5897 | 0.0076 | True | backtested |
| round_phase_model | 3696 | 0.3122 | 0.5141 | -0.2019 | False | weak_or_failed_baseline |
| odds_calibration_model | 0 |  |  |  | False | skipped |

## Production Readiness Gates
| Model | Production Status | Failed Gates | Public Warning |
|---|---|---|---|
| odds_calibration_model | blocked | model_blocked | This model is blocked until required data quality gates pass. |
| winner_model | high_confidence_only | source_holdout_stable, winner_leakage_audit_passes | Use only as selective model evidence; winner audit gates are not strong enough for production-ready status. |
| finish_model | production_candidate | source_holdout_not_run | Model is promising but still has failed production gates. |
| goes_distance_model | production_candidate | source_holdout_not_run | Model is promising but still has failed production gates. |
| method_model | experimental | source_holdout_not_run | Model has not passed enough production-readiness gates for public confidence claims. |
| round_phase_model | weak_or_failed_baseline | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, source_holdout_not_run | This model did not beat the chronological baseline and should not be used for user-facing confidence. |
| strike_volume_model | experimental | balanced_accuracy_not_dangerously_low, calibration_acceptable, high_confidence_not_tiny_sample_noise, source_holdout_not_run | Model has not passed enough production-readiness gates for public confidence claims. |
| takedown_control_model | experimental | calibration_acceptable, source_holdout_not_run | Model has not passed enough production-readiness gates for public confidence claims. |

## Models Not Run
- `odds_calibration_model`: Trusted pre-fight odds snapshots are not available.

## Best Predictions
- Alice Ardelean vs Montserrat Conejo Ruiz (method_model): predicted `Decision` with confidence 0.9967.
- Gabriel Miranda vs Morgan Charriere (goes_distance_model): predicted `0` with confidence 0.9966.
- Felipe dos Santos vs Lone'er Kavanagh (method_model): predicted `Decision` with confidence 0.9966.
- Blake Bilder vs JeongYeong Lee (method_model): predicted `Decision` with confidence 0.9965.
- Gabriel Miranda vs Morgan Charriere (goes_distance_model): predicted `0` with confidence 0.9965.

## Worst Misses
- Draw/NC vs Makhmud Muradov (round_phase_model): predicted `late` with confidence 1.0.
- Draw/NC vs Rodolfo Bellato (round_phase_model): predicted `late` with confidence 1.0.
- Draw/NC vs Rodolfo Bellato (round_phase_model): predicted `late` with confidence 1.0.
- Draw/NC vs Nikolas Motta (round_phase_model): predicted `late` with confidence 0.9999.
- Draw/NC vs Sedriques Dumas (round_phase_model): predicted `late` with confidence 0.9999.

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
- weight_class:Bantamweight: {'rows': 292, 'accuracy': 0.8459, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8626, 'unstable_sample_warning': False}
- weight_class:Catch Weight: {'rows': 30, 'accuracy': 0.8, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 297, 'accuracy': 0.8485, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.8295, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 202, 'accuracy': 0.8465, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8462, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 175, 'accuracy': 0.7429, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.7397, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 175, 'accuracy': 0.8457, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8684, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 335, 'accuracy': 0.8209, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8784, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 323, 'accuracy': 0.8111, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8828, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.7805, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7803, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 105, 'accuracy': 0.9238, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.9556, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 122, 'accuracy': 0.8279, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8519, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 162, 'accuracy': 0.7716, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 477, 'accuracy': 0.8889, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3219, 'accuracy': 0.8198, 'unstable_sample_warning': False}
### method_model
- weight_class:Bantamweight: {'rows': 292, 'accuracy': 0.7089, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.7405, 'unstable_sample_warning': False}
- weight_class:Catch Weight: {'rows': 30, 'accuracy': 0.6667, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 297, 'accuracy': 0.633, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.6357, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 202, 'accuracy': 0.6485, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.6264, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 175, 'accuracy': 0.64, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.6575, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 175, 'accuracy': 0.6629, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.6974, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 335, 'accuracy': 0.6209, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.6892, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 323, 'accuracy': 0.6223, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.6621, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.6202, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.6061, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 105, 'accuracy': 0.7714, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.7778, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 122, 'accuracy': 0.7623, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.7963, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 162, 'accuracy': 0.6852, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.7465, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 477, 'accuracy': 0.608, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3219, 'accuracy': 0.6741, 'unstable_sample_warning': False}
### round_phase_model
- weight_class:Bantamweight: {'rows': 292, 'accuracy': 0.3664, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.3817, 'unstable_sample_warning': False}
- weight_class:Catch Weight: {'rows': 30, 'accuracy': 0.1, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 297, 'accuracy': 0.2492, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.2636, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 202, 'accuracy': 0.3218, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.3187, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 175, 'accuracy': 0.2343, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.274, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 175, 'accuracy': 0.2229, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.2763, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 335, 'accuracy': 0.3313, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.3378, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 323, 'accuracy': 0.2384, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.2276, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.2265, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.2348, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 105, 'accuracy': 0.5524, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.5333, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 122, 'accuracy': 0.4016, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.463, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 162, 'accuracy': 0.5617, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.5915, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 477, 'accuracy': 0.283, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3219, 'accuracy': 0.3166, 'unstable_sample_warning': False}
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

## Next Steps
- Improve safe winner-model orientation before backtesting winner probabilities.
- Add trusted pre-fight odds timestamps before odds calibration.
- Keep weak models out of production-ready status until they beat baseline.
