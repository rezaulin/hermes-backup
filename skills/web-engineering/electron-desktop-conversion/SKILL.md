---
name: electron-desktop-conversion
description: Convert web apps (Vite/React/PWA) to desktop .exe using Electron. Covers architecture (main/preload/renderer), IPC patterns, TypeScript pitfalls, license/HWID systems, backup/restore, auto-updater, and electron-builder packaging.
triggers:
  - convert to exe
  - electron app
  - desktop app
  - electron wrapper
  - hwid license
  - electron-builder
  - convert pwa to desktop
  - aplikasi desktop
  - installer exe
---

# Electron Desktop Conversion

Convert existing web apps (Vite + React + PWA) to native Windows desktop applications using Electron.

## When to Use

- User wants to wrap existing web app as desktop .exe
- Need offline-first with hardware binding (license/HWID)
- Need native features: system tray, printer detection, keyboard shortcuts, auto-start
- Target: Windows installer (.exe) via electron-builder

## Architecture Pattern

```
electron/
├── main.js              # Main process (window, tray, IPC handlers)
├── preload.js           # Context bridge (expose APIs to renderer)
├── utils/
│   ├── paths.js         # App directories (userData, databases, backups)
│   ├── logger.js        # File-based logging
│   └── windowState.js   # Remember window position/size
├── printer/
│   ├── detect.js        # USB/system printer detection
│   └── thermal.js       # ESC/POS thermal printing
├── license/
│   ├── hardware.js      # HWID generation (MAC + Disk + CPU + Hostname)
│   ├── storage.js       # Encrypted license file (AES-256-CBC)
│   ├── validator.js     # Check license status (trial/active/expired/locked)
│   └── activator.js     # Online activation flow
└── backup/
    ├── export.js        # IndexedDB → ZIP backup
    ├── import.js        # ZIP → IndexedDB restore
    └── scheduler.js     # Auto-backup on app close
```

## Key Implementation Steps

### 1. Electron Setup
```bash
npm install --save-dev electron electron-builder concurrently wait-on cross-env
```

### 2. IPC Pattern (Main ↔ Renderer)
**Main process (electron/main.js):**
```javascript
ipcMain.handle('license:status', () => {
  return getLicenseStatus();
});
```

**Preload (electron/preload.js):**
```javascript
contextBridge.exposeInMainWorld('electronAPI', {
  getLicenseStatus: () => ipcRenderer.invoke('license:status'),
});
```

**Renderer:**
```typescript
const status = await window.electronAPI.getLicenseStatus();
```

### 3. TypeScript Integration
- Add `src/types/electron.d.ts` with full `ElectronAPI` interface
- Declare `window.electronAPI?: ElectronAPI` in global scope
- Use type narrowing when accessing union type properties

### 4. Build Configuration
```json
{
  "main": "electron/main.js",
  "scripts": {
    "electron:dev": "concurrently \"vite\" \"wait-on http://localhost:5173 && electron .\"",
    "electron:build": "vite build && electron-builder"
  }
}
```

### 5. Hardware ID Generation
Combine multiple hardware identifiers for uniqueness:
- MAC address (primary network interface)
- Disk serial number
- CPU ID
- Hostname

Hash with SHA-256, take first 16 chars.

### 6. License File Encryption
Use AES-256-CBC with random IV:
```javascript
const iv = crypto.randomBytes(16);
const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
```
Store encrypted in `userData/license.dat` with backup at `license.bak`.

### 7. Backup System
- Export: Serialize all Dexie tables → JSON → ZIP (.omnibackup)
- Import: Unzip → parse JSON → bulkPut to Dexie
- Auto-backup: Trigger on `app.on('before-quit')`
- Retention: Keep last 7 backups, delete older

## Common Pitfalls

### TypeScript Strict Mode Issues

**Problem:** Union types cause property access errors
```typescript
// ❌ ERROR: Property 'tier' does not exist on type '{ success: boolean; error: string; }'
if (result.success) {
  console.log(result.tier); // TypeScript error
}

// ✅ FIX: Type narrowing
if (result.success && 'tier' in result) {
  console.log(result.tier);
}
```

