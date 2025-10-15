const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Backend API
  backend: {
    checkHealth: () => ipcRenderer.invoke('backend:health'),
    getUrl: () => ipcRenderer.invoke('backend:getUrl'),
  },

  // App API
  app: {
    getVersion: () => ipcRenderer.invoke('app:getVersion'),
    openExternal: (url) => ipcRenderer.invoke('app:openExternal', url),
    showNotification: (title, body) => ipcRenderer.invoke('app:showNotification', { title, body }),
    checkForUpdates: () => ipcRenderer.invoke('app:checkForUpdates'),
  },

  // Platform info
  platform: process.platform,
  isElectron: true,
});

// Log that preload script executed
console.log('[Preload] Electron API initialized');

