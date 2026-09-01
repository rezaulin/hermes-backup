---
title: RAPOT Print Layout (SIM Mubtadiat)
name: rapot-print-layout
status: active
version: v29
last_updated: 2026-08-25
tags: [print, layout, arabic-typography, word-source]
description: Implementation guide for printing SIM Mubtadiat report cards matching Word source exactly, fitting F4 per semester with Arabic typography and correct column widths.
---

# RAPOT Print Layout Implementation\n\n## Quick Reference\n**Goal**: Generate print-ready rapor matching Word source exactly, fitting F4 per semester.\n\n## Paper Specs (Confirmed User Preference)\n- **Size**: F4 (215.9mm x 330.2mm) → NOT A4!\n  - ❌ Common mistake: using A4 (210mm × 297mm) = separuh page visible\n  - ✅ Correct: `@page { size: 215.9mm 330.2mm; margin: 15mm 15mm 15mm 15mm; }`\n- **Margins**: Top 2.5cm, Left/Right 1.5cm, Bottom 2cm\n- **Min-height**: `270mm` (headroom for overflow control)

## Font Stack
| Element | Arabic Font | Size | Weight |
|---------|-------------|------|--------|
| Title/Semester | Uthman Taha Naskh | 18pt | Bold |
| School Name/Year | Uthman Taha Naskh | 16pt | Regular |
| Subject Headers | Uthman Taha Naskh | 16pt | Bold |
| Values | Times New Roman | 14pt | Regular/Bold |

## Critical Fixes v5 (Aug 25, 2026) - Logo Position Pattern
### ⚠️ **RTL Flexbox Logo Order Rule - v35**

**CRITICAL MISTAKE I MADE MULTIPLE TIMES**: Thinking RTL flips flexbox DOM order visually.

**THE TRUTH**: With `dir="rtl"` on container and default `flex-direction: row`:
- **Element PERTAMA (first in HTML)** → appears on KIRI visually (left side of paper)
- **Element TERAKHIR (last in HTML)** → appears on KANAN visually (right side of paper)

This is OPPOSITE of what most people expect! In RTL, DOM order IS visual order left-to-right.

**CORRECT PATTERN (Logo on LEFT as user wants):**
```html
<!-- ✅ DO THIS: Image BEFORE text -->
<div class="flex items-center pb-3 mb-2 text-biru" dir="rtl">
    <img src="/logo-raport-bw-v5.png" class="header-logo">  <!-- Element 1 = KIRI -->
    <div class="header-text" style="line-height: 1.2;">     <!-- Element 2 = KANAN -->
        <h1>كشف الدرجات الدراسية</h1>
        <h2>المدرسة...</h2>
    </div>
</div>
```

