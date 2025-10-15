#!/usr/bin/env python3
"""
Script to build the FastAPI backend as a standalone executable using PyInstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    backend_dir = project_root / 'backend'
    spec_file = backend_dir / 'build_backend.spec'
    dist_dir = project_root / 'backend-dist'
    
    print("=" * 60)
    print("Building FastAPI Backend Executable")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✓ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    
    # Clean previous builds
    if dist_dir.exists():
        print(f"\nCleaning previous build: {dist_dir}")
        shutil.rmtree(dist_dir)
    
    build_dir = backend_dir / 'build'
    if build_dir.exists():
        print(f"Cleaning build directory: {build_dir}")
        shutil.rmtree(build_dir)
    
    pyinstaller_dist = backend_dir / 'dist'
    if pyinstaller_dist.exists():
        print(f"Cleaning PyInstaller dist: {pyinstaller_dist}")
        shutil.rmtree(pyinstaller_dist)
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Run PyInstaller
    print(f"\nRunning PyInstaller with spec file: {spec_file.name}")
    cmd = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--clean',
        '--noconfirm',
        str(spec_file.name)
    ]
    
    print(f"Command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"\n✗ PyInstaller failed with exit code {result.returncode}")
        sys.exit(1)
    
    # Move dist to backend-dist
    source_dist = backend_dir / 'dist' / 'main'
    if not source_dist.exists():
        print(f"\n✗ Build output not found at {source_dist}")
        sys.exit(1)
    
    print(f"\nMoving build output to {dist_dir}")
    shutil.move(str(source_dist), str(dist_dir))
    
    # Clean up
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if pyinstaller_dist.exists():
        shutil.rmtree(pyinstaller_dist)
    
    # Verify executable
    if sys.platform == 'win32':
        exe_path = dist_dir / 'main.exe'
    else:
        exe_path = dist_dir / 'main'
    
    if not exe_path.exists():
        print(f"\n✗ Executable not found at {exe_path}")
        sys.exit(1)
    
    exe_size = exe_path.stat().st_size / (1024 * 1024)  # MB
    print(f"\n✓ Build successful!")
    print(f"  Executable: {exe_path}")
    print(f"  Size: {exe_size:.2f} MB")
    
    # List all files in dist
    print(f"\nBuild contents:")
    for item in sorted(dist_dir.rglob('*')):
        if item.is_file():
            size = item.stat().st_size / 1024  # KB
            rel_path = item.relative_to(dist_dir)
            print(f"  {rel_path} ({size:.1f} KB)")
    
    print("\n" + "=" * 60)
    print("Backend build complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()

