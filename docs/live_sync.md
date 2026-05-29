# UFCStats Live Sync

This app now has a safe live-sync path for UFCStats data, but scheduled scraping is intentionally not enabled by default.

## Current Source Limitation

UFCStats may return a browser JavaScript challenge instead of normal HTML. The app detects that response and stops safely. It does not try to bypass CAPTCHA, access controls, login walls, or anti-abuse protections.

If UFCStats is challenged, use cache-only mode, manual HTML import planning, or CSV imports until the source is available again.

## Fetch Modes

- Live fetch: requests UFCStats with polite rate limiting and limited retries.
- Cached HTML mode: reads previously cached HTML and does not make network requests. Use this for parser validation when cached pages are known-good.
- Manual HTML import mode: save source HTML manually and parse it offline. Keep this review-driven; do not use it as a bot-protection bypass.
- CSV import mode: import historical fights from local CSV. Use this for Elo/model training when live source health is challenged.
- Future backup source mode: placeholder for other licensed or stable sources. Do not add aggressive scraping.
- Optional Playwright: available by flag for ordinary JavaScript-rendered pages only. It is not required for app startup and is not used as a bot-protection bypass.

## Safe Local Commands

Check current sync/source status:

```powershell
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"
& $env:MMA_AI_PYTHON scripts\sync_database.py --status
```

Check UFCStats source health:

```powershell
& $env:MMA_AI_PYTHON scripts\sync_database.py --source-health
```

Run the detailed UFCStats scraper diagnostic:

```powershell
& $env:MMA_AI_PYTHON scripts\diagnose_scraper.py --fetcher requests
```

Cache-only diagnostic:

```powershell
& $env:MMA_AI_PYTHON scripts\diagnose_scraper.py --fetcher requests --cache-only
```

Save debug HTML for local inspection only:

```powershell
& $env:MMA_AI_PYTHON scripts\diagnose_scraper.py --fetcher requests --save-debug-html
```

Run a dry-run limited sync:

```powershell
& $env:MMA_AI_PYTHON scripts\sync_database.py --dry-run --recent-days 14 --fetcher requests
```

Run cache-only mode:

```powershell
& $env:MMA_AI_PYTHON scripts\sync_database.py --dry-run --cache-only --limit-events 1
```

Parse a manually saved UFCStats event page without live fetching:

```powershell
& $env:MMA_AI_PYTHON scripts\diagnose_scraper.py --manual-html C:\path\to\ufcstats_event.html --page-type event_detail
& $env:MMA_AI_PYTHON scripts\sync_database.py --dry-run --event-html C:\path\to\ufcstats_event.html
```

Manual HTML flow:

1. Open the UFCStats page in your browser.
2. Save the page HTML to a local file.
3. Run `diagnose_scraper.py --manual-html` with the matching `--page-type`.
4. For event detail pages, run `sync_database.py --event-html ... --dry-run`.

Import local historical CSV data when live source health is challenged:

```powershell
& $env:MMA_AI_PYTHON scripts\import_historical_fights.py --source-file ufc_predictor\data\raw\fights.csv --dry-run
```

Run a production-style recent sync manually:

```powershell
& $env:MMA_AI_PYTHON scripts\sync_database.py --recent-days 14 --fetcher requests
```

Generate rankings without scraping:

```powershell
& $env:MMA_AI_PYTHON scripts\generate_rankings.py
```

Refresh Elo without scraping:

```powershell
& $env:MMA_AI_PYTHON scripts\update_elo.py --no-refresh
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

## Optional Playwright Fetcher

Playwright is optional and should only be used for normal JavaScript-rendered pages. Do not use it to bypass CAPTCHA, anti-bot checks, challenge pages, or access controls.

Install optional support:

```powershell
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"
& $env:MMA_AI_PYTHON -m pip install playwright
& $env:MMA_AI_PYTHON -m playwright install chromium
```

Run source-health with Playwright:

```powershell
& $env:MMA_AI_PYTHON scripts\sync_database.py --source-health --fetcher playwright
```

## Render Cron Recommendation

Do not enable a recurring live sync until manual runs are stable and source health is not repeatedly `challenged`.

When ready, use a Render Cron Job instead of making normal users trigger scraping:

```bash
python scripts/sync_database.py --recent-days 14 --fetcher requests
```

Use only after source-health checks are stable. If UFCStats challenge pages are frequent, keep the cron disabled and use manual/cache/CSV imports.

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

Source-health checks record source state in `scraper_sources` and add a zero-data audit row to `sync_runs`. Dry-run syncs do not write app fight/event/fighter data.

## Rollback / Disable

To disable live data updates, do not run the sync script or cron job. The app can continue using Supabase data, local CSV import backups, and existing Elo/rankings.
