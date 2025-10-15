# NPM Troubleshooting Script for Windows
# This script helps diagnose and fix common npm installation issues on Windows

param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$CleanOnly,
    [switch]$ReinstallOnly,
    [switch]$CheckOnly,
    [string]$Strategy = "standard"
)

# Color functions for better output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠ $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" "Red"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ $Message" "Cyan"
}

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Kill any Node.js processes that might be locking files
function Stop-NodeProcesses {
    Write-Info "Checking for running Node.js processes..."
    
    $nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
    if ($nodeProcesses) {
        Write-Warning "Found $($nodeProcesses.Count) Node.js process(es) running"
        if (-not $DryRun) {
            try {
                $nodeProcesses | Stop-Process -Force
                Write-Success "Stopped Node.js processes"
            }
            catch {
                Write-Error "Failed to stop Node.js processes: $($_.Exception.Message)"
            }
        }
        else {
            Write-Info "Would stop Node.js processes (dry run)"
        }
    }
    else {
        Write-Success "No Node.js processes found"
    }
}

# Check for file locks
function Test-FileLocks {
    Write-Info "Checking for file locks in node_modules..."
    
    $lockedFiles = @()
    try {
        $nodeModulesPath = Join-Path $PWD "node_modules"
        if (Test-Path $nodeModulesPath) {
            $files = Get-ChildItem -Path $nodeModulesPath -Recurse -File -ErrorAction SilentlyContinue | Select-Object -First 100
            foreach ($file in $files) {
                try {
                    $stream = [System.IO.File]::Open($file.FullName, 'Open', 'ReadWrite', 'None')
                    $stream.Close()
                }
                catch {
                    $lockedFiles += $file.FullName
                }
            }
        }
    }
    catch {
        Write-Warning "Could not check all files for locks: $($_.Exception.Message)"
    }
    
    if ($lockedFiles.Count -gt 0) {
        Write-Warning "Found $($lockedFiles.Count) locked files"
        if ($DryRun) {
            Write-Info "Locked files would be handled (dry run)"
        }
    }
    else {
        Write-Success "No file locks detected"
    }
}

# Clean npm cache
function Clear-NpmCache {
    Write-Info "Clearing npm cache..."
    
    if ($DryRun) {
        Write-Info "Would clear npm cache (dry run)"
        return
    }
    
    try {
        npm cache clean --force
        Write-Success "NPM cache cleared"
    }
    catch {
        Write-Error "Failed to clear npm cache: $($_.Exception.Message)"
    }
}

# Remove node_modules and package-lock.json
function Remove-NodeModules {
    Write-Info "Removing node_modules and package-lock.json..."
    
    if ($DryRun) {
        Write-Info "Would remove node_modules and package-lock.json (dry run)"
        return
    }
    
    try {
        # Remove node_modules
        $nodeModulesPath = Join-Path $PWD "node_modules"
        if (Test-Path $nodeModulesPath) {
            Remove-Item -Path $nodeModulesPath -Recurse -Force
            Write-Success "Removed node_modules directory"
        }
        
        # Remove package-lock.json
        $lockFile = Join-Path $PWD "package-lock.json"
        if (Test-Path $lockFile) {
            Remove-Item -Path $lockFile -Force
            Write-Success "Removed package-lock.json"
        }
        
        # Remove .npm directory if it exists
        $npmDir = Join-Path $PWD ".npm"
        if (Test-Path $npmDir) {
            Remove-Item -Path $npmDir -Recurse -Force
            Write-Success "Removed .npm directory"
        }
        
    }
    catch {
        Write-Error "Failed to remove files: $($_.Exception.Message)"
        Write-Warning "You may need to run this script as Administrator"
    }
}

# Install dependencies with different strategies
function Install-Dependencies {
    param([string]$Strategy)
    
    Write-Info "Installing dependencies with strategy: $Strategy"
    
    if ($DryRun) {
        Write-Info "Would install dependencies with strategy: $Strategy (dry run)"
        return
    }
    
    try {
        switch ($Strategy) {
            "standard" {
                npm install
            }
            "force" {
                npm install --force
            }
            "legacy" {
                npm install --legacy-peer-deps
            }
            "force-legacy" {
                npm install --force --legacy-peer-deps
            }
            "ci" {
                npm ci
            }
            default {
                npm install
            }
        }
        Write-Success "Dependencies installed successfully"
    }
    catch {
        Write-Error "Failed to install dependencies: $($_.Exception.Message)"
        return $false
    }
    return $true
}

