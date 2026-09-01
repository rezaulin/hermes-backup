# Electron Desktop Conversion — Vite + React PWA → .exe

> Convert existing Vite/React/Tailwind v4 web app into Windows desktop installer (.exe) using Electron. Preserves 95% of existing code.

## When to use
- User wants to sell/distribute web app as installable desktop software
- Need offline-first desktop app with license system
- Need thermal printer / USB barcode scanner native access
- Need system tray, auto-start, auto-updater

## Prerequisites (npm)
```bash
npm install --save-dev electron electron-builder concurrently wait-on cross-env
```

## Phase 1: Electron Setup (Day 1-2)

### File structure
```
electron/
├── main.js              # Main process (window + tray + IPC)
├── preload.js           # Context bridge (expose API to renderer)
└── utils/
    ├── paths.js         # App directories (userData, backups, logs)
    └── logger.js        # File logging to userData/logs/
electron-builder.yml     # Build config (NSIS installer)
build/
├── icon.png             # App icon (replace placeholder before release)
└── license.txt          # EULA text shown in installer
src/types/electron.d.ts  # TypeScript definitions for window.electronAPI
```

### package.json changes
```json
{
  "version": "1.0.0",
  "main": "electron/main.js",
  "scripts": {
    "electron:dev": "concurrently -k \"cross-env BROWSER=none vite\" \"wait-on http://localhost:5173 && cross-env NODE_ENV=development electron .\"",
    "electron:build": "cross-env ELECTRON=true vite build && electron-builder",
    "electron:preview": "cross-env ELECTRON=true vite build && electron ."
  }
}
```

### vite.config.ts — dual-mode (web + Electron)
```ts
const isElectron = process.env.ELECTRON === 'true'
return {
  base: isElectron ? './' : '/',     // relative paths for file:// protocol
  build: {
    target: isElectron ? 'node18' : 'esnext',
  },
}
```

**CRITICAL:** `base: './'` is REQUIRED for Electron — without it, assets use absolute paths (`/assets/...`) which break on `file://` protocol. App loads blank white.

### electron/main.js — key patterns
```js
import { app, BrowserWindow, ipcMain, Tray, Menu } from 'electron';

// Window config
mainWindow = new BrowserWindow({
  width: 1280, height: 800,
  minWidth: 1024, minHeight: 768,
  webPreferences: {
    preload: path.join(__dirname, 'preload.js'),
    contextIsolation: true,    // ALWAYS true for security
    nodeIntegration: false,    // ALWAYS false for security
  },
  show: false,  // show after ready-to-show (prevents flash)
});

// Load dev or production build
if (isDev) {
  mainWindow.loadURL('http://localhost:5173');
  mainWindow.webContents.openDevTools();
} else {
  mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
}

// Minimize to tray instead of close
mainWindow.on('close', (event) => {
  if (!app.isQuitting) {
    event.preventDefault();
    mainWindow.hide();
  }
});
```

### electron/preload.js — contextBridge
```js
contextBridge.exposeInMainWorld('electronAPI', {
  getVersion: () => ipcRenderer.invoke('app:version'),
  getHardwareId: () => ipcRenderer.invoke('license:get-hwid'),
  activateLicense: (key, code) => ipcRenderer.invoke('license:activate', key, code),
  getLicenseStatus: () => ipcRenderer.invoke('license:status'),
  getPrinters: () => ipcRenderer.invoke('printer:list'),
  printRaw: (printerName, data) => ipcRenderer.invoke('printer:raw', printerName, data),
  exportBackup: (path) => ipcRenderer.invoke('backup:export', path),
  importBackup: (path) => ipcRenderer.invoke('backup:import', path),
  selectDirectory: () => ipcRenderer.invoke('dialog:select-dir'),
  minimizeToTray: () => ipcRenderer.send('window:minimize-tray'),
  checkUpdate: () => ipcRenderer.invoke('update:check'),
  onUpdateAvailable: (cb) => ipcRenderer.on('update:available', (_, info) => cb(info)),
});
```

### electron-builder.yml — NSIS installer
```yaml
appId: com.yourcompany.appname
productName: App Name
directories:
  output: release
  buildResources: build
files:
  - dist/**/*
  - electron/**/*
  - package.json
win:
  target:
    - target: nsis
      arch: [x64]
  icon: build/icon.ico
nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
  createDesktopShortcut: true
  createStartMenuShortcut: true
  deleteAppDataOnUninstall: false  # KEEP user data on uninstall!
```

