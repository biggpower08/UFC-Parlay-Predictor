param(
    [string]$BasePython = "C:\Program Files\Python314\python.exe"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

if ($RepoRoot.Path -ne "C:\dev\mma-ai") {
    Write-Warning "Expected repo path is C:\dev\mma-ai. Current path is $($RepoRoot.Path)."
}

if ($RepoRoot.Path -like "*OneDrive*") {
    throw "Do not run setup from OneDrive. Use C:\dev\mma-ai."
}

if (-not (Test-Path "requirements.txt")) {
    throw "requirements.txt was not found. Run this script from the mma-ai repo."
}

$ExternalVenvRoot = "C:\venvs\mma-ai"
$ExternalVenvPython = Join-Path $ExternalVenvRoot "Scripts\python.exe"
$DefaultVenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$PythonExe = if ($env:MMA_AI_PYTHON) {
    $env:MMA_AI_PYTHON
} elseif (Test-Path $ExternalVenvPython) {
    $ExternalVenvPython
} else {
    $DefaultVenvPython
}

Write-Host "Checking Python..."
if ($env:MMA_AI_PYTHON -or (Test-Path $ExternalVenvPython)) {
    Write-Host "Using Python: $PythonExe"
    if (-not (Test-Path $PythonExe)) {
        throw "Python executable does not exist: $PythonExe"
    }
    & $PythonExe --version
    if ($LASTEXITCODE -ne 0) {
        throw "Python is not executable: $PythonExe"
    }
} else {
    if (-not (Test-Path $BasePython)) {
        throw "Base Python was not found: $BasePython. Install Python 3.14 for all users, or pass -BasePython with a known Python 3.14 path. Python 3.13 is the fallback if a dependency blocks 3.14."
    }

    Write-Host "Using base Python: $BasePython"
    & $BasePython --version
    if ($LASTEXITCODE -ne 0) {
        throw "Base Python failed: $BasePython"
    }

    & $BasePython -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 14) else 14)"
    if ($LASTEXITCODE -ne 0) {
        throw "Expected Python 3.14. Pass -BasePython with a Python 3.14 interpreter. Use Python 3.13 only as a compatibility fallback."
    }

    if (-not (Test-Path $ExternalVenvPython)) {
        Write-Host "Creating external venv at $ExternalVenvRoot..."
        $venvParent = Split-Path -Parent $ExternalVenvRoot
        if (-not (Test-Path $venvParent)) {
            New-Item -ItemType Directory -Path $venvParent | Out-Null
        }
        & $BasePython -m venv $ExternalVenvRoot
        if ($LASTEXITCODE -ne 0) {
            throw "Could not create external venv at $ExternalVenvRoot."
        }
    } else {
        Write-Host "External venv already exists."
    }
    $PythonExe = $ExternalVenvPython
    Write-Host "Using project Python: $PythonExe"
    & $PythonExe --version
    if ($LASTEXITCODE -ne 0) {
        throw "Project Python is not executable: $PythonExe"
    }
}

Write-Host "Upgrading pip..."
& $PythonExe -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "pip upgrade failed."
}

Write-Host "Installing requirements..."
& $PythonExe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw "requirements installation failed."
}

if (Test-Path "requirements-dev.txt") {
    Write-Host "Installing development requirements..."
    & $PythonExe -m pip install -r requirements-dev.txt
    if ($LASTEXITCODE -ne 0) {
        throw "development requirements installation failed."
    }
}

Write-Host ""
Write-Host "Setup complete. No activation is required."
Write-Host "Python used: $PythonExe"
Write-Host "To persist this Python path for future shells:"
Write-Host "[Environment]::SetEnvironmentVariable('MMA_AI_PYTHON', '$PythonExe', 'User')"
Write-Host "Run backend tests:"
Write-Host ".\scripts\dev_test_backend.ps1"
Write-Host ""
Write-Host "Run sync status:"
Write-Host "& `"$PythonExe`" scripts\sync_database.py --status"
