# Electron Implementation Patterns (Phase 1-3 Actual Code)

> Real implementation patterns from converting Omni POS to desktop app. Phase 1-3 completed successfully.

## Phase 1: Core Setup (Completed)

### electron/main.js — Window with state persistence
```js
import { app, BrowserWindow, ipcMain, Menu, Tray, globalShortcut, dialog } from 'electron';
import { loadWindowState, saveWindowState } from './utils/windowState.js';

function createWindow() {
  const windowState = loadWindowState();  // Restore position/size
  
  mainWindow = new BrowserWindow({
    x: windowState.x,
    y: windowState.y,
    width: windowState.width,
    height: windowState.height,
    minWidth: 1024,
    minHeight: 768,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    icon: path.join(__dirname, '../build/icon.png'),
    show: false,  // Prevent flash
  });

  if (windowState.isMaximized) mainWindow.maximize();

  // Load dev or production
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.once('ready-to-show', () => mainWindow.show());

  // Save state on move/resize
  mainWindow.on('resize', () => saveWindowState(mainWindow));
  mainWindow.on('move', () => saveWindowState(mainWindow));

  // Minimize to tray instead of close
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });
}
```

### electron/utils/windowState.js — Persist window position/size
```js
import { app } from 'electron';
import fs from 'fs';
import path from 'path';

const WINDOW_STATE_FILE = path.join(app.getPath('userData'), 'window-state.json');

export function loadWindowState() {
  try {
    if (fs.existsSync(WINDOW_STATE_FILE)) {
      return JSON.parse(fs.readFileSync(WINDOW_STATE_FILE, 'utf-8'));
    }
  } catch (error) {}
  
  return { x: undefined, y: undefined, width: 1280, height: 800, isMaximized: false };
}

export function saveWindowState(window) {
  const bounds = window.getBounds();
  const state = {
    x: bounds.x, y: bounds.y,
    width: bounds.width, height: bounds.height,
    isMaximized: window.isMaximized(),
  };
  fs.writeFileSync(WINDOW_STATE_FILE, JSON.stringify(state, null, 2));
}
```

## Phase 2: Native Features (Completed)

### System Tray
```js
function createTray() {
  const iconPath = path.join(__dirname, '../build/icon.png');
  tray = new Tray(iconPath);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show Omni POS',
      click: () => { mainWindow?.show(); mainWindow?.focus(); },
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => { app.isQuitting = true; app.quit(); },
    },
  ]);

  tray.setToolTip('Omni POS');
  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    if (mainWindow?.isVisible()) mainWindow.focus();
    else mainWindow?.show();
  });
}
```

### Keyboard Shortcuts (globalShortcut API)
```js
function registerShortcuts() {
  globalShortcut.register('F1', () => mainWindow?.webContents.send('shortcut:pos'));
  globalShortcut.register('F2', () => mainWindow?.webContents.send('shortcut:products'));
  globalShortcut.register('F3', () => mainWindow?.webContents.send('shortcut:customers'));
  globalShortcut.register('F4', () => mainWindow?.webContents.send('shortcut:reports'));
  globalShortcut.register('CommandOrControl+P', () => mainWindow?.webContents.send('shortcut:print'));
  globalShortcut.register('CommandOrControl+Shift+F', () => {
    mainWindow?.setFullScreen(!mainWindow.isFullScreen());
  });
}

// Unregister on quit
app.on('will-quit', () => globalShortcut.unregisterAll());
```

Renderer listens via preload:
```js
// preload.js
onShortcut: (shortcut, callback) => ipcRenderer.on(`shortcut:${shortcut}`, callback),
```

```tsx
// React component
useEffect(() => {
  window.electronAPI?.onShortcut('pos', () => navigate('/pos'));
}, []);
```

