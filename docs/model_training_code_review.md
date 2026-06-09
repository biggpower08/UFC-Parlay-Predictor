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

## Hierarchical Fight Outcome Refactor
The previous reports trained `finish_model` and `goes_distance_model` as separate flat classifiers even though their labels are direct inverses. They now share the same umbrella duration signal:

- `fight_duration_model`: predicts finish probability.
- `finish_model`: compatibility output backed by `fight_duration_model`.
- `goes_distance_model`: compatibility output where `goes_distance_probability = 1 - finish_probability`.

The old flat `method_model` tried to classify decision, KO/TKO, submission, and other outcomes in one step. The safer structure is now:

- `finish_type_model`: conditional model trained only on fights that finished.
- `method_umbrella_model`: combines duration probability with conditional finish-type probability.

Combined method logic:
- `P(decision) = P(goes_distance)`
- `P(KO/TKO) = P(finish) * P(KO/TKO | finish)`
- `P(submission) = P(finish) * P(submission | finish)`
- `P(other_finish) = P(finish) * P(other_finish | finish)`

Round-phase modeling is now decomposed into binary targets:
- `over_1_5_model`
- `over_2_5_model`
- `ends_before_round_3_model`
- `finish_in_round_1_model`

This avoids treating all round outcomes as one multiclass problem before the data proves that approach works.

## Automatic Interaction Discovery
Interaction discovery now groups safe pre-fight features by meaning and generates candidate products, ratios, context interactions, and nonlinear transforms. Candidate interactions are filtered for forbidden inputs, low coverage, low variance, and candidate caps. Selection uses training/validation only; final-test rows are not used to choose interactions.

Current interaction audit results:
- Winner model tested the expanded MMA interaction families but kept base features in the latest report; it remains `high_confidence_only` because source-holdout and leakage-review gates still fail.
- Fight duration, over 1.5, ends-before-round-3, finish-type, and strike-volume selected limited interaction sets on validation.
- Over 2.5, finish-in-round-1, and takedown/control kept base features in the latest report where interactions did not clear validation/calibration selection gates.
- Method and round compatibility outputs inherit their underlying family status and should not be treated as independent interaction wins.

## Evaluation Notes
- Final-test reports are fight-level after source-priority deduping.
- Feature schema selection is based on train/validation data only; final-test rows are held back for scoring.
- The `--calibrate` flag is currently reported as basic probability scoring only, not a final-test calibration step.
- High-confidence metrics report coverage and calibration gap.
- Models that only perform well on narrow high-confidence slices should be treated as selective, not globally reliable.

## Remaining Risks
- Source duplicate quality still needs periodic auditing.
- Odds rows are not production-training-ready without trusted pre-fight timestamps.
- Method and round labels are now decomposed, but finish-type and round-1 finish remain weak until they beat baseline with acceptable balanced metrics.
- Winner model source-transfer is not uniformly strong; the red-team audit found `ufc_fight_forecast` holdout weakness.
- High-confidence winner performance should be used as selective evidence only until source-holdout stability is improved.

## Feature Strategy Review
The feature strategy now includes dedicated modules for prior-history style scores and opponent-weakness proxies. These modules are intentionally limited to rolling pre-fight history and are safe to use as candidate model features or interaction inputs. They do not read current-fight labels.

The interaction audit should specifically report whether it tested:

- striking x opponent weakness
- grappling x opponent weakness
- finishing x durability
- pace x age/activity
- scheduled rounds x pace/duration
- fighter strength vs opponent weakness

Any selected interactions must remain runtime-computable and must not be selected using final-test performance.
