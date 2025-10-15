#!/usr/bin/env python3
"""
MSI installer and distribution package builder for BOLT AI Neural Agent System
"""
import os
import sys
import shutil
import subprocess
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class InstallerBuilder:
    """MSI installer and distribution package builder"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.build_dir = project_root / "build"
        self.dist_dir = project_root / "dist-electron"
        self.installer_dir = project_root / "installer"
        
        # Create directories
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        self.installer_dir.mkdir(exist_ok=True)
        
        # Configuration
        self.app_name = "Bolt AI Crypto"
        self.app_version = "1.0.0"
        self.app_id = "com.boltai.crypto"
        self.company_name = "Bolt AI Team"
        self.description = "Advanced Cryptocurrency Neural AI Agent System"
        
        logger.info("Installer builder initialized")
    
    def build_frontend(self) -> bool:
        """Build React frontend"""
        logger.info("Building React frontend...")
        
        try:
            # Install dependencies
            subprocess.run(["npm", "ci"], cwd=self.project_root, check=True)
            
            # Build frontend
            subprocess.run(["npm", "run", "build"], cwd=self.project_root, check=True)
            
            logger.info("Frontend build completed")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Frontend build failed: {e}")
            return False
    
    def build_backend(self) -> bool:
        """Build FastAPI backend with PyInstaller"""
        logger.info("Building FastAPI backend...")
        
        try:
            backend_dir = self.project_root / "backend"
            
            # Install Python dependencies
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], cwd=backend_dir, check=True)
            
            # Build with PyInstaller
            subprocess.run([
                sys.executable, "-m", "PyInstaller",
                "build_backend.spec",
                "--distpath", str(self.project_root / "backend-dist"),
                "--workpath", str(self.build_dir / "pyinstaller_work")
            ], cwd=backend_dir, check=True)
            
            logger.info("Backend build completed")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Backend build failed: {e}")
            return False
    
    def build_electron_app(self) -> bool:
        """Build Electron application"""
        logger.info("Building Electron application...")
        
        try:
            # Build Electron app
            subprocess.run([
                "npm", "run", "build:electron"
            ], cwd=self.project_root, check=True)
            
            logger.info("Electron build completed")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Electron build failed: {e}")
            return False
    
    def create_msi_installer(self) -> bool:
        """Create MSI installer using electron-builder"""
        logger.info("Creating MSI installer...")
        
        try:
            # Build MSI installer
            subprocess.run([
                "npm", "run", "build:win"
            ], cwd=self.project_root, check=True)
            
            # Check if MSI was created
            msi_files = list(self.dist_dir.glob("*.msi"))
            if msi_files:
                logger.info(f"MSI installer created: {msi_files[0]}")
                return True
            else:
                logger.error("MSI installer not found")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"MSI installer creation failed: {e}")
            return False
    
    def create_portable_version(self) -> bool:
        """Create portable version"""
        logger.info("Creating portable version...")
        
        try:
            # Build portable version
            subprocess.run([
                "npm", "run", "build:portable"
            ], cwd=self.project_root, check=True)
            
            # Check if portable was created
            portable_files = list(self.dist_dir.glob("*portable*"))
            if portable_files:
                logger.info(f"Portable version created: {portable_files[0]}")
                return True
            else:
                logger.error("Portable version not found")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Portable version creation failed: {e}")
            return False
    
    def sign_executable(self, executable_path: Path, cert_path: str = None, cert_password: str = None) -> bool:
        """Sign Windows executable"""
        if not cert_path or not cert_password:
            logger.warning("Code signing certificate not provided, skipping signing")
            return True
        
        logger.info("Signing executable...")
        
        try:
            # Use signtool to sign the executable
            subprocess.run([
                "signtool", "sign",
                "/f", cert_path,
                "/p", cert_password,
                "/t", "http://timestamp.digicert.com",
                str(executable_path)
            ], check=True)
            
            logger.info("Executable signed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Code signing failed: {e}")
            return False
    
    def create_installer_script(self) -> bool:
        """Create installer script for advanced features"""
        logger.info("Creating installer script...")
        
        installer_script = self.installer_dir / "installer.ps1"
        
        script_content = f"""
# BOLT AI Neural Agent System Installer Script
# Version: {self.app_version}
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

param(
    [string]$InstallPath = "$env:ProgramFiles\\{self.company_name}\\{self.app_name}",
    [switch]$CreateDesktopShortcut = $true,
    [switch]$CreateStartMenuShortcut = $true,
    [switch]$RegisterFileAssociations = $true,
    [switch]$InstallService = $false
)

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {{
    Write-Error "This script requires administrator privileges. Please run as administrator."
    exit 1
}}

Write-Host "Installing {self.app_name} v{self.app_version}..." -ForegroundColor Green

# Create installation directory
if (-not (Test-Path $InstallPath)) {{
    New-Item -ItemType Directory -Path $InstallPath -Force
    Write-Host "Created installation directory: $InstallPath" -ForegroundColor Yellow
}}

