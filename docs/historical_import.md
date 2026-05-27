# Historical Fight Import

Use this when Supabase has fighter rows but the `fights` table is empty. Elo and rankings need real fight history, so this import should run before Elo refresh.

Live UFCStats scraping is still not the right path while UFCStats returns browser challenge pages. Use the local CSV first.

## Selected Source

Default source file:

```text
ufc_predictor/data/raw/fights.csv
```

Expected columns:

```text
event, fighter_1, fighter_2, result, method, round, time
```

This file has historical completed fight results. It does not include event dates or weight classes, so those fields are left empty during import instead of being guessed.

## Dry Run

Run this first. It validates the CSV and estimates inserts without writing rows if `DATABASE_URL` is missing.

```powershell
.\.venv312\Scripts\python.exe scripts\import_historical_fights.py --source-file ufc_predictor\data\raw\fights.csv --dry-run
```

If `DATABASE_URL` is set, dry-run also checks how many matching `source_hash` rows already exist.

## Limited Test Import

Use this only after the dry-run looks correct:

```powershell
.\.venv312\Scripts\python.exe scripts\import_historical_fights.py --source-file ufc_predictor\data\raw\fights.csv --limit 100
```

## Full Import

```powershell
.\.venv312\Scripts\python.exe scripts\import_historical_fights.py --source-file ufc_predictor\data\raw\fights.csv
```

The import is idempotent. It uses a stable `source_hash` and does not delete existing fight rows.

## After Import

Run Elo and rankings:

```powershell
.\.venv312\Scripts\python.exe scripts\update_elo.py --no-refresh
.\.venv312\Scripts\python.exe scripts\generate_rankings.py
.\.venv312\Scripts\python.exe scripts\sync_database.py --status
```

## Supabase Verification SQL

```sql
select count(*) from fights;

select count(*) from fighter_elo_history;

select max(computed_at) as latest_elo
from fighter_elo_history;

select count(*) from fighter_rankings;

select max(generated_at) as latest_rankings
from fighter_rankings;

select name, normalized_name, elo, peak_elo, elo_fights_count, elo_source, elo_computed_at
from fighters
where coalesce(elo_fights_count, 0) > 0
order by elo desc
limit 20;
```

## Do Not Run Yet

Do not run unrestricted live UFCStats sync while source health says `challenged`. That means UFCStats returned a browser challenge page, not normal fight data.
