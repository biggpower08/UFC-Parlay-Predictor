# Training Data Sources

Use curated datasets as the primary training path. Live UFCStats scraping remains optional source-health tooling and should not block product progress.

Before using any dataset commercially, verify its license and terms. Do not commit raw downloaded datasets.

Place local files in one of:

```powershell
C:\dev\mma-ai\data\imports
C:\dev\mma-ai\ufc_predictor\data\imports
```

## Recommended Sources

| Dataset/source category | Source type | Best use | Likely files | Expected labels | Helps models | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| UFC Fight Forecast / gold modeling dataset style | Kaggle/manual download | Strong pre-fight modeling rows with rolling stats | one or more fight-level CSVs | winner, method, round, dates, fighter stats, sometimes odds | winner, finish, distance, method, round phase | Best if columns are already leakage-aware pre-fight features. Verify commercial rights. |
| Ultimate UFC Dataset style | Kaggle/manual download | Broad fight and fighter history | fights.csv, fighters.csv, enhanced_fights.csv, fighter_stats.csv | winner, method, round, event date, fighter metadata | finish, distance, method, round phase | Good general refresh source if dates are reliable. |
| UFC Betting Odds daily snapshots | Kaggle/API/manual download | Odds calibration later | odds snapshots, moneyline history, opening/closing odds | sportsbook, odds, timestamp, fighter/fight identifiers | odds calibration, future betting-value model | Do not train odds models until historical snapshots and outcomes are matched. |
| UFC fight/fighter stats datasets | Kaggle/manual download | Fight-result labels and per-fight stat labels | fight stats CSVs, fighter stats CSVs | method, round, sig strikes, takedowns, control time | strike volume, takedown/control, finish, method | Current-fight stats can be labels only, not pre-fight features. |
| UFCStats-style GitHub CSV datasets | GitHub/manual download | UFCStats-like event/fight/stat tables without live scraping | ufc_events.csv, ufc_fight_details.csv, ufc_fight_results.csv, ufc_fight_stats.csv, ufc_fighter_details.csv, ufc_fighter_tott.csv | event dates, fighters, methods, rounds, sig strikes, takedowns | all dedicated prop models if complete | Prefer cached CSV exports over challenged live scraping. Verify repo license. |
| SportsDataIO | Paid API later | Structured fight/event/fighter data | API responses | event/fight metadata, results, stats depending plan | refresh pipeline, model labels | Paid provider. Do not require key for app startup. |
| The Odds API | Paid/free API later | Current odds/status and future odds snapshots | API responses | moneylines, books, timestamps | odds status now; odds calibration later after history exists | Do not show fake odds. Historical storage is required before edge modeling. |
| Sportradar / OddsMatrix | Paid API later | Enterprise-grade sports/odds data | API responses | odds history, event mapping | odds calibration, market movement | Consider only after MVP revenue validates cost. |

## Curated Dataset Slugs

These source names are stored in `ufc_predictor/training/dataset_sources.py` for repeatable downloads:

```text
jerzyszocik/ufc-fight-forecast-complete-gold-modeling-dataset
mdabbert/ultimate-ufc-dataset
jerzyszocik/ufc-betting-odds-daily-dataset
cadelueker/ufc-fighter-and-fight-stats-as-of-04-9-2025
rajaisrarkiani/ufc-fights-and-fighter-stats-dataset
https://github.com/komaksym/UFC-DataLab
```

## Import Commands

```powershell
cd C:\dev\mma-ai
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"

& $env:MMA_AI_PYTHON scripts\import_training_dataset.py --input-dir data\imports --dry-run
& $env:MMA_AI_PYTHON scripts\import_training_dataset.py --input-dir data\imports
& $env:MMA_AI_PYTHON scripts\build_training_dataset.py --source imported_csv --dry-run --missingness-report
& $env:MMA_AI_PYTHON scripts\build_training_dataset.py --source imported_csv --output ufc_predictor\data\processed\training_dataset.csv
```

Optional Kaggle download helper:

```powershell
& $env:MMA_AI_PYTHON scripts\download_training_datasets.py --dry-run
& $env:MMA_AI_PYTHON scripts\download_training_datasets.py --copy --output-dir data\imports
```

Kaggle may require local authentication. If download fails, download manually from Kaggle and place CSVs under `data\imports`.

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