**WRONG PATTERN (DON'T SWAP):**
```html
<!-- ❌ DON'T DO THIS: Swapped order puts logo RIGHT -->
<div dir="rtl" class="flex">
    <div class="header-text">...</div>  <!-- Element 1 = KIRI (text left) -->
    <img>                               <!-- Element 2 = KANAN (logo right) -->
</div>
```

**WHY I KEEP GETTING WRONG**: My brain thinks "RTL should flip things so text right, logo left" but that requires explicit CSS transforms or different flex configuration. Default RTL keeps DOM order = visual order.

**USER CORRECTION TRIGGER**: When user says "logo di kiri tapi masih di kanan" or "kok malah kanan", immediately swap to put `<img>` first in HTML source before text div.

**Verification**: After edit, screenshot preview shows logo on LEFT side of header, text center/right aligned.

---

### ⚠️ **Logo Position Fix via Absolute Positioning - v36 (Aug 26 Session)**

When flexbox with RTL fails repeatedly or causes layout shifts:

**ROOT CAUSE**: Flexbox alignment gets confused when combined with RTL direction, especially if parent container has unexpected width/height constraints.

**ULTIMATE FIX**: Use `position: absolute` for logo instead of flexbox ordering.

**PATTERN:**
```css
.header-wrapper {
    position: relative;
    width: 100%;
    min-height: 80px;
    margin-bottom: 15px;
}

.header-logo {
    position: absolute;
    left: 0;
    top: 0;
    width: 90px;
    height: auto;
}

.header-text {
    margin-left: 120px; /* Enough space for logo */
    text-align: center;
    direction: rtl;
}
```

**WHY THIS WORKS**: 
- Absolute positioning bypasses flexbox + RTL interaction entirely
- Logo pinned to exact coordinate (left: 0 = guaranteed left side)
- Text gets marginLeft offset equal to logo width + gap
- No flexbox reflow confusion

**Trigger this fix when**:
- User reports "logo belum pindah kekiri" after multiple flexbox attempts
- Layout keeps shifting between tries
- Need deterministic, unambiguous positioning

---

### ⚠️ **Border Removal Ultimate Solution - Pure DIV/FLEX (v36 Aug 26)**

**CRITICAL INSIGHT**: `<table>` elements render default borders even with extensive CSS overrides. Hard to disable 100% due to browser user-agent stylesheets.

**ULTRA-SIMPLE SOLUTION**: Replace entire table structure with pure `<div>` + flexbox layout.

**BEFORE (Broken Borders Pattern):**
```html
<!-- ❌ HAS BORDERS (tables always have default styling) -->
<table class="student-table">
    <tr><td class="st-label">Nama</td><td>:</td><td>Zulaikha</td></tr>
</table>
```

CSS overrides required:
```css
.student-table td {
    border: none !important;
    border-top: none !important;
    border-right: none !important;
    border-bottom: none !important;
    border-left: none !important;
    outline: none !important;
    box-shadow: none !important;
    background: transparent !important;
}
```
Result: Still renders invisible borders in some browsers!

**AFTER (Pure DIV/FLEX Pattern):**
```html
<!-- ✅ NO BORDERS (no table semantics at all) -->
<div class="student-data" dir="ltr">
    <div class="student-left">
        <div><span class="st-label">Nama</span><span class="st-colon">:</span><span class="st-value">Zulaikha</span></div>
    </div>
</div>
```

CSS simplified:
```css
.student-data {
    display: flex;
    justify-content: space-between;
    font-size: 14pt;
    color: #000000;
}

.student-left {
    display: flex;
    flex-direction: column;
    gap: 1mm;
    width: 50%;
}

.st-label, .st-colon, .st-value {
    white-space: nowrap;
}
```

**WHY THIS WORKS**: 
- No table semantics = no default border inheritance
- Flex layout more predictable than table cell rendering
- Explicit control over every spacing value
- Cleaner HTML structure

**User trigger pattern**: "kotak di identitas masih ada" or "tidak mau hilang garisnya"

**Action**: Immediately replace `<table>` → `<div>` wrapper, change `class="st-*"` to span elements inside flex rows.

---

### Header Structure (v34+ Session Correction)
- **Logo HITAM PUTIH** di kiri (left side visual)
- Text Arab center/right
- Garis pembatas narrow (70% width), compact spacing

**Structure pattern:**
```html
<!-- HEADER: Logo KIRI + Text ARAB -->
<div class="flex items-center pb-3 mb-2 text-biru">
    <img src="/logo-raport-bw-v5.png" alt="Logo Raport BW" class="header-logo">
    <div class="header-text" style="line-height: 1.2;">
        <h1 class="ft-uth-18">كشف الدرجات الدراسية</h1>
        <h1 data-field="semester-title" class="ft-uth-18" style="font-size: 18pt;">فصل الدراسة الثانية</h1>
        <h2 data-field="madrasah-line" class="ft-uth-16" style="font-size: 16pt;">المدرسة الابتدائية للبنات هداية المبتدئات كديري ليربيا</h2>
    </div>
</div>

<!-- GARIS PEMBATAS: Narrow & compact -->
<hr style="border:none;height:1px;background-color:#000;margin:3px auto 5px;width:70%;">

<!-- Tahun ajaran: centered below line -->
<div class="text-center mb-2">
    <p class="hdr-tahun ft-uth-16" style="font-family: 'KFGQPC Uthman Taha Naskh','Amiri',serif; font-size: 16pt;">
        سنة : <span data-field="tahun-ajaran">١٤٤٧ - ١٤٤٨ هـ / ٢٠٢٦ - ٢٠٢٧ م</span>
    </p>
</div>
```

**Key specs:**
- Logo size: 3cm × 3cm (`.header-logo { width: 3cm; height: 3cm; }`)
- HR width: 70% (not 90% - too wide!)
- HR margin: `3px auto 5px` (compact gap ~10mm total)
- Year spacing: `mb-2` (close to line above)

User explicit feedback: "logo raport lo bos yang dimaksud... sekarang logo ada dikanan seharusnya dikiri"

---

## Previous Issues (Fixed Before v34)
### Layout Collapse Debugging

```html
<!-- ✅ v5 CORRECT: Pure text stack, NO logo, single div container -->
<div class="header-text text-center mb-4" style="line-height: 1.3;">
    <h1 class="ft-uth-18">كشف الدرجات الدراسية</h1>
    <h1 data-field="semester-title" class="ft-uth-18">فصل الدراسة الثانية</h1>
    <h2 data-field="madrasah-line" class="ft-uth-16">المدرسة الابتدائية للبنات هداية المبتدئات ليربيا كديري</h2>
</div>

<hr style="border:none;height:1px;background-color:#000;margin:8px auto;width:90%;">

<div class="text-center mb-4 text-biru">
    <p class="hdr-tahun">سنة : <span data-field="tahun-ajaran">١٤٤٧ - ١٤٤٨ هـ / ٢٠٢٦ - ٢٠٢٧ م</span></p>
</div>
```

❌ **WRONG PATTERN (DON'T DO)**: Logo + complex layout:
```html
<!-- ❌ NEVER DO THIS: Creates visual mess -->
<div class="flex items-center pb-2 mb-2 text-biru">
    <div class="header-logo"></div>
    <div class="header-text">...</div>
    <img src="/logo-raport.png">
</div>
```

**Rule #1**: Header = pure vertical text stack, NO logos, all centered in single div
**Rule #2**: HR line after school name, margin `8px auto`, width 90%
**Rule #3**: Year in separate centered block below HR

### Reference Verification Source
**Word .docx DOM analysis shows:**
- First 121 paragraphs contain ONLY table and student data
- NO paragraph contains header text before table
- Header lines found inside table structure (Row headers), not as document body elements
- Therefore: Generate from code pattern based on user's explicit requirements, not reverse-engineer from docx


❌ **WRONG PATTERN (v27-v33)**: Grid or complex flex mixes break visual flow:
```html
<!-- ❌ DON'T DO THIS: Creates misaligned layout -->
<div class="grid grid-cols-[1fr_auto_1fr]">
    <!-- Logo dan text ter-split across 3 columns -->
    <!-- Visual result: header text center, but logo left/right mismatch -->
</div>
```

**Rule #1**: Kop = single row (logo + text), HR line, then Identitas = separate 2-col below line.
**Rule #2**: No `white-space-wrap` on labels (No.Stambuk = one line).

### Signature Order
**Fixed in v34**: Position must match RTL visual (Manager LEFT, Teacher RIGHT):

```css
/* ✓ CSS */
.signature-box { display: flex; justify-content: space-between; margin-top: 4px !important; }
```

```html
<div class="signature-box">
    <!-- KIRI (Left in DOM): المدير (Director/Principal) -->
    <div class="text-center">
        <p>المدير</p>
        <div style="height:36px;"></div>
        <p>(.........................)</p>
    </div>
    <!-- KANAN (Right in DOM): المدرس (Teacher/Mudarris) -->
    <div class="text-center" data-field="sig-mudarris-box">
        <p>المدرس</p>
        <div style="height:36px;"></div>
        <p>.........................</p>
    </div>
</div>
```

**User feedback captured**: "Mudir kiri, Mudarris kanan, rapatkan margin (4px dari tabel)."

### Table Width & Spacing
```diff
- width: 90% (too wide, full-width effect)
+ width: 92%; margin: 0 auto; (slightly narrower, centered, proper margins)
```

**User preference**: Tabel tidak full-width, ada margin kiri-kanan, compact spacing.

---

## Previous Issues (Fixed Before v34)
### Layout Collapse Debugging
```diff
- الكتب المدرسية
+ الكتب الدراسية

- فصل الدراسةاسية الأولى
+ فصل الدراسة الأولى

- المدرسة العالية للبنات...
+ المدرسة الابتدائية للبنات...

- ليربيا كديري
+ كديري ليربيا

- ١٤٤٦ - ١٤٤٧ هـ / ٢٠٠٥ - ٢٠٠٦ م
+ ١٤٤٧ - ١٤٤٨ هـ / ٢٠٢٦ - ٢٠٢٧ م
```

### Structure Fixes
```html
<!-- ✅ CORRECT: Flex row, center alignment -->
<div class="flex items-center border-b-4 border-black pb-3 mb-3">
    <div class="header-logo" style="width:60px;height:60px;"></div>
    <div class="header-text" style="text-align:center;">...</div>
    <img src="/logo-raport-bw-v5.png" class="header-logo">
</div>

<!-- ❌ WRONG: RTL wrapper flips logo position -->
<div class="rtl-wrapper"> <!-- breaks flexbox order -->
```

### Column Widths (After Subjects)
| Col | % | px | Spec |
|-----|---|----|------|
| الرقم | 8% | 35 | narrowest |
| الكتب | 27% | 122 | wide |
| الفنون | 25% | 114 | medium |
| الخاصة | 17% | 78 | narrow |
| العامة | 23% | 107 | wider |

⚠️ Never `80px 80px` — columns 4&5 are unequal!

### Footer Logic
```
Row 1: Total
  Label colspan=3 | Kolom Khusus (val) | Umum (val)

Rows 2-3: Absent Days (rowspan=2)
  Label colspan=2 rowspan=2 (RTL right)
  Sub-row 1: بإذن label | kosong | kosong
  Sub-row 2: بغيره label | angka hari | sel kosong terpisah

Row 4: Statement
  Nilai colspan=2 | Student colspan=3
```

## Typography Rules
- **Descender handling**: Letters خ ص ض ظ غ لا don't over-touch baseline
  - Padding: `1px 8px 3px 6px`
  - Line-height: `1.1` (not 1.5 Tailwind default)
- **Tfoot padding**: Small values only (`1px 6px 4px 6px`)
- **Table rows**: ~8.7px/data row, total content ~260mm

## Overflow Prevention
**Root cause**: Fixed margin overrides footer-pinning
```css
/* ❌ KILLER BUG */
.signature-box { margin-top: 1.27cm !important; }

/* ✅ FIX: Inline style in template */
<td style="margin-top:auto">Signature here</td>
```

## Verification Protocol
1. Render live PDF from production data
2. Check page count = 2 pages (1 per semester)
3. Header: 3 elements horizontal, text centered
4. All Arabic text matches Word .docx EXACTLY
5. Column widths unequal (17% vs 23%)
6. Absent days rows have vertical lines uninterrupted
7. Signatures at bottom edge, not floating

## Gold Standard Sources
- **Word .docx**: `/root/.hermes/cache/documents/doc_2fd6c11f3372_1 Aliyah A (2).docx` (PRIMARY)
- **Reference photo**: `/root/.hermes/cache/images/img_02813cf7d4f2.jpg` (secondary, distorted)

## Troubleshooting Matrix
| Symptom | Cause | Fix |
|---------|-------|-----|
| 3+ pages | Fixed margin on signature | Remove `!important` rule |
| Gaps in absent rows | Missing empty cell | Add `<td></td>` for umum |
| Overflow continues | Columns equalized | Set 17%/23% separately |
| Misaligned Arabic | Flex-start + RTL | Explicit `text-align:center` |
| Tall text | Wrong metrics | Verify font glyph support |

## Build Checklist (v36+ Aug 26)\n- [ ] Paper size = F4 (215.9mm × 330.2mm), NOT A4! Verify `@page { size: 215.9mm 330.2mm; }`\n- [ ] Logo position verified LEFT side:\n    - Try flexbox first: put `<img>` BEFORE text in HTML\n    - If still wrong, use absolute positioning (`position: absolute; left: 0;` on logo, `margin-left: 120px` on text)\n- [ ] Border removal confirmed: Use pure `<div>` + flex for student data, NEVER tables if "kotak" issue reported\n- [ ] Table header: أرقام الدرجات using colspan="2", NOT rowspan="2" (v5)\n- [ ] Header structure: pure vertical text stack, NO logo, all centered (v5)\n- [ ] HR line after school name: margin `8px auto`, width 90%\n- [ ] Reference verification: analyze Word .docx DOM first to understand pattern before coding\n- [ ] White-space: nowrap on label values (No.Stambuk = one line)\n- [ ] Table width: 92%, margin: 0 auto (compact centered look)\n- [ ] Signature order: Mudir LEFT, Mudarris RIGHT, margin-top: 4px\n- [ ] No over-engineering with complex layouts - follow user's explicit "Urutan #1,#2,#3" instruction\n- [ ] Service Worker cache bumped: increment CACHE_NAME from v28→v29+, add `/rapot.html` to urlsToCache array\n- [ ] DOCKER BUILD STEP REQUIRED: Run `npm run build` in `/opt/simmubtadiat/frontend/` AFTER HTML patch, THEN restart container\n- [ ] Cache name bumped to v34+\n\n---\n\n## Deployment Workflow (Docker + Vite) ⚠️\n\n**CRITICAL PATTERN**: Frontend changes require **THREE STEPS** in exact order:\n\n```bash\n# Step 1: Patch HTML source (already done in editor)\n\n# Step 2: Rebuild frontend (generates production dist/)\ncd /opt/simmubtadiat/frontend && npm run build\n# Output: public/dist/rapot.html with hash-bundled assets\n\n# Step 3: Restart docker container (loads new build)\ndocker compose down && docker compose up -d\n```\n\n**WHY THIS MATTERS**:\n- Source files live in `/opt/simmubtadiat/frontend/*.html`\n- Container loads files from `/app/public/dist/*.html` (built output)\n- Direct edit to source file → **NOT automatically synced** to container!\n- Need `npm run build` to copy/copy into `public/dist/`\n- Then `docker compose restart` loads new files\n\n**COMMON MISTAKE I MAKE**:\n- ❌ Edit HTML → `docker compose restart app` → unchanged because old build persists\n- ❌ Assume git commit pushes changes → no! Git only stores source, not built output\n- ❌ Only rebuild backend (`go build`) → frontend separate build step required\n\n**Verification Steps**:\n1. Check build timestamp: `ls -la /opt/simmubtadiat/public/dist/rapot.html`\n2. Verify content: `grep "font-weight.*bold" /opt/simmubtadiat/public/dist/rapot.html | wc -l`\n3. Inspect browser DevTools → Elements tab → verify computed styles match expected\n4. Test print preview: should render full page, not cropped\n\n**Service Worker Cache Bump Pattern**:\nWhen making any HTML change that users might not see immediately:\n```javascript\n// In public/sw.js:\nconst CACHE_NAME = 'mubtadiaat-cache-v29'; // ← bump version number!\nconst urlsToCache = [\n  '/',\n  '/index.html',\n  '/rapot.html',  // ← ADD changed files here\n  '/dist/rapot.html'\n];\n```\nVersion bump forces browser to fetch fresh copy instead of serving cached stale HTML.\n\n**Full Deploy Sequence**:\n```bash\n# 1. Edit source files\nvim /opt/simmubtadiat/frontend/rapot.html\n\n# 2. Bump SW version (if needed)\nvim /opt/simmubtadiat/frontend/public/sw.js  # Change CACHE_NAME\n\n# 3. Build frontend\ncd /opt/simmubtadiat/frontend && npm run build\n\n# 4. Restart containers\ndocker compose down && docker compose up -d\n\n# 5. Verify deployment\ndocker logs simmubtadiat-app-1 --tail 10\n```\n\n---\n\n## Previous Issues (Fixed Before v34)\n### Pattern Anti-Patterns (DON'T DO):
1. **Grid wrapper for header** → Split layout across 3 columns breaks vertical flow
2. **Mixed flex/grid in same container** → Creates alignment mismatches
3. **Horizontal-only header layout** → Missing clear stacking order
4. **Complex CSS abstraction** → User prefers simple, explicit structure

### When User Gets Frustrated:
> "Haduh semakin melenceng jauh"

**Action**: Immediately STOP and reset to simplest possible structure matching EXACTLY what user described ("Urutan #1, #2, #3"). Don't add features, don't optimize, just implement the pattern exactly as specified.

### Verification Before Deploy:
1. Check screenshot comparison - does it match reference photo visually?
2. Verify Arabic text from Word .docx source (NOT just text extract)
3. Run playwiright render test - should be EXACTLY 2 pages for F4
4. Inspect DOM - header should have clean hierarchy: kop > hr > identitas
