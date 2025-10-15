# NPM Troubleshooting Script for Windows
param(
    [switch]$DryRun,
    [switch]$CheckOnly,
    [string]$Strategy = "standard"
)

Write-Host "NPM Troubleshooting Script for Windows" -ForegroundColor Magenta
Write-Host "=====================================" -ForegroundColor Magenta

if ($DryRun) {
    Write-Host "DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
}

# Check system requirements
Write-Host "Checking system requirements..." -ForegroundColor Cyan

$nodeVersion = node --version 2>$null
if ($nodeVersion) {
    Write-Host "Node.js version: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "Node.js not found or not working" -ForegroundColor Red
    exit 1
}

$npmVersion = npm --version 2>$null
if ($npmVersion) {
    Write-Host "NPM version: $npmVersion" -ForegroundColor Green
} else {
    Write-Host "NPM not found or not working" -ForegroundColor Red
    exit 1
}

if ($CheckOnly) {
    Write-Host "Check-only mode - stopping after system check" -ForegroundColor Cyan
    exit 0
}

# Check for running Node processes
Write-Host "Checking for running Node.js processes..." -ForegroundColor Cyan
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host "Found $($nodeProcesses.Count) Node.js process(es) running" -ForegroundColor Yellow
    if (-not $DryRun) {
        $nodeProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
        Write-Host "Stopped Node.js processes" -ForegroundColor Green
    } else {
        Write-Host "Would stop Node.js processes (dry run)" -ForegroundColor Cyan
    }
} else {
    Write-Host "No Node.js processes found" -ForegroundColor Green
}

# Clean npm cache
Write-Host "Clearing npm cache..." -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "Would clear npm cache (dry run)" -ForegroundColor Cyan
} else {
    npm cache clean --force 2>$null
    Write-Host "NPM cache cleared" -ForegroundColor Green
}

# Remove node_modules and package-lock.json
Write-Host "Removing node_modules and package-lock.json..." -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "Would remove node_modules and package-lock.json (dry run)" -ForegroundColor Cyan
} else {
    if (Test-Path "node_modules") {
        Remove-Item -Path "node_modules" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Removed node_modules directory" -ForegroundColor Green
    }
    
    if (Test-Path "package-lock.json") {
        Remove-Item -Path "package-lock.json" -Force -ErrorAction SilentlyContinue
        Write-Host "Removed package-lock.json" -ForegroundColor Green
    }
    
    if (Test-Path ".npm") {
        Remove-Item -Path ".npm" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Removed .npm directory" -ForegroundColor Green
    }
}

# Install dependencies
Write-Host "Installing dependencies with strategy: $Strategy" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "Would install dependencies with strategy: $Strategy (dry run)" -ForegroundColor Cyan
} else {
    switch ($Strategy) {
        "standard" { npm install }
        "force" { npm install --force }
        "legacy" { npm install --legacy-peer-deps }
        "force-legacy" { npm install --force --legacy-peer-deps }
        "ci" { npm ci }
        default { npm install }
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "Failed to install dependencies" -ForegroundColor Red
        Write-Host "Try different strategies:" -ForegroundColor Yellow
        Write-Host "  .\npm-fix-final.ps1 -Strategy force" -ForegroundColor Yellow
        Write-Host "  .\npm-fix-final.ps1 -Strategy legacy" -ForegroundColor Yellow
        Write-Host "  .\npm-fix-final.ps1 -Strategy force-legacy" -ForegroundColor Yellow
        exit 1
    }
}

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "Would verify installation (dry run)" -ForegroundColor Cyan
} else {
    $missingDeps = npm ls --depth=0 2>&1 | Select-String "UNMET DEPENDENCY"
    if ($missingDeps) {
        Write-Host "Found missing dependencies:" -ForegroundColor Yellow
        $missingDeps | ForEach-Object { Write-Host "  $($_.Line)" -ForegroundColor Yellow }
    } else {
        Write-Host "No missing dependencies found" -ForegroundColor Green
    }
    
    $extraneous = npm ls --depth=0 2>&1 | Select-String "extraneous"
    if ($extraneous) {
        Write-Host "Found extraneous packages:" -ForegroundColor Yellow
        $extraneous | ForEach-Object { Write-Host "  $($_.Line)" -ForegroundColor Yellow }
    }
    
    Write-Host "Installation verification completed" -ForegroundColor Green
}

Write-Host "NPM troubleshooting completed!" -ForegroundColor Green
Write-Host "You can now run: npm run dev" -ForegroundColor Cyan
