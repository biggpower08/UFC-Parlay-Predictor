# MMA Model Training Methodology

## Plain-English Summary

The training system must act as if every historical prediction was made before the fight happened. Raw datasets are imported locally, normalized into a shared schema, deduped, checked for leakage, converted into safe targets, split chronologically, trained only on older fights, and evaluated on truly held-out newer fights. A model is useful only if it beats a simple baseline without using information that would not have existed before fight night.

## Pipeline

The standard pipeline is:

```text
raw datasets
-> preprocessing
-> normalization
-> deduping
-> safe target creation
-> leakage scan
-> runtime-compatible feature generation
-> chronological train/validation/final-test split
-> baseline comparison
-> model training
-> calibration
-> segment evaluation
-> model registry update
```

Raw Kaggle, GitHub, manual HTML, and CSV imports belong under `data/imports/` and are never committed. Normalized reports and small JSON artifacts can be committed when they are useful for reproducibility.

## Leakage Policy

Features must be knowable before fight start. Current-fight or post-fight columns are labels only or excluded.

Never use these as input features:

- winner, loser, result, method, method group, scorecards, judge scores
- finish round, finish time, current-fight round result
- current-fight significant strikes, total strikes, takedowns, control time, or submission attempts
- post-fight records, post-fight rankings, or target columns

Target columns such as `f1_wins_safe`, `went_distance`, `over_2_5`, `method_class`, strike thresholds, and takedown thresholds must remain labels and must not enter the feature matrix.

## Split Policy

Use chronological final-test evaluation as the headline result whenever `event_date` exists. Older fights are training, middle fights are validation/calibration, and the newest fights are final test.

Random split may only be reported as a comparison. It should never be the only headline result for production readiness.

The final test set must not be used for:

- feature fitting
- imputer/scaler/encoder fitting
- hyperparameter tuning
- calibration
- threshold selection

Encoders, imputers, and scalers should be fit only on the training split, preferably inside an sklearn `Pipeline`.

## Metrics Policy

Classification metrics:

- accuracy
- balanced accuracy
- F1 or macro F1
- ROC AUC where possible
- log loss where possible
- Brier score where possible
- confusion matrix
- majority-class baseline

Regression metrics:

- MAE
- RMSE
- median absolute error
- mean or median baseline

Relative improvement:

- Classification: model metric minus baseline metric.
- Regression: percent error reduction versus baseline.

Every model report should include sample size, date range, baseline, relative improvement, calibration notes, leakage risk, runtime compatibility, and segment metrics where possible.

## Model Status Policy

Allowed statuses:

- `production_ready`: beats baseline on held-out data, low leakage risk, runtime compatible, acceptable calibration, adequate sample size.
- `production_candidate`: promising held-out result, but one production criterion still needs review.
- `trained`: artifact and metrics exist, but production readiness is not claimed.
- `experimental`: real artifact/metrics exist, but performance, calibration, or sample quality is weak.
- `weak_or_failed_baseline`: evaluated and did not beat baseline.
- `insufficient_data`: labels or rows are not enough.
- `blocked`: required labels, dates, features, or trusted source timing are missing.

Weak or failed-baseline models must not be marked `production_ready`.

## Model-Specific Notes

### Winner Model

Target is `f1_wins_safe`. It must be built from explicit fighter and winner names, not a one-line assumption that the first fighter always won.

### Finish And Goes-Distance Models

These are inverse concepts and should be evaluated consistently. If one model says finish and the other says goes distance with conflicting confidence, the report should flag that inconsistency.

### Method Model

Method classes are imbalanced. Use balanced accuracy, macro F1, per-class recall, and confusion matrix instead of relying on accuracy alone.

### Round-Phase Model

Exact round prediction is difficult. Prefer prop-useful targets first: `over_1_5`, `over_2_5`, `ends_before_round_3`, and `goes_distance`.

### Strike Volume Model

Strike targets are independent from winner. A fighter can land 50+ significant strikes and still lose. Current-fight strike totals are labels only.

### Takedown/Control Model

Takedown and control targets are independent from winner. A fighter can hit takedown/control props and still lose. Current-fight grappling totals are labels only.

### Odds Calibration Model

Odds can only be used when timestamp quality is pre-fight or otherwise trusted. Unknown timestamp odds are `review_needed`, not a production-ready input.

## Standard Commands

```powershell
cd C:\dev\mma-ai
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"

& $env:MMA_AI_PYTHON scripts\preprocess_imported_datasets.py --input-root data\imports --all --write-summary
& $env:MMA_AI_PYTHON scripts\evaluate_model_accuracy.py --input-dir data\imports --split chronological --calibrate --by-segment
& $env:MMA_AI_PYTHON scripts\backtest_historical_fights.py --input-dir data\imports --split chronological --all-test-fights --by-segment

$TempTestDir = "$env:TEMP\mma_ai_pytest_$([guid]::NewGuid().ToString())"
& $env:MMA_AI_PYTHON -m pytest ufc_predictor\tests -q --basetemp $TempTestDir
```
