# Model Artifact Packaging Plan

## Plain-English Summary
Only small, safe, runtime-needed artifacts should be committed. Raw datasets, generated training rows, large caches, debug HTML, local databases, and weak experimental artifacts should stay out of Git.

## Commit Candidates
Commit only when each artifact has:

- saved model data
- metadata
- metrics
- feature list
- production or selective-use status
- runtime compatibility notes
- clear limitations

Small JSON artifacts can be committed when the deployed app needs them.

## Do Not Package Weak Models As Production
Do not package `weak_or_failed_baseline`, `blocked`, `not_trained`, or source-transfer-unstable models as production artifacts. They may remain in reports or research outputs, but public scoring should ignore them or use them only as labeled context.

## Current Guidance
- `winner_model`: package only after artifact/runtime gate review; current public use should be selective.
- `fight_duration_model`: candidate only; do not package until artifact/runtime review is explicitly approved.
- Stable round members: candidate only; do not package until artifact/runtime review is explicitly approved.
- `finish_type_model`, strike-volume, takedown/control, and method outputs: report/context only until source transfer and baseline behavior improve.
- `odds_calibration_model`: do not package until pre-fight odds timestamps are trusted.

## Never Commit
- `data/imports/`
- raw Kaggle/Silver files
- `ufc_predictor/data/imports/`
- `ufc_predictor/data/processed/training_imports/`
- `ufc_predictor/data/processed/*.db`
- `ufc_predictor/data/processed/backtest_predictions.json`
- scraper cache/debug HTML
- `.venv/`, `C:\venvs\`, `node_modules/`, `.next/`
