---
name: sim-mubtadiat-rapot-print-layout-fix
category: web-engineering
description: Fix raport HTML/CSS print layout issues (line width, spacing, visibility)
---

# SIM Mubtadiat Raport Print Layout Fix

## New Pattern (2026-08-26)

### Header Container Class

Use `.header-container` for balanced logo/title layout:

```css
.header-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
}

.header-logo { width: 75px; height: auto; }
.header-title { text-align: center; flex-grow: 1; direction: rtl; }
.header-divider { border-top: 2px solid #000; margin: 10px 0 6px 0; }
.year-text { text-align: center; direction: rtl; font-size: 14px; font-weight: bold; }
```

HTML Template:
```html
<div class="header-container">
  <img src="/logo-raport-bw-v5.png" class="header-logo">
  <div class="header-title">
    <h2>كشف الدرجات الدراسية</h2>
    <h3 data-field="semester-title">فصل الدراسة الثانية</h3>
    <p data-field="madrasah-line">المدرسة...</p>
  </div>
  <div style="width: 75px;"></div> <!-- Spacer -->
</div>
<hr class="header-divider">
<div class="year-text">سنة : ...</div>
```

### Identity Table Pattern

Fixed-width labels for colon alignment:

```html
<table class="identity-table">
  <tr><td class="lbl">Nama</td><td class="colon">:</td><td class="val"><strong data-field="nama"></strong></td></tr>
  <!-- etc -->
</table>
```

```css
.identity-table td.lbl { width: 90px; }
.identity-table td.colon { width: 10px; text-align: center; }
```

**Trigger:** When user reports misaligned identity fields or unbalanced header.

### Issue 1: Line Too Long (Mepet Logo)

**Symptom:** Horizontal line after school name touches logo on right side.

**Fix:** Reduce `width` from 75% to 50-55%, add `min-width` fallback:

```css
/* BEFORE */
<hr style="border:none;height:1px;background-color:#000;margin:3px auto;width:75%;">

/* AFTER */
<hr style="border:none;height:2px;background-color:#000;margin:2px auto 8px auto;width:55%; min-width: 120px;">
```

Changes:
- `width:55%` → shorter line (was 75%)
- `height:2px` → thicker line (was 1px)  
- `margin:2px auto 8px auto` → tighter top spacing, ~8px gap below (was 3px only)

### Issue 2: Line Missing in Print Preview

**Symptom:** Line visible on screen but disappears when printing/printing to PDF.

**Fix:** Add explicit print media query:

```css
@media print {
    .rapot-sheet hr {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
        display: block !important;
    }
}
```

Key flags:
- `print-color-adjust: exact` → force background color rendering
- `display: block !important` → override any hidden state

---

## Implementation Pattern

1. **Patch source file** (`/opt/simmubtadiat/frontend/rapot.html`)
   - Locate `<hr>` tag in template (around line 534)
   - Modify inline styles OR add CSS rule

2. **Add print media support**
   - Insert `@media print` block with HR visibility rules
   - Position after `.rapot-sheet` definition (around line 76)

3. **Rebuild Docker image**
   ```bash
   cd /opt/simmubtadiat
   docker build -t simmubtadiat-app . --no-cache
   ```

4. **Restart container with correct env vars**
   ```bash
   docker rm -f simmubtadiat-app-1 2>/dev/null
   
   docker run -d --name simmubtadiat-app-1 \
     --network simmubtadiat_default \
     -e DB_HOST=db \
     -e DB_PORT=5432 \
     -e DB_USER=mubtadiaat \
     -e DB_PASS=mubtadiaat_secret \
     -e DB_NAME=mubtadiaat_db \
     -p 8080:8080 \
     simmubtadiat-app
   ```

5. **Verify live**
   ```bash
   curl -s http://localhost:8080/rapot.html | grep -A2 "Garis pembatas"
   ```

---

## Architecture Notes