# Copy application files
$SourceDir = "."
$Files = @(
    "bolt-ai-crypto.exe",
    "backend\\boltai_backend.exe",
    "config\\*",
    "models\\*"
)

foreach ($File in $Files) {{
    if (Test-Path $File) {{
        if ((Get-Item $File).PSIsContainer) {{
            Copy-Item -Path $File -Destination $InstallPath -Recurse -Force
        }} else {{
            Copy-Item -Path $File -Destination $InstallPath -Force
        }}
        Write-Host "Copied: $File" -ForegroundColor Cyan
    }}
}}

# Create desktop shortcut
if ($CreateDesktopShortcut) {{
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\\Desktop\\{self.app_name}.lnk")
    $Shortcut.TargetPath = "$InstallPath\\bolt-ai-crypto.exe"
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.Description = "{self.description}"
    $Shortcut.Save()
    Write-Host "Created desktop shortcut" -ForegroundColor Green
}}

# Create start menu shortcut
if ($CreateStartMenuShortcut) {{
    $StartMenuPath = "$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\{self.company_name}"
    if (-not (Test-Path $StartMenuPath)) {{
        New-Item -ItemType Directory -Path $StartMenuPath -Force
    }}
    
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$StartMenuPath\\{self.app_name}.lnk")
    $Shortcut.TargetPath = "$InstallPath\\bolt-ai-crypto.exe"
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.Description = "{self.description}"
    $Shortcut.Save()
    Write-Host "Created start menu shortcut" -ForegroundColor Green
}}

# Register file associations
if ($RegisterFileAssociations) {{
    $RegPath = "HKCR:\\Applications\\{self.app_name}.exe\\shell\\open\\command"
    $RegValue = "`"$InstallPath\\bolt-ai-crypto.exe`" `"%1`""
    
    New-Item -Path $RegPath -Force | Out-Null
    Set-ItemProperty -Path $RegPath -Name "(Default)" -Value $RegValue
    
    Write-Host "Registered file associations" -ForegroundColor Green
}}

# Install Windows service (optional)
if ($InstallService) {{
    $ServiceName = "{self.app_name}Service"
    $ServiceDisplayName = "{self.app_name} Background Service"
    $ServiceDescription = "Background service for {self.app_name}"
    
    # Create service
    New-Service -Name $ServiceName -DisplayName $ServiceDisplayName -Description $ServiceDescription -BinaryPathName "$InstallPath\\bolt-ai-crypto.exe --service" -StartupType Automatic
    
    Write-Host "Installed Windows service: $ServiceName" -ForegroundColor Green
}}

# Create uninstaller
$UninstallerPath = "$InstallPath\\uninstall.ps1"
$UninstallerContent = @"
# {self.app_name} Uninstaller
# Version: {self.app_version}

param(
    [switch]$RemoveData = $false
)

Write-Host "Uninstalling {self.app_name}..." -ForegroundColor Red

# Stop service if running
try {{
    Stop-Service -Name "{self.app_name}Service" -Force -ErrorAction SilentlyContinue
    Remove-Service -Name "{self.app_name}Service" -ErrorAction SilentlyContinue
}} catch {{}}

# Remove shortcuts
Remove-Item "$env:USERPROFILE\\Desktop\\{self.app_name}.lnk" -ErrorAction SilentlyContinue
Remove-Item "$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\{self.company_name}\\{self.app_name}.lnk" -ErrorAction SilentlyContinue

# Remove file associations
Remove-Item "HKCR:\\Applications\\{self.app_name}.exe" -Recurse -ErrorAction SilentlyContinue

# Remove installation directory
if (Test-Path "$InstallPath") {{
    Remove-Item -Path "$InstallPath" -Recurse -Force
    Write-Host "Removed installation directory: $InstallPath" -ForegroundColor Yellow
}}

# Remove user data if requested
if ($RemoveData) {{
    $UserDataPath = "$env:APPDATA\\{self.app_name}"
    if (Test-Path $UserDataPath) {{
        Remove-Item -Path $UserDataPath -Recurse -Force
        Write-Host "Removed user data: $UserDataPath" -ForegroundColor Yellow
    }}
}}

Write-Host "Uninstallation completed." -ForegroundColor Green
"@

    Set-Content -Path $UninstallerPath -Value $UninstallerContent
    Write-Host "Created uninstaller: $UninstallerPath" -ForegroundColor Green

