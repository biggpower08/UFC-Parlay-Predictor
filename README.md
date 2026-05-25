# UFC Predictor

Installable UFC/MMA prediction PWA served by FastAPI on Render with a Supabase Postgres production database.

## Production Deploy

### 1. Supabase

Create a Supabase project and copy these values:

- Project URL
- anon public key
- service role key
- Postgres connection string

Use the Postgres connection string as `DATABASE_URL`.

Run database migrations before importing data:

```bash
alembic upgrade head
python scripts/import_supabase.py
```

Import source CSV data, not the local SQLite cache. Do not upload `fighters.db` or model pickle files to Supabase.

### 2. Full app on Render

Render uses `render.yaml`. The Render service builds the frontend static app and serves it from the FastAPI backend, so the public app and API share one URL.

Set these Render environment variables:

```text
DATABASE_URL=your Supabase Postgres connection string
SUPABASE_URL=your Supabase project URL
SUPABASE_SERVICE_KEY=your Supabase service role key
UFC_PREDICTOR_DATA_DIR=/opt/render/project/src/ufc_predictor/data
FRONTEND_ORIGINS=https://your-vercel-app.vercel.app
LOG_LEVEL=INFO
```

Render start command:

```bash
alembic upgrade head && uvicorn ufc_predictor.api.app:app --host 0.0.0.0 --port $PORT
```

Health checks:

```text
GET /api/health
GET /health
```

### 3. Optional frontend on Vercel

Vercel is optional while stabilizing. The preferred production URL is the Render app URL.

If you still deploy Vercel as a backup, use source directory:

```text
app/frontend
```

Set these Vercel environment variables:

```text
NEXT_PUBLIC_API_URL=https://your-render-api.onrender.com
NEXT_PUBLIC_SUPABASE_URL=your Supabase project URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=your Supabase anon key
```

The PWA files are still in:

```text
app/frontend/public/manifest.json
app/frontend/public/service-worker.js
app/frontend/public/icon.svg
```

After deploying the single Render app, open the Render URL in a browser and use the browser install option to add it to desktop or phone.

## Live Database Updates

After setting `DATABASE_URL`, run:

```bash
python scripts/update_live_database.py --apply-schema
```

To compare the current Elo engine with the staged v2 placeholder:

```bash
python scripts/compare_elo_versions.py
```

## Local Run

Backend:

```bash
python -m uvicorn ufc_predictor.api.app:app --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd app/frontend
npm install
npm run dev
```

Local frontend defaults to `/api`, which proxies to `http://127.0.0.1:8000`.
