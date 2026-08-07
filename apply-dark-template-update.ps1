$ErrorActionPreference = "Stop"
Write-Host "[history-card-factory] Dark template update" -ForegroundColor Cyan

if (-not (Test-Path ".\remotion\package.json")) {
  throw "Run this script from the history-card-factory root folder."
}

Write-Host "1/2 Installing updated Remotion dependencies..." -ForegroundColor Yellow
npm --prefix remotion install
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "2/2 Opening Remotion preview..." -ForegroundColor Yellow
npm run preview
