# Codex MCP Workflow

This repo can use globally configured Codex MCP servers to make development easier, but MCPs should support the existing architecture rather than reshape it.

## Project Context

- App type: UFC/MMA prediction and fight-intelligence web app.
- Backend: FastAPI, SQLAlchemy, Alembic, Supabase Postgres.
- Frontend: static Next.js app under `app/frontend`, served by the single Render-hosted FastAPI deployment.
- Data/modeling: local raw imports under `data/imports/`, normalized outputs and small reports/artifacts under `ufc_predictor/data/processed` when safe.
- Deployment target: one Render web service using `render.yaml`.

## MCP Servers Detected

Detected with:

```powershell
codex mcp list
```

Connected and enabled:

- `playwright`
- `context7`
- `sequential-thinking`
- `github`
- `memory`
- `node_repl`
- `exa`

Requested but not currently connected in this setup:

- `perplexity`
- `firecrawl`

If Perplexity or Firecrawl are added later, rerun `codex mcp list` and update this file.

## How To Use Each MCP

### Playwright

Use for:

- Browser-based verification of Home, Analysis, Stats, Odds, Models, and Pricing pages.
- Navigation and stale-state bugs.
- Console error checks.
- Visual checks after UI changes.
- End-to-end smoke flows such as searching fighters, generating a prediction, then opening deeper pages.

Do not use for:

- Backend-only model or data validation.
- Replacing unit tests.
- Large, brittle test suites before core user flows are stable.

Recommended first browser smoke checks:

1. Open `/`.
2. Confirm no default fighters are selected.
3. Generate a prediction.
4. Open `/analysis`, `/stats`, `/odds`, and `/models`.
5. Confirm the latest matchup is shown and no page 404s.
6. Confirm Odds remains market-readiness only and shows no fake lines or bet placement.

### Context7

Use for current documentation lookup when changing library/framework behavior, especially:

- Next.js App Router and static export behavior.
- FastAPI request/response patterns and lifespan migration.
- SQLAlchemy/Alembic migration behavior.
- Playwright test syntax if formal tests are added.
- Supabase/Postgres client or deployment behavior.

Do not use for:

- Private repo content.
- Business logic that should be understood from local files.
- Replacing local tests.

Documentation note from Context7 for this repo:

- The frontend uses `output: "export"` in `app/frontend/next.config.js`.
- `npm run build` produces static output in `app/frontend/out`.
- `next start` is not the right production verification command for `output: "export"`; serve the exported `out` folder when a local static smoke test is needed.

### Sequential Thinking

Use for:

- Multi-step debugging.
- Non-trivial refactors.
- Training/evaluation planning.
- Paywall/product architecture planning.
- Risky changes that need a small plan before edits.

Do not use for:

- Tiny copy edits.
- Simple one-file fixes where reading the file is enough.
- Creating long abstract plans detached from the repo.

Before major edits, write a short implementation plan tied to actual files.

### Perplexity

Status: not connected.

If connected later, use for:

- Current public research.
- Deployment/runtime issue research.
- External API/package behavior comparisons.

Do not use for:

- Private repo content.
- Secrets, database URLs, service keys, or raw private data.

### Firecrawl

Status: not connected.

If connected later, use for:

- Structured extraction from public documentation pages.
- Public source documentation snapshots that need repeatable summarization.

Do not use for:

- Random broad crawling.
- CAPTCHA, anti-bot, or access-control bypassing.
- UFCStats evasion or aggressive scraping.

## Normal Local Commands

Use the project venv directly:

```powershell
cd C:\dev\mma-ai
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"
```

Backend tests:

```powershell
$TempTestDir = "$env:TEMP\mma_ai_pytest_$([guid]::NewGuid().ToString())"
& $env:MMA_AI_PYTHON -m pytest ufc_predictor\tests -q --basetemp $TempTestDir
```

Frontend build:

```powershell
cd C:\dev\mma-ai\app\frontend
npm run build
```

Dataset download:

```powershell
cd C:\dev\mma-ai
& $env:MMA_AI_PYTHON scripts\download_kaggle_datasets.py --all --skip-existing
```

Preprocess imported datasets:

```powershell
& $env:MMA_AI_PYTHON scripts\preprocess_imported_datasets.py --input-root data\imports --all --write-summary
```

Evaluate models:

```powershell
& $env:MMA_AI_PYTHON scripts\evaluate_model_accuracy.py --input-dir data\imports --split chronological --calibrate --by-segment
```

## Local Static Frontend Verification

Because the frontend is configured for static export:

```powershell
cd C:\dev\mma-ai\app\frontend
npm run build
& $env:MMA_AI_PYTHON -m http.server 5173 --bind 127.0.0.1 --directory out
```

Then open:

```text
http://127.0.0.1:5173/
```

Use Playwright or the in-app browser for route checks after the static server is running.

## Safety Rules

- Do not commit raw datasets, ZIPs, `kaggle.json`, `.env`, service keys, `node_modules`, `.venv`, `C:\venvs`, `.next`, pytest temp folders, or `ufc_predictor/data/processed/fighters.db`.
- Do not use MCPs to bypass CAPTCHA, bot protection, source protections, or access controls.
- Do not train or mark models as production-ready without real data, leakage checks, validation metrics, and saved metadata.
- Keep odds calibration blocked until timestamp-safe odds mapping and modeling review pass.
- Keep the single Render-hosted FastAPI architecture.
- Do not split frontend/backend deployment unless explicitly requested.

## When To Update This File

Update this workflow note when:

- A new MCP server is connected.
- A project command changes.
- A new high-value browser test flow is added.
- Deployment architecture changes.
- Model/data safety rules change.
