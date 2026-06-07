# Runtime Feature Factory

The app now has a shared feature factory for building model inputs from the same schema in two places:

- historical training rows
- live user-selected matchups

This matters because a model is only useful in production if the app can recreate its input columns at prediction time. Raw training files can have many columns, but the deployed app should only rely on features that can be produced from Supabase/backend data and bundled model artifacts.

## Core Files

- `ufc_predictor/features/feature_schema.py`
- `ufc_predictor/features/fighter_snapshots.py`
- `ufc_predictor/features/matchup_features.py`
- `ufc_predictor/features/runtime_availability.py`

## Historical Mode

Historical mode builds features as of the fight date. It uses fights before the target fight and keeps the current fight outcome as labels only.

Labels such as `winner`, `method_class`, `finish_binary`, and strike/takedown totals can exist beside the row for training, but they are not model input features.

## Live Mode

Live mode builds the same schema for two selected fighters. It uses current fighter profile/history data available to the backend. Missing values stay null and are reported through:

- `missing_features`
- `unavailable_features`
- `data_quality_warnings`
- `model_feature_coverage`

The live factory does not fake missing stats, odds, or detailed style data.

## Supported Model Families

Initial schemas exist for:

- `winner_v1`
- `finish_v1`
- `goes_distance_v1`
- `method_v1`
- `round_phase_v1`
- `strike_volume_v1`
- `takedown_control_v1`
- `odds_calibration_v1`

The first runtime-compatible required feature set is the prior-history baseline:

- `a_prior_fights`
- `b_prior_fights`
- `a_prior_wins`
- `b_prior_wins`
- `a_prior_finishes`
- `b_prior_finishes`
- `a_prior_decisions`
- `b_prior_decisions`

These are the required inputs for the current prop-model artifacts. Richer profile, Elo, size, striking, and grappling features are optional until coverage is good enough.

## Leakage Protection

The factory validates model features against the leakage scanner. It rejects outcome and post-fight fields as inputs, including:

- winner/loser/result
- method and finish timing
- `f1_wins`
- distance/round target columns
- current-fight strikes, takedowns, control time, and judge/scorecard style fields

Those values can be labels during training, but they must not enter feature dictionaries.

## Actual Fight vs Pound For Pound

`actual_fight` mode keeps size, reach, and weight-class context because real fights are affected by physical differences.

`pound_for_pound` mode neutralizes size-advantage fields. It keeps the same schema shape but sets weight, height, and reach advantage fields to neutral values and marks `size_features_used` as false.

## Missing Features Today

The app can produce the prior-history baseline now. The following are still incomplete or optional depending on source coverage:

- age and date-of-birth coverage
- consistent height/reach/stance coverage in historical rows
- Elo before each historical fight
- per-fight significant-strike attempts/absorbed values
- takedown attempts/defense/control-time history
- pre-fight odds snapshots matched to fight timestamps

These should be added as runtime-compatible optional features before they become required model inputs.

## Future Automation

The training dataset builder writes small audit reports:

- `ufc_predictor/data/processed/training_dataset_summary.json`
- `ufc_predictor/data/processed/feature_availability_report.json`

The model registry stores schema metadata so future automation can verify that artifacts are compatible before they are exposed in predictions.
