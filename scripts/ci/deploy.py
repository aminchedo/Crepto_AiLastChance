#!/usr/bin/env python3
"""
Deployment script for BOLT AI Neural Agent System
"""
import os
import sys
import subprocess
import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import logging


class DeploymentManager:
    """Deployment manager for BOLT AI system"""
    
    def __init__(self, environment: str):
        self.environment = environment
        self.setup_logging()
        self.config = self.load_config()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'deployment-{self.environment}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self) -> Dict:
        """Load deployment configuration"""
        config_file = Path(f"config/deployment-{self.environment}.json")
        
        if not config_file.exists():
            self.logger.warning(f"Config file not found: {config_file}")
            return self.get_default_config()
        
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def get_default_config(self) -> Dict:
        """Get default deployment configuration"""
        return {
            "servers": {
                "staging": {
                    "host": "staging.bolt-ai.com",
                    "user": "deploy",
                    "path": "/opt/bolt-ai",
                    "port": 22
                },
                "production": {
                    "host": "prod.bolt-ai.com",
                    "user": "deploy",
                    "path": "/opt/bolt-ai",
                    "port": 22
                }
            },
            "health_checks": {
                "endpoints": ["/health", "/api/v1/health"],
                "timeout": 30,
                "retries": 3
            },
            "rollback": {
                "enabled": True,
                "max_versions": 5
            }
        }
    
    def run_command(self, command: List[str], cwd: Path = None) -> bool:
        """Run a command and return success status"""
        try:
            self.logger.info(f"Running command: {' '.join(command)}")
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.logger.info("Command completed successfully")
                return True
            else:
                self.logger.error(f"Command failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Command timed out")
            return False
        except Exception as e:
            self.logger.error(f"Command error: {e}")
            return False
    
    def check_prerequisites(self) -> bool:
        """Check deployment prerequisites"""
        self.logger.info("Checking deployment prerequisites...")
        
        # Check if build artifacts exist
        artifacts_dir = Path("dist-electron")
        if not artifacts_dir.exists():
            self.logger.error("Build artifacts not found. Run build first.")
            return False
        
        # Check if backend executable exists
        backend_dir = Path("backend-dist")
        if not backend_dir.exists():
            self.logger.error("Backend executable not found. Run build first.")
            return False
        
        # Check if configuration files exist
        config_dir = Path("config")
        if not config_dir.exists():
            self.logger.warning("Configuration directory not found")
        
        self.logger.info("Prerequisites check completed")
        return True
    
    def backup_current_version(self) -> bool:
        """Backup current version before deployment"""
        self.logger.info("Backing up current version...")
        
        try:
            server_config = self.config["servers"][self.environment]
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup-{timestamp}"
            
            # Create backup directory
            backup_cmd = [
                "ssh", f"{server_config['user']}@{server_config['host']}",
                f"mkdir -p {server_config['path']}/backups/{backup_name}"
            ]
            
            if not self.run_command(backup_cmd):
                return False
            
            # Copy current version to backup
            backup_cmd = [
                "ssh", f"{server_config['user']}@{server_config['host']}",
                f"cp -r {server_config['path']}/current/* {server_config['path']}/backups/{backup_name}/"
            ]
            
            if not self.run_command(backup_cmd):
                return False
            
            self.logger.info(f"Backup created: {backup_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False
    
    def deploy_artifacts(self) -> bool:
        """Deploy build artifacts to server"""
        self.logger.info("Deploying artifacts...")
        
        try:
            server_config = self.config["servers"][self.environment]
            
            # Create deployment directory
            deploy_cmd = [
                "ssh", f"{server_config['user']}@{server_config['host']}",
                f"mkdir -p {server_config['path']}/deploy"
            ]
            
            if not self.run_command(deploy_cmd):
                return False
            
            # Copy artifacts to server
            copy_cmd = [
                "scp", "-r", "dist-electron/*",
                f"{server_config['user']}@{server_config['host']}:{server_config['path']}/deploy/"
            ]
            
            if not self.run_command(copy_cmd):
                return False
            
            # Copy backend executable
            copy_backend_cmd = [
                "scp", "-r", "backend-dist/*",
                f"{server_config['user']}@{server_config['host']}:{server_config['path']}/deploy/"
            ]
            
            if not self.run_command(copy_backend_cmd):
                return False
            
            self.logger.info("Artifacts deployed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Artifact deployment failed: {e}")
            return False
    
    def update_symlinks(self) -> bool:
        """Update symlinks to point to new version"""
        self.logger.info("Updating symlinks...")
        
        try:
            server_config = self.config["servers"][self.environment]
            
            # Update symlink to new version
            symlink_cmd = [
                "ssh", f"{server_config['user']}@{server_config['host']}",
                f"ln -sfn {server_config['path']}/deploy {server_config['path']}/current"
            ]
            
            if not self.run_command(symlink_cmd):
                return False
            
            self.logger.info("Symlinks updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Symlink update failed: {e}")
            return False
    
    def restart_services(self) -> bool:
        """Restart services on the server"""
        self.logger.info("Restarting services...")
        
        try:
            server_config = self.config["servers"][self.environment]
            
            # Restart services
            restart_cmd = [
                "ssh", f"{server_config['user']}@{server_config['host']}",
                f"cd {server_config['path']}/current && ./restart-services.sh"
            ]
            
            if not self.run_command(restart_cmd):
                return False
            
            # Wait for services to start
            time.sleep(10)
            
            self.logger.info("Services restarted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Service restart failed: {e}")
            return False
    
    def run_health_checks(self) -> bool:
        """Run health checks on deployed services"""
        self.logger.info("Running health checks...")
        
        try:
            server_config = self.config["servers"][self.environment]
            health_config = self.config["health_checks"]
            
            for endpoint in health_config["endpoints"]:
                url = f"https://{server_config['host']}{endpoint}"
                
                # Run health check
                health_cmd = [
                    "curl", "-f", "-s", "--max-time", str(health_config["timeout"]),
                    url
                ]
                
                retries = health_config["retries"]
                for attempt in range(retries):
                    if self.run_command(health_cmd):
                        self.logger.info(f"Health check passed: {url}")
                        break
                    else:
                        if attempt < retries - 1:
                            self.logger.warning(f"Health check failed (attempt {attempt + 1}/{retries}): {url}")
                            time.sleep(5)
                        else:
                            self.logger.error(f"Health check failed after {retries} attempts: {url}")
                            return False
            
            self.logger.info("All health checks passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def rollback_deployment(self) -> bool:
        """Rollback to previous version"""
        self.logger.info("Rolling back deployment...")
        
        try:
            server_config = self.config["servers"][self.environment]
            
            # Get list of backups
            list_backups_cmd = [
                "ssh", f"{server_config['user']}@{server_config['host']}",
                f"ls -t {server_config['path']}/backups/ | head -2"
            ]
            
            result = subprocess.run(list_backups_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error("Failed to list backups")
                return False
            
            backups = result.stdout.strip().split('\n')
            if len(backups) < 2:
                self.logger.error("No previous backup found")
                return False
            
            previous_backup = backups[1]  # Second most recent
            
            # Rollback to previous version
            rollback_cmd = [
                "ssh", f"{server_config['user']}@{server_config['host']}",
                f"ln -sfn {server_config['path']}/backups/{previous_backup} {server_config['path']}/current"
            ]
            
            if not self.run_command(rollback_cmd):
                return False
            
            # Restart services
            if not self.restart_services():
                return False
            
            self.logger.info(f"Rolled back to: {previous_backup}")
            return True
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            return False
    
    def cleanup_old_versions(self) -> bool:
        """Clean up old versions to save disk space"""
        self.logger.info("Cleaning up old versions...")
        
        try:
            server_config = self.config["servers"][self.environment]
            max_versions = self.config["rollback"]["max_versions"]
            
            # Keep only the most recent versions
            cleanup_cmd = [
                "ssh", f"{server_config['user']}@{server_config['host']}",
                f"cd {server_config['path']}/backups && ls -t | tail -n +{max_versions + 1} | xargs rm -rf"
            ]
            
            if not self.run_command(cleanup_cmd):
                return False
            
            self.logger.info("Old versions cleaned up")
            return True
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return False
    
    def deploy(self) -> bool:
        """Main deployment process"""
        self.logger.info(f"Starting deployment to {self.environment}")
        
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                return False
            
            # Backup current version
            if not self.backup_current_version():
                self.logger.error("Backup failed, aborting deployment")
                return False
            
            # Deploy artifacts
            if not self.deploy_artifacts():
                self.logger.error("Artifact deployment failed, rolling back")
                self.rollback_deployment()
                return False
            
            # Update symlinks
            if not self.update_symlinks():
                self.logger.error("Symlink update failed, rolling back")
                self.rollback_deployment()
                return False
            
            # Restart services
            if not self.restart_services():
                self.logger.error("Service restart failed, rolling back")
                self.rollback_deployment()
                return False
            
            # Run health checks
            if not self.run_health_checks():
                self.logger.error("Health checks failed, rolling back")
                self.rollback_deployment()
                return False
            
            # Cleanup old versions
            self.cleanup_old_versions()
            
            self.logger.info(f"Deployment to {self.environment} completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            return False
    
    def status(self) -> bool:
        """Check deployment status"""
        self.logger.info(f"Checking deployment status for {self.environment}")
        
        try:
            server_config = self.config["servers"][self.environment]
            
            # Check current version
            version_cmd = [
                "ssh", f"{server_config['user']}@{server_config['host']}",
                f"ls -la {server_config['path']}/current"
            ]
            
            if not self.run_command(version_cmd):
                return False
            
            # Check service status
            status_cmd = [
                "ssh", f"{server_config['user']}@{server_config['host']}",
                f"cd {server_config['path']}/current && ./status.sh"
            ]
            
            if not self.run_command(status_cmd):
                return False
            
            # Run health checks
            if not self.run_health_checks():
                return False
            
            self.logger.info("Deployment status check completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Status check failed: {e}")
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Deploy BOLT AI Neural Agent System")
    parser.add_argument("environment", choices=["staging", "production"], help="Deployment environment")
    parser.add_argument("--action", choices=["deploy", "status", "rollback"], default="deploy", help="Action to perform")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without actual deployment")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE - No actual deployment will be performed")
        return 0
    
    deployment = DeploymentManager(args.environment)
    
    if args.action == "deploy":
        success = deployment.deploy()
    elif args.action == "status":
        success = deployment.status()
    elif args.action == "rollback":
        success = deployment.rollback_deployment()
    else:
        print(f"Unknown action: {args.action}")
        return 1
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