- App runs in **Docker container** (`simmubtadiat-app-1`)
- Nginx at `reviewtechno.me` proxies to localhost:8080  
- Frontend built into image via multi-stage Dockerfile
- **NOT bind mounted** — changes require rebuild + restart
- Database in separate container (`simmubtadiat-db-1`) on shared network

### Common Pitfall: DB Connection Failures

**Error:** `connection refused to localhost:5432`

**Cause:** Container uses `DB_HOST=localhost` from `.env` inside Dockerfile instead of `db`.

**Solution:** Always pass environment via `docker run -e` with `DB_HOST=db`.

---

## References

Session-specific diagnostics and logs stored in:
- `references/layout-fix-2026-08-25.md` — This session's transcript
- `references/rapot-template-analysis.pdf` — Physical reference PDF inspection

---
## Critical Pitfalls (2026-08-26)

### Issue 3: CSS Changes Not Reflecting Despite Correct Source

**Symptom:** User reports "tidak berubah" after CSS patch and rebuild. Browser shows old styles even in incognito mode.

**Root Cause:** 
1. **Service Worker cache** not invalidated → serves old cached files
2. **Tailwind arbitrary classes** might auto-generate styles at runtime
3. **Browser computed style override** - verify via DevTools Elements → Computed tab

**Fix Pattern:**

#### Step 1: Verify source code BEFORE debugging user's browser
```bash
# Check live server output directly
curl -sL http://reviewtechno.me/rapot.html | grep "\.st-value"

# Should show no font-weight:bold in .st-value rule
.st-value { padding-left: 4px; }
```

If source is correct but browser still wrong → **Service Worker issue**, NOT CSS problem.

#### Step 2: Force Service Worker cache clear
Increment `CACHE_NAME` version in `/opt/simmubtadiat/frontend/public/sw.js`:

```javascript
// BEFORE
const CACHE_NAME = 'mubtadiaat-cache-v28';

// AFTER  
const CACHE_NAME = 'mubtadiaat-cache-v29';
```

Add new assets to cache list:
```javascript
const urlsToCache = [
  '/index.html',
  '/logo.jpg',
  '/favicon.svg',
  '/style.css',
  '/rapot.html',           // Explicitly add
  '/dist/rapot.html'       // And dist variant
];
```

Then rebuild + restart:
```bash
cd /opt/simmubtadiat/frontend && npm run build
docker compose restart app
```

Service Worker v29 will auto-delete v28 cache on activate.

#### Step 3: User-side hard reload instruction
If service worker cleared but still caching client-side:
- PC: **Ctrl+Shift+R**
- Mac: **Cmd+Shift+R**
- DevTools: Network tab → Check "Disable cache" → Refresh

### Issue 4: Bold Font Weight Unexpectedly Applied

**Symptom:** `.st-value` class should be normal weight but renders bold.

**Debug Path:**
1. Check HTML source for inline style attributes
2. Inspect Tailwind utility classes that might inject `font-bold` (e.g., `text-biru`, `font-semibold`)
3. Verify computed style vs source - if computed says normal but visual is bold, this is **not a CSS bug**

**Common False Alarms:**
- `.header-text h3` IS supposed to be bold → don't confuse with student values
- `<th>` grade table headers are bold → separate element scope
- Status cells (`bإذن/bغيره`) have `style="font-weight:bold"` → different context

**Key Insight:** Total `font-weight: bold` count in production HTML can be 7-9 without violating spec. Only inspect rules targeting `.st-value` or identity fields specifically.

### Pattern: Don't Blindly Trust "Server Output" Claims

When user says "masih bold" or "tidak berubah":
1. **First**: Fetch live endpoint with `curl -sL URL` to bypass browser UI entirely
2. **Second**: Run exact grep/regex search from command line (execute_code tool)
3. **Third**: If curl shows correct output, THEN investigate client-side (SW cache, browser settings, network inspection)

This saves hours of debugging when the actual bug is **client-side caching**, not server output.