# Verify installation
function Test-Installation {
    Write-Info "Verifying installation..."
    
    if ($DryRun) {
        Write-Info "Would verify installation (dry run)"
        return
    }
    
    try {
        # Check for missing dependencies
        $missingDeps = npm ls --depth=0 2>&1 | Select-String "UNMET DEPENDENCY"
        if ($missingDeps) {
            Write-Warning "Found missing dependencies:"
            $missingDeps | ForEach-Object { Write-Warning "  $($_.Line)" }
            return $false
        }
        
        # Check for extraneous packages
        $extraneous = npm ls --depth=0 2>&1 | Select-String "extraneous"
        if ($extraneous) {
            Write-Warning "Found extraneous packages:"
            $extraneous | ForEach-Object { Write-Warning "  $($_.Line)" }
        }
        
        Write-Success "Installation verification completed"
        return $true
    }
    catch {
        Write-Error "Failed to verify installation: $($_.Exception.Message)"
        return $false
    }
}

# Check system requirements
function Test-SystemRequirements {
    Write-Info "Checking system requirements..."
    
    # Check Node.js version
    try {
        $nodeVersion = node --version
        Write-Success "Node.js version: $nodeVersion"
        
        # Check if version is supported
        $version = [version]($nodeVersion -replace 'v', '')
        if ($version -lt [version]"18.0.0") {
            Write-Warning "Node.js version $nodeVersion is older than recommended (18.0.0+)"
        }
    }
    catch {
        Write-Error "Node.js not found or not working"
        return $false
    }
    
    # Check npm version
    try {
        $npmVersion = npm --version
        Write-Success "NPM version: $npmVersion"
    }
    catch {
        Write-Error "NPM not found or not working"
        return $false
    }
    
    # Check available disk space
    $drive = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
    $freeSpaceGB = [math]::Round($drive.FreeSpace / 1GB, 2)
    Write-Info "Available disk space: $freeSpaceGB GB"
    
    if ($freeSpaceGB -lt 2) {
        Write-Warning "Low disk space warning: $freeSpaceGB GB available"
    }
    
    return $true
}

# Main execution
function Main {
    Write-ColorOutput "NPM Troubleshooting Script for Windows" "Magenta"
    Write-ColorOutput "=====================================" "Magenta"
    
    if ($DryRun) {
        Write-Warning "DRY RUN MODE - No changes will be made"
    }
    
    # Check if running as administrator
    if (-not (Test-Administrator)) {
        Write-Warning "Not running as Administrator. Some operations may fail."
        Write-Info "Consider running PowerShell as Administrator for better results."
    }
    
    # System requirements check
    if (-not (Test-SystemRequirements)) {
        Write-Error "System requirements check failed"
        return
    }
    
    if ($CheckOnly) {
        Write-Info "Check-only mode - stopping after system check"
        return
    }
    
    # Stop Node processes
    Stop-NodeProcesses
    
    # Check for file locks
    Test-FileLocks
    
    if ($CleanOnly) {
        Write-Info "Clean-only mode - stopping after cleanup"
        Remove-NodeModules
        Clear-NpmCache
        return
    }
    
    # Clean installation
    if (-not $ReinstallOnly) {
        Remove-NodeModules
        Clear-NpmCache
    }
    
    # Install dependencies
    $installSuccess = Install-Dependencies -Strategy $Strategy
    
    if ($installSuccess) {
        # Verify installation
        $verifySuccess = Test-Installation
        
        if ($verifySuccess) {
            Write-Success "NPM troubleshooting completed successfully!"
            Write-Info "You can now run: npm run dev"
        }
        else {
            Write-Warning "Installation completed but verification found issues"
            Write-Info "Try running with different strategy: -Strategy force-legacy"
        }
    }
    else {
        Write-Error "Installation failed. Try different strategies:"
        Write-Info "  .\npm-fix.ps1 -Strategy force"
        Write-Info "  .\npm-fix.ps1 -Strategy legacy"
        Write-Info "  .\npm-fix.ps1 -Strategy force-legacy"
    }
}

# Run main function
Main