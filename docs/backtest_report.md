# Historical Fight Backtest Report

## Plain-English Summary
This backtest simulated 5537 historical fights by hiding outcome labels until after model predictions were generated from pre-fight features.

## Backtest Setup
- Date range: {'min': '2023-11-18', 'max': '2026-05-16'}
- Data hidden before prediction: combined_sig_strikes, fighter_a_sig_strikes, fighter_a_takedowns, fighter_b_sig_strikes, fighter_b_takedowns, finish_binary, finish_round, finish_time, goes_distance_binary, grappling_heavy_binary, loser, method, method_class, method_group, result, round_phase_class, takedown_control_bucket, winner
- Models run: finish_model, goes_distance_model, method_model, round_phase_model, strike_volume_model, takedown_control_model
- Source rows in train: {'mdabbert_ultimate': 4771, 'ufc_1994_2025': 6176, 'ufc_1994_2026': 6154, 'ufc_fight_forecast': 6062, 'ufc_stats_complete': 6184}
- Source rows in final test: {'mdabbert_ultimate': 1210, 'ufc_1994_2025': 922, 'ufc_1994_2026': 1164, 'ufc_fight_forecast': 955, 'ufc_stats_complete': 1286}

## Overall Ranking
| Model | Fights Tested | Main Metric | Baseline | Improvement | Beats Baseline | Status |
|---|---:|---:|---:|---:|---|---|
| finish_model | 5537 | 0.6101 | 0.5183 | 0.0918 | True | backtested |
| goes_distance_model | 5537 | 0.6101 | 0.5183 | 0.0918 | True | backtested |
| strike_volume_model | 3163 | 0.4006 | 0.3721 | 0.0285 | True | backtested |
| takedown_control_model | 4327 | 0.5193 | 0.5653 | -0.046 | False | weak_or_failed_baseline |
| method_model | 5537 | 0.3235 | 0.5183 | -0.1948 | False | weak_or_failed_baseline |
| round_phase_model | 5537 | 0.1663 | 0.5183 | -0.352 | False | weak_or_failed_baseline |
| winner_model | 0 |  |  |  | False | skipped |
| odds_calibration_model | 0 |  |  |  | False | skipped |

## Models Not Run
- `winner_model`: Safe f1/f2 winner orientation is not runtime-compatible yet.
- `odds_calibration_model`: Trusted pre-fight odds snapshots are not available.

## Best Predictions
- Islam Makhachev vs Dustin Poirier (round_phase_model): predicted `late` with confidence 0.769.
- Islam Makhachev vs Dustin Poirier (round_phase_model): predicted `late` with confidence 0.7673.
- Islam Makhachev vs Dustin Poirier (round_phase_model): predicted `late` with confidence 0.7654.
- Islam Makhachev vs Dustin Poirier (round_phase_model): predicted `late` with confidence 0.7653.
- Islam Makhachev vs Dustin Poirier (round_phase_model): predicted `late` with confidence 0.7633.

## Worst Misses
- Max Holloway vs Dustin Poirier (round_phase_model): predicted `late` with confidence 0.8077.
- Max Holloway vs Dustin Poirier (round_phase_model): predicted `late` with confidence 0.8076.
- Max Holloway vs Dustin Poirier (round_phase_model): predicted `late` with confidence 0.8076.
- Max Holloway vs Dustin Poirier (round_phase_model): predicted `late` with confidence 0.8075.
- Max Holloway vs Dustin Poirier (round_phase_model): predicted `late` with confidence 0.8074.

## Prop Examples
- Jose Johnson vs Chad Anheliger: fighter 1 over 50 sig strikes=True, fighter 2 1+ takedown=True.
- Joanderson Brito vs Jonathan Pearce: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Myktybek Orolbai vs Uros Medic: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Joanderson Brito vs Jonathan Pearce: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Jose Johnson vs Chad Anheliger: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.

