# Three-Week Data Refresh Workflow

Run this every three weeks when you want fresher data and model artifacts.

This is a manual, review-first workflow. It is intentionally not a destructive auto-update job.

## 1. Download or update datasets

Download curated Kaggle datasets manually and place CSV files in:

```powershell
C:\dev\mma-ai\data\imports\kaggle
```

or:

```powershell
C:\dev\mma-ai\ufc_predictor\data\imports
```

Do not commit raw datasets.

Optional helper for the stored Kaggle source catalog:

```powershell
& $env:MMA_AI_PYTHON scripts\download_kaggle_datasets.py --dry-run
& $env:MMA_AI_PYTHON scripts\download_kaggle_datasets.py
& $env:MMA_AI_PYTHON scripts\download_kaggle_datasets.py --only betting_odds_daily
```

If Kaggle asks for credentials, download the files manually and keep them in `data\imports\kaggle`.

## 2. Dry-run the importer

```powershell
cd C:\dev\mma-ai
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"

& $env:MMA_AI_PYTHON scripts\import_training_dataset.py --input-dir data\imports\kaggle --dry-run
```

Review:

- supported files
- unknown files
- missing columns
- duplicate fight count
- event-date coverage
- label availability
- odds row detection

## 3. Run the importer

```powershell
& $env:MMA_AI_PYTHON scripts\import_training_dataset.py --input-dir data\imports\kaggle
```

This writes normalized imported fight rows under `ufc_predictor\data\processed\training_imports`.

## 4. Build and audit training rows

```powershell
& $env:MMA_AI_PYTHON scripts\build_training_dataset.py --source imported_csv --dry-run --missingness-report
```

Only proceed if:

- event dates exist
- labels exist
- missingness is understood
- class distributions are usable
- current-fight stats are labels only

## 5. Train models

```powershell
& $env:MMA_AI_PYTHON scripts\train_prop_models.py --source imported_csv --dry-run
& $env:MMA_AI_PYTHON scripts\train_prop_models.py --source imported_csv
```

Models should stay `experimental`, `insufficient_data`, or `blocked` unless the data and validation justify a stronger status.

## 6. Review registry and artifacts

Review:

```powershell
Get-Content ufc_predictor\data\processed\model_registry.json
Get-Content ufc_predictor\data\processed\prop_model_metrics.json
```

Commit only small, safe artifacts that are needed by the app. Do not commit raw datasets.

## 7. Run validation

```powershell
$TempTestDir = "$env:TEMP\mma_ai_pytest_$([guid]::NewGuid().ToString())"
& $env:MMA_AI_PYTHON -m pytest ufc_predictor\tests -q -p no:cacheprovider --basetemp $TempTestDir

cd C:\dev\mma-ai\app\frontend
npm run build
```

If PowerShell blocks the npm wrapper:

```powershell
& "C:\Program Files\nodejs\node.exe" node_modules\next\dist\bin\next build
```

## 8. Optional Codex audit

Use Codex for a report-first audit, not an automatic push:

```powershell
codex exec --cd C:\dev\mma-ai --sandbox workspace-write "Run the data refresh audit and report what changed. Do not commit."
```

Review the report before staging or pushing.

## 9. Commit and deploy

```powershell
git status
git add <small safe files>
git commit -m "Refresh training data and model registry"
git push
```

Deploy after tests and build pass.
