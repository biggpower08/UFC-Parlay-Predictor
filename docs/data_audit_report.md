# Training Data Audit Report

Input folder: `data\imports`
Normalized fight rows: 16268
Target rows inspected: 16268

## Model Readiness
- `winner_model`: offline_benchmark (16268 rows). Winner target exists, but normalized winner/loser rows are not enough for runtime-compatible f1/f2 prediction.
- `finish_model`: training_data_ready (16268 rows). 
- `goes_distance_model`: training_data_ready (16268 rows). 
- `method_model`: training_data_ready (16268 rows). Multiclass method remains harder and must beat baseline before production use.
- `round_phase_model`: training_data_ready (16268 rows). Round-phase label exists; exact round props remain future work.
- `strike_volume_model`: training_data_ready (8209 rows). Strike props are independent of winner and need segment calibration.
- `takedown_control_model`: training_data_ready (8209 rows). Takedown/control props are independent of winner and need segment calibration.
- `odds_calibration_model`: blocked (0 rows). Odds rows were detected separately, but are not yet safely matched to fight outcomes and timestamps.
- `expert_signal_model`: blocked (0 rows). No verified pre-fight expert timestamped signal dataset is available.

## Leakage Summary
`{"label_only": 27, "leakage_excluded": 417, "runtime_available": 1221, "unknown_review_needed": 10282}`

## Mentor Silver Review
Decision: `offline_benchmark_until_chronological_split_low_leakage_and_runtime_features_are_proven`
