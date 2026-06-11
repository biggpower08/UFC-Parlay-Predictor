# Development Run Modes

## Plain-English Summary
Use the lightest validation mode that matches the task. Full audits are useful, but they are slow and should be saved for major model/status/artifact decisions.

## Fast Mode
Use for:
- Docs consolidation.
- Master status generation.
- Schema helpers.
- Small backend/API additions.
- UI labels or badges.
- Focused tests.

Recommended commands:

```powershell
cd C:\dev\mma-ai
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"
& $env:MMA_AI_PYTHON scripts\build_master_project_status.py
& $env:MMA_AI_PYTHON -m pytest ufc_predictor\tests\test_master_project_status.py -q
```

## Medium Mode
Use for:
- Affected model-family evaluation.
- Source diagnostics.
- Source eligibility review.
- Report regeneration from existing outputs.
- Relevant tests.

Recommended commands:

```powershell
& $env:MMA_AI_PYTHON scripts\source_transfer_diagnostics.py
$TempTestDir = "$env:TEMP\mma_ai_pytest_$([guid]::NewGuid().ToString())"
& $env:MMA_AI_PYTHON -m pytest ufc_predictor\tests -q --basetemp $TempTestDir
```

## Full Audit Mode
Use only before major model/status/artifact decisions.

```powershell
& $env:MMA_AI_PYTHON scripts\preprocess_imported_datasets.py --input-root data\imports --all --write-summary
& $env:MMA_AI_PYTHON scripts\evaluate_model_accuracy.py --input-dir data\imports --split chronological --calibrate --by-segment --force-rebuild
& $env:MMA_AI_PYTHON scripts\backtest_historical_fights.py --input-dir data\imports --split chronological --all-test-fights --by-segment
& $env:MMA_AI_PYTHON scripts\audit_metric_jumps.py
```
