$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

if ($RepoRoot.Path -like "*OneDrive*") {
    throw "Do not run tests from OneDrive. Use C:\dev\mma-ai."
}

$ExternalVenvPython = "C:\venvs\mma-ai\Scripts\python.exe"
$PythonExe = if ($env:MMA_AI_PYTHON) {
    $env:MMA_AI_PYTHON
} elseif (Test-Path $ExternalVenvPython) {
    $ExternalVenvPython
} else {
    Join-Path $RepoRoot ".venv\Scripts\python.exe"
}
Write-Host "Using Python: $PythonExe"
if (-not (Test-Path $PythonExe)) {
    throw "Python executable was not found. Run .\scripts\dev_setup.ps1 or set MMA_AI_PYTHON."
}

& $PythonExe --version
if ($LASTEXITCODE -ne 0) {
    throw "Python is not executable: $PythonExe"
}

$TempTestDir = Join-Path $env:TEMP ("mma_ai_pytest_" + [guid]::NewGuid().ToString())
Write-Host "Using pytest temp dir: $TempTestDir"
& $PythonExe -m pytest ufc_predictor\tests -q -p no:cacheprovider --basetemp $TempTestDir
