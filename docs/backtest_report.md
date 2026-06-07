# Historical Fight Backtest Report

## Plain-English Summary
This backtest simulated 2440 historical fights by hiding outcome labels until after model predictions were generated from pre-fight features.

## Backtest Setup
- Date range: {'min': '2023-03-04', 'max': '2025-10-04'}
- Data hidden before prediction: combined_sig_strikes, fighter_a_sig_strikes, fighter_a_takedowns, fighter_b_sig_strikes, fighter_b_takedowns, finish_binary, finish_round, finish_time, goes_distance_binary, grappling_heavy_binary, loser, method, method_class, method_group, result, round_phase_class, takedown_control_bucket, winner
- Models run: finish_model, goes_distance_model, method_model, round_phase_model, strike_volume_model, takedown_control_model

## Overall Ranking
| Model | Fights Tested | Main Metric | Baseline | Improvement | Beats Baseline | Status |
|---|---:|---:|---:|---:|---|---|
| finish_model | 2440 | 0.5627 | 0.5201 | 0.0426 | True | backtested |
| goes_distance_model | 2440 | 0.5627 | 0.5201 | 0.0426 | True | backtested |
| strike_volume_model | 1348 | 0.4073 | 0.3917 | 0.0156 | True | backtested |
| takedown_control_model | 1348 | 0.523 | 0.549 | -0.026 | False | weak_or_failed_baseline |
| method_model | 2440 | 0.2557 | 0.5201 | -0.2644 | False | weak_or_failed_baseline |
| round_phase_model | 2440 | 0.2279 | 0.5201 | -0.2922 | False | weak_or_failed_baseline |
| winner_model | 0 |  |  |  | False | skipped |
| odds_calibration_model | 0 |  |  |  | False | skipped |

## Models Not Run
- `winner_model`: Safe f1/f2 winner orientation is not runtime-compatible yet.
- `odds_calibration_model`: Trusted pre-fight odds snapshots are not available.

## Best Predictions
- Islam Makhachev vs Dustin Poirier (round_phase_model): predicted `late` with confidence 0.8043.
- islam makhachev vs dustin poirier (round_phase_model): predicted `late` with confidence 0.803.
- max holloway vs justin gaethje (round_phase_model): predicted `late` with confidence 0.8014.
- Max Holloway vs Justin Gaethje (round_phase_model): predicted `late` with confidence 0.8014.
- jared cannonier vs gregory rodrigues (round_phase_model): predicted `late` with confidence 0.7966.

## Worst Misses
- Max Holloway vs Dustin Poirier (round_phase_model): predicted `late` with confidence 0.8434.
- islam makhachev vs renato moicano (round_phase_model): predicted `late` with confidence 0.842.
- Islam Makhachev vs Renato Moicano (round_phase_model): predicted `late` with confidence 0.842.
- deiveson figueiredo vs cody garbrandt (round_phase_model): predicted `late` with confidence 0.8409.
- Deiveson Figueiredo vs Cody Garbrandt (round_phase_model): predicted `late` with confidence 0.8409.

## Prop Examples
- Shavkat Rakhmonov vs Geoff Neal: fighter 1 over 50 sig strikes=True, fighter 2 1+ takedown=False.
- Cody Garbrandt vs Trevin Jones: fighter 1 over 50 sig strikes=False, fighter 2 1+ takedown=True.
- Alexa Grasso vs Valentina Shevchenko: fighter 1 over 50 sig strikes=True, fighter 2 1+ takedown=True.
- Marc-Andre Barriault vs Julian Marquez: fighter 1 over 50 sig strikes=True, fighter 2 1+ takedown=False.
- Farid Basharat vs Da'Mon Blackshear: fighter 1 over 50 sig strikes=True, fighter 2 1+ takedown=True.

## Segment Performance
### finish_model
- low_fighter_history: {'rows': 1081, 'accuracy': 0.5282, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 1359, 'accuracy': 0.5901, 'unstable_sample_warning': False}
### goes_distance_model
- low_fighter_history: {'rows': 1081, 'accuracy': 0.5282, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 1359, 'accuracy': 0.5901, 'unstable_sample_warning': False}
### method_model
- low_fighter_history: {'rows': 1081, 'accuracy': 0.1721, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 1359, 'accuracy': 0.3223, 'unstable_sample_warning': False}
### round_phase_model
- low_fighter_history: {'rows': 1081, 'accuracy': 0.3053, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 1359, 'accuracy': 0.1663, 'unstable_sample_warning': False}
### strike_volume_model
- low_fighter_history: {'rows': 595, 'accuracy': 0.3748, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 753, 'accuracy': 0.4329, 'unstable_sample_warning': False}
### takedown_control_model
- low_fighter_history: {'rows': 595, 'accuracy': 0.4824, 'unstable_sample_warning': False}
- enough_fighter_history: {'rows': 753, 'accuracy': 0.5551, 'unstable_sample_warning': False}

## Next Steps
- Improve safe winner-model orientation before backtesting winner probabilities.
- Add trusted pre-fight odds timestamps before odds calibration.
- Keep weak models out of production-ready status until they beat baseline.
