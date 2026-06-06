# Build and Run

## Local Development

Start backend:

```powershell
cd C:\dev\mma-ai
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"
& $env:MMA_AI_PYTHON -m uvicorn ufc_predictor.api.app:app --host 127.0.0.1 --port 8000
```

Start frontend:

```powershell
cd C:\dev\mma-ai\app\frontend
npm ci
npm run dev
```

Open:

```text
http://localhost:5173
```

The frontend calls its own `/api` proxy during local development. The proxy forwards to `BACKEND_URL`, which defaults to `http://127.0.0.1:8000`.

Or run:

```powershell
.\scripts\dev.ps1
```

## PWA Build

```powershell
.\scripts\build_pwa.ps1
```

## Deploy Frontend

Deploy `app/frontend` to Vercel.

Set:

```text
NEXT_PUBLIC_API_BASE=https://your-backend-url
```

## Deploy Backend

Use `render.yaml`, or create a Render/Railway service with:

```text
Build: pip install -r requirements.txt
Start: uvicorn ufc_predictor.api.app:app --host 0.0.0.0 --port $PORT
```

## ELO Update

Manual:

```powershell
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"
& $env:MMA_AI_PYTHON scripts\update_elo.py
```

Cached data only:

```powershell
& $env:MMA_AI_PYTHON scripts\update_elo.py --no-refresh
```

This script is safe for Task Scheduler or cron.

## Supabase Import

Create tables with `supabase/schema.sql`, then set:

```powershell
$env:SUPABASE_DB_URL="postgresql://postgres:<password>@<host>:5432/postgres"
```

Import:

```powershell
& $env:MMA_AI_PYTHON scripts\import_supabase.py --apply-schema
```
