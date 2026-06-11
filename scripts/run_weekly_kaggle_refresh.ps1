$ErrorActionPreference = "Stop"

$RepoRoot = "C:\dev\mma-ai"
$PythonExe = if ($env:MMA_AI_PYTHON) { $env:MMA_AI_PYTHON } else { "C:\venvs\mma-ai\Scripts\python.exe" }
$LogDir = Join-Path $RepoRoot "logs\kaggle_refresh"
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogPath = Join-Path $LogDir "kaggle_refresh_$Stamp.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
Set-Location $RepoRoot
$env:MMA_AI_PYTHON = $PythonExe

function Invoke-Logged {
    param([string]$Label, [scriptblock]$Command)
    "[$(Get-Date -Format o)] START $Label" | Tee-Object -FilePath $LogPath -Append
    & $Command 2>&1 | Tee-Object -FilePath $LogPath -Append
    if ($LASTEXITCODE -ne 0) {
        "[$(Get-Date -Format o)] FAILED $Label exit=$LASTEXITCODE" | Tee-Object -FilePath $LogPath -Append
        exit $LASTEXITCODE
    }
    "[$(Get-Date -Format o)] OK $Label" | Tee-Object -FilePath $LogPath -Append
}

Invoke-Logged "Python version" { & $PythonExe --version }
Invoke-Logged "Refresh Kaggle datasets" { & $PythonExe scripts\refresh_kaggle_datasets.py --all --skip-existing --write-summary }
Invoke-Logged "Audit Kaggle odds timestamps" { & $PythonExe scripts\audit_kaggle_odds_timestamps.py }

$ManifestPath = Join-Path $RepoRoot "data\imports\kaggle\_download_manifest.json"
$Changed = $false
if (Test-Path $ManifestPath) {
    try {
        $Manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
        $Changed = [bool]$Manifest.changed
    } catch {
        "[$(Get-Date -Format o)] Could not parse download manifest: $_" | Tee-Object -FilePath $LogPath -Append
    }
}

if ($Changed) {
    Invoke-Logged "Preprocess imported datasets" { & $PythonExe scripts\preprocess_imported_datasets.py --input-root data\imports --all --write-summary }
} else {
    "[$(Get-Date -Format o)] No new downloads detected; preprocess skipped." | Tee-Object -FilePath $LogPath -Append
}

"[$(Get-Date -Format o)] Weekly Kaggle refresh complete. Log: $LogPath" | Tee-Object -FilePath $LogPath -Append
