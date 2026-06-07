# Model Accuracy Report

## Plain-English Summary
Models were evaluated on the newest chronological holdout from normalized historical fight data. Metrics are approximate final-test results, not guarantees.

## Split
- Train: 11388 rows, {'min': '1994-03-11', 'max': '2020-09-19'}
- Validation: 2440 rows, {'min': '2020-09-26', 'max': '2023-03-04'}
- Final test: 2440 rows, {'min': '2023-03-04', 'max': '2025-10-04'}

## Model Ranking
| Model | Status | Test Rows | Main Metric | Baseline | Improvement | Beats Baseline | Notes |
|---|---|---:|---:|---:|---:|---|---|
| finish_model | evaluated | 2440 | 0.5627 | 0.5201 | 0.0426 | True |  |
| goes_distance_model | evaluated | 2440 | 0.5627 | 0.5201 | 0.0426 | True |  |
| strike_volume_model | evaluated | 1348 | 0.4073 | 0.3917 | 0.0156 | True | Balanced accuracy is weak; keep as experimental context. |
| takedown_control_model | weak_or_failed_baseline | 1348 | 0.523 | 0.549 | -0.026 | False | Does not beat majority-class baseline on final chronological test set. |
| strike_volume_regression | baseline_only | 1348 | 55.3286 | 52.5681 | -0.0525 | False | Regression model is currently a simple baseline harness; add trained regressors before public use. |
| method_model | weak_or_failed_baseline | 2440 | 0.2557 | 0.5201 | -0.2644 | False | Does not beat majority-class baseline on final chronological test set.; Balanced accuracy is weak; keep as experimental context. |
| round_phase_model | weak_or_failed_baseline | 2440 | 0.2279 | 0.5201 | -0.2922 | False | Does not beat majority-class baseline on final chronological test set.; Balanced accuracy is weak; keep as experimental context. |
| winner_model | blocked | 0 |  |  |  | False | Winner rows are winner/loser oriented in the normalized importer; safe f1/f2 runtime winner evaluation needs mirrored matchup orientation. |
| odds_calibration_model | blocked | 0 |  |  |  | False | Pre-fight odds snapshots are not yet safely matched to outcomes and timestamps. |

## Segment Performance
### finish_model
- enough_fighter_history: {'rows': 1359, 'accuracy': 0.5901}
- low_fighter_history: {'rows': 1081, 'accuracy': 0.5282}
### goes_distance_model
- enough_fighter_history: {'rows': 1359, 'accuracy': 0.5901}
- low_fighter_history: {'rows': 1081, 'accuracy': 0.5282}
### method_model
- enough_fighter_history: {'rows': 1359, 'accuracy': 0.3223}
- low_fighter_history: {'rows': 1081, 'accuracy': 0.1721}
### round_phase_model
- enough_fighter_history: {'rows': 1359, 'accuracy': 0.1663}
- low_fighter_history: {'rows': 1081, 'accuracy': 0.3053}
### strike_volume_model
- enough_fighter_history: {'rows': 753, 'accuracy': 0.4329}
- low_fighter_history: {'rows': 595, 'accuracy': 0.3748}
### takedown_control_model
- enough_fighter_history: {'rows': 753, 'accuracy': 0.5551}
- low_fighter_history: {'rows': 595, 'accuracy': 0.4824}
