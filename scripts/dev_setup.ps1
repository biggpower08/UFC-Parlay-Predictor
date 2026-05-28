param(
    [string]$PythonCommand = "py -3.13"
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

$DefaultVenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$PythonExe = if ($env:MMA_AI_PYTHON) { $env:MMA_AI_PYTHON } else { $DefaultVenvPython }

function Invoke-Python {
    param([string[]]$Arguments)
    $parts = $PythonCommand -split " "
    $command = $parts[0]
    $prefixArgs = @()
    if ($parts.Length -gt 1) {
        $prefixArgs = $parts[1..($parts.Length - 1)] | Where-Object { $_ }
    }
    & $command @prefixArgs @Arguments
}

Write-Host "Checking Python..."
if ($env:MMA_AI_PYTHON) {
    Write-Host "Using MMA_AI_PYTHON: $PythonExe"
    if (-not (Test-Path $PythonExe)) {
        throw "MMA_AI_PYTHON points to a file that does not exist: $PythonExe"
    }
    & $PythonExe --version
    if ($LASTEXITCODE -ne 0) {
        throw "MMA_AI_PYTHON is not executable: $PythonExe"
    }
} else {
    Invoke-Python @("--version")
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: $PythonCommand"
    }
    Invoke-Python @("-c", "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 13) else 13)")
    if ($LASTEXITCODE -ne 0) {
        throw "Expected Python 3.13. Pass -PythonCommand with a Python 3.13 interpreter if needed."
    }

    if (-not (Test-Path $DefaultVenvPython)) {
        Write-Host "Creating .venv..."
        Invoke-Python @("-m", "venv", ".venv")
        if ($LASTEXITCODE -ne 0) {
            throw "Could not create .venv."
        }
    } else {
        Write-Host ".venv already exists."
    }
    $PythonExe = $DefaultVenvPython
    Write-Host "Using repo Python: $PythonExe"
    & $PythonExe --version
    if ($LASTEXITCODE -ne 0) {
        throw "Repo-local Python is not executable: $PythonExe"
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

Write-Host ""
Write-Host "Setup complete. No activation is required."
Write-Host "Python used: $PythonExe"
Write-Host "Run backend tests:"
Write-Host ".\scripts\dev_test_backend.ps1"
Write-Host ""
Write-Host "Run sync status:"
Write-Host "& `"$PythonExe`" scripts\sync_database.py --status"
