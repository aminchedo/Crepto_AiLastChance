const { app, BrowserWindow, ipcMain, Tray, Menu, shell, dialog } = require('electron');
const { autoUpdater } = require('electron-updater');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

// Platform-specific modules
let electronSquirrelStartup;
try {
    electronSquirrelStartup = require('electron-squirrel-startup');
} catch (e) {
    electronSquirrelStartup = false;
}

// Handle Squirrel events for Windows
if (electronSquirrelStartup) {
    app.quit();
}

// Global references
let mainWindow = null;
let tray = null;
let backendProcess = null;
let backendReady = false;

// App configuration
const isDevelopment = !app.isPackaged;
const BACKEND_PORT = 8000;
const BACKEND_URL = `http://localhost:${BACKEND_PORT}`;

// Logging utilities
function log(level, message, ...args) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [${level}] ${message}`, ...args);
}

// Backend process management
function startBackendProcess() {
    return new Promise((resolve, reject) => {
        log('INFO', 'Starting backend process...');

        let backendPath;

        if (isDevelopment) {
            // Development: Run Python directly
            backendPath = path.join(__dirname, '..', 'backend', 'main.py');

            // Check if virtual environment exists
            const venvPython = path.join(__dirname, '..', 'backend', 'venv', 'Scripts', 'python.exe');
            const pythonExecutable = fs.existsSync(venvPython) ? venvPython : 'python';

            backendProcess = spawn(pythonExecutable, [backendPath], {
                cwd: path.join(__dirname, '..', 'backend'),
                env: {
                    ...process.env,
                    PYTHONUNBUFFERED: '1',
                    HOST: '127.0.0.1',
                    PORT: BACKEND_PORT.toString(),
                },
            });
        } else {
            // Production: Use PyInstaller bundled executable
            backendPath = path.join(process.resourcesPath, 'backend', 'main.exe');

            if (!fs.existsSync(backendPath)) {
                const error = `Backend executable not found at ${backendPath}`;
                log('ERROR', error);
                reject(new Error(error));
                return;
            }

            backendProcess = spawn(backendPath, [], {
                env: {
                    ...process.env,
                    HOST: '127.0.0.1',
                    PORT: BACKEND_PORT.toString(),
                },
            });
        }

        backendProcess.stdout.on('data', (data) => {
            const output = data.toString().trim();
            log('BACKEND', output);

            // Check if backend is ready
            if (output.includes('Uvicorn running') || output.includes('Application startup complete')) {
                backendReady = true;
                log('INFO', 'Backend is ready');
                resolve();
            }
        });

        backendProcess.stderr.on('data', (data) => {
            log('BACKEND_ERROR', data.toString().trim());
        });

        backendProcess.on('error', (error) => {
            log('ERROR', 'Backend process error:', error);
            reject(error);
        });

        backendProcess.on('exit', (code, signal) => {
            log('INFO', `Backend process exited with code ${code}, signal ${signal}`);
            backendReady = false;

            // Auto-restart if unexpected exit
            if (code !== 0 && code !== null && !app.isQuitting) {
                log('INFO', 'Restarting backend process...');
                setTimeout(() => {
                    startBackendProcess().catch(err => {
                        log('ERROR', 'Failed to restart backend:', err);
                    });
                }, 3000);
            }
        });

        // Timeout for startup
        setTimeout(() => {
            if (!backendReady) {
                log('WARN', 'Backend startup timeout - assuming ready');
                resolve();
            }
        }, 15000);
    });
}

function stopBackendProcess() {
    if (backendProcess) {
        log('INFO', 'Stopping backend process...');

        try {
            if (process.platform === 'win32') {
                // Windows: Use taskkill for graceful shutdown
                spawn('taskkill', ['/pid', backendProcess.pid, '/f', '/t']);
            } else {
                backendProcess.kill('SIGTERM');
            }
        } catch (error) {
            log('ERROR', 'Error stopping backend:', error);
        }

        backendProcess = null;
        backendReady = false;
    }
}

// Health check for backend
async function checkBackendHealth() {
    if (!backendReady) return false;

    try {
        const http = require('http');

        return new Promise((resolve) => {
            const req = http.get(`${BACKEND_URL}/health`, { timeout: 2000 }, (res) => {
                resolve(res.statusCode === 200);
            });

            req.on('error', () => resolve(false));
            req.on('timeout', () => {
                req.destroy();
                resolve(false);
            });
        });
    } catch (error) {
        return false;
    }
}

// Create main window
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1600,
        height: 1000,
        minWidth: 1200,
        minHeight: 800,
        backgroundColor: '#0a0a0f',
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.cjs'),
        },
        icon: path.join(__dirname, '..', 'build', 'icon.png'),
        show: false, // Show after ready
    });

    // Load app
    if (isDevelopment) {
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'));
    }

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        log('INFO', 'Main window ready');
    });

    // Handle window close
    mainWindow.on('close', (event) => {
        if (!app.isQuitting && process.platform === 'win32') {
            event.preventDefault();
            mainWindow.hide();

            // Show tray notification
            if (tray) {
                tray.displayBalloon({
                    title: 'Bolt AI Crypto',
                    content: 'Application minimized to system tray',
                });
            }
        }
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // External links in default browser
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });
}

// Create system tray
function createTray() {
    const iconPath = path.join(__dirname, '..', 'build', 'icon.png');

    tray = new Tray(iconPath);

    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'Show App',
            click: () => {
                if (mainWindow) {
                    mainWindow.show();
                    mainWindow.focus();
                }
            },
        },
        {
            label: 'Backend Status',
            enabled: false,
            sublabel: backendReady ? 'Running' : 'Stopped',
        },
        { type: 'separator' },
        {
            label: 'Quit',
            click: () => {
                app.isQuitting = true;
                app.quit();
            },
        },
    ]);

    tray.setToolTip('Bolt AI Crypto - Neural Trading System');
    tray.setContextMenu(contextMenu);

    tray.on('double-click', () => {
        if (mainWindow) {
            mainWindow.show();
            mainWindow.focus();
        }
    });
}

// Auto-updater configuration
function setupAutoUpdater() {
    if (isDevelopment) {
        log('INFO', 'Auto-updater disabled in development mode');
        return;
    }

    autoUpdater.autoDownload = false;
    autoUpdater.autoInstallOnAppQuit = true;

    autoUpdater.on('checking-for-update', () => {
        log('INFO', 'Checking for updates...');
    });

    autoUpdater.on('update-available', (info) => {
        log('INFO', 'Update available:', info.version);

        dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'Update Available',
            message: `A new version ${info.version} is available. Would you like to download it now?`,
            buttons: ['Download', 'Later'],
            defaultId: 0,
        }).then((result) => {
            if (result.response === 0) {
                autoUpdater.downloadUpdate();
            }
        });
    });

    autoUpdater.on('update-not-available', () => {
        log('INFO', 'No updates available');
    });

    autoUpdater.on('download-progress', (progress) => {
        log('INFO', `Download progress: ${progress.percent.toFixed(2)}%`);

        if (mainWindow) {
            mainWindow.setProgressBar(progress.percent / 100);
        }
    });

    autoUpdater.on('update-downloaded', (info) => {
        log('INFO', 'Update downloaded:', info.version);

        if (mainWindow) {
            mainWindow.setProgressBar(-1);
        }

        dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'Update Ready',
            message: 'Update downloaded. The application will restart to install the update.',
            buttons: ['Restart Now', 'Later'],
            defaultId: 0,
        }).then((result) => {
            if (result.response === 0) {
                app.isQuitting = true;
                autoUpdater.quitAndInstall();
            }
        });
    });

    autoUpdater.on('error', (error) => {
        log('ERROR', 'Auto-updater error:', error);
    });

    // Check for updates on startup
    setTimeout(() => {
        autoUpdater.checkForUpdates();
    }, 5000);

    // Check for updates every 4 hours
    setInterval(() => {
        autoUpdater.checkForUpdates();
    }, 4 * 60 * 60 * 1000);
}

// IPC handlers
function setupIpcHandlers() {
    // Backend health check
    ipcMain.handle('backend:health', async () => {
        return await checkBackendHealth();
    });

    // Backend API URL
    ipcMain.handle('backend:getUrl', () => {
        return BACKEND_URL;
    });

    // App version
    ipcMain.handle('app:getVersion', () => {
        return app.getVersion();
    });

    // Open external URL
    ipcMain.handle('app:openExternal', async (event, url) => {
        await shell.openExternal(url);
    });

    // Show notification
    ipcMain.handle('app:showNotification', (event, { title, body }) => {
        if (tray) {
            tray.displayBalloon({ title, content: body });
        }
    });

    // Check for updates manually
    ipcMain.handle('app:checkForUpdates', () => {
        if (!isDevelopment) {
            autoUpdater.checkForUpdates();
        }
        return !isDevelopment;
    });
}

// App lifecycle
app.whenReady().then(async () => {
    log('INFO', `Bolt AI Crypto v${app.getVersion()} starting...`);

    try {
        // Start backend process
        await startBackendProcess();

        // Wait a bit for backend to fully initialize
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Create main window
        createWindow();

        // Create system tray
        createTray();

        // Setup IPC handlers
        setupIpcHandlers();

        // Setup auto-updater
        setupAutoUpdater();

        log('INFO', 'Application ready');
    } catch (error) {
        log('ERROR', 'Failed to start application:', error);

        dialog.showErrorBox(
            'Startup Error',
            `Failed to start Bolt AI Crypto:\n\n${error.message}\n\nPlease check the logs and try again.`
        );

        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    } else if (mainWindow) {
        mainWindow.show();
    }
});

app.on('before-quit', () => {
    app.isQuitting = true;
});

app.on('will-quit', () => {
    log('INFO', 'Application shutting down...');
    stopBackendProcess();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    log('ERROR', 'Uncaught exception:', error);

    dialog.showErrorBox(
        'Application Error',
        `An unexpected error occurred:\n\n${error.message}\n\nThe application will continue running, but may be unstable.`
    );
});

process.on('unhandledRejection', (reason, promise) => {
    log('ERROR', 'Unhandled rejection at:', promise, 'reason:', reason);
});

