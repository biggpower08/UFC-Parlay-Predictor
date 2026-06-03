# Supabase Setup

This app uses Supabase Postgres as the production database. FastAPI remains the public API layer; the frontend should not connect directly to privileged database credentials.

## What Supabase Stores

- fighters
- fights
- predictions
- feedback
- Elo snapshots and fight-by-fight Elo history
- rankings
- future subscription and entitlement records

## Required Environment Variables

Production needs:

```powershell
DATABASE_URL="YOUR_SUPABASE_CONNECTION_STRING"
```

Future Stripe placeholders, not required yet:

```powershell
ENABLE_STRIPE=false
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_PREMIUM_MONTHLY=
STRIPE_PRICE_PRO_MONTHLY=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
```

Do not expose `DATABASE_URL`, service role keys, or Stripe secret keys to the frontend.

## Verify DATABASE_URL Locally

Use a redacted/encoded connection string. If the password has special characters, URL-encode it first.

```powershell
cd C:\dev\mma-ai
$env:DATABASE_URL="YOUR_SUPABASE_CONNECTION_STRING"
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"
& $env:MMA_AI_PYTHON -c "from ufc_predictor.db.schema import using_postgres; print('postgres:', using_postgres())"
```

Expected:

```text
postgres: True
```

## Migration Approach

Preferred production flow:

1. Commit Alembic migration files.
2. Deploy to Render.
3. Run migrations from a controlled Render job or GitHub Action when configured.

Manual local migration against Supabase:

```powershell
cd C:\dev\mma-ai
$env:DATABASE_URL="YOUR_SUPABASE_CONNECTION_STRING"
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"
& $env:MMA_AI_PYTHON -m alembic upgrade head
```

Local SQLite development does not use Alembic migrations. Local tables are created by `init_db()` when the app or maintenance scripts run.

## SQL Verification Queries

Run these in the Supabase SQL editor after migrations/imports:

```sql
select table_name
from information_schema.tables
where table_schema = 'public'
order by table_name;

select * from alembic_version;

select count(*) from fighters;
select count(*) from fights;
select count(*) from fighter_elo_history;
select count(*) from fighter_elo_fight_history;
select count(*) from fighter_rankings;
select count(*) from predictions;
select count(*) from feedback;
```

## Security Notes

- Server/backend code can use `DATABASE_URL`.
- Do not expose `DATABASE_URL` to browser code.
- Do not expose Supabase service role keys.
- If frontend Supabase access is added later, enable Row Level Security first and add explicit policies.
- For now, keep database access behind the FastAPI backend.
- Rotate any password that was pasted into a chat, screenshot, terminal transcript, or commit by accident.

## Future Subscription Tables

These are planned for after Supabase Auth and Stripe are added. They are not required for the current MVP.

- `user_profiles`
- `stripe_customers`
- `subscriptions`
- `entitlement_events`
- `stripe_webhook_events`

The future paywall should check backend entitlement state before returning premium-only data. Do not rely on frontend-only checks for paid access.

## Do Not Commit

- `.env`
- `.env.local`
- `DATABASE_URL`
- Supabase service role keys
- Stripe secret keys
- downloaded datasets
- generated DB files
- `node_modules`
- `.venv`
- `C:\venvs`
- `pytest_tmp_codex`
