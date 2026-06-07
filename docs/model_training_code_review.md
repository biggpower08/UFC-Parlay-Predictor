# Model Training Code Review

## Plain-English Summary
The training pipeline now separates label creation from fighter orientation, uses canonical fight-group splitting, and evaluates models on a final chronological holdout. The biggest remaining caution is that imported datasets have duplicate coverage of many fights, so model reports use source-priority fight-level deduping for final scoring.

## Winner Orientation Review
- Previous blocker: imported known-winner rows were often normalized as winner first.
- Fix: training rows now orient fighters by deterministic normalized-name sorting.
- Target: `f1_wins_safe = 1` only when the safely oriented fighter 1 won.
- Result: winner labels are no longer constant.

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
