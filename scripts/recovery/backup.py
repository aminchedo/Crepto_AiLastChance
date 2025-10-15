#!/usr/bin/env python3
"""
Backup utility for BOLT AI Neural Agent System
"""
from pathlib import Path
from datetime import datetime
import shutil
import argparse


def backup(project_root: Path, output_dir: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = output_dir / f"boltai-backup-{timestamp}"
    backup_root.mkdir(parents=True, exist_ok=True)

    include_paths = [
        project_root / "backend" / "models",
        project_root / "backend" / "db",
        project_root / "backend-dist",
        project_root / "config",
        project_root / "exports",
        project_root / "reports",
    ]

    for p in include_paths:
        if p.exists():
            dest = backup_root / p.name
            if p.is_dir():
                shutil.copytree(p, dest)
            else:
                shutil.copy2(p, dest)

    return backup_root


def main():
    parser = argparse.ArgumentParser(description="Backup BOLT AI data and artifacts")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=Path.cwd() / "backups")
    args = parser.parse_args()

    args.output_dir.mkdir(exist_ok=True)
    path = backup(args.project_root, args.output_dir)
    print(f"Backup created at: {path}")


if __name__ == "__main__":
    main()


