# NPM Troubleshooting Guide

This guide helps you diagnose and fix common npm installation issues on Windows, particularly for the Crepto_Ai project.

## Quick Fix Commands

### For PowerShell (Recommended)
```powershell
# Standard fix
npm run fix:npm

# Force fix with legacy peer deps
npm run fix:npm:force

# Check current state only
npm run fix:npm:check

# Manual clean and reinstall
npm run clean
npm run reinstall
```

### For Git Bash/WSL
```bash
# Standard fix
./scripts/npm-fix.sh

# Force fix with legacy peer deps
./scripts/npm-fix.sh --strategy force-legacy

# Check current state only
./scripts/npm-fix.sh --check-only

# Dry run to see what would be done
./scripts/npm-fix.sh --dry-run
```

## Common Issues and Solutions

### 1. Missing Dependencies (UNMET DEPENDENCY)

**Symptoms:**
- `npm ls` shows "UNMET DEPENDENCY" errors
- Build fails with "Cannot find module" errors
- Some packages appear as "extraneous"

**Causes:**
- Corrupted `node_modules` directory
- Incomplete installation
- Version conflicts
- File system issues on Windows

**Solutions:**
1. **Clean and reinstall:**
   ```powershell
   npm run clean
   npm install
   ```

2. **Use force with legacy peer deps:**
   ```powershell
   npm install --force --legacy-peer-deps
   ```

3. **Clear cache and reinstall:**
   ```powershell
   npm cache clean --force
   npm run clean
   npm install
   ```

### 2. File Lock Errors (EBUSY)

**Symptoms:**
- "EBUSY: resource busy or locked" errors
- Cannot delete `node_modules` directory
- Installation fails with file access errors

**Causes:**
- Node.js processes still running
- Antivirus software locking files
- Windows file system locks
- IDE/editor with open files

**Solutions:**
1. **Stop all Node processes:**
   ```powershell
   # Check for running processes
   Get-Process -Name "node" -ErrorAction SilentlyContinue
   
   # Kill all Node processes
   Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
   ```

2. **Close your IDE/editor** before running npm commands

3. **Run as Administrator:**
   - Right-click PowerShell/CMD
   - Select "Run as Administrator"

4. **Temporarily disable antivirus** during installation

### 3. Electron Installation Issues

**Symptoms:**
- "Cannot find module 'debug'" errors
- Electron installation fails
- `extract-zip` module errors

**Causes:**
- Missing native dependencies
- Platform-specific build issues
- Corrupted cache

**Solutions:**
1. **Use the troubleshooting script:**
   ```powershell
   npm run fix:npm:force
   ```

2. **Manual Electron fix:**
   ```powershell
   npm cache clean --force
   npm install electron --force
   npm install
   ```

3. **Rebuild native modules:**
   ```powershell
   npm rebuild
   ```

### 4. Version Conflicts

**Symptoms:**
- Peer dependency warnings
- Version mismatch errors
- Incompatible package versions

**Solutions:**
1. **Use legacy peer deps:**
   ```powershell
   npm install --legacy-peer-deps
   ```

2. **Force installation:**
   ```powershell
   npm install --force
   ```

3. **Update packages:**
   ```powershell
   npm update
   ```

### 5. Cache Issues

**Symptoms:**
- Stale packages being installed
- Inconsistent behavior
- Installation succeeds but packages don't work

**Solutions:**
1. **Clear npm cache:**
   ```powershell
   npm cache clean --force
   ```

2. **Clear all caches:**
   ```powershell
   npm cache clean --force
   npm run clean
   rm -rf ~/.npm
   ```

## Prevention Tips

### 1. Environment Setup
- Use Node.js 18+ (current project uses 20.19.5)
- Keep npm updated (`npm install -g npm@latest`)
- Use PowerShell or CMD instead of Git Bash for npm commands on Windows

### 2. Best Practices
- Always close your IDE before running npm commands
- Run PowerShell as Administrator when needed
- Don't interrupt npm installations
- Use `npm ci` in CI/CD environments

### 3. Project-Specific
- This project uses Electron, which requires native compilation
- Some packages may need Windows build tools
- Consider using `--legacy-peer-deps` for complex dependency trees

## Troubleshooting Scripts

### PowerShell Script (`scripts/npm-fix.ps1`)

**Features:**
- Automatic Node.js process detection and termination
- File lock detection
- Multiple installation strategies
- System requirements checking
- Dry-run mode for testing

**Usage:**
```powershell
# Standard fix
.\scripts\npm-fix.ps1

# Force fix with legacy peer deps
.\scripts\npm-fix.ps1 -Strategy force-legacy

# Check only (no changes)
.\scripts\npm-fix.ps1 -CheckOnly

# Dry run (see what would be done)
.\scripts\npm-fix.ps1 -DryRun
```

### Bash Script (`scripts/npm-fix.sh`)

**Features:**
- Compatible with Git Bash and WSL
- Same functionality as PowerShell script
- Unix-style command line options

**Usage:**
```bash
# Make executable (first time only)
chmod +x scripts/npm-fix.sh

# Standard fix
./scripts/npm-fix.sh

# Force fix with legacy peer deps
./scripts/npm-fix.sh --strategy force-legacy

# Check only (no changes)
./scripts/npm-fix.sh --check-only

# Dry run (see what would be done)
./scripts/npm-fix.sh --dry-run
```

## Advanced Troubleshooting

### 1. Complete Environment Reset
```powershell
# Remove all Node.js installations
# (Use Windows "Add or Remove Programs")

# Clear all npm data
rm -rf ~/.npm
rm -rf ~/.node-gyp

# Reinstall Node.js from nodejs.org
# Reinstall npm: npm install -g npm@latest
```

### 2. Network Issues
```powershell
# Use different registry
npm config set registry https://registry.npmjs.org/

# Check proxy settings
npm config get proxy
npm config get https-proxy

# Clear network cache
npm cache clean --force
```

### 3. Permission Issues
```powershell
# Fix npm permissions (Windows)
npm config set prefix ~/.npm-global
npm config set cache ~/.npm-cache

# Or run as Administrator
```

## Project-Specific Notes

### Current Project State
- **Node.js:** v20.19.5
- **npm:** 10.8.2
- **OS:** Windows 10 (Build 19045)
- **Key Dependencies:** Electron, React, TypeScript, Vite

### Known Issues
1. **Electron 28.1.4** - May have compatibility issues with newer Node.js versions
2. **MSW 2.11.5** - Can cause file lock issues during installation
3. **ESBuild** - Native module that may need rebuilding

### Recommended Fix Strategy
1. Start with `npm run fix:npm:check` to assess current state
2. Use `npm run fix:npm:force` for most issues
3. If that fails, try manual clean + `npm install --legacy-peer-deps`
4. For persistent issues, consider updating to newer package versions

## Getting Help

If you continue to experience issues:

1. **Check the logs:**
   ```powershell
   # npm logs are usually in:
   # %APPDATA%\npm-cache\_logs\
   ```

2. **Run diagnostics:**
   ```powershell
   npm doctor
   npm ls --depth=0
   npm audit
   ```

3. **Create a minimal reproduction:**
   - Create a new directory
   - Copy only `package.json`
   - Try `npm install`
   - Compare results

4. **Check system requirements:**
   - Ensure you have enough disk space (2GB+ recommended)
   - Check Windows version compatibility
   - Verify antivirus isn't interfering

Remember: Most npm issues on Windows can be resolved with a clean reinstall using the provided scripts!
