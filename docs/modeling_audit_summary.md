# Modeling Audit Summary

## Steps
- `leakage_scan`: ok
- `import_training_dataset`: ok
- `training_data_audit`: ok
- `training_dataset_dry_run`: ok
- `winner_silver_benchmark_audit`: ok
- `prop_training_plan`: ok
- `benchmark_report`: ok
- `segment_evaluation`: ok

## Final Summary Table

| Model | Status | Rows Used | Main Metric | Baseline | Beats Baseline | Leakage Risk | Runtime Compatible | Notes |
|---|---|---:|---:|---:|---|---|---|---|
| expert_signal_model | blocked | 0 |  |  |  | unknown_review_needed | False | No verified pre-fight expert timestamped signal dataset is available. |
| finish_model | trained | 16268 | 0.5486 | 0.5031 | True | low | True | Features are limited to pre-fight rolling win/finish/decision history from the available source order. |
| goes_distance_model | trained | 16268 | 0.5486 | 0.5031 | True | low | True | Features are limited to pre-fight rolling win/finish/decision history from the available source order. |
| method_model | experimental | 16268 | 0.2667 | 0.4969 | False | low | True | Validation is weak; treat this as an experimental model-supported read, not a confident prop projection. |
| odds_calibration_model | blocked | 0 |  |  |  | unknown_review_needed | False | Historical odds snapshots are not available, so odds calibration/value modeling is blocked. |
| round_model | experimental | 16268 | 0.2382 | 0.4969 | False | low | True | Validation is weak; treat this as an experimental model-supported read, not a confident prop projection. |
| strike_volume_model | experimental | 8209 | 0.4093 | 0.3806 | True | low | True | Validation is weak; treat this as an experimental model-supported read, not a confident prop projection. |
| takedown_control_model | experimental | 8209 | 0.5219 | 0.5542 | False | low | True | Validation is weak; treat this as an experimental model-supported read, not a confident prop projection. |
| winner_model | blocked | 16268 |  |  |  | unknown_review_needed | False | Winner prediction already uses the existing sklearn/Elo pipeline; this pass does not retrain it. |
