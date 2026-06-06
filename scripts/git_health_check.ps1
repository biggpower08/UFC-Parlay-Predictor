$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

Write-Host "Repo: $($RepoRoot.Path)"
if ($RepoRoot.Path -like "*OneDrive*") {
    Write-Warning "This repo is inside OneDrive. Use C:\dev\mma-ai to avoid Git and npm permission problems."
}

git rev-parse --show-toplevel | Out-Null

$LockPath = Join-Path $RepoRoot ".git\index.lock"
if (Test-Path $LockPath) {
    $lock = Get-Item $LockPath
    $gitProcess = Get-Process git -ErrorAction SilentlyContinue
    $ageMinutes = ((Get-Date) - $lock.LastWriteTime).TotalMinutes
    if (-not $gitProcess -and $ageMinutes -gt 10) {
        Write-Warning "Removing stale .git\index.lock older than 10 minutes."
        Remove-Item -Force $LockPath
    } else {
        Write-Warning ".git\index.lock exists and was not removed. Close Git tools or remove it manually if stale:"
        Write-Host "Remove-Item -Force .git\index.lock -ErrorAction SilentlyContinue"
    }
} else {
    Write-Host "No .git\index.lock file found."
}

Write-Host ""
Write-Host "Git status:"
git status --short

Write-Host ""
Write-Host "Generated folders/files that should usually stay uncommitted:"
$GeneratedPaths = @(
    ".venv*",
    "docs\.venv",
    "node_modules",
    "app\frontend\node_modules",
    "app\frontend\.next",
    "app\frontend\out",
    ".pytest_cache",
    "pytest_tmp_codex",
    ".mypy_cache",
    ".ruff_cache",
    "htmlcov",
    "__pycache__"
)
foreach ($path in $GeneratedPaths) {
    $matches = Resolve-Path -Path $path -ErrorAction SilentlyContinue
    foreach ($match in $matches) {
        Write-Host "  present: $($match.Path.Replace($RepoRoot.Path + '\', ''))"
    }
}

Write-Host ""
Write-Host "Manual Git flow:"
Write-Host "git status"
Write-Host "git add <files>"
Write-Host 'git commit -m "your message"'
Write-Host "git push"
