# Weekly Kaggle Refresh Automation

## Plain-English Summary
This workflow refreshes local Kaggle UFC/MMA datasets once a week, writes a download manifest, and audits odds timestamps. It does not commit raw data, does not train production models, and does not unblock odds modeling by itself.

## What It Refreshes
- Raw Kaggle files under `data/imports/kaggle/<dataset_id>/`.
- Local download manifest at `data/imports/kaggle/_download_manifest.json`.
- Odds timestamp audit at `docs/odds_timestamp_audit.md`.
- Machine-readable odds timestamp audit at `ufc_predictor/data/processed/odds_timestamp_audit.json`.

## Manual Run

```powershell
cd C:\dev\mma-ai
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"
powershell -NoProfile -ExecutionPolicy Bypass -File C:\dev\mma-ai\scripts\run_weekly_kaggle_refresh.ps1
```

## Windows Task Scheduler Setup

Run this once in PowerShell:

```powershell
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\dev\mma-ai\scripts\run_weekly_kaggle_refresh.ps1"
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 8:00am
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "MMA AI Weekly Kaggle Refresh" -Action $Action -Trigger $Trigger -Settings $Settings -Description "Refresh Kaggle UFC datasets and run odds timestamp audit weekly"
```

## Kaggle Credentials
- Keep `kaggle.json` under your user profile, usually `C:\Users\<you>\.kaggle\kaggle.json`.
- Do not place Kaggle credentials inside the repo.
- Do not commit Kaggle credentials.
- You can also set `KAGGLE_USERNAME` and `KAGGLE_KEY` locally.

## Safety Rules
- Raw data stays local and uncommitted.
- `data/imports/` stays ignored by Git.
- Downloading odds data does not unblock `odds_calibration_model`.
- Odds rows need trusted collection timestamps before odds modeling.
- Closing odds can only be used for closing-line mode unless earlier snapshots exist.

## GitHub Actions Note
Do not move this to GitHub Actions yet unless there is a specific reason. Raw Kaggle data is large, Kaggle credentials would need GitHub secrets, and the workflow should not commit downloaded data. Local Windows Task Scheduler is preferred for now.
