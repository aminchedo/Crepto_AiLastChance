#!/usr/bin/env python3
"""
Rollback utility for BOLT AI Neural Agent System
"""
from pathlib import Path
import shutil
import argparse


def rollback(backups_root: Path, project_root: Path) -> None:
    backups = sorted([p for p in backups_root.glob("boltai-backup-*") if p.is_dir()], reverse=True)
    if len(backups) < 2:
        raise RuntimeError("No previous backup to rollback to.")

    # The second most recent backup is the previous version
    target = backups[1]

    # Restore from target
    for item in target.iterdir():
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
    parser = argparse.ArgumentParser(description="Rollback BOLT AI to previous backup")
    parser.add_argument("--backups-root", type=Path, default=Path.cwd() / "backups")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    rollback(args.backups_root, args.project_root)
    print("Rollback completed.")


if __name__ == "__main__":
    main()


