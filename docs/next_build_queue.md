# Next Build Queue

## Plain-English Summary
The next build should stay focused on turning promising model reports into dependable product behavior. The priority is source-holdout validation for production candidates, then artifact packaging, then carefully wiring model signals into public prediction output.

## Highest Priority
1. Run source-holdout validation for `fight_duration_model`, `over_2_5_model`, `ends_before_round_3_model`, and `takedown_control_model`.
2. Decide whether production candidates with `source_holdout_not_run` should remain candidates or be downgraded until holdout tests exist.
3. Package only small runtime-safe artifacts with metadata, selected interactions, failed gates, and public warning text.
4. Add an API-facing `ensemble_breakdown` object only after runtime feature parity is confirmed.

## Modeling Work
- Improve source-transfer stability for `winner_model`.
- Keep `winner_model` as `high_confidence_only` until source-holdout and cold-start gates pass.
- Improve `finish_type_model` before method probabilities are treated as reliable.
- Keep `strike_volume_model` and `takedown_control_model` experimental/contextual unless segment and source-holdout metrics improve.
- Keep `odds_calibration_model` blocked until odds timestamps are trusted as pre-fight.

## Product Work
- Show model status and data-quality warnings in plain language.
- Keep weak models as context only.
- Avoid fake odds, fake edge, and guaranteed language.
- Keep raw Kaggle/import data local-only and out of runtime startup.

## Automation Work
- Add a single modeling-audit command that runs preprocessing, evaluation, backtest, registry validation, and report consistency checks.
- Keep report JSON PowerShell-readable by normalizing segment keys.
- Add source-holdout summaries to registry and docs whenever those runs become available.
