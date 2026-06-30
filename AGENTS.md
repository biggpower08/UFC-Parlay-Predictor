# Project Instructions For Codex

This is a UFC/MMA prediction and fight-intelligence app.

## Local Commands

Use this Python executable for local commands unless instructed otherwise:

```powershell
C:\venvs\mma-ai\Scripts\python.exe
```

Standard local workflow:

```powershell
cd C:\dev\mma-ai
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"
```

Download datasets:

```powershell
& $env:MMA_AI_PYTHON scripts\download_kaggle_datasets.py --all --skip-existing
```

Preprocess:

```powershell
& $env:MMA_AI_PYTHON scripts\preprocess_imported_datasets.py --input-root data\imports --all --write-summary
```

Evaluate:

```powershell
& $env:MMA_AI_PYTHON scripts\evaluate_model_accuracy.py --input-dir data\imports --split chronological --calibrate --by-segment
```

Run tests safely:

```powershell
$TempTestDir = "$env:TEMP\mma_ai_pytest_$([guid]::NewGuid().ToString())"
& $env:MMA_AI_PYTHON -m pytest ufc_predictor\tests -q --basetemp $TempTestDir
```

Frontend build only if frontend changed:

```powershell
cd app\frontend
npm run build
```

## MCP Workflow

Use MCP servers only when they clearly improve the work. Do not rewrite project architecture just because an MCP is available.

Check available servers with:

```powershell
codex mcp list
```

Current useful MCP roles for this repo:

- Playwright: browser QA, route checks, visual checks, navigation bugs, console errors, and core user flows.
- Context7: current docs for Next.js, FastAPI, SQLAlchemy/Alembic, Supabase, Playwright, and other library behavior.
- Sequential Thinking: practical planning for non-trivial debugging, refactors, model/data changes, and architecture decisions.
- Perplexity: use only if connected, for current public research and external tooling/deployment questions.
- Firecrawl: use only if connected, for structured extraction from public docs/pages.

Do not use MCPs for secrets, private data transmission, CAPTCHA or anti-bot bypassing, fake data/model claims, or unnecessary broad crawling.

See `docs/MCP_WORKFLOW.md` for the full repo-specific MCP workflow.

## Raw Data Rules

- Raw Kaggle/GitHub/manual datasets live under `data/imports/`.
- Never commit raw datasets, ZIPs, `kaggle.json`, `.env`, service keys, `node_modules`, `.venv`, `C:\venvs`, `.next`, pytest temp folders, or `ufc_predictor/data/processed/fighters.db`.
- Small safe JSON reports/artifacts may be committed only if useful.
- Supabase is still the production database. Raw Kaggle/GitHub files are training inputs, not runtime dependencies.

## Model Training Rules

- Models must be trained on pre-fight features only.
- Labels must be kept separate from features.
- Never use winner/result/method/finish_round/finish_time/current-fight strikes/current-fight takedowns/current-fight control/judges scores/post-fight records as input features.
- Target columns such as `f1_wins_safe`, `went_distance`, `over_2_5`, `method_class`, strike thresholds, and takedown thresholds must not be input features.
- Use the runtime-compatible feature factory when possible.
- Historical training features must be generated as of `event_date`.
- Live prediction features and historical training features should share the same schema where possible.

## Evaluation Rules

- Report actual held-out performance, not only "can train".
- Use chronological final-test evaluation as the headline metric when `event_date` exists.
- Random split may only be reported as a comparison.
- Keep final test data out of training, preprocessing fit, tuning, and calibration.
- Fit encoders/imputers/scalers only on the training split, preferably with an sklearn `Pipeline`.
- Compare every model against a baseline.
- Report relative improvement over baseline.
- Report calibration metrics for probability models when possible.
- Report segment metrics where possible.
- Do not mark `production_ready` unless the model beats baseline on held-out data, leakage risk is low, runtime compatibility is true, calibration is acceptable, and sample size is adequate.

## Model-Specific Rules

- `winner_model` target: `f1_wins_safe`.
- `finish_model` and `goes_distance_model` should be evaluated consistently because they are inverse concepts.
- `method_model` must use balanced/macro metrics because classes are imbalanced.
- `round_phase_model` should prioritize useful prop targets like `over_1_5`, `over_2_5`, `ends_before_round_3`, and `goes_distance`.
- `strike_volume_model` targets are independent from winner; a fighter can land 50+ significant strikes and still lose.
- `takedown_control_model` targets are independent from winner; a fighter can hit takedown/control props and still lose.
- `odds_calibration_model` may only use odds if timestamp quality is pre-fight or trusted; unknown timestamp odds are `review_needed`.