### Auto-Start on Windows (PowerShell shortcut)
```js
import { exec } from 'child_process';

export function enableAutoStart() {
  if (process.platform !== 'win32') return { success: false, error: 'Platform not supported' };

  const appPath = process.execPath;
  const appFolder = path.dirname(appPath);
  const startupFolder = path.join(process.env.APPDATA, 'Microsoft\\Windows\\Start Menu\\Programs\\Startup');
  const shortcutPath = path.join(startupFolder, 'Omni POS.lnk');
  
  // Create batch file to launch app
  const batchContent = `@echo off\nstart "" "${appPath}"\n`;
  const batchPath = path.join(appFolder, 'autostart.bat');
  fs.writeFileSync(batchPath, batchContent);
  
  // Create shortcut using PowerShell
  const psCommand = `$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('${shortcutPath}'); $Shortcut.TargetPath = '${batchPath}'; $Shortcut.Save()`;
  
  exec(`powershell -Command "${psCommand}"`, (error) => {
    if (error) logger.error('Failed to create auto-start shortcut:', error.message);
  });
  
  return { success: true };
}

export function disableAutoStart() {
  const shortcutPath = path.join(process.env.APPDATA, 'Microsoft\\Windows\\Start Menu\\Programs\\Startup', 'Omni POS.lnk');
  if (fs.existsSync(shortcutPath)) fs.unlinkSync(shortcutPath);
  return { success: true };
}
```

### Thermal Printer Detection (USB)
```bash
npm install node-thermal-printer usb
```

```js
// electron/printer/detect.js
import { getDeviceList } from 'usb';

export async function detectUSBPrinters() {
  const devices = getDeviceList();
  const printers = [];

  for (const device of devices) {
    const descriptor = device.deviceDescriptor;
    
    // Class 7 = printer
    if (descriptor.bDeviceClass === 7 || descriptor.bInterfaceClass === 7) {
      printers.push({
        vendorId: descriptor.idVendor,
        productId: descriptor.idProduct,
        port: `usb:${descriptor.idVendor}:${descriptor.idProduct}`,
      });
    }
  }
  return printers;
}
```

### Thermal Printer ESC/POS Commands
```js
// electron/printer/thermal.js
import { ThermalPrinter, PrinterTypes } from 'node-thermal-printer';

export async function printReceiptUSB(printerPort, receiptData) {
  const [, vendorId, productId] = printerPort.split(':');
  
  const printer = new ThermalPrinter({
    type: PrinterTypes.EPSON,
    interface: `usb:${vendorId}:${productId}`,
  });

  const isConnected = await printer.isPrinterConnected();
  if (!isConnected) throw new Error('Printer not connected');

  // Store name (centered, bold, larger)
  printer.alignCenter();
  printer.bold(true);
  printer.setTextSize(1, 2);
  printer.println(receiptData.storeName);
  printer.setTextSize(1, 1);
  printer.bold(false);

  // Items
  printer.alignLeft();
  receiptData.items.forEach(item => {
    printer.leftRight(`${item.name}`, '');
    printer.leftRight(`   ${item.qty} x ${formatCurrency(item.price)}`, formatCurrency(item.total));
  });

  // Total (bold, larger)
  printer.bold(true);
  printer.setTextSize(1, 2);
  printer.leftRight('TOTAL:', formatCurrency(receiptData.total));
  printer.setTextSize(1, 1);
  printer.bold(false);

  printer.cut();
  await printer.execute();
}

// Open cash drawer (ESC p command)
export async function openCashDrawer(printerPort) {
  const printer = new ThermalPrinter({ /* ... */ });
  printer.print('\x1B\x70\x00\x19\xFA');  // ESC p m t1 t2
  await printer.execute();
}
```

## Phase 3: Backup/Restore (Completed)

### Export IndexedDB to ZIP
```bash
npm install adm-zip
```

