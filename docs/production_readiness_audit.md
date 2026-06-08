# Production Readiness Audit

## Plain-English Summary
The repo hygiene check found that the main config files are multi-line and parseable locally, but the ignore rules needed stronger explicit protection and an accidental root file named `notepad .gitignore` was present. The app dependency and Render config validation passed. One protected generated file, `ufc_predictor/data/processed/fighters.db`, is already tracked and must be untracked with Git metadata write access before the repo is fully clean.

## Repo Hygiene Result
- `.gitignore`: fixed with explicit rules for secrets, raw imports, local virtual environments, frontend build output, pytest caches, the local SQLite database, normalized import CSV, and backtest prediction JSON.
- `requirements.txt`: valid one-requirement-per-line file.
- `render.yaml`: valid YAML and still deploys the FastAPI app through Uvicorn.
- Root clutter: accidental `notepad .gitignore` existed and was removed from the working tree.

## Protected File Tracking Check
Command reviewed:

```powershell
git ls-files | findstr /i "kaggle.json .env data/imports fighters.db normalized_fights_combined backtest_predictions"
```

Result:
- `.env.example`: tracked intentionally as a template.
- `app/frontend/.env.example`: tracked intentionally as a template.
- `alembic/env.py`: false-positive match for `.env`.
- `ufc_predictor/data/processed/fighters.db`: tracked and should be removed from Git tracking.

Required cleanup:

```powershell
git rm --cached ufc_predictor\data\processed\fighters.db
```

This removes the database from Git tracking without deleting the local file.

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

## Remaining Production Blockers
- Untrack `ufc_predictor/data/processed/fighters.db`.
- Keep raw Kaggle/import datasets out of Git.
- Keep `normalized_fights_combined.csv` and `backtest_predictions.json` out of Git.
- Resolve winner-model source-holdout instability before production-ready claims.
- Improve weak method/finish-type and round-1 finish models before public confidence claims.
- Add trusted pre-fight odds timestamps before odds calibration or betting-edge modeling.