Write-Host "Installation completed successfully!" -ForegroundColor Green
Write-Host "Installation path: $InstallPath" -ForegroundColor Cyan
Write-Host "To uninstall, run: $InstallPath\\uninstall.ps1" -ForegroundColor Yellow
"""
        
        try:
            with open(installer_script, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            logger.info(f"Installer script created: {installer_script}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create installer script: {e}")
            return False
    
    def create_auto_update_config(self) -> bool:
        """Create auto-update configuration"""
        logger.info("Creating auto-update configuration...")
        
        update_config = {
            "updater": {
                "provider": "generic",
                "url": "https://updates.boltai.crypto/releases",
                "channel": "latest",
                "autoDownload": True,
                "autoInstallOnAppQuit": True,
                "allowDowngrade": False,
                "allowPrerelease": False
            },
            "notifications": {
                "enabled": True,
                "showReleaseNotes": True,
                "showUpdateAvailable": True,
                "showUpdateDownloaded": True,
                "showUpdateInstalled": True
            },
            "security": {
                "verifySignature": True,
                "requireSignature": True,
                "signatureAlgorithm": "sha256"
            }
        }
        
        config_file = self.installer_dir / "update-config.json"
        
        try:
            with open(config_file, 'w') as f:
                json.dump(update_config, f, indent=2)
            
            logger.info(f"Auto-update configuration created: {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create auto-update config: {e}")
            return False
    
    def create_distribution_package(self) -> bool:
        """Create complete distribution package"""
        logger.info("Creating distribution package...")
        
        try:
            # Create distribution directory
            dist_package_dir = self.project_root / "distribution"
            dist_package_dir.mkdir(exist_ok=True)
            
            # Copy MSI installer
            msi_files = list(self.dist_dir.glob("*.msi"))
            if msi_files:
                shutil.copy2(msi_files[0], dist_package_dir)
                logger.info(f"Copied MSI installer: {msi_files[0].name}")
            
            # Copy portable version
            portable_files = list(self.dist_dir.glob("*portable*"))
            if portable_files:
                shutil.copy2(portable_files[0], dist_package_dir)
                logger.info(f"Copied portable version: {portable_files[0].name}")
            
            # Copy installer script
            installer_script = self.installer_dir / "installer.ps1"
            if installer_script.exists():
                shutil.copy2(installer_script, dist_package_dir)
                logger.info("Copied installer script")
            
            # Copy auto-update config
            update_config = self.installer_dir / "update-config.json"
            if update_config.exists():
                shutil.copy2(update_config, dist_package_dir)
                logger.info("Copied auto-update configuration")
            
            # Create README
            readme_content = f"""
# {self.app_name} v{self.app_version}

{self.description}

## Installation Options

### 1. MSI Installer (Recommended)
- Double-click `{self.app_name} Setup {self.app_version}.msi`
- Follow the installation wizard
- Automatically creates shortcuts and file associations

### 2. Portable Version
- Extract `{self.app_name} Portable {self.app_version}.zip` to desired location
- Run `bolt-ai-crypto.exe`
- No installation required

### 3. Advanced Installation
- Run `installer.ps1` as administrator for advanced options
- Supports custom installation paths
- Optional Windows service installation

## System Requirements

- Windows 10/11 (64-bit)
- 4GB RAM minimum, 8GB recommended
- 2GB free disk space
- Internet connection for market data

## Auto-Update

The application includes automatic update functionality:
- Checks for updates on startup
- Downloads updates in background
- Installs updates on application restart
- Verifies update signatures for security

## Support

For technical support and documentation, visit:
https://docs.boltai.crypto

## License

Copyright © 2025 {self.company_name}
All rights reserved.

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            readme_file = dist_package_dir / "README.txt"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            logger.info(f"Distribution package created: {dist_package_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create distribution package: {e}")
            return False
    
    def build_all(self, sign_cert: str = None, sign_password: str = None) -> bool:
        """Build complete installer package"""
        logger.info("Starting complete installer build...")
        
        try:
            # Build frontend
            if not self.build_frontend():
                return False
            
            # Build backend
            if not self.build_backend():
                return False
            
            # Build Electron app
            if not self.build_electron_app():
                return False
            
            # Create MSI installer
            if not self.create_msi_installer():
                return False
            
            # Create portable version
            if not self.create_portable_version():
                return False
            
            # Sign executables if certificate provided
            if sign_cert and sign_password:
                exe_files = list(self.dist_dir.glob("*.exe"))
                for exe_file in exe_files:
                    self.sign_executable(exe_file, sign_cert, sign_password)
            
            # Create installer script
            if not self.create_installer_script():
                return False
            
            # Create auto-update config
            if not self.create_auto_update_config():
                return False
            
            # Create distribution package
            if not self.create_distribution_package():
                return False
            
            logger.info("Complete installer build finished successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Installer build failed: {e}")
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Build BOLT AI Neural Agent System installer")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root directory")
    parser.add_argument("--sign-cert", help="Path to code signing certificate")
    parser.add_argument("--sign-password", help="Certificate password")
    parser.add_argument("--msi-only", action="store_true", help="Build only MSI installer")
    parser.add_argument("--portable-only", action="store_true", help="Build only portable version")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    builder = InstallerBuilder(args.project_root)
    
    if args.msi_only:
        success = builder.create_msi_installer()
    elif args.portable_only:
        success = builder.create_portable_version()
    else:
        success = builder.build_all(args.sign_cert, args.sign_password)
    
    if success:
        print("Installer build completed successfully!")
        sys.exit(0)
    else:
        print("Installer build failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()