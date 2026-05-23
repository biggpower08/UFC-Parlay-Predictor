$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ui = Join-Path $root "app\frontend"
$nodeModules = Join-Path $ui "node_modules"

Set-Location $root
Write-Host "Checking Python packages..."
python -m pip install -r requirements.txt --disable-pip-version-check

Write-Host "Checking Playwright browser support..."
python -m playwright install chromium

Set-Location $ui
if (Test-Path $nodeModules) {
    Write-Host "Node packages already installed. Skipping npm install."
} else {
    Write-Host "Installing Node packages..."
    npm install
}

Write-Host "Building installable PWA..."
npm run build

Write-Host ""
Write-Host "PWA build complete. For real users, deploy this folder to Vercel."
