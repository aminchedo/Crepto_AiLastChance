#!/usr/bin/env python3
"""
Auto-update service for BOLT AI Neural Agent System
"""
import os
import sys
import json
import requests
import hashlib
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
import zipfile
import semver

logger = logging.getLogger(__name__)


class AutoUpdateService:
    """Auto-update service for BOLT AI system"""
    
    def __init__(self, config_file: Path = None):
        self.config_file = config_file or Path("update-config.json")
        self.config = self.load_config()
        
        # Update service configuration
        self.update_url = self.config.get("updater", {}).get("url", "https://updates.boltai.crypto/releases")
        self.channel = self.config.get("updater", {}).get("channel", "latest")
        self.auto_download = self.config.get("updater", {}).get("autoDownload", True)
        self.auto_install = self.config.get("updater", {}).get("autoInstallOnAppQuit", True)
        self.verify_signature = self.config.get("security", {}).get("verifySignature", True)
        
        # Current version
        self.current_version = self.get_current_version()
        
        logger.info(f"Auto-update service initialized, current version: {self.current_version}")
    
    def load_config(self) -> Dict:
        """Load update configuration"""
        if not self.config_file.exists():
            return self.get_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
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
    
    def get_current_version(self) -> str:
        """Get current application version"""
        try:
            # Try to read from package.json
            package_json = Path("package.json")
            if package_json.exists():
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    return data.get("version", "1.0.0")
            
            # Try to read from version file
            version_file = Path("version.txt")
            if version_file.exists():
                return version_file.read_text().strip()
            
            # Default version
            return "1.0.0"
            
        except Exception as e:
            logger.error(f"Failed to get current version: {e}")
            return "1.0.0"
    
    def check_for_updates(self) -> Optional[Dict]:
        """Check for available updates"""
        try:
            logger.info("Checking for updates...")
            
            # Get update manifest
            manifest_url = f"{self.update_url}/manifest.json"
            response = requests.get(manifest_url, timeout=30)
            response.raise_for_status()
            
            manifest = response.json()
            
            # Find latest version for current channel
            latest_version = None
            latest_release = None
            
            for release in manifest.get("releases", []):
                if release.get("channel") == self.channel:
                    if latest_version is None or semver.compare(release["version"], latest_version) > 0:
                        latest_version = release["version"]
                        latest_release = release
            
            if not latest_release:
                logger.info("No releases found for current channel")
                return None
            
            # Check if update is available
            if semver.compare(latest_version, self.current_version) <= 0:
                logger.info(f"Already up to date: {self.current_version}")
                return None
            
            logger.info(f"Update available: {self.current_version} -> {latest_version}")
            return latest_release
            
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
            return None
    
    def download_update(self, release: Dict) -> Optional[Path]:
        """Download update package"""
        try:
            logger.info(f"Downloading update: {release['version']}")
            
            # Get download URL
            download_url = release.get("downloadUrl")
            if not download_url:
                logger.error("No download URL in release")
                return None
            
            # Create temporary directory
            temp_dir = Path(tempfile.mkdtemp())
            update_file = temp_dir / f"update-{release['version']}.zip"
            
            # Download update
            response = requests.get(download_url, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(update_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            logger.info(f"Download progress: {progress:.1f}%")
            
            # Verify file integrity
            if not self.verify_update_integrity(update_file, release):
                logger.error("Update integrity verification failed")
                shutil.rmtree(temp_dir)
                return None
            
            logger.info(f"Update downloaded: {update_file}")
            return update_file
            
        except Exception as e:
            logger.error(f"Failed to download update: {e}")
            return None
    
    def verify_update_integrity(self, update_file: Path, release: Dict) -> bool:
        """Verify update file integrity"""
        try:
            # Check file size
            expected_size = release.get("size")
            if expected_size and update_file.stat().st_size != expected_size:
                logger.error(f"File size mismatch: expected {expected_size}, got {update_file.stat().st_size}")
                return False
            
            # Check checksum
            expected_checksum = release.get("checksum")
            if expected_checksum:
                actual_checksum = self.calculate_checksum(update_file)
                if actual_checksum != expected_checksum:
                    logger.error(f"Checksum mismatch: expected {expected_checksum}, got {actual_checksum}")
                    return False
            
            # Verify signature if enabled
            if self.verify_signature:
                signature = release.get("signature")
                if signature and not self.verify_signature(update_file, signature):
                    logger.error("Signature verification failed")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Integrity verification failed: {e}")
            return False
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def verify_signature(self, file_path: Path, signature: str) -> bool:
        """Verify file signature"""
        try:
            # This would typically use a cryptographic library to verify signatures
            # For now, we'll implement a placeholder
            logger.info("Signature verification not implemented")
            return True
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def install_update(self, update_file: Path) -> bool:
        """Install downloaded update"""
        try:
            logger.info("Installing update...")
            
            # Create backup of current installation
            backup_dir = Path("backup") / datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup current files
            self.backup_current_installation(backup_dir)
            
            # Extract update
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                zip_ref.extractall(".")
            
            # Run post-installation script if present
            post_install_script = Path("post-install.bat")
            if post_install_script.exists():
                subprocess.run([str(post_install_script)], check=True)
            
            logger.info("Update installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install update: {e}")
            return False
    
    def backup_current_installation(self, backup_dir: Path):
        """Backup current installation"""
        try:
            # Files to backup
            files_to_backup = [
                "bolt-ai-crypto.exe",
                "backend/boltai_backend.exe",
                "config/",
                "models/",
                "logs/"
            ]
            
            for item in files_to_backup:
                source = Path(item)
                if source.exists():
                    if source.is_dir():
                        shutil.copytree(source, backup_dir / source.name)
                    else:
                        shutil.copy2(source, backup_dir / source.name)
            
            logger.info(f"Backup created: {backup_dir}")
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
    
    def rollback_update(self, backup_dir: Path) -> bool:
        """Rollback to previous version"""
        try:
            logger.info("Rolling back update...")
            
            # Restore files from backup
            for item in backup_dir.iterdir():
                if item.is_dir():
                    shutil.copytree(item, Path(item.name), dirs_exist_ok=True)
                else:
                    shutil.copy2(item, Path(item.name))
            
            logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback: {e}")
            return False
    
    def notify_update_available(self, release: Dict):
        """Notify user about available update"""
        try:
            if not self.config.get("notifications", {}).get("showUpdateAvailable", True):
                return
            
            # This would typically show a system notification
            # For now, we'll log the information
            logger.info(f"Update available: {release['version']}")
            logger.info(f"Release notes: {release.get('releaseNotes', 'No release notes available')}")
            
        except Exception as e:
            logger.error(f"Failed to notify about update: {e}")
    
    def notify_update_downloaded(self, release: Dict):
        """Notify user that update has been downloaded"""
        try:
            if not self.config.get("notifications", {}).get("showUpdateDownloaded", True):
                return
            
            logger.info(f"Update downloaded: {release['version']}")
            
        except Exception as e:
            logger.error(f"Failed to notify about download: {e}")
    
    def notify_update_installed(self, release: Dict):
        """Notify user that update has been installed"""
        try:
            if not self.config.get("notifications", {}).get("showUpdateInstalled", True):
                return
            
            logger.info(f"Update installed: {release['version']}")
            
        except Exception as e:
            logger.error(f"Failed to notify about installation: {e}")
    
    def run_update_check(self) -> bool:
        """Run complete update check and installation process"""
        try:
            # Check for updates
            release = self.check_for_updates()
            if not release:
                return True
            
            # Notify about available update
            self.notify_update_available(release)
            
            # Download update if auto-download is enabled
            if self.auto_download:
                update_file = self.download_update(release)
                if not update_file:
                    return False
                
                # Notify about downloaded update
                self.notify_update_downloaded(release)
                
                # Install update if auto-install is enabled
                if self.auto_install:
                    success = self.install_update(update_file)
                    if success:
                        self.notify_update_installed(release)
                        return True
                    else:
                        logger.error("Update installation failed")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Update check failed: {e}")
            return False
    
    def get_update_status(self) -> Dict:
        """Get current update status"""
        try:
            release = self.check_for_updates()
            
            status = {
                "current_version": self.current_version,
                "update_available": release is not None,
                "latest_version": release.get("version") if release else None,
                "release_notes": release.get("releaseNotes") if release else None,
                "last_check": datetime.now().isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get update status: {e}")
            return {
                "current_version": self.current_version,
                "update_available": False,
                "error": str(e)
            }


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BOLT AI Auto-Update Service")
    parser.add_argument("--config", type=Path, help="Update configuration file")
    parser.add_argument("--check-only", action="store_true", help="Only check for updates")
    parser.add_argument("--status", action="store_true", help="Show update status")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create update service
    update_service = AutoUpdateService(args.config)
    
    if args.status:
        # Show update status
        status = update_service.get_update_status()
        print(json.dumps(status, indent=2))
    elif args.check_only:
        # Only check for updates
        release = update_service.check_for_updates()
        if release:
            print(f"Update available: {release['version']}")
        else:
            print("No updates available")
    else:
        # Run full update process
        success = update_service.run_update_check()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
