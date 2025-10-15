# NPM Check Script
Write-Host "NPM Troubleshooting Script for Windows" -ForegroundColor Magenta
Write-Host "=====================================" -ForegroundColor Magenta

Write-Host "Checking system requirements..." -ForegroundColor Cyan

$nodeVersion = node --version 2>$null
if ($nodeVersion) {
    Write-Host "✓ Node.js version: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Node.js not found" -ForegroundColor Red
    exit 1
}

$npmVersion = npm --version 2>$null
if ($npmVersion) {
    Write-Host "✓ NPM version: $npmVersion" -ForegroundColor Green
} else {
    Write-Host "✗ NPM not found" -ForegroundColor Red
    exit 1
}

Write-Host "System check completed!" -ForegroundColor Green
