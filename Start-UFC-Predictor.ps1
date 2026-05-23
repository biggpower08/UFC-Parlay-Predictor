$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ui = Join-Path $root "app\frontend"
$python = "C:\Users\trish\AppData\Local\Programs\Python\Python313\python.exe"
$npm = "C:\Program Files\nodejs\npm.cmd"

if (!(Test-Path $python)) {
    $python = "python"
}

if (!(Test-Path $npm)) {
    $npm = "npm"
}

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; & '$python' -m uvicorn ufc_predictor.api.app:app --host 127.0.0.1 --port 8000"
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ui'; & '$npm' run dev"
Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"
