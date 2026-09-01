# Portable .exe vs Installer .exe

## Perbedaan Utama

| Aspek | Installer (NSIS) | Portable |
|-------|------------------|----------|
| File size | ~150MB | ~150-200MB |
| Perlu install | ✅ Ya (wizard) | ❌ Tidak |
| Admin rights | ✅ Perlu | ❌ Tidak perlu |
| Data location | `%AppData%/Omni POS/` | Sebelah .exe (folder sama) |
| Uninstall | Via Control Panel | Delete folder |
| Auto-update | Gampang (electron-updater) | Ribet (manual replace) |
| Use case | Production, client deployment | Testing, demo, USB carry |
| Professional | ✅ Ya (kayak software komersial) | ⚠️ Kurang |

## User Confusion Signal

Kalau user tanya **"berarti bukan exe one click?"** atau **"yang langsung jalan tanpa install"**, itu tandanya:
1. User bingung antara installer vs portable
2. User sebenarnya mau portable (tinggal double-click)
3. Jangan langsung asumsikan installer yang "benar" — tanyakan use case

## electron-builder.json Config (Portable + Installer)

```json
{
  "win": {
    "target": [
      { "target": "nsis", "arch": ["x64"] },
      { "target": "portable", "arch": ["x64"] }
    ],
    "icon": "build/icon.png"
  },
  "portable": {
    "artifactName": "OmniPOS-Portable-${version}.${ext}",
    "requestExecutionLevel": "user"
  },
  "nsis": {
    "oneClick": false,
    "allowToChangeInstallationDirectory": true,
    "createDesktopShortcut": true
  }
}
```

Build command:
```bash
# Both
npx electron-builder --win

# Portable only
npx electron-builder --win portable

# Installer only
npx electron-builder --win nsis
```

## Portable Data Location

Portable version simpan data di folder yang sama dengan .exe (bukan AppData):

```
OmniPOS-Portable.exe
├── data/
│   ├── omni-pos.db
│   ├── settings.json
│   └── license.key
└── backups/
    └── backup-*.omnibackup
```

**Important:** Kalau user copy .exe ke komputer lain, semua data ikut. Ini bisa jadi PRO (portable) atau CON (security risk).

## Testing dengan Portable

Portable lebih cocok buat testing karena:
- Gak perlu admin rights
- Gak perlu install
- Bisa test di multiple machines
- Gampang cleanup (tinggal delete)

Setelah testing selesai dan siap production, switch ke installer.

## One-Click Install (Alternative)

Kalau user mau installer tapi tanpa wizard (one-click install):

```json
"nsis": {
  "oneClick": true,
  "allowToChangeInstallationDirectory": false,
  "perMachine": false
}
```

Ini tetep installer (ada shortcut, uninstaller, dll) tapi tanpa user interaction.
