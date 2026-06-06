# Local Development on Windows

Use this workflow for local development and validation.

## Repo Location

Use:

```powershell
cd C:\dev\mma-ai
```

Do not use the old OneDrive folder. OneDrive caused Git, npm, Next, and virtual-environment permission problems.

## Python Version Policy

Recommended local target:

- Python 3.14
- External venv: `C:\venvs\mma-ai`
- Project Python env var: `MMA_AI_PYTHON=C:\venvs\mma-ai\Scripts\python.exe`

Compatibility fallback:

- Python 3.13 is acceptable if a dependency blocks Python 3.14 on a specific machine.
- Do not use old numbered repo venv folders.
- Do not require activation. Run tools through the venv Python directly.

The repo does not define `pyproject.toml`, `setup.py`, or `setup.cfg`; Python dependencies are listed in `requirements.txt`. Development/test dependencies are listed in `requirements-dev.txt`.

## First-Time Setup

```powershell
cd C:\dev\mma-ai
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

$BasePython = "C:\Program Files\Python314\python.exe"
# If your Python 3.14 executable is elsewhere, verify paths with:
py -0p
Get-Command python -All

& $BasePython --version
& $BasePython -m venv C:\venvs\mma-ai

[Environment]::SetEnvironmentVariable("MMA_AI_PYTHON", "C:\venvs\mma-ai\Scripts\python.exe", "User")
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"

& $env:MMA_AI_PYTHON --version
& $env:MMA_AI_PYTHON -m pip install --upgrade pip
& $env:MMA_AI_PYTHON -m pip install -r requirements.txt
& $env:MMA_AI_PYTHON -m pip install -r requirements-dev.txt
```

Or use the setup script:

```powershell
cd C:\dev\mma-ai
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"
.\scripts\dev_setup.ps1
```

If Windows cannot run `C:\venvs\mma-ai\Scripts\python.exe`, recreate it from the all-users Python install:

```powershell
Remove-Item -Recurse -Force C:\venvs\mma-ai -ErrorAction SilentlyContinue
& "C:\Program Files\Python314\python.exe" -m venv C:\venvs\mma-ai
```

## Backend Tests

Use a unique temp folder outside the repo. This avoids Windows file handle problems with a reused repo temp directory.

```powershell
cd C:\dev\mma-ai
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"
$TempTestDir = "$env:TEMP\mma_ai_pytest_$([guid]::NewGuid().ToString())"
& $env:MMA_AI_PYTHON -m pytest ufc_predictor\tests -q -p no:cacheprovider --basetemp $TempTestDir
```

Or:

```powershell
.\scripts\dev_test_backend.ps1
```

If an old repo temp folder is stuck, remove it from your normal PowerShell:

```powershell
Remove-Item -Recurse -Force .\pytest_tmp_codex -ErrorAction SilentlyContinue
```

## Frontend Build

```powershell
cd C:\dev\mma-ai
.\scripts\dev_test_frontend.ps1
```

The script uses `npm ci` when `app\frontend\package-lock.json` exists, then runs the production build.

If `npm run build` fails because of a Windows npm wrapper or PATH issue, run this from `app\frontend`:

```powershell
& "C:\Program Files\nodejs\node.exe" node_modules\next\dist\bin\next build
```

Do not use the fallback to hide real Next build errors. It only bypasses local npm wrapper/PATH problems.

## Sync Status and Source Health

Check current sync/source status:

```powershell
cd C:\dev\mma-ai
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"
& $env:MMA_AI_PYTHON scripts\sync_database.py --status
```

Check source health:

```powershell
& $env:MMA_AI_PYTHON scripts\sync_database.py --source-health
```

Safe dry-run, without writing production data:

```powershell
& $env:MMA_AI_PYTHON scripts\sync_database.py --dry-run --recent-days 14 --fetcher requests
```

Training dataset readiness dry-run:

```powershell
& $env:MMA_AI_PYTHON scripts\build_training_dataset.py --dry-run --missingness-report
```

## Git Workflow

Codex can edit files, but you should manually stage, commit, and push.

Before staging:

```powershell
cd C:\dev\mma-ai
.\scripts\git_health_check.ps1
```

Normal flow:

```powershell
git status
git add <files>
git commit -m "Your commit message"
git push
```

If Git reports a stale index file and no Git process is running:

```powershell
Remove-Item -Force .git\index.lock -ErrorAction SilentlyContinue
```

## Access Denied Fixes

- Make sure the repo is `C:\dev\mma-ai`, not OneDrive.
- Use an all-users Python install such as `C:\Program Files\Python314\python.exe`.
- Recreate the external venv if it points at an old blocked user-profile Python.
- Close VS Code terminals or Git GUI tools that may hold files open.

If Git complains about ownership:

```powershell
git config --global --add safe.directory C:/dev/mma-ai
```

## Defender / Controlled Folder Access

If Python exists but Windows returns `Access is denied`, Windows Security may be blocking execution from the repo or venv folder.

Manual steps:

1. Open Windows Security.
2. Go to Virus & threat protection.
3. Open Manage settings.
4. Open Exclusions.
5. Choose Add or remove exclusions.
6. Add folder `C:\dev\mma-ai`.
7. Add folder `C:\venvs\mma-ai`.

Optional admin PowerShell commands:

```powershell
Add-MpPreference -ExclusionPath "C:\dev\mma-ai"
Add-MpPreference -ExclusionPath "C:\venvs\mma-ai"
```

## Do Not Commit

Do not commit:

- `.venv*`
- `C:\venvs`
- `docs\.venv`
- `node_modules`
- `app\frontend\node_modules`
- `app\frontend\.next`
- `app\frontend\out`
- `.pytest_cache`
- repo-local pytest temp folders
- `__pycache__`
- generated SQLite DB files
- raw downloaded datasets
- `.env` or `.env.local`