**Problem:** Unused variables in strict mode
```typescript
// ❌ ERROR: 'loading' is declared but never read
const { license, loading } = useLicense();

// ✅ FIX: Remove unused or use underscore prefix
const { license } = useLicense();
```

**Problem:** Missing required properties
```typescript
// ❌ ERROR: Property 'hwid' is missing
setLicense(status);

// ✅ FIX: Add missing property
const hwid = await window.electronAPI.getHWID();
setLicense({ ...status, hwid });
```

### JavaScript vs TypeScript Syntax Confusion

**Problem:** Using TypeScript syntax in .js files
```javascript
// ❌ ERROR in preload.js (JavaScript file)
exportBackup: (path?: string) => ipcRenderer.invoke('backup:export', path)

// ✅ FIX: Remove type annotations in .js files
exportBackup: (path) => ipcRenderer.invoke('backup:export', path)
```

### JSX Nesting Errors

**Problem:** Forgetting closing tags when wrapping components
```tsx
// ❌ ERROR: JSX element 'LicenseGuard' has no corresponding closing tag
<LicenseGuard>
  <BrowserRouter>
    <Routes>...</Routes>
  </BrowserRouter>
// Missing </LicenseGuard>

// ✅ FIX: Close all tags
<LicenseGuard>
  <BrowserRouter>
    <Routes>...</Routes>
  </BrowserRouter>
</LicenseGuard>
```

### Duplicate Type Definitions

**Problem:** Copy-paste creates duplicate method signatures
```typescript
// ❌ ERROR: Duplicate property 'activateLicense'
interface ElectronAPI {
  activateLicense: (key: string, code: string) => Promise<...>;
  // ... 50 lines later ...
  activateLicense: (key: string) => Promise<...>;
}

// ✅ FIX: Single source of truth, delete duplicates
```

## Critical Pitfall: Verify Before Claiming Done

**NEVER claim code "berfungsi" or "works" without running `npm run build` first.**

User will ask: "kamu sudah yakin kalau file kita ini berfungsi?"

This question means:
1. You probably made a mistake somewhere
2. You should have tested before claiming completion
3. Run the build NOW and fix all errors

**Workflow:**
```
1. Write code
2. Run: npm run build (or npx tsc --noEmit for TypeScript only)
3. Fix ALL errors (not just "most")
4. Run build again until 0 errors
5. THEN claim it works
```

**Common TypeScript strict mode errors to watch for:**
- Union type property access without type narrowing
- Unused variables (TS6133)
- Missing required properties in object literals
- Duplicate interface property definitions
- JSX nesting mismatches (opening/closing tags)

**Example:**
```bash
# ❌ WRONG: Claim "done" without testing
"Bos, Phase 4 License System udah selesai! 🎉"

# User asks: "kamu sudah yakin kalau file kita ini berfungsi?"

# Run build:
npm run build
# Result: 8 TypeScript errors 😅

# ✅ RIGHT: Test first, then claim
npm run build
# Fix all errors
npm run build  
# 0 errors
# "Bos, build sukses, siap test manual!"
```

### ⚠️ electron-builder NSIS: Verify all referenced files exist before build

**Problem:** NSIS installer build fails with cryptic "cannot find specified resource" errors when `electron-builder.yml` references files that don't exist.

**Real session error:**
```
⨯ cannot find specified resource "build/installer-icon.ico",
nor relative to "/root/omni-pos/build", neither relative to project dir
```

**Root cause:** Config referenced `installerIcon`, `uninstallerIcon`, and `installerHeaderIcon` pointing to `.ico` files that were never created. Only `icon.png` existed in `build/`.

**Prevention checklist before running `electron:build`:**
1. Read `electron-builder.yml` carefully
2. For every file path referenced (icons, license, etc.), verify it exists with `ls`
3. If `.ico` files are referenced but only `.png` exists, either:
   - Convert `.png` to `.ico` (online converter or imagemagick)
   - Remove the reference from config (electron-builder will use default)
4. Check `build/` directory contains all referenced assets

