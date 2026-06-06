$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ui = Join-Path $root "app\frontend"
$externalPython = "C:\venvs\mma-ai\Scripts\python.exe"
$repoPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$python = if ($env:MMA_AI_PYTHON) {
    $env:MMA_AI_PYTHON
} elseif (Test-Path $externalPython) {
    $externalPython
} else {
    $repoPython
}

Write-Host "Using Python: $python"
& $python --version
if ($LASTEXITCODE -ne 0) {
    throw "Python is not executable: $python"
}
$npm = "C:\Program Files\nodejs\npm.cmd"

if (!(Test-Path $npm)) {
    $npm = "npm"
}

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; & '$python' -m uvicorn ufc_predictor.api.app:app --host 127.0.0.1 --port 8000"
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ui'; & '$npm' run dev"
Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"
