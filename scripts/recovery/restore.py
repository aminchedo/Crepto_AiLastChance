#!/usr/bin/env python3
"""
Restore utility for BOLT AI Neural Agent System
"""
from pathlib import Path
import shutil
import argparse


def restore(backup_dir: Path, project_root: Path) -> None:
    if not backup_dir.exists() or not backup_dir.is_dir():
        raise FileNotFoundError(f"Backup directory not found: {backup_dir}")

    for item in backup_dir.iterdir():
        dest = project_root / item.name
        if dest.exists():
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)


def main():
    parser = argparse.ArgumentParser(description="Restore BOLT AI data and artifacts from backup")
    parser.add_argument("backup_dir", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    restore(args.backup_dir, args.project_root)
    print("Restore completed.")


if __name__ == "__main__":
    main()


