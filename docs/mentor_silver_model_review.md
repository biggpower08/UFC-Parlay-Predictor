# Mentor Silver Model Review

This review covers the mentor files from `ufcpredictions.zip`. The files were inspected as text only. No mentor code was executed.

## Files Reviewed

| File | Purpose | Integration decision |
|---|---|---|
| `preprocess_ufc_winner.py` | Reads `UFC_full_data_silver.csv`, creates `f1_wins`, writes `UFC_full_data_encoded.csv`. | Rewrite the target logic. Do not use directly. |
| `reproduce_silver_run.py` | Rebuilds the mentor LightGBM winner-model pipeline from encoded Silver data. | Use as an offline benchmark/reference. Do not wire into production yet. |
| `audit.jsonl` | Detailed phase/tool audit from the mentor run. | Review-only evidence. Do not commit raw log. |
| `client.log` | Human-readable run log with data cleaning/modeling notes. | Review-only evidence. Do not commit raw log. |

## Key Mentor Results

The mentor run reports a Silver dataset shape of about `8,231 rows x 362 columns`.

Best reported winner-model result:

- Model: LightGBM binary classifier
- Target: `f1_wins`
- Test rows: `1,647`
- Train rows: `6,584` before oversampling in the final cached split
- Accuracy: `0.7535`
- Balanced accuracy: `0.7251`
- Weighted F1: `0.7521`
- ROC AUC: `0.8265`

These are useful benchmark numbers, but they are not enough to make the model production-ready.

## Safer Target Handling

The mentor preprocessing uses:

```python
df["f1_wins"] = (df["winner"] == df["f_1_name"]).astype(int)
```

That silently turns missing, malformed, draw, no-contest, or unmatched winners into `0`, which means "fighter 2 won." The safer app target logic is:

```text
if normalized winner == normalized f_1_name: f1_wins = 1
elif normalized winner == normalized f_2_name: f1_wins = 0
else: f1_wins = null and invalid_target_reason = missing_or_unmatched_winner
```

Invalid winner rows should be dropped from binary winner training and reported.

## Leakage And Runtime Audit

Positive signs:

- The mentor pipeline explicitly drops obvious outcome columns: winner, result, result details, finish round, finish time.
- Whole-fight totals and per-round in-fight stats are dropped before winner modeling.
- Missing indicators and differential features are used.
- Odds-derived features are treated as pre-fight market features.

Risks that block production use today:

- Main split is stratified/random, not chronological headline validation.
- Target encoding was reported without a time column, which can leak future aggregate target information.
- `event_date_year` appeared as a very strong feature and may act as a regime shortcut.
- Runtime compatibility is not proven. The live app cannot yet generate the exact 149-156 feature Silver row for any arbitrary selected matchup.
- Odds features need timestamp confirmation before being used as pre-fight features.
- The target construction needs the safer invalid-target handling above.

## Reproduction Recipe Extracted

`reproduce_silver_run.py` defines a reproducible offline winner-model recipe:

- Input: `data/ufc/silver/UFC_full_data_encoded.csv`
- Target: `f1_wins`
- Model type: `LightGBM LGBMClassifier`
- Dependencies: pandas, numpy, scikit-learn, LightGBM, imbalanced-learn, category-encoders, joblib
- Split: `sklearn.model_selection.train_test_split` with stratification
- Oversampling: `RandomOverSampler` on the training split
- Artifact behavior: saves a joblib bundle with model, fit state, and feature columns
- Prediction mode: loads the bundle, applies stored preprocessing state, and predicts `f1_wins` for new rows

The mentor script has explicit drop groups:

- `DROP_FIGHT_OUTCOME`: winner/result/result details/finish timing/URLs/name fragments
- `DROP_IN_FIGHT`: whole-fight and per-round strikes, takedowns, submissions, reversals, and control time
- `DROP_STRING_CONTEXT`: event/fighter identity/date strings after feature engineering
- `DROP_LOW_IMPORTANCE`: low-importance engineered fields removed late in the run

Main feature families:

- fighter physical stats
- fighter record stats
- striking/grappling profile stats
- rankings
- moneyline and method odds
- missingness flags
- date parts
- differential features
- implied probability/log-odds features
- stance interactions
- composite/efficiency scores

Runtime gap:

The production app cannot yet recreate this exact feature row for arbitrary selected fighters. Until the app has a Silver-compatible runtime feature builder, the mentor model stays an offline benchmark.

## Mentor Audit Trail Summary

The mentor audit trail is valuable because it records:

- dataset shape: about `8,231 x 362`
- leakage drops for post-fight totals and round stats
- missingness handling
- winsorization and indicator creation
- multiple model families tried
- LightGBM best individual model around `0.7535` accuracy
- tuning plateau below the desired `0.80` target
- warning that the remaining gap is likely feature-signal related, not just hyperparameters

Important caution from the audit:

Target encoding was reported without a time column. For future-fight prediction, that is a potential temporal leakage path unless replaced with chronological/out-of-fold encoding that respects event dates.

## Classification

- Leakage risk: `moderate_risk`
- App status: `offline_benchmark`
- Production decision: do not wire into live predictions yet.

## What To Reuse

Reuse the ideas:

- Silver f1/f2 orientation for winner modeling
- explicit leakage drops
- differential features
- missing indicators
- odds-aware vs no-odds winner model comparison
- LightGBM as a candidate benchmark

Do not reuse blindly:

- unsafe `f1_wins` creation
- random split as the main metric
- target encoding without chronological safeguards
- any model artifact whose runtime feature row cannot be recreated by the app
