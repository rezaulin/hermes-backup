# SIM Mubtadiat Rapot Layout Fix - 2026-08-25

## Session Context

**Date:** 2026-08-25  
**User:** jarvis BALAP  
**Platform:** Docker container at reviewtechno.me (port 8080)  
**Problem:** Garis horizontal di header raport terlalu panjang dan spacing salah ke tahun ajaran

---

## Root Cause Analysis

### Problem: Garis Terlalu Panjang & Spacing Salah

**Symptom from user:**
- "Garis atas sebelum tahun ajaran terlalu lebar jaraknya kebawah kurang mepet"
- "Terlalu panjang sampai hampir menyentuh logo"
- "Di print preview gak muncul garisnya"

### Investigation Steps

1. **Extract reference PDF** via PyMuPDF:
   ```bash
   file /root/.hermes/cache/documents/doc_96ebb567db0c_3\ TSN\ C.pdf
   # Output: JPEG image data, 960x1280px
   ```

2. **Check Word template**:
   ```bash
   python -c "from docx import Document; d=Document('...'); print(d.tables[1].rows)"
   # Confirmed 15 mapel + jaml structure
   ```

3. **Locate HTML source**:
   File: `/opt/simmubtadiat/frontend/rapot.html` line 534
   
   Original code:
   ```html
   <hr style="border:none;height:1px;background-color:#000;margin:3px auto;width:75%;">
   ```

### Issues Identified

1. `width:75%` → Line too wide, reaches toward logo on right
2. `height:1px` → Too thin visually  
3. `margin:3px auto` → Only top margin, no explicit bottom spacing to tahun ajaran text
4. Missing `print-color-adjust` → Disappears in print preview/PDF export

---

## Solution Applied

### Patch 1: Reduce Line Width & Tighten Spacing

File: `/opt/simmubtadiat/frontend/rapot.html` line 534

```diff
-      <hr style="border:none;height:1px;background-color:#000;margin:3px auto;width:75%;">
+      <hr style="border:none;height:2px;background-color:#000;margin:2px auto 8px auto;width:55%; min-width: 120px;">
```

Changes:
- `width:75%` → `width:55%` (shorter, doesn't reach logo)
- `min-width:120px` ensures minimum visibility even at small viewport widths
- `height:1px` → `height:2px` (thicker for better visibility)
- `margin:3px auto` → `margin:2px auto 8px auto` (top=2px tight against school name, bottom=8px gap before tahun ajaran)

### Patch 2: Add Print Visibility Support

File: `/opt/simmubtadiat/frontend/rapot.html` after `.rapot-sheet` definition (~line 76)

Added to `@media print` block:
```css
/* Garis hr harus explicit print-visible */
.rapot-sheet hr {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    display: block !important;
}
```

Purpose: Force browser to render HR background color and ensure display:block overrides any CSS conflicts during print rendering.

---

## Deployment Process

### Step 1: Rebuild Docker Image

```bash
cd /opt/simmubtadiat && docker build -t simmubtadiat-app . --no-cache
```

Output truncated:
```
#21 [frontend-builder] RUN npm run build
✓ built in 4.01s
#22 [backend-builder 8/8] RUN GOMAXPROCS=1 go build ...
#23 [stage-2 5/9] COPY frontend/dist ./public/dist
#30 exporting to image ... done
```

Total time: ~67 seconds (rebuild with --no-cache)

### Step 2: Restart Container with Correct DB Config

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

**Critical note:** DB connection requires `DB_HOST=db` because container uses internal Docker DNS name, NOT `localhost`. Using `localhost` causes `connection refused to 127.0.0.1:5432`.

Initial startup error when using wrong env:
```
failed to connect to `user=root database=`: 172.18.0.2:5432 (db): 
failed SASL auth: password authentication failed for user "root"
```

After fixing env vars:
```
Selesai. 0 migrasi baru diterapkan (total berkas: 51).
[entrypoint] Memulai server...
Server is running on port 8080
```

### Step 3: Verify Changes Live

```bash
curl -s http://localhost:8080/rapot.html | grep -A2 "Garis pembatas"
```

Result confirmed patched HTML:
```html
<hr style="border:none;height:2px;background-color:#000;margin:2px auto 8px auto;width:55%; min-width: 120px;">
```

---

## Verification Checklist

- [x] Source file patched (`rapot.html` line 534)
- [x] Print media query added for HR visibility
- [x] Docker image rebuilt successfully
- [x] Container started with correct DB environment
- [x] Migration executed (51 total files, 0 new applied)
- [x] Server listening on port 8080
- [x] Endpoint verified live via curl

---

## User Feedback & Corrections

### Correction: "Jangan kemana-mana, aku cuma mau perbaiki garis diatas tahun ajaran itu saja"

**Issue:** Previous response included excessive context about Word templates, architecture, alternative approaches.

**Lesson:** User wants surgical fix only — minimal explanation, direct action, no tangential discussion.

**Action captured in skill:** Emphasize direct execution path over verbose analysis.

---

## Environment Details

- **Host:** Linux (5.15.0-181-generic)  
- **Docker version:** Not recorded, working fine
- **Database:** PostgreSQL 15 Alpine (`simmubtadiat-db-1`)
- **Network:** `simmubtadiat_default` bridge network
- **Frontend framework:** Vite + raw JS (no React/Vue bundling in this session)
- **Backend:** Go binary (`main`) compiled with `go build -p 1`

---

## References

- Physical rapport PDF: `/root/.hermes/cache/documents/doc_96ebb567db0c_3 TSN C.pdf`
- Word reference document: `/root/.hermes/cache/documents/doc_9f6e0ca8e707_1 Aliyah A (I).docx`
- Skill created: `sim-mubtadiat-rapot-print-layout-fix`

---

## Next Actions (If Needed)

1. Test actual print preview in browser: `https://reviewtechno.me/rapot.html`
2. Check line width matches physical Word reference exactly
3. Adjust percentages if visual test reveals still-too-wide/thin
4. Save as `references/print-spec-final.md` once locked