## Segment Performance
### finish_model
- weight_class:Bantamweight: {'rows': 404, 'accuracy': 0.646, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.6031, 'unstable_sample_warning': False}
- weight_class:Catch Weight: {'rows': 38, 'accuracy': 0.5789, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 409, 'accuracy': 0.6357, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.6357, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 279, 'accuracy': 0.5448, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.5385, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 232, 'accuracy': 0.6078, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.5753, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 234, 'accuracy': 0.5641, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.5658, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 465, 'accuracy': 0.5634, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.5676, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 442, 'accuracy': 0.6697, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.6414, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 399, 'accuracy': 0.5489, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.5, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 144, 'accuracy': 0.6458, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.6444, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 172, 'accuracy': 0.6512, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.6111, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 226, 'accuracy': 0.6681, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.6338, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.6542, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.6667, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.5753, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.6182, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.5692, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.6032, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.7069, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.5596, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.6216, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.6939, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.6393, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 631, 'accuracy': 0.6006, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 4906, 'accuracy': 0.6113, 'unstable_sample_warning': False}
### goes_distance_model
- weight_class:Bantamweight: {'rows': 404, 'accuracy': 0.646, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.6031, 'unstable_sample_warning': False}
- weight_class:Catch Weight: {'rows': 38, 'accuracy': 0.5789, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 409, 'accuracy': 0.6357, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.6357, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 279, 'accuracy': 0.5448, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.5385, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 232, 'accuracy': 0.6078, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.5753, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 234, 'accuracy': 0.5641, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.5658, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 465, 'accuracy': 0.5634, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.5676, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 442, 'accuracy': 0.6697, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.6414, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 399, 'accuracy': 0.5489, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.5, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 144, 'accuracy': 0.6458, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.6444, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 172, 'accuracy': 0.6512, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.6111, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 226, 'accuracy': 0.6681, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.6338, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.6542, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.6667, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.5753, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.6182, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.5692, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.6032, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.7069, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.5596, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.6216, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.6939, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.6393, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 631, 'accuracy': 0.6006, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 4906, 'accuracy': 0.6113, 'unstable_sample_warning': False}
### method_model
- weight_class:Bantamweight: {'rows': 404, 'accuracy': 0.2797, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.2443, 'unstable_sample_warning': False}
- weight_class:Catch Weight: {'rows': 38, 'accuracy': 0.2368, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 409, 'accuracy': 0.3423, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.3411, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 279, 'accuracy': 0.2652, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.2747, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 232, 'accuracy': 0.1595, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.137, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 234, 'accuracy': 0.3974, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.4079, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 465, 'accuracy': 0.3226, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.3311, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 442, 'accuracy': 0.2828, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.3034, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 399, 'accuracy': 0.3133, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.3106, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 144, 'accuracy': 0.4931, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.4889, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 172, 'accuracy': 0.4419, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.4074, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 226, 'accuracy': 0.4071, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.3803, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.2897, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.3519, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.2466, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.1818, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.3846, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.3175, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.2845, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.3119, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.5135, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.4898, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.4426, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 631, 'accuracy': 0.1664, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 4906, 'accuracy': 0.3437, 'unstable_sample_warning': False}
### round_phase_model
- weight_class:Bantamweight: {'rows': 404, 'accuracy': 0.1535, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.1679, 'unstable_sample_warning': False}
- weight_class:Catch Weight: {'rows': 38, 'accuracy': 0.0526, 'unstable_sample_warning': True}
- weight_class:Featherweight: {'rows': 409, 'accuracy': 0.1711, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.1628, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 279, 'accuracy': 0.19, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.1868, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 232, 'accuracy': 0.1422, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.1507, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 234, 'accuracy': 0.094, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.0789, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 465, 'accuracy': 0.1763, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.1622, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 442, 'accuracy': 0.1561, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.1448, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 399, 'accuracy': 0.1328, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.1136, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 144, 'accuracy': 0.2153, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.2222, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 172, 'accuracy': 0.1977, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.1852, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 226, 'accuracy': 0.2743, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.2958, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.1963, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.1667, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.2192, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.1818, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.0769, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.2063, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.1638, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.1284, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.2432, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.2041, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.2951, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 631, 'accuracy': 0.13, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 4906, 'accuracy': 0.171, 'unstable_sample_warning': False}
### strike_volume_model
- weight_class:Bantamweight: {'rows': 262, 'accuracy': 0.4122, 'unstable_sample_warning': False}
- weight_class:Featherweight: {'rows': 264, 'accuracy': 0.4129, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 180, 'accuracy': 0.4056, 'unstable_sample_warning': False}
- weight_class:Heavyweight: {'rows': 151, 'accuracy': 0.3775, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight: {'rows': 149, 'accuracy': 0.4698, 'unstable_sample_warning': False}
- weight_class:Lightweight: {'rows': 304, 'accuracy': 0.352, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 288, 'accuracy': 0.4757, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 260, 'accuracy': 0.3538, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 94, 'accuracy': 0.3404, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 112, 'accuracy': 0.4375, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight: {'rows': 147, 'accuracy': 0.3265, 'unstable_sample_warning': False}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.4206, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.4167, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.4247, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.3818, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.4462, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.3571, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.4828, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.3578, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.3514, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.4898, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.3115, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 385, 'accuracy': 0.4234, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 2778, 'accuracy': 0.3974, 'unstable_sample_warning': False}
### takedown_control_model
- weight_class:Bantamweight: {'rows': 262, 'accuracy': 0.542, 'unstable_sample_warning': False}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.5573, 'unstable_sample_warning': False}
- weight_class:Featherweight: {'rows': 264, 'accuracy': 0.4659, 'unstable_sample_warning': False}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.4651, 'unstable_sample_warning': False}
- weight_class:Flyweight: {'rows': 180, 'accuracy': 0.5056, 'unstable_sample_warning': False}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.5714, 'unstable_sample_warning': True}
- weight_class:Heavyweight: {'rows': 151, 'accuracy': 0.5298, 'unstable_sample_warning': False}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.5205, 'unstable_sample_warning': True}
- weight_class:Light Heavyweight: {'rows': 149, 'accuracy': 0.6577, 'unstable_sample_warning': False}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.6842, 'unstable_sample_warning': True}
- weight_class:Lightweight: {'rows': 304, 'accuracy': 0.5362, 'unstable_sample_warning': False}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.5405, 'unstable_sample_warning': False}
- weight_class:Middleweight: {'rows': 288, 'accuracy': 0.5382, 'unstable_sample_warning': False}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.5931, 'unstable_sample_warning': False}
- weight_class:Welterweight: {'rows': 260, 'accuracy': 0.4923, 'unstable_sample_warning': False}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.5606, 'unstable_sample_warning': False}
- weight_class:Women's Bantamweight: {'rows': 94, 'accuracy': 0.5745, 'unstable_sample_warning': True}
- weight_class:Women's Bantamweight Bout: {'rows': 45, 'accuracy': 0.5111, 'unstable_sample_warning': True}
- weight_class:Women's Flyweight: {'rows': 112, 'accuracy': 0.4018, 'unstable_sample_warning': False}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.463, 'unstable_sample_warning': True}
- weight_class:Women's Strawweight: {'rows': 147, 'accuracy': 0.3605, 'unstable_sample_warning': False}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.4225, 'unstable_sample_warning': True}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.5327, 'unstable_sample_warning': False}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.4815, 'unstable_sample_warning': False}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.5342, 'unstable_sample_warning': True}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.5273, 'unstable_sample_warning': True}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.6923, 'unstable_sample_warning': True}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.5317, 'unstable_sample_warning': False}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.5431, 'unstable_sample_warning': False}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.5138, 'unstable_sample_warning': False}
- weight_class:women's bantamweight: {'rows': 37, 'accuracy': 0.5676, 'unstable_sample_warning': True}
- weight_class:women's flyweight: {'rows': 49, 'accuracy': 0.4082, 'unstable_sample_warning': True}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.377, 'unstable_sample_warning': True}
- low_fighter_history: {'rows': 581, 'accuracy': 0.401, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 3746, 'accuracy': 0.5376, 'unstable_sample_warning': False}

## Next Steps
- Improve safe winner-model orientation before backtesting winner probabilities.
- Add trusted pre-fight odds timestamps before odds calibration.
- Keep weak models out of production-ready status until they beat baseline.