```js
// electron/backup/export.js
import AdmZip from 'adm-zip';

export async function exportBackup(outputPath = null) {
  const mainWindow = BrowserWindow.getAllWindows()[0];
  
  // Get IndexedDB data from renderer via executeJavaScript
  const dbData = await mainWindow.webContents.executeJavaScript(`
    (async () => {
      const db = await new Promise((resolve, reject) => {
        const request = indexedDB.open('omni-pos-db', 3);
        request.onsuccess = () => resolve(request.result);
      });
      
      const data = {};
      for (const storeName of Array.from(db.objectStoreNames)) {
        const transaction = db.transaction([storeName], 'readonly');
        const store = transaction.objectStore(storeName);
        const request = store.getAll();
        await new Promise((resolve) => {
          request.onsuccess = () => { data[storeName] = request.result; resolve(); };
        });
      }
      db.close();
      return data;
    })()
  `);

  // Create ZIP
  const zip = new AdmZip();
  const manifest = { version: app.getVersion(), createdAt: new Date().toISOString() };
  zip.addFile('manifest.json', Buffer.from(JSON.stringify(manifest, null, 2), 'utf8'));

  for (const [storeName, records] of Object.entries(dbData)) {
    zip.addFile(`${storeName}.json`, Buffer.from(JSON.stringify(records, null, 2), 'utf8'));
  }

  const filename = outputPath || path.join(getBackupDirectory(), `omnipos-backup-${timestamp}.omnibackup`);
  zip.writeZip(filename);
  
  return { success: true, path: filename };
}
```

### Import ZIP to IndexedDB
```js
// electron/backup/import.js
export async function importBackup(inputPath = null) {
  // Show file dialog if no path
  if (!inputPath) {
    const result = await dialog.showOpenDialog(mainWindow, {
      filters: [{ name: 'Omni POS Backup', extensions: ['omnibackup'] }],
    });
    if (result.canceled) return { success: false, error: 'User canceled' };
    inputPath = result.filePaths[0];
  }

  // Confirm before restore (destructive!)
  const confirmResult = await dialog.showMessageBox(mainWindow, {
    type: 'warning',
    message: 'Peringatan: Restore akan menghapus semua data saat ini!',
    buttons: ['Batal', 'Restore'],
  });
  if (confirmResult.response === 0) return { success: false, error: 'User canceled' };

  // Extract ZIP
  const zip = new AdmZip(inputPath);
  const dbData = {};
  for (const entry of zip.getEntries()) {
    if (!entry.entryName.endsWith('.json') || entry.entryName === 'manifest.json') continue;
    const storeName = entry.entryName.replace('.json', '');
    dbData[storeName] = JSON.parse(entry.getData().toString('utf8'));
  }

  // Import to IndexedDB in renderer
  await mainWindow.webContents.executeJavaScript(`
    (async () => {
      // Delete old database
      indexedDB.deleteDatabase('omni-pos-db');
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Create new database with imported data
      const db = await new Promise((resolve, reject) => {
        const request = indexedDB.open('omni-pos-db', 3);
        request.onupgradeneeded = (event) => {
          const db = event.target.result;
          const stores = ${JSON.stringify(Object.keys(dbData))};
          stores.forEach(storeName => {
            if (!db.objectStoreNames.contains(storeName)) {
              db.createObjectStore(storeName, { keyPath: 'id' });
            }
          });
        };
        request.onsuccess = () => resolve(request.result);
      });
      
      // Import data
      const data = ${JSON.stringify(dbData)};
      for (const [storeName, records] of Object.entries(data)) {
        const transaction = db.transaction([storeName], 'readwrite');
        const store = transaction.objectStore(storeName);
        store.clear();
        records.forEach(record => store.add(record));
        await new Promise((resolve) => transaction.oncomplete = resolve);
      }
      db.close();
    })()
  `);

  // Restart app after 3 seconds
  setTimeout(() => { app.relaunch(); app.exit(0); }, 3000);
  
  return { success: true };
}
```

### Auto-Backup on Quit
```js
// electron/main.js
app.on('before-quit', async (event) => {
  if (!app.isQuitting && !app.hasAutoBackedUp) {
    event.preventDefault();
    app.hasAutoBackedUp = true;
    
    const result = await exportBackup();
    if (result.success) logger.info(`Auto-backup completed: ${result.path}`);
    
    app.quit();
  }
});
```

### Backup Retention (Keep 7 latest)
```js
// electron/backup/scheduler.js
const MAX_BACKUPS = 7;

export function cleanupOldBackups() {
  const backups = getBackups().backups.sort((a, b) => b.createdAt - a.createdAt);
  
  if (backups.length > MAX_BACKUPS) {
    const toDelete = backups.slice(MAX_BACKUPS);
    toDelete.forEach(backup => fs.unlinkSync(backup.path));
  }
}
```

