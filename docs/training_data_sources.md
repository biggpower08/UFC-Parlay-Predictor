# Training Data Sources

Use curated Kaggle datasets as the primary training path. Live scraping and paid APIs are not part of this workflow.

Before using any dataset commercially, verify its license and terms. Do not commit raw downloaded datasets.

Place local files in one of:

```powershell
C:\dev\mma-ai\data\imports
C:\dev\mma-ai\ufc_predictor\data\imports
```

## Recommended Kaggle Sources

| Dataset/source category | Source type | Best use | Likely files | Expected labels | Helps models | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| UFC Fight Forecast Complete Gold Modeling Dataset | Kaggle | Strong pre-fight modeling rows with rolling stats | one or more fight-level CSVs | winner, method, round, dates, fighter stats, sometimes odds | winner, finish, distance, method, round phase | Best if columns are already leakage-aware pre-fight features. Verify commercial rights. |
| UFC Stats Complete Dataset | Kaggle | UFCStats-style fight and fighter statistics | fight stats CSVs, fighter stats CSVs | method, round, sig strikes, takedowns, control time | strike volume, takedown/control, finish, method | Current-fight stats can be labels only, not pre-fight features. |
| UFC Dataset 1994-2026 | Kaggle | Long historical fight/stat coverage | fight-level CSVs | event dates, methods, rounds, stats | finish, distance, method, round, strike, control | Use chronological split when dates are available. |
| MMAStats Complete Database | Kaggle | Granular technical stats | fight/fighter stat CSVs | strikes, takedowns, control, outcomes | strike volume, takedown/control | Importer will report whether UFC-only filtering and labels are usable. |
| UFC Fight Statistics July 2016-Nov 2024 | Kaggle | Round/fight-level stats | fight statistics CSVs | round stats, sig strikes, methods | strike volume, round phase | Useful for labels, not current-fight features. |
| UFC Betting Odds Daily Dataset | Kaggle | Historical odds snapshots | odds snapshots | sportsbook, odds, timestamp, fighter/fight identifiers | odds calibration | Do not train odds models until snapshots are matched to outcomes. |
| UFC Fights 2010-2020 with Betting Odds | Kaggle | Basic historical moneyline odds | fight odds CSVs | moneyline odds, outcomes if matched | odds calibration | Odds calibration remains blocked if matching is incomplete. |

## Curated Dataset Slugs

These source names are stored in `ufc_predictor/training/dataset_sources.py` for repeatable downloads:

```text
jerzyszocik/ufc-fight-forecast-complete-gold-modeling-dataset
leandroiber/ufc-stats-complete-dataset
jossilva3110/ufc-dataset-1994-2026
leandroiber/mmastats
alexmagnus24/ufc-fight-statistics-july-2016-nov-2024
jerzyszocik/ufc-betting-odds-daily-dataset
mdabbert/ufc-fights-2010-2020-with-betting-odds
```

## Import Commands

```powershell
cd C:\dev\mma-ai
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"

& $env:MMA_AI_PYTHON scripts\import_training_dataset.py --input-dir data\imports\kaggle --dry-run
& $env:MMA_AI_PYTHON scripts\import_training_dataset.py --input-dir data\imports\kaggle
& $env:MMA_AI_PYTHON scripts\build_training_dataset.py --source imported_csv --dry-run --missingness-report
& $env:MMA_AI_PYTHON scripts\build_training_dataset.py --source imported_csv --output ufc_predictor\data\processed\training_dataset.csv
```

Optional Kaggle download helper:

```powershell
& $env:MMA_AI_PYTHON scripts\download_kaggle_datasets.py --dry-run
& $env:MMA_AI_PYTHON scripts\download_kaggle_datasets.py
& $env:MMA_AI_PYTHON scripts\download_kaggle_datasets.py --only betting_odds_daily
```

Kaggle may require local authentication. If download fails, download manually from Kaggle and place CSVs under `data\imports\kaggle`.

## Commit Policy

Usually commit:

- importer code
- tests
- small model metadata/artifacts needed by the app
- documentation

Do not commit:

- raw downloaded datasets
- local import folders
- generated large training datasets
- `.env` files
- service keys
- `node_modules`
- virtual environments