### TypeScript definitions (src/types/electron.d.ts)
```ts
export interface ElectronAPI {
  getVersion: () => Promise<string>;
  getHardwareId: () => Promise<string>;
  activateLicense: (key: string, code: string) => Promise<{success: boolean; tier?: string}>;
  // ... all IPC methods
}
declare global {
  interface Window { electronAPI?: ElectronAPI; }
}
```

Usage in React: `window.electronAPI?.getVersion()` — optional chaining because undefined in browser mode.

## Phase 2-8: Feature phases (2 weeks total)

| Phase | Days | Features |
|-------|------|----------|
| 2: Native Features | 3-5 | System tray, auto-start, printer detection, USB scanner, keyboard shortcuts |
| 3: Backup/Restore | 5-6 | Auto-backup daily, manual export/import .omnibackup (ZIP), retention 7 files |
| 4: License System | 7-9 | Hardware fingerprint, activation online, trial 30 days, tier enforcement |
| 5: UI Desktop | 9-10 | Custom title bar, activation page, license badge, splash screen |
| 6: Auto-Updater | 10-11 | electron-updater, GitHub Releases, changelog, skip version, rollback |
| 7: Build & Dist | 11-12 | NSIS installer, code signing (optional), version numbering |
| 8: License Admin | 12-13 | Web admin panel, generate keys, manage clients, dashboard |

## Pitfalls

### 1. Base path breaks in Electron
`base: '/'` (default Vite) → assets load from root → `file:///assets/index.js` doesn't exist. Fix: `base: './'` when `ELECTRON=true`.

### 2. IndexedDB works as-is in Electron
Electron bundles Chromium → IndexedDB/Dexie works identically to browser. NO migration needed. Data persists in `app.getPath('userData')`.

### 3. Firebase SDK works in Electron renderer
Firebase client SDK runs in Chromium renderer process — same as browser. Demo mode (isDemoMode) still works. No changes needed.

### 4. `crypto.randomUUID` ALWAYS works in Electron
Electron's Chromium is always a secure context (even without HTTPS) — `crypto.randomUUID()` is always available. The HTTP non-localhost pitfall (BUG 3) does NOT apply.

### 5. System tray icon must exist before Tray()
`new Tray(iconPath)` throws if file doesn't exist. Always create placeholder icon first.

### 6. electron-builder downloads binary on first build
First `electron-builder` run downloads ~150MB Electron binary. Subsequent builds use cache. On CI/slow connections, pre-download with `npx electron@latest` first.

### 7. NSIS installer needs .ico not .png for Windows
Electron-builder auto-converts .png → .ico, but results can be poor. Generate proper .ico with multiple sizes (16, 32, 48, 64, 128, 256) for best results.

### 8. DevTools in production builds
Don't ship `webContents.openDevTools()` in production. Guard with `if (isDev)`.

## Hardware Fingerprint (License System)
```js
// Combine multiple hardware IDs for unique machine fingerprint
const raw = `${macAddress}|${diskSerial}|${cpuId}|${hostname}`;
const hwid = crypto.createHash('sha256').update(raw).digest('hex').slice(0, 32);
// Output: "A3F2B1C4D5E6F7A8B9C0D1E2F3A4B5C6"
```

Allow 3 re-activations per year for hardware changes (fair to customer).

## License Server (Cloudflare Workers — FREE tier)
Lightweight API for license validation. 100K requests/day free.
```
POST /api/activate   { licenseKey, hardwareId } → { activationCode, tier }
POST /api/validate   { activationCode, hardwareId } → { valid, tier, daysLeft }
POST /api/deactivate { activationCode, hardwareId } → { success }
```
Database: Cloudflare D1 (SQLite, 5GB free).

## License Flow in App
```
App Start → license.dat exists?
  YES → hardware match + not expired? → ✅ Full access
  NO  → trial mode (30 days from first launch, stored in localStorage)
         → trial expired? → ❌ Lock app, show activation page
```

Activation page: show HWID → user inputs license key → calls license server → saves activation to license.dat.

## Cost: Rp 0 at launch
- Electron: open source, free
- electron-builder: open source, free  
- Cloudflare Workers: free tier (100K req/day)
- Cloudflare D1: free (5GB)
- GitHub Releases: free (host installer files)
- Code signing: ~Rp 3jt/year (optional, later)
