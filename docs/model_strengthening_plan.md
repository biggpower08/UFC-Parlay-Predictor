# Model Strengthening Plan

## Plain-English Summary
The winner model is no longer blocked by winner-oriented rows. Historical fights are now oriented deterministically by fighter name before the winner target is created, and duplicated canonical fights stay inside the same chronological split. The next work is to turn the strongest evaluated models into saved, versioned artifacts only after runtime feature compatibility is verified end to end.

## Current Status
- `winner_model`: unblocked for evaluation with safe deterministic orientation.
- `finish_model`: strong held-out performance and useful high-confidence slices.
- `goes_distance_model`: strong held-out performance and mirrors finish probability.
- `method_model`: beats baseline on accuracy, but balanced accuracy remains modest because decision-heavy buckets dominate.
- `round_phase_model`: still weak on final-test evaluation.
- `strike_volume_model`: improved but still experimental.
- `takedown_control_model`: barely beats baseline and should remain experimental.
- `odds_calibration_model`: blocked until pre-fight odds timestamps are trusted.

## Safety Rules
- Do not use winner/loser/result/method/current-fight stats as features.
- Do not assign fighter 1 based on who won.
- Do not let duplicate or mirrored canonical fights cross train, validation, and final-test splits.
- Do not tune or calibrate on the final test set.
- Do not label high-confidence slices as overall model accuracy.

## Next Steps
1. Save versioned artifacts for models that beat baseline and pass runtime compatibility.
2. Add artifact-level metadata for selected algorithm, feature schema, source datasets, and high-confidence thresholds.
3. Improve method and round-phase targets with hierarchical and bettor-style binary targets.
4. Add trusted pre-fight odds snapshots before training odds calibration.
5. Keep production status conservative until backtest, calibration, and live-runtime feature generation agree.
