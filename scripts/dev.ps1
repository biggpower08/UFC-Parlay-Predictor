$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$frontend = Join-Path $root "app\frontend"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; python -m uvicorn ufc_predictor.api.app:app --host 127.0.0.1 --port 8000"
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontend'; npm run dev"
Start-Sleep -Seconds 4
Start-Process "http://localhost:5173"