## React UI Integration

### BackupSettings Component Pattern
```tsx
import { Card, CardContent, CardHeader } from '../ui/Card';
import { Button } from '../ui/Button';
import { Dialog, DialogHeader, DialogTitle, DialogContent, DialogFooter } from '../ui/Dialog';

export function BackupSettings() {
  const [backups, setBackups] = useState<BackupFile[]>([]);
  
  useEffect(() => {
    if (window.electronAPI) loadBackups();
  }, []);

  const handleExport = async () => {
    const result = await window.electronAPI?.exportBackup();
    if (result?.success) setMessage({ type: 'success', text: `Backup berhasil: ${result.path}` });
  };

  // Dialog component API: NO title prop, use DialogHeader + DialogTitle
  return (
    <Dialog open={showDialog} onClose={() => setShowDialog(false)}>
      <DialogHeader>
        <DialogTitle>Konfirmasi Restore</DialogTitle>
      </DialogHeader>
      <DialogContent>
        {/* content */}
      </DialogContent>
      <DialogFooter>
        <Button variant="outline" onClick={onCancel}>Batal</Button>
        <Button variant="danger" onClick={onConfirm}>Ya, Restore</Button>
      </DialogFooter>
    </Dialog>
  );
}
```

## Pitfalls Encountered

### 1. Dialog component API (no title prop)
**Error:** `Property 'title' does not exist on type 'IntrinsicAttributes & DialogProps'`

**Fix:** Use children pattern with DialogHeader + DialogTitle:
```tsx
// WRONG
<Dialog open={open} onClose={onClose} title="Judul">

// CORRECT
<Dialog open={open} onClose={onClose}>
  <DialogHeader><DialogTitle>Judul</DialogTitle></DialogHeader>
  <DialogContent>...</DialogContent>
</Dialog>
```

### 2. Date type mismatch in backup list
**Error:** `Type 'Date' is not assignable to type 'string'`

**Fix:** Convert Date objects to ISO strings when loading:
```tsx
const backupsWithStringDates = result.backups.map(b => ({
  ...b,
  createdAt: b.createdAt instanceof Date ? b.createdAt.toISOString() : String(b.createdAt)
}));
```

### 3. executeJavaScript for IndexedDB access
Main process CANNOT access IndexedDB directly (it's in renderer). Must use `webContents.executeJavaScript()` to run code in renderer context and return data to main process.

### 4. Auto-backup blocks quit
`app.on('before-quit')` event must call `event.preventDefault()` to delay quit, then call `app.quit()` after backup completes. Use flag `app.hasAutoBackedUp` to prevent infinite loop.

### 5. USB printer detection requires permissions
On Linux/macOS, USB device access may require udev rules or sudo. On Windows, drivers must be installed. Test with `lsusb` (Linux) or Device Manager (Windows) first.

## Build Commands

```bash
# Development (hot reload)
npm run electron:dev

# Build production .exe
npm run electron:build

# Test production build without building installer
npm run electron:preview
```

## File Structure (Actual)
```
omni-pos/
├── electron/
│   ├── main.js                    # Main process + IPC handlers
│   ├── preload.js                 # Context bridge API
│   ├── backup/
│   │   ├── export.js              # IndexedDB → ZIP
│   │   ├── import.js              # ZIP → IndexedDB
│   │   └── scheduler.js           # Auto backup + cleanup
│   ├── printer/
│   │   ├── detect.js              # USB printer detection
│   │   └── thermal.js             # ESC/POS thermal printing
│   └── utils/
│       ├── autoStart.js           # Windows auto-start on boot
│       ├── logger.js              # File logging
│       ├── paths.js               # App directories
│       └── windowState.js         # Window position/size persistence
├── build/
│   ├── icon.png                   # App icon (placeholder 1x1 PNG)
│   └── license.txt                # EULA text
├── src/
│   ├── components/settings/
│   │   └── BackupSettings.tsx     # Backup/restore UI
│   └── types/
│       └── electron.d.ts          # TypeScript definitions
└── electron-builder.yml           # Build config
```
