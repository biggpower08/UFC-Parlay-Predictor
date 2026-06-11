# Prediction Output Policy

## Plain-English Summary
The app should show useful fight intelligence without overstating model strength. Strong models can support probabilities when data-quality gates pass; weak, blocked, or experimental models should appear only as clearly labeled context or be hidden.

## Customer-Facing Language Policy
- Use polished user-facing labels instead of raw internal statuses.
- `high_confidence_only` should appear as "High-confidence research signal."
- `production_candidate` should appear as "Validated candidate signal."
- `experimental` should appear as "Experimental insight."
- `weak_or_failed_baseline` should appear as "Under review."
- `blocked` or `not_trained` should appear as "Not yet available."
- Avoid raw model names such as `odds_calibration_model` in customer-facing card titles.
- Market comparison should be described as inactive while odds mapping and timing checks are completed.

## Model-Specific Narratives
- Each visible model/signal card should include a short matchup read paragraph, not just a badge or number.
- Narratives should be deterministic from existing response fields and status metadata.
- Narratives should sound like sports analysis while preserving uncertainty.
- Experimental and under-review signals may provide context, but should not be framed as final-grade forecasts.
- Odds/market narratives must stay inactive until odds mapping, cutoff policy, and modeling review pass.

## Output Levels
- Full probability: allowed only when model gates, data-quality gates, runtime parity, and selective confidence policy pass.
- Lean: allowed when the model is available but not strong enough for a hard probability.
- Scenario context: allowed for experimental or weak models when clearly labeled.
- Hidden: required when data quality is dangerous or the model is blocked/not trained.

## Current Policy By Model
- `winner_model`: high-confidence selective output only until source-holdout stability improves.
- `fight_duration_model`: production candidate after the latest source-holdout pass, but public full-probability output still requires artifact/runtime review.
- `finish_model` and `goes_distance_model`: compatibility outputs should follow the duration model.
- `method_umbrella_model`: experimental context only until method components transfer across sources.
- `finish_type_model`: experimental context only while method-label transfer remains unstable.
- `round_phase_model` and round submodels: production candidates where source-holdout is stable, but public full-probability output still requires artifact/runtime review.
- `strike_volume_model`: experimental context until source transfer, calibration, and runtime coverage improve.
- `takedown_control_model`: experimental context until source transfer and stat definitions improve.
- `odds_calibration_model`: blocked until trusted pre-fight odds timestamps exist.

## Required Warnings
High-confidence or betting-read text must include uncertainty. Do not use guaranteed language, lock language, fake odds, fake edge, units, or sportsbook-style certainty.

## Data-Quality Behavior
- `strong`: full eligible model output can be shown if model gates pass.
- `medium`: show leans and probabilities cautiously.
- `limited`: show warnings and prefer context.
- `dangerous`: hide probability-style output and show a data-quality warning.

## Source-Transfer Behavior
- Experimental models can provide scenario context, but should not display full probability-style prop outputs.
- `ensemble_breakdown` should include `unavailable_models`, `unstable_models`, `data_quality`, `data_quality_reasons`, and `public_warning_text`.
- Any model with `source_holdout_unstable`, `source_holdout_not_run`, or severe source regression must be hidden or downgraded in public output.
