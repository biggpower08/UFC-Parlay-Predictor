$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$frontend = Join-Path $root "app\frontend"
$externalPython = "C:\venvs\mma-ai\Scripts\python.exe"
$python = if ($env:MMA_AI_PYTHON) {
    $env:MMA_AI_PYTHON
} elseif (Test-Path $externalPython) {
    $externalPython
} else {
    Join-Path $root ".venv\Scripts\python.exe"
}

if (-not (Test-Path $python)) {
    throw "Python executable was not found. Run .\scripts\dev_setup.ps1 or set MMA_AI_PYTHON."
}

Write-Host "Using Python: $python"
& $python --version
if ($LASTEXITCODE -ne 0) {
    throw "Python is not executable: $python"
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; & '$python' -m uvicorn ufc_predictor.api.app:app --host 127.0.0.1 --port 8000"
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontend'; npm run dev"
Start-Sleep -Seconds 4
Start-Process "http://localhost:5173"
