# Final Prediction Ensemble Plan

## Plain-English Summary
The final prediction should be a cautious blend of learned winner probability, Elo, model context, and data quality. Winner probability and Elo matter most; prop-style models should shape confidence and explanation unless they become truly production-ready.

## Signal Hierarchy
1. `winner_model`: primary learned win-probability model when available and gated.
2. Elo: major supporting signal when both fighters have computed Elo.
3. Finish/goes-distance/method/round models: confidence, volatility, and analysis context.
4. Strike-volume and takedown/control models: style and matchup-shape context.
5. Odds calibration: blocked until trusted pre-fight odds history exists.

## Ensemble Breakdown Contract
Prediction responses should continue moving toward an `ensemble_breakdown` object with:

- `winner_model_signal`
- `elo_signal`
- `finish_model_signal`
- `method_model_signal`
- `round_model_signal`
- `strike_volume_signal`
- `takedown_control_signal`
- `odds_calibration_signal`
- `final_probability`
- `confidence`
- `data_quality`
- `unavailable_models`

## Guardrails
- Do not let experimental prop models overpower winner/Elo evidence.
- Do not use blocked or not-trained models in numeric scoring.
- Do not expose formulas or implementation details publicly.
- Do not use current-fight outcome stats as prediction features.
- Keep fallback text honest when model evidence is unavailable.