**Minimal working config (no custom .ico needed):**
```yaml
win:
  icon: build/icon.png
  target: [nsis, portable]
  forceCodeSigning: false

nsis:
  oneClick: false
  perMachine: false
  allowToChangeInstallationDirectory: true
  createDesktopShortcut: true
  createStartMenuShortcut: true
  license: build/license.txt
  # Do NOT reference .ico files unless you created them
```

**If NSIS build fails with "cannot find resource":**
```bash
# 1. Check what files exist
ls -la build/

# 2. Check what config references
grep -E "icon|license" electron-builder.yml

# 3. Remove references to non-existent files, then rebuild
npm run electron:build -- --win
```

**Note:** Build failures from disk-full or CPU overload are common on resource-constrained servers. Always check `df -h` and `uptime` before starting a build.

### ⚠️ Native module VERSION compatibility — pin versions that match your code's API

**Problem:** A native module is in `dependencies` and included in the asar, but crashes at runtime because the installed version has a different API than what the code imports:

```
SyntaxError: The requested module 'usb' does not provide an export named 'getDeviceList'
```

**Real session error:** Code used `import { getDeviceList, usb } from 'usb'` (v2.x API), but `npm install usb` pulled v3.0.1 which only exports `usb`, `webusb`, `WebUSB` — completely different API surface.

**Prevention checklist:**
```bash
# 1. Check what version is installed
npm list <package>

# 2. Check what the code actually imports
grep -rn "from ['\"]<package>['\"]" electron/

# 3. Verify the exports match
node -e "const m = require('<package>'); console.log(Object.keys(m))"

# 4. Pin the compatible version if needed
npm install <package>@<compatible-version>
```

**Example — `usb` package:**
- v2.x: exports `getDeviceList`, `usb` (legacy API used by node-thermal-printer)
- v3.x: exports `usb`, `webusb`, `WebUSB` (WebUSB API, breaking change)
- **Fix:** `npm install usb@2.13.0` (or whatever version matches your code)

**Key rule:** After installing a native module, ALWAYS verify the exports match what your code imports. Major version bumps often mean breaking API changes. Pin the version explicitly in `package.json`.

**After fixing version, rebuild:**
```bash
npm run electron:build -- --win
```

### ⚠️ Native Node modules must be in `dependencies` — not just installed locally

