# Model Training Code Review

## Plain-English Summary
The training pipeline now separates label creation from fighter orientation, uses canonical fight-group splitting, and evaluates models on a final chronological holdout. The biggest remaining caution is that imported datasets have duplicate coverage of many fights, so model reports use source-priority fight-level deduping for final scoring.

## Winner Orientation Review
- Previous blocker: imported known-winner rows were often normalized as winner first.
- Fix: training rows now orient fighters by deterministic normalized-name sorting.
- Target: `f1_wins_safe = 1` only when the safely oriented fighter 1 won.
- Result: winner labels are no longer constant.

## Winner Feature List Summary
The winner model currently uses runtime-compatible pre-fight history, form, Elo availability/count, matchup-size context, and data-quality flags. The exact feature list is written in `docs/winner_model_leakage_audit.md`.

Flagged review terms:
- `a_prior_finishes`
- `b_prior_finishes`

Those are prior-history fields, not current-fight labels. Removing suspicious finish-named features did not collapse winner performance in the audit.

## Source-Holdout Summary
- `mdabbert_ultimate`: strong.
- `ufc_1994_2025`: strong.
- `ufc_1994_2026`: acceptable but weaker.
- `ufc_fight_forecast`: weak transfer result.
- `ufc_stats_complete`: insufficient safe winner rows in the holdout slice.

Because source holdout is mixed, winner model cannot be marked `production_ready`.

## Runtime Parity Summary
Runtime parity passed for the current winner feature set. The live feature factory can generate all current winner features, but production use still depends on stable source-holdout and cold-start behavior.

## Selective Prediction Policy
High-confidence performance may be reported only with:
- confidence threshold
- row count
- coverage percentage
- accuracy
- balanced accuracy
- calibration gap
- small-sample warning when applicable

High-confidence accuracy must not be described as overall model accuracy.

## Production Readiness Gates
A model can only be `production_ready` if all gates pass:
- beats chronological final-test baseline
- leakage risk is low
- duplicate/mirrored fight leakage is prevented
- source-holdout performance is stable
- runtime parity passes
- calibration is acceptable
- high-confidence performance is not tiny-sample noise
- cold-start/low-history segments are not dangerously poor

If source holdout fails while other metrics are strong, status must be `high_confidence_only` or `production_candidate`, not `production_ready`.

## Leakage Controls
- Target/result columns are excluded from feature schemas.
- Current-fight strike/takedown/method labels remain labels, not features.
- Chronological split groups by canonical fight key.
- Mirrored or duplicate fight rows stay in the same split.
- Algorithm selection uses validation data, not final test data.

## Algorithms Compared
- Balanced logistic regression.
- Random forest.
- Extra trees.
- Histogram gradient boosting.

## Evaluation Notes
- Final-test reports are fight-level after source-priority deduping.
- High-confidence metrics report coverage and calibration gap.
- Models that only perform well on narrow high-confidence slices should be treated as selective, not globally reliable.

## Remaining Risks
- Source duplicate quality still needs periodic auditing.
- Odds rows are not production-training-ready without trusted pre-fight timestamps.
- Method and round-phase labels need better target decomposition before public confidence claims.
- Winner model source-transfer is not uniformly strong; the red-team audit found `ufc_fight_forecast` holdout weakness.
- High-confidence winner performance should be used as selective evidence only until source-holdout stability is improved.
