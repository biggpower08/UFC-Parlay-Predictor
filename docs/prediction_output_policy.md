# Prediction Output Policy

## Plain-English Summary
The app should show useful fight intelligence without overstating model strength. Strong models can support probabilities when data-quality gates pass; weak, blocked, or experimental models should appear only as clearly labeled context or be hidden.

## Output Levels
- Full probability: allowed only when model gates, data-quality gates, runtime parity, and selective confidence policy pass.
- Lean: allowed when the model is available but not strong enough for a hard probability.
- Scenario context: allowed for experimental or weak models when clearly labeled.
- Hidden: required when data quality is dangerous or the model is blocked/not trained.

## Current Policy By Model
- `winner_model`: high-confidence selective output only until source-holdout stability improves.
- `fight_duration_model`: may support finish/goes-distance context when gates pass.
- `finish_model` and `goes_distance_model`: compatibility outputs should follow the duration model.
- `method_umbrella_model`: context only until method submodels are stronger.
- `finish_type_model`: context only while weak or failed baseline.
- `round_phase_model` and round submodels: context or selective output only by gate status.
- `strike_volume_model`: experimental context until stronger validation and runtime coverage.
- `takedown_control_model`: experimental context until stronger validation.
- `odds_calibration_model`: blocked until trusted pre-fight odds timestamps exist.

## Required Warnings
High-confidence or betting-read text must include uncertainty. Do not use guaranteed language, lock language, fake odds, fake edge, units, or sportsbook-style certainty.

## Data-Quality Behavior
- `strong`: full eligible model output can be shown if model gates pass.
- `medium`: show leans and probabilities cautiously.
- `limited`: show warnings and prefer context.
- `dangerous`: hide probability-style output and show a data-quality warning.
