@echo off
setlocal

set ROOT=%~dp0
set UI=%ROOT%app\frontend
set NPM=C:\Program Files\nodejs\npm.cmd

if not exist "%NPM%" (
  set NPM=npm
)

echo Starting UFC Predictor backend...
start "UFC Predictor Backend" cmd /k "cd /d "%ROOT%" && python -m uvicorn ufc_predictor.api.app:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo Starting UFC Predictor UI...
start "UFC Predictor UI" cmd /k "cd /d "%UI%" && "%NPM%" run dev -- --host 127.0.0.1"

timeout /t 5 /nobreak >nul

start http://localhost:5173

endlocal
