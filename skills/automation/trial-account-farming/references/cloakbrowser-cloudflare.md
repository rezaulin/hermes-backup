# CloakBrowser stealth Chromium — Cloudflare bypass recipe

Verified 2026-08 on headless Linux server (datacenter IP).

## Problem

Targets behind Cloudflare (e.g. genspark.ai) block automation:

- **Vanilla headless Chrome** → `Page crashed` on the CF JS challenge unless
  `--single-process` is passed; even with it, stuck on "Just a moment..."
  (title never changes, body = "Performing security verification").
- **Patchright** (Playwright stealth fork, `pip install patchright`) → same:
  stuck on "Just a moment..." with both its bundled chromium-headless-shell
  (page crashed) and system Chrome + `--single-process` (stuck).
- **2Captcha Browser API** (cloud browser) → works in principle but the
  browser account needs a proxy configured; with no proxy the IP is still
  flagged. Also the ws:// URL is truncated in the dashboard UI — get the full
  URL via "Generate URLs".

## What works

**CloakBrowser** stealth Chromium (patched binary) + `--single-process`.

```python
from cloakbrowser import browser as cb

ctx = cb.launch_persistent_context(
    str(profile_dir),               # per-account isolation
    headless=True,
    viewport={"width": 1366, "height": 900},
    locale="en-US", timezone="Asia/Jakarta",
    args=["--single-process", "--no-zygote", "--disable-gpu"],
    proxy={"server": "http://user:pass@host:port"},  # optional, recommended
)
page = ctx.new_page()
page.goto("https://target.com/", wait_until="domcontentloaded")
# page.title() should be the real site, not "Just a moment..."
```

## Install

```bash
pip install cloakbrowser
python3 -m cloakbrowser install   # ~206MB stealth Chromium, sig-verified
cloakbrowser info                  # verify binary path + license
```

## Key facts

- `cloakbrowser.browser.launch()` / `launch_persistent_context()` are drop-in
  replacements for Playwright's `chromium.launch` /
  `launch_persistent_context` — same kwargs (headless, proxy, viewport,
  locale, timezone, args). Return a Playwright Browser / BrowserContext.
- `stealth_args=True` by default (fingerprint spoofing).
- Free license = 1 concurrent session; more needs a key (`cloakbrowser login`).
- `--single-process` is REQUIRED on this server or the CF JS challenge crashes
  the browser ("Target crashed"). Matches the known quirk: JS-heavy pages crash
  unless `--single-process`.
- Datacenter IP still risks Google phone-verification at OAuth login; use a
  residential proxy for better account survival.

## What failed (don't retry)

- `patchright` + bundled chromium-headless-shell → page crashed / stuck on CF.
- DataImpulse proxy creds hardcoded in the original genspark bot → dead
  (`ERR_HTTP_RESPONSE_CODE_FAILURE`). Always take fresh proxy creds from the user.
