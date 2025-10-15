// Type definitions for Electron API exposed via contextBridge

export interface ElectronAPI {
    backend: {
        checkHealth: () => Promise<boolean>;
        getUrl: () => Promise<string>;
    };
    app: {
        getVersion: () => Promise<string>;
        openExternal: (url: string) => Promise<void>;
        showNotification: (title: string, body: string) => Promise<void>;
        checkForUpdates: () => Promise<boolean>;
    };
    platform: string;
    isElectron: boolean;
}

declare global {
    interface Window {
        electronAPI?: ElectronAPI;
    }
}

export { };

