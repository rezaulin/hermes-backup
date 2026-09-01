---
name: web-app-source-extraction
description: >
  Extract deployed source code and assets from hosted web apps
  (Firebase Hosting, Vercel, Netlify, Cloudflare Pages, etc.).
  Trigger when user asks to pull/download/clone code from a live
  deployed URL, Firebase Hosting project, or any static site host.
  Covers static asset extraction, SPA fallback detection, bundle
  analysis, and Firestore/database data access patterns.
tags:
  - firebase
  - hosting
  - scraping
  - spa
  - web-app
  - source-code
  - firestore
---

# Web App Source Extraction

Pull deployed code and assets from hosted web applications. Works for Firebase Hosting, Vercel, Netlify, Cloudflare Pages, GitHub Pages, and any static site host.

## Trigger Conditions

- User shares a hosting URL and asks to "pull", "download", "clone", or "tarik" the code
- User wants source code from a Firebase/Vercel/Netlify project
- User wants to inspect or reverse-engineer a deployed web app
- User asks to extract data from Firestore or similar hosted databases

## Workflow

### Step 1: Reconnaissance

1. Navigate to the URL in browser, capture full HTML
2. Identify all linked assets from `<head>` and `<body>`:
   - JS bundles: `<script src="/assets/...">`
   - CSS: `<link href="/assets/...">`
   - PWA: `manifest.webmanifest`, icons, service workers
   - Fonts, images, other static resources
3. Note the build tool (Vite, webpack, Create React App) from asset naming patterns

### Step 2: Download Static Assets

```bash
mkdir -p output/assets
# Download index.html
curl -s -o output/index.html https://<url>/
# Download JS/CSS bundles (from Step 1)
curl -s -o output/assets/<bundle>.js https://<url>/assets/<bundle>.js
curl -s -o output/assets/<bundle>.css https://<url>/assets/<bundle>.css
# Download PWA assets
curl -s -o output/manifest.webmanifest https://<url>/manifest.webmanifest
curl -s -o output/favicon.png https://<url>/favicon.png
```

### Step 3: Verify Downloads (CRITICAL — SPA Fallback Trap)

⚠️ **Pitfall**: Most SPA hosts use rewrite rules that return `index.html` for ANY unknown path with HTTP 200. This means `robots.txt`, `firebase.json`, `sitemap.xml`, or non-existent icon paths all appear to "succeed" but actually return the SPA shell.

**Detection**:
```bash
# Check if downloaded file is actually HTML (SPA fallback)
head -1 output/some-file.ext
# If it starts with <!doctype html> → it's the SPA fallback, delete it
# Also use `file` command to verify actual file type
file output/pwa-192x192.png  # may reveal it's actually JPEG
```

**Rule**: Any path not explicitly referenced in `index.html` or `manifest.webmanifest` is likely a SPA fallback. Delete these.

### Step 4: Bundle Analysis

For minified JS bundles:
- **Firebase config** — search for `apiKey`, `authDomain`, `projectId`, `initializeApp` patterns. Often externalized via env vars and absent from production bundles.
- **API endpoints** — grep for URL patterns, route definitions
- **Lazy chunks** — search for dynamic `import()` patterns referencing other asset paths
- **Route mapping** — SPA routes are client-side; server returns same HTML for all routes

```python
import re
with open('bundle.js', 'r', errors='ignore') as f:
    js = f.read()
# Find Firebase-related strings
for pattern in [r'"[A-Za-z0-9_-]+\.firebaseapp\.com"', r'"AIza[A-Za-z0-9_-]{35}"', r'projectId\s*:\s*"([^"]+)"']:
    matches = re.findall(pattern, js)
    if matches: print(f"{pattern}: {matches[:5]}")
```

### Step 5: Firestore / Database Data Access

If user also wants database data, credentials are required:

| Access Method | What's Needed | Approach |
|---|---|---|
| Service account key | JSON from Firebase Console → Project Settings → Service Accounts | Use Firebase Admin SDK |
| Web API key | From Firebase Console → Project Settings → General | Firestore REST API |
| App login credentials | Username/password for the web app | Login → extract auth token → query Firestore |
| Bundle inspection | No credentials | Search JS bundle for config (rarely present in prod) |

**Firestore REST API pattern** (with API key):
```bash
# List collections
curl "https://firestore.googleapis.com/v1/projects/<project-id>/databases/(default)/documents?key=<api-key>"
# Get specific document
curl "https://firestore.googleapis.com/v1/projects/<project-id>/databases/(default)/documents/<collection>/<doc-id>?key=<api-key>"
```

## Extracting a design system to restyle another app

When the goal isn't the code but the *look* — user wants app B to match the look of
deployed app A — the production CSS bundle is the whole design spec. See
`references/design-system-extraction.md`: pull `:root{}` tokens + component classes,
port into the target (for Tailwind v4, tokens go in BOTH `@theme{}` and `:root{}`),
then verify with side-by-side screenshots.

## Common Hosting Patterns

| Host | Asset location | Rewrite behavior |
|---|---|---|
| Firebase Hosting | `/assets/<hash>.<ext>` | SPA rewrite returns index.html for unknown paths |
| Vercel | `/_next/static/...` (Next.js) | Fallback to index.html |
| Netlify | `/assets/<hash>.<ext>` (Vite) or hashed filenames | Redirect rules configurable |
| Cloudflare Pages | Various, often hashed | SPA fallback configurable |

## Limitations

- **Source code recovery**: Minified/bundled JS cannot be un-bundled into original source components. You get the production artifact, not the dev source.
- **Server-side code**: Cloud Functions, backend APIs, security rules are NOT accessible from the client side.
- **Environment variables**: Typically stripped from production bundles or replaced at build time.
