# Supabase Setup

## 1. Create the tables

Preferred production path:

```powershell
$env:DATABASE_URL="postgresql://postgres:<password>@<host>:5432/postgres?sslmode=require"
alembic upgrade head
```

Manual fallback: open your Supabase project, go to SQL Editor, and run `supabase/schema.sql`.

Both paths create:

- `fighters`
- `fights`
- `fighter_elo_history`
- `predictions`
- `feedback`
- `scrape_cache`

## 2. Set your database URL

In PowerShell:

```powershell
$env:DATABASE_URL="postgresql://postgres:<password>@<host>:5432/postgres?sslmode=require"
```

Use the direct Postgres connection string from Supabase project settings.

## 3. Import local data

From the repo root:

```powershell
python scripts\import_supabase.py --apply-schema
```

The importer reads:

- `ufc_predictor/data/raw/fighters.csv`
- `ufc_predictor/data/raw/fights.csv`
- `ufc_predictor/data/feedback/feedback_log.csv`

It does not import:

- `fighters.db`
- `latest_model.pkl`
- `model_metrics.json`
- `model_weights.json`

## 4. Verify row counts

In Supabase SQL Editor:

```sql
select count(*) from fighters;
select count(*) from fights;
select count(*) from fighter_elo_history;
select count(*) from feedback;
```
