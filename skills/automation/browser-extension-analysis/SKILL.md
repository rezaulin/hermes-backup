---
name: browser-extension-analysis
description: "Analyze, deobfuscate, debug, and modify Chrome/browser extensions (.crx/.rar/.zip). Covers manifest.json v3 structure, obfuscated JS detection, autofill/payment extension troubleshooting, and extension installation in developer mode."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Browser, Extension, Chrome, Automation, Obfuscation, Autofill, Payment]
    related_skills: [browser-automation-playwright]
---

# Browser Extension Analysis & Troubleshooting

## When to Load
- User sends a browser extension file (.crx, .rar, .zip containing extension)
- User asks about Chrome/Firefox extension internals
- User reports extension features not working (autofill, auto-payment, etc.)
- User wants to install extension in developer mode
- Extension code is obfuscated and needs analysis

## Installation (Developer Mode)

```
1. Extract extension files to a folder
2. Open browser → chrome://extensions/
3. Toggle "Developer mode" ON (top right)
4. Click "Load unpacked"
5. Select the extension folder (must contain manifest.json)
```

## Extension Structure (Manifest V3)

```
extension-folder/
├── manifest.json          ← Required. Defines permissions, scripts, icons
├── icons/                 ← Extension icons (16, 48, 128px)
├── script/
│   ├── background.js      ← Service worker (runs in background)
│   ├── content.js         ← Injected into web pages
│   ├── inject.js          ← Injected into page context
│   ├── autofill.js        ← Form autofill logic
│   └── ...
├── dashboard.html         ← Extension UI page
├── styles.css             ← Extension styles
└── rules.json             ← DeclarativeNetRequest rules
```

## Common Permissions & What They Mean

| Permission | Purpose |
|------------|---------|
| `storage` | Save/load extension settings |
| `activeTab` | Access current tab |
| `scripting` | Inject scripts into pages |
| `declarativeNetRequest` | Modify/redirect network requests |
| `cookies` | Read/write browser cookies |
| `proxy` | Route traffic through proxy |
| `webRequest` | Monitor/modify network requests |
| `<all_urls>` host_permission | Run on any website |

## Obfuscated Code Detection

**Signs of obfuscation:**
- Variable names like `_0x1cb6`, `_0x5289a9`
- Large string arrays with encoded values
- Hex/unicode escapes everywhere
- Single-line minified files (100KB+ on one line)
- Self-modifying code patterns

**Approach:**
1. Don't try to fully deobfuscate — focus on entry points
2. Look for `manifest.json` content_scripts/background to understand structure
3. Check `READ_ME.txt` or documentation files first
4. Search for readable strings (URLs, function names, DOM selectors)
5. Use browser DevTools to observe runtime behavior instead of static analysis

## Troubleshooting: Extension Features Not Working

### Autofill/Auto-Payment Not Triggering

**Checklist:**
1. **Selector mismatch** — Extension uses CSS selectors to find form fields. Website DOM structure may differ from what extension expects.
2. **Config not set** — Open extension dashboard, check if payment/profile data is configured.
3. **Timing issue** — Script runs before page fully loads. Check `run_at` in manifest (`document_start` vs `document_idle`).
4. **Website blocks injection** — Some sites use CSP headers that block injected scripts.
5. **Extension disabled on that site** — Check if extension is active for current URL pattern.

**Debugging approach:**
```
1. F12 → Console tab → reload page
2. Look for extension-related errors (red text)
3. Check Network tab for blocked script injections
4. Inspect Elements tab → check if form fields have expected selectors
5. Try extension on a known-working test site first
```

### MCP Server / API Key Issues in Extensions

Some extensions connect to external APIs. Check:
- API key validity (expired?)
- Endpoint URL format (no `www.`, correct domain)
- Network connectivity (CORS, firewall)

## Pitfalls

### ⚠️ Don't trust 0-byte extraction — use full `unrar` for RAR5
Always verify extracted extension files have non-zero size. RAR5 archives (common for extensions distributed as .rar) fail SILENTLY with wrong tools, producing empty 0-byte files that look like a valid folder structure.

**Failing tools on RAR5 (silently output empty files):**
- `unrar-free` — only supports RAR 2.0, prints "unknown archive type"
- `7z`/`p7zip 16.02` — prints `ERROR: Unsupported Method` per file, writes 0-byte placeholders

**Fix (Ubuntu/Debian): install the full `unrar` package (RAR 6.x):**
```bash
apt-get install -y unrar     # full unrar 6.x, NOT unrar-free
rm -rf /tmp/extract && mkdir -p /tmp/extract
unrar x "archive.rar" /tmp/extract/ && ls -la /tmp/extract/ext-folder/script/*.js
```

**Gotcha:** After a failed extraction, `read_file` dedups based on filename + may return a stale "unchanged" result showing the 0-byte content. Force-verify with `ls -la` / `cat` via terminal rather than re-reading with `read_file`, then exarchive to a FRESH path (the empty files won't be overwritten by re-extracting to the same dir).

**Verify real content before analysis:** the extracted → analyze flow blocks silent empty-file pitfalls.
```bash
find /tmp/extract -type f -size 0 -print   # catches silent failures immediately
```

### ⚠️ Obfuscated code is not always malicious
Many commercial extensions obfuscate to protect IP. Focus on behavior analysis (what it does at runtime) rather than trying to read every line.

### ⚠️ Payment autofill rarely works universally
Every payment page has different DOM structure. Extensions that claim "universal autofill" usually only work on popular platforms (Stripe, PayPal, Shopify). Custom sites need custom selectors.

## Related Skills
- `browser-automation-playwright` — For programmatic browser automation
- `ocr-and-documents` — For extracting documents before analysis
