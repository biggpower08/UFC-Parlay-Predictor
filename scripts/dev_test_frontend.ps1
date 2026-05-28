$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$FrontendRoot = Join-Path $RepoRoot "app\frontend"

if ($RepoRoot.Path -like "*OneDrive*") {
    throw "Do not run the frontend build from OneDrive. Use C:\dev\mma-ai."
}

if (-not (Test-Path (Join-Path $FrontendRoot "package.json"))) {
    throw "app\frontend\package.json was not found."
}

Set-Location $FrontendRoot

if (Test-Path "package-lock.json") {
    Write-Host "Installing frontend dependencies with npm ci..."
    npm ci
} else {
    Write-Host "Installing frontend dependencies with npm install..."
    npm install
}
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Running frontend production build..."
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Warning "npm run build failed. If this is a Windows npm wrapper or PATH access issue, try:"
    Write-Host '& "C:\Program Files\nodejs\node.exe" node_modules\next\dist\bin\next build'
    exit $LASTEXITCODE
}
