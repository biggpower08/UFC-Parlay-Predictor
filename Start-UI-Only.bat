@echo off
setlocal

set ROOT=%~dp0
set UI=%ROOT%app\frontend
set NPM=C:\Program Files\nodejs\npm.cmd

if not exist "%NPM%" (
  set NPM=npm
)

start "UFC Predictor UI" cmd /k "cd /d "%UI%" && "%NPM%" run dev -- --host 127.0.0.1"
timeout /t 4 /nobreak >nul
start http://localhost:5173

endlocal
