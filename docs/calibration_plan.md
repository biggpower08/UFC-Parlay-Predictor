# Calibration Plan

## Plain-English Summary
The project currently reports probability-style scores, but it does not yet have a full validation-only calibration layer. Calibration matters because a model that is often correct can still be badly overconfident.

## Current State
- `--calibrate` currently means basic probability scoring/reporting.
- It is not yet a complete validation-only calibration refactor.
- Final-test rows must never be used to fit calibration.

## First Models To Calibrate
- `winner_model` high-confidence output.
- `fight_duration_model`.
- `over_2_5_model`.
- `ends_before_round_3_model`.

## Not Worth Calibrating Yet
- Weak method models.
- Blocked odds model.
- Source-transfer unstable experimental models.

## Future Implementation Plan
1. Fit calibration only on validation rows.
2. Keep final-test rows untouched until final scoring.
3. Report Brier score and log loss before/after calibration.
4. Add calibration buckets.
5. Track high-confidence reliability.
6. Review worst high-confidence misses.
7. Report calibration by source, weight class, low-history segment, and data-quality segment.