**Problem:** A native module like `usb` is imported in Electron main process code (e.g., `electron/printer/detect.js`) but is NOT listed in `package.json` dependencies. It works during dev (because it's in `node_modules/`), but electron-builder won't include it in the asar, causing a runtime crash on the target machine:

```
Error [ERR_MODULE_NOT_FOUND]: Cannot find package 'usb' imported from
C:\Users\...\resources\...\detect.js
```

**Root cause:** electron-builder only packages modules listed in `dependencies` (not `devDependencies`). If a module was installed via `npm install` but not saved to `package.json`, or was installed as `--save-dev`, it won't be included.

**Pre-build checklist:**
```bash
# 1. Grep for all imports in electron/ main process code
grep -rh "from ['\"]" electron/ | grep -oP "from ['\"]([^'\"]+)['\"]" | sort -u

# 2. Verify each is in dependencies (not devDependencies)
cat package.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('\n'.join(d.get('dependencies',{}).keys()))"

# 3. Install any missing ones properly
npm install <package>  # NOT --save-dev for runtime deps used in electron main process
```

**Key rule:** ANY npm package imported in `electron/*.js` main process files MUST be in `dependencies`, not `devDependencies`. This includes native modules (`usb`, `serialport`, `better-sqlite3`, `node-thermal-printer`) and pure-JS packages alike.

**After adding the package, always rebuild** — native modules need platform-specific binaries:
```bash
npm run electron:build -- --win
```

### ⚠️ Wine required for cross-platform NSIS builds on Linux

**Problem:** Building Windows NSIS installer (.exe) on Linux fails with:
```
⨯ wine process failed ENOENT
Exit code: ENOENT. spawn wine ENOENT
```

**Root cause:** electron-builder uses Wine to run NSIS's `makensis.exe` (a Windows binary) on Linux.

**Fix (Ubuntu/Debian):**
```bash
dpkg --add-architecture i386
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y wine64 wine32
wine --version  # verify: wine-6.0.3+
```

**Build sequence on Linux for Windows target:**
```bash
# 1. Ensure Wine is installed
wine --version || (dpkg --add-architecture i386 && apt-get update && apt-get install -y wine64 wine32)

# 2. Build
npm run electron:build -- --win

# 3. Output will be in release/
ls -lh release/*.exe
```

**Note:** Wine is only needed for NSIS (installer) and portable targets. If building `--dir` (unpacked only) or AppImage for Linux, Wine is not needed.

### ⚠️ BrowserRouter breaks in Electron — must use HashRouter for `file://` protocol

**Problem:** App opens with a blank/black screen after install. No console errors visible to user.

**Root cause:** React Router's `BrowserRouter` uses the History API which requires a web server. Electron loads `index.html` via `file://` protocol — `BrowserRouter` cannot resolve routes without a server, resulting in a blank page.

**Real session error:** OmniPOS built successfully, installer ran fine, but app showed blank black screen on Windows. The `BrowserRouter` couldn't handle `file:///C:/Users/.../resources/app.asar/dist/index.html`.

**Fix — auto-detect Electron and switch router:**
```tsx
import { BrowserRouter, HashRouter, Routes, Route } from 'react-router-dom'

const isElectron = navigator.userAgent.toLowerCase().includes('electron')
const Router = isElectron ? HashRouter : BrowserRouter

function App() {
  return (
    <Router>
      <Routes>...</Routes>
    </Router>
  )
}
```

**Why this works:**
- `HashRouter` uses URL hash fragments (`/#/dashboard`) which work with `file://` protocol
- `BrowserRouter` uses clean URLs (`/dashboard`) which need a server to resolve
- Auto-detection means the same codebase works in both browser and Electron

**Pre-build checklist for routing:**
1. Check if app uses `BrowserRouter` — `grep -r "BrowserRouter" src/`
2. If yes, add auto-detection with `HashRouter` fallback for Electron
3. Verify `vite.config.ts` sets `base: './'` for Electron builds (relative paths)
4. Test the built `.exe` — blank screen is the #1 symptom of wrong router

### ⚠️ Vite build can overwrite root `index.html` if outDir misconfigured

**Problem:** `npm run electron:build` fails with:
```
Error: Failed to resolve ./assets/index-D5R_-dmr.js from /root/omni-pos/index.html
```

**Root cause:** A previous build wrote output assets directly to root `index.html`, replacing the source entry point (`<script type="module" src="/src/main.tsx">`) with built asset references (`<script src="./assets/index-D5R_-dmr.js">`).

**Fix:** Always verify root `index.html` contains the source entry:
```html
<!-- CORRECT: source entry point -->
<script type="module" src="/src/main.tsx"></script>

<!-- WRONG: build output leaked into root -->
<script type="module" src="./assets/index-D5R_-dmr.js"></script>
```

**Prevention:** Ensure `vite.config.ts` has `build.outDir: 'dist'` (not root). If root `index.html` gets corrupted, restore it from git or rewrite with the source script tag.

## Verification Before Production

**ALWAYS test manually before deploying to clients:**

1. Build installer on Windows machine
2. Install and run
3. Verify all Electron features work:
   - Hardware ID generation
   - License file encryption/decryption
   - Backup/restore cycle
   - Printer detection
   - Auto-backup on app close
4. Test edge cases:
   - Corrupted license file
   - Network timeout during activation
   - Low disk space during backup

**Build command:**
```bash
npm run electron:build
# Output: release/OmniPOS-Setup-1.0.0.exe
```

## License Tier Structure

| Tier | Features | Price Range |
|------|----------|-------------|
| Trial | All features, 30 days, watermark | Free |
| Basic | POS, Products, Customers, Reports | Rp 2.5jt |
| Pro | + Inventory, Export, Loyalty | Rp 5jt |
| Enterprise | + Accounting, PO/Supplier, Returns, Multi-warehouse | Rp 10jt |

## References

- See `references/electron-ipc-patterns.md` for detailed IPC examples
- See `references/license-server-cloudflare-worker.md` for server implementation
- See `references/testing-checklist.md` for manual testing guide
