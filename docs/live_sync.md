# UFCStats Live Sync

This app now has a safe live-sync path for UFCStats data, but scheduled scraping is intentionally not enabled by default.

## Current Source Limitation

UFCStats may return a browser JavaScript challenge instead of normal HTML. The app detects that response and stops safely. It does not try to bypass CAPTCHA, access controls, login walls, or anti-abuse protections.

If UFCStats is challenged, use cache-only mode, fixture tests, or manual imports until the source is available again.

## Fetch Modes

- Live fetch: requests UFCStats with polite rate limiting and retries.
- Cache-only: reads previously cached HTML and does not make network requests.
- Fixture/sample: used by tests with saved HTML files.
- Manual import: future-safe path for CSV/HTML files when live scraping is unavailable.
- Optional Playwright: available by flag for ordinary JavaScript-rendered pages only. It is not required for app startup and is not used as a bot-protection bypass.

## Safe Local Commands

Check current sync/source status:

```powershell
.\.venv312\Scripts\python.exe scripts\sync_database.py --status
```

Check UFCStats source health:

```powershell
.\.venv312\Scripts\python.exe scripts\sync_database.py --source-health
```

Run a dry-run limited sync:

```powershell
.\.venv312\Scripts\python.exe scripts\sync_database.py --dry-run --limit-events 1
```

Run cache-only mode:

```powershell
.\.venv312\Scripts\python.exe scripts\sync_database.py --dry-run --cache-only --limit-events 1
```

Run a production-style recent sync manually:

```powershell
.\.venv312\Scripts\python.exe scripts\sync_database.py --recent-days 14
```

Generate rankings without scraping:

```powershell
.\.venv312\Scripts\python.exe scripts\generate_rankings.py
```

Refresh Elo without scraping:

```powershell
.\.venv312\Scripts\python.exe scripts\update_elo.py --no-refresh
```

## Optional Environment Variables

None of these are required for normal app startup.

- `ENABLE_LIVE_SYNC=false`: keeps future manual sync triggers disabled by default.
- `SYNC_SECRET`: enables protected internal sync status endpoints when set.
- `SCRAPER_FETCHER=requests`: default fetcher. Optional value: `playwright`.
- `SCRAPER_RATE_LIMIT_SECONDS=1.0`: delay between live requests.
- `SCRAPER_CACHE_DIR`: override scraper cache folder.
- `SCRAPER_USER_AGENT`: override the polite user agent string.
- `SCRAPER_MAX_RESPONSE_BYTES`: safety limit for source responses.

## Render Cron Recommendation

Do not enable a recurring live sync until manual runs are stable and source health is not repeatedly `challenged`.

When ready, use a Render Cron Job instead of making normal users trigger scraping:

```bash
python scripts/sync_database.py --recent-days 14 --fetcher requests
```

If UFCStats challenge pages are frequent, keep the cron disabled and use manual/cache imports.

Recommended early schedule: once per day during off-peak hours. Avoid hourly scraping unless repeated manual checks show the source is healthy.

## Inspect Sync State

Latest sync runs:

```sql
select source, status, dry_run, events_seen, fights_seen, fighters_seen, started_at, finished_at, message
from sync_runs
order by started_at desc
limit 20;
```

Expanded sync counts:

```sql
select source, status, events_seen, fights_seen, fighters_seen,
       inserted_count, updated_count, skipped_count, failed_count,
       started_at, finished_at, message
from sync_runs
order by started_at desc
limit 20;
```

Source health:

```sql
select source, enabled, last_success_at, last_failed_at, challenge_detected,
       consecutive_failures, last_status_code, average_fetch_ms, last_error, updated_at
from scraper_sources
order by updated_at desc;
```

Current lock:

```sql
select lock_name, owner, started_at, expires_at
from sync_locks
order by started_at desc;
```

Latest Elo and rankings:

```sql
select max(computed_at) as latest_elo from fighter_elo_history;
select max(generated_at) as latest_rankings from fighter_rankings;
```

## Troubleshooting

- `challenged`: UFCStats returned a browser challenge. The sync stopped safely.
- `unavailable`: the source timed out, returned an error, or cache-only mode had no usable cache.
- `partial`: at least one event failed, but other parsed data may have been processed.
- `failed`: no safe sync could complete.

The sync uses a database lock so overlapping live jobs do not run at the same time. Expired locks are cleared automatically.

## Rollback / Disable

To disable live data updates, do not run the sync script or cron job. The app can continue using Supabase data, local CSV import backups, and existing Elo/rankings.
