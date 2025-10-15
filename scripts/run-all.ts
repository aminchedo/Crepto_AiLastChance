import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

// Configuration
const config = {
  frontend: {
    command: 'npm',
    args: ['run', 'dev', '--', '--port', '3000'],
    name: 'FRONTEND',
    color: '\x1b[36m' // Cyan
  },
  backend: {
    command: process.platform === 'win32' ? '.venv\\Scripts\\python.exe' : '.venv/bin/python',
    args: ['backend/main.py'],
    name: 'BACKEND',
    color: '\x1b[32m' // Green
  }
};

// Track processes so we can kill them later
const processes: ChildProcess[] = [];
let shuttingDown = false;

// Helper to format log output
function formatLog(name: string, color: string, data: Buffer): string {
  const timestamp = new Date().toLocaleTimeString();
  const lines = data.toString().trim().split('\n');
  return lines.map(line => `${color}[${timestamp}][${name}]\x1b[0m ${line}`).join('\n');
}

// Start a process
function startProcess(options: typeof config.frontend | typeof config.backend): void {
  console.log(`\x1b[33m[RUNNER] Starting ${options.name}...\x1b[0m`);
  
  const proc = spawn(options.command, options.args, { 
    stdio: 'pipe',
    shell: true
  });
  
  processes.push(proc);
  
  proc.stdout?.on('data', (data) => {
    console.log(formatLog(options.name, options.color, data));
  });
  
  proc.stderr?.on('data', (data) => {
    console.error(formatLog(options.name, '\x1b[31m', data));
  });
  
  proc.on('close', (code) => {
    if (!shuttingDown) {
      console.log(`\x1b[33m[RUNNER] ${options.name} process exited with code ${code}\x1b[0m`);
      if (code !== 0 && !shuttingDown) {
        console.log(`\x1b[33m[RUNNER] Attempting to restart ${options.name}...\x1b[0m`);
        startProcess(options);
      }
    }
  });
}

// Check if backend exists and has required files
function checkBackend(): boolean {
  const backendDir = path.join(process.cwd(), 'backend');
  const mainFile = path.join(backendDir, 'main.py');
  const envFile = path.join(process.cwd(), '.env');
  const venvDir = path.join(process.cwd(), '.venv');
  
  if (!fs.existsSync(backendDir)) {
    console.error('\x1b[31m[ERROR] Backend directory not found\x1b[0m');
    return false;
  }
  
  if (!fs.existsSync(mainFile)) {
    console.error('\x1b[31m[ERROR] Backend main.py not found\x1b[0m');
    return false;
  }
  
  // Check for virtual environment
  if (!fs.existsSync(venvDir)) {
    console.error('\x1b[31m[ERROR] Virtual environment not found. Please run setup-dev.ps1 first\x1b[0m');
    return false;
  }
  
  // Create .env file if it doesn't exist
  if (!fs.existsSync(envFile)) {
    console.log('\x1b[33m[SETUP] Creating .env file with default values...\x1b[0m');
    const envContent = `DATABASE_URL=sqlite:///./crypto_ai.db
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30`;
    fs.writeFileSync(envFile, envContent);
  }
  
  return true;
}

// Check if frontend exists and has required files
function checkFrontend(): boolean {
  const packageJsonPath = path.join(process.cwd(), 'package.json');
  
  if (!fs.existsSync(packageJsonPath)) {
    console.error('\x1b[31m[ERROR] package.json not found\x1b[0m');
    return false;
  }
  
  try {
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));
    if (!packageJson.scripts?.dev) {
      console.error('\x1b[31m[ERROR] "dev" script not found in package.json\x1b[0m');
      return false;
    }
  } catch (err) {
    console.error('\x1b[31m[ERROR] Failed to parse package.json\x1b[0m');
    return false;
  }
  
  return true;
}

// Handle graceful shutdown
function shutdown() {
  if (shuttingDown) return;
  shuttingDown = true;
  
  console.log('\x1b[33m[RUNNER] Shutting down all processes...\x1b[0m');
  
  // Kill all processes
  processes.forEach(proc => {
    if (!proc.killed) {
      proc.kill('SIGINT');
    }
  });
  
  // Give processes a moment to clean up
  setTimeout(() => {
    processes.forEach(proc => {
      if (!proc.killed) {
        proc.kill('SIGKILL');
      }
    });
    console.log('\x1b[33m[RUNNER] All processes terminated\x1b[0m');
    process.exit(0);
  }, 5000);
}

// Main function
async function main() {
  console.log('\x1b[33m[RUNNER] Starting development environment...\x1b[0m');
  
  // Validate environment
  const backendOk = checkBackend();
  const frontendOk = checkFrontend();
  
  if (!backendOk || !frontendOk) {
    console.error('\x1b[31m[ERROR] Failed to validate environment\x1b[0m');
    process.exit(1);
  }
  
  // Register shutdown handlers
  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
  process.on('uncaughtException', (error) => {
    console.error('\x1b[31m[ERROR] Uncaught exception:\x1b[0m', error);
    shutdown();
  });
  
  // Start backend first
  startProcess(config.backend);
  
  // Wait a bit before starting frontend
  setTimeout(() => {
    startProcess(config.frontend);
    console.log('\x1b[33m[RUNNER] Development environment started!\x1b[0m');
    console.log('\x1b[33m[RUNNER] Press Ctrl+C to stop all processes\x1b[0m');
  }, 2000);
}

// Run the script
main().catch(err => {
  console.error('\x1b[31m[ERROR] Failed to start development environment:\x1b[0m', err);
  process.exit(1);
});
