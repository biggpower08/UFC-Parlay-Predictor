# Development Setup

This project is maintained primarily on Windows in `C:\dev\mma-ai`.

## Python

Recommended local target:

- Python 3.14
- External venv: `C:\venvs\mma-ai`
- Env var: `MMA_AI_PYTHON=C:\venvs\mma-ai\Scripts\python.exe`

Fallback:

- Python 3.13 can be used if a package does not yet support Python 3.14 on a specific machine.

Setup:

```powershell
cd C:\dev\mma-ai

$BasePython = "C:\Program Files\Python314\python.exe"
& $BasePython --version
& $BasePython -m venv C:\venvs\mma-ai

[Environment]::SetEnvironmentVariable("MMA_AI_PYTHON", "C:\venvs\mma-ai\Scripts\python.exe", "User")
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"

& $env:MMA_AI_PYTHON -m pip install --upgrade pip
& $env:MMA_AI_PYTHON -m pip install -r requirements.txt
& $env:MMA_AI_PYTHON -m pip install -r requirements-dev.txt
```

Run tests with a temp folder outside the repo:

```powershell
$TempTestDir = "$env:TEMP\mma_ai_pytest_$([guid]::NewGuid().ToString())"
& $env:MMA_AI_PYTHON -m pytest ufc_predictor\tests -q -p no:cacheprovider --basetemp $TempTestDir
```

## Frontend

```powershell
cd C:\dev\mma-ai\app\frontend
npm ci
npm run build
```

If PowerShell blocks the npm wrapper, use:

```powershell
& "C:\Program Files\nodejs\node.exe" node_modules\next\dist\bin\next build
```

## Generated Files

Do not commit virtual environments, frontend build output, local pytest temp folders, generated SQLite databases, raw imported datasets, or secrets.
