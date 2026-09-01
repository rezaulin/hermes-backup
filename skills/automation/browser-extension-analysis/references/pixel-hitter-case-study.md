# Pixel Hitter Extension Case Study

## Overview
Pixel Hitter (PIXEL HITER v.1.2litex) is an automation browser extension with autofill, proxy handling, and captcha solving capabilities.

## Manifest V3 Structure
```json
{
  "manifest_version": 3,
  "name": "PIXEL HITER: v.1.2litex",
  "permissions": [
    "storage", "activeTab", "scripting",
    "declarativeNetRequest", "proxy", "webRequest",
    "cookies", "tabs", "webNavigation"
  ],
  "host_permissions": ["<all_urls>"],
  "background": {
    "service_worker": "script/background.js"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["script/content.js"],
      "run_at": "document_start",
      "all_frames": true
    }
  ]
}
```

## Heavily Obfuscated Code
The extension uses heavy obfuscation:
- Variable names: `_0x1cb6`, `_0x5289a9`, `_0x27be1c`
- String arrays with encoded values
- Self-modifying code patterns
- Hex/unicode escapes throughout

**Analysis approach:** Don't try to deobfuscate. Focus on:
1. Manifest structure (what permissions/scripts)
2. Runtime behavior (DevTools observation)
3. User-facing config (dashboard)

## Auto-Payment Troubleshooting

### User Issue
Extension installed successfully, but "auto payment" feature not working.

### Root Cause Analysis
1. **Selector mismatch** — Extension expects specific DOM selectors for payment forms. Target website structure differs.
2. **No config set** — Dashboard empty, no payment profile configured.
3. **Obfuscated logic** — Cannot easily trace where payment detection fails.

### Solution Path
1. **Check dashboard** — Click extension icon, open dashboard, verify payment data configured
2. **Console errors** — F12 → Console → look for extension errors on payment page
3. **Test on known site** — Try extension on demo.stripe.dev or sandbox.paypal.com first
4. **Inspect DOM** — Check if target site's payment form uses expected field names/IDs

## Key Takeaway
For heavily obfuscated commercial extensions:
- Don't waste time deobfuscating
- Focus on configuration and runtime debugging
- Test on known-working platforms first
- Use DevTools to observe actual behavior
