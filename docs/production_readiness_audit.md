# Production Readiness Audit

## Plain-English Summary
The repo hygiene check now confirms generated local data is ignored and `ufc_predictor/data/processed/fighters.db` is not tracked. Model gates remain conservative: no model is marked production-ready, and artifact packaging is still blocked until explicit review.

## Repo Hygiene Result
- `.gitignore`: protects secrets, raw imports, local virtual environments, frontend build output, pytest caches, the local SQLite database, normalized import CSV, and backtest prediction JSON.
- `requirements.txt`: valid one-requirement-per-line file.
- `render.yaml`: valid YAML and still deploys the FastAPI app through Uvicorn.
- Root clutter: no new cleanup required in this pass.

## Protected File Tracking Check
Command reviewed:

```powershell
git ls-files | findstr /i "kaggle.json .env data/imports fighters.db normalized_fights_combined backtest_predictions"
```

Result:
- `ufc_predictor/data/processed/fighters.db` is not tracked.
- `.env.example` files remain tracked intentionally as templates.
- `alembic/env.py` remains a false-positive text match for `.env`.

## Ignore Validation
Validated with `git check-ignore --no-index -v`:
- `kaggle.json`: ignored.
- `data\imports\test.csv`: ignored.
- `ufc_predictor\data\processed\fighters.db`: ignored.
- `ufc_predictor\data\processed\imports\normalized_fights_combined.csv`: ignored.
- `ufc_predictor\data\processed\backtest_predictions.json`: ignored.

## Dependency Validation
Command:

```powershell
& $env:MMA_AI_PYTHON -m pip install --dry-run -r requirements.txt
```

Result: passed. The environment already satisfies the listed requirements.

## Render Config Validation
Command:

```powershell
@'
import yaml
from pathlib import Path
data = yaml.safe_load(Path("render.yaml").read_text())
print(data)
'@ | & $env:MMA_AI_PYTHON
```

Result: passed. `render.yaml` parses as YAML and keeps the Python web service, Render build command, FastAPI Uvicorn start command, and `/health` health check.

## Model Production Gates
Current automated gates still enforce:
- Weak models cannot be `production_ready`.
- Winner model cannot be `production_ready` while source-holdout weakness remains.
- Odds calibration remains blocked without trusted pre-fight odds timestamps.
- Duplicate/mirrored fight leakage must be prevented.
- Calibration status must be explicit.
- Final-test rows must not decide model feature schema.
- Elo leakage audit must pass: historical rows can use pre-fight/pre-event Elo only, never latest/current/post-fight Elo.

## Elo Leakage Result
- Status: passed.
- Historical feature mode: strict pre-fight Elo with same-event pre-event cutoff.
- Unsafe current/latest Elo historical mode: blocked, not run.
- Winner-model strict Elo ablation: 0.9606 accuracy, 0.9604 balanced accuracy.
- Winner-model no-Elo ablation: 0.9585 accuracy, 0.9588 balanced accuracy.
- Registry entries now expose Elo audit fields so this is automatically checked in reports instead of living only as prose.

## Metric Jump Audit
The current metric-jump audit is documented in `docs/metric_jump_audit.md`.

Key result:
- Fight rows stayed stable at 49,355.
- Feature count increased from 136 to 157.
- The final date range did not change.
- Several gains are plausible feature/interaction improvements, but they are not production-ready until artifact packaging and runtime review are explicitly approved.
- Source-holdout validation now runs for non-winner classifiers and blocks or downgrades unstable candidates.
- `--calibrate` still means `basic_probability_scores_only`, not true validation-only calibration.

## Source-Holdout Result
The new source-holdout method trains each eligible non-winner model on train/validation rows excluding one source, then scores the held-out final-test rows from that source. This is a transfer robustness check, not a feature-selection step.

Current result:
- `fight_duration_model`, `finish_model`, and `goes_distance_model` currently pass automated source-holdout gates and are production candidates, not production-ready.
- `over_1_5_model`, `over_2_5_model`, `ends_before_round_3_model`, and `finish_in_round_1_model` currently pass automated source-holdout gates and are production candidates, not production-ready.
- `takedown_control_model` is not stable enough for production-candidate use.
- `finish_type_model` and `strike_volume_model` remain experimental.
- `method_umbrella_model` now runs a dedicated composite source-holdout check but failed the chronological baseline after safer non-win label handling.
- `odds_calibration_model` remains blocked.

## Remaining Production Blockers
- Keep raw Kaggle/import datasets out of Git.
- Keep `normalized_fights_combined.csv` and `backtest_predictions.json` out of Git.
- Resolve winner-model source-holdout instability before production-ready claims.
- Review candidate model artifacts and runtime parity before packaging any non-winner artifacts.
- Improve weak method/finish-type and round-1 finish models before public confidence claims.
- Add trusted pre-fight odds timestamps before odds calibration or betting-edge modeling.
