---
name: print-layout-match
category: web-engineering
description: Engineering print-ready layouts that match physical reference documents
---

# Print Layout Matching — Match HTML/CSS Output to Physical Reference Documents

Goal: Produce HTML/CSS print output that is **plek ketiplek** with physical reference documents (report cards, letters, forms, etc.). This requires precise measurement, source verification, and iterative adjustment.

## When to Use

- User provides photo of printed document → need to replicate layout exactly
- User has original Word/Excel source file → use as gold standard
- Need to fix overflow, spacing, alignment, or typography mismatch between digital and physical versions

## Core Principles

1. **Source files are ground truth** — If user has .docx/.xlsx, extract structure directly. Never guess from photos alone.
2. **Photos are estimates only** — Raster distortion, angle, lighting all introduce ±1–2mm error. Photos ≠ spec.
3. **Print rendering ≠ screen rendering** — Chrome print vs Word rendering differ in font metrics, line-height, rounding. Expect subpixel variance.
4. **Iterate pixel-level** — Don't guess; measure, verify, adjust, re-measure.

## Step-by-Step Workflow

### 1. Extract Gold Standard Data
If Word source available:

```python
from zipfile import ZipFile
import re

with ZipFile('document.docx', 'r') as z:
    doc_xml = z.read('word/document.xml').decode('utf-8')
    
# Page size (twips → mm: divide by 1440 then multiply by 25.4)
pgsz = re.search(r'<w:pgSz([^>]*/>)', doc_xml)
attrs = dict(re.findall(r'w:(\w+)="(\d+)"', pgsz.group()))
w_mm = int(attrs['w']) * 25.4 / 1440
h_mm = int(attrs['h']) * 25.4 / 1440
print(f"Page size: {w_mm:.1f}mm x {h_mm:.1f}mm")

# Paragraphs with font info
para_tags = re.findall(r'<w:p[^>]*>(.*?)</w:p>', doc_xml, re.DOTALL)
for tag in para_tags[:20]:
    text_match = re.search(r'<w:t[^>]*>([^<]+)</w:t>', tag)
    if text_match:
        text = text_match.group(1)
        # Check font, size, bold
        font_name = re.search(r'w:ansi="([^"]*)"', tag)
        font_size = re.search(r'w:sz[^>]*w:val="(\d+)"', tag)
        is_bold = '<w:b/>' in tag
        print(f"'{text}' - [{font_name}] {font_size}")
```

### 2. Measure Reference Photo (If No Source)
Extract crops for header/body/footer regions, analyze pixel positions of lines/columns:

```python
from PIL import Image
im = Image.open('reference.jpg')
px = im.load()

# Find vertical grid lines (high-contrast columns)
for x in range(im.width):
    red_count = sum(1 for y in range(h) if px[x,y][0] > 200)
    if red_count > h*0.9:
        vertical_lines.append(x)
```

Document column widths as percentages from pixel measurements:

| Column | Pixel Range | Width % |
|--------|-------------|---------|
| umum   | 511-618     | 23%     |
| khusus | 476-511     | 17%     |
| art    | 354-476     | 25%     |
| books  | 240-354     | 27%     |
| num    | 55-240      | 8%      |

### 3. Build HTML Template Structure

#### Header Layout Options

**Option A: Flexbox (simple two-element)**
```html
<div class="flex items-center gap-4">
  <div class="header-logo"></div>
  <div class="header-text"></div>
</div>
```

**Option B: Grid (three-column aligned)**
```html
<div class="grid" style="grid-template-columns: 1fr auto 1fr; gap: 20px;">
  <div class="left-col">Identitas Kiri</div>
  <div class="center-col">Kop Surat Center</div>
  <div class="right-col">Identitas Kanan</div>
</div>
```

#### Table Structure
Always use explicit width percentages for columns:
```css
th { width: 23%; } /* umum */
th { width: 17%; } /* khusus */
/* ... other cols ... */
```

Set table centered with margin:
```css
table { width: 90%; margin: 0 auto; border-spacing: 0; }
```

### 4. Typography Setup

Map Word font specs to CSS:

| Tier | Usage | Font Family | Size | Style |
|------|-------|-------------|------|-------|
| Orange | Title/Headers | KFGQPC Uthman Taha Naskh | 18pt | Bold |
| Blue | Body Arab | KFGQPC Uthman Taha Naskh | 16pt | Regular |
| Green | Labels | Times New Roman | 14pt | Regular |

CSS:
```css
.ft-uth-18 { font-family: 'Uthman Taha Naskh'; font-size: 18pt; font-weight: bold; }
.ft-uth-16 { font-family: 'Uthman Taha Naskh'; font-size: 16pt; }
.ft-tnr    { font-family: 'Times New Roman'; font-size: 14pt; }
```

### 5. Print Media Configuration

@page margins must match paper spec:
```css
@page {
  size: F4 portrait; /* 215.9mm x 330.2mm */
  margin-top: 2.5cm; /* or owner spec */
  margin-left: 1.5cm;
  margin-right: 1.5cm;
  margin-bottom: 2cm;
}
```

Sheet min-height calculation:
```css
.rapot-sheet {
  min-height: 270mm !important; /* area = 330.2 - 25 - 20 = 285.2mm minus headroom */
}
```

Why not 285mm? Subpixel rounding causes overflow. 270mm gives ~15mm headroom.

### 6. Overflow Troubleshooting

Symptoms: Content spills to page 2 or 3 instead of 1 page per semester.

Debug sequence:
1. **Measure content height** via JavaScript:
```javascript
const sheet = document.querySelector('.rapot-sheet');
const table = sheet.querySelector('table');
console.log(`Sheet total: ${sheet.offsetHeight}px`);
console.log(`Table body: ${table.tBodies[0].offsetHeight}px`);
```

2. **Check footer padding bugs** — Common cause of bloat:
```css
tfoot th { padding: 1.27cm !important; } /* WRONG — adds 25mm/baris! */
tfoot th { padding: 1px 6px 4px 6px !important; } /* CORRECT */
```

3. **Signature-box margin override**:
```css
.signature-box { margin-top: 1.27cm !important; } /* WRONG — prevents pinning */
.signature-box { margin-top: auto; } /* CORRECT — pins to bottom */
```

4. **Tighten line-height**:
```css
tr td { line-height: 1.1; } /* vs default 1.5 or 1.22 */
```

Reduce iteratively until total fit:
- Before fixes: ~394mm (5 pages)
- After tfoot fix: ~353mm (4 pages)
- After signature fix: ~330mm (2 pages ✅)

### 7. Side-by-Side Verification

Generate comparison image:

```python
from PIL import Image
ref = Image.open('reference_photo.jpg')
now = Image.open('render_output.png')

def scale(im, height=900):
    r = height / im.height
    return im.resize((int(im.width * r), height))

ref_s = scale(ref)
now_s = scale(now)

canvas = Image.new('RGB', (ref_s.width*2 + 30, ref_s.height + 50), 'white')
canvas.paste(ref_s, (0, 50))
canvas.paste(now_s, (ref_s.width + 30, 50))
canvas.save('compare_final.png')
```

Verify visually:
- Header alignment (centered text, logo position)
- Column widths (vertical lines match)
- Footer structure (merged cells, no extra rows)
- Signature placement (left/right labels correct)

## Pitfalls & Fixes

| Symptom | Root Cause | Fix |
|---------|------------|-----|
| "No. Stambuk" wraps to 2 lines | label column too narrow | Add `white-space: nowrap;` to value span |
| Extra HR line appears | flex container has `border-b-4` | Remove border-bottom styling |
| Signature box floats mid-page | `margin-top: X cm !important` overrides `auto` | Use `margin-top: auto` |
| Content spills to page 3 | min-height equals available area (no headroom) | Reduce to 270mm for 15mm headroom |
| Column widths don't match photo | using generic percentages (e.g., 20%/20%) | Measure pixel ranges from reference, compute exact % |
| Arabic letters touch baseline grid | descender gap insufficient | Keep line-height ≥ 1.1, preserve padding-bottom |
| Line numbers wrap awkwardly | colon separator sits alone | Group label+colon: `<span class="lbl">No.</span><span class="colon">:</span>` same element |
| Vite build fails: "nested-comment" parse error | HTML comment ends with `--&gt;` instead of `-->` | Replace entity encoding with proper arrow syntax |

### Common Arabic Text Corrections

Based on SIM Mubtadiat raport verification:

```html
❌ Wrong → ✅ Correct
فصل الدراسية الأولى → فصل الدراسة الأولى
المدرسة العالية للبنات → المدرسة الابتدائية للبنات
ليربيا كديري → كديري ليربيا (city order reversed)
١٤٤٦ - ١٤٤٧ هـ / ٢٠٠٥ - ٢٠٠٦ م → ٢٠٢٦ - ٢٠٢٧ م (year order: Hijri/Masehi) 
```

Always cross-check against Word source file when available — photos may have distorted text or misaligned columns due to angle/lighting.

#### Header Layout Patterns
⚠️ **CRITICAL:** When using `dir="rtl"` on wrapper div with `display: flex` (row direction), first child aligns to RIGHT, not LEFT. This inverts logo placement for Arabic layouts where you want logo KIRI and text CENTER/RIGHT.

Example that FAILS (logo appears kanan):
```html
<div class="flex items-center gap-4" dir="rtl">
  <img src="/logo.png" />   <!-- Element 1 = RIGHT (wrong!) -->
  <div class="header-text"></div>  
</div>
```

Example that WORKS (logo left via explicit LTR):
```html
<div class="flex items-center gap-4" dir="ltr">
  <div class="header-logo"><img src="/logo.png"/></div>
  <div class="header-text" dir="rtl"></div>  
</div>
```

**Pattern B: `display: table-cell` (most reliable)** — Never inverted by RTL:
```html
<style>
.header-container { display: table; width: 100%; }
.header-left { display: table-cell; width: 100px; vertical-align: middle; }
.header-title { display: table-cell; vertical-align: middle; text-align: center; direction: rtl; }
</style>

<div class="header-container">
  <div class="header-left"><img src="/logo.png"/></div>
  <div class="header-title">...</div>
</div>
```

Why `display: table-cell` wins: Table layout is **inherently LTR** regardless of wrapper's `dir` attribute. Only children can override with their own `direction: rtl`. Perfect for Arabic layouts requiring logo-fixed positioning + centered Arabic text.

---

## Word .docx Logo Position Fix

**Symptom:** Logo appears RIGHT side instead of LEFT in print layout.

**Root cause:** With `dir='rtl'`, paragraph element order = visual position. First `<w:p>` = KANAN side. If header has only one para containing logo → logo at kanan.

**Fix:** Insert empty `<w:p>` BEFORE logo paragraph via direct XML edit of `word/header1.xml`. See skill [`word-print-layout-fix`](../../word-print-layout-fix/SKILL.md) with complete Python implementation.

**Pitfall:** Don't search for `w:drawing` alone — Word uses `wp:inline` within `w:drawing`. Parse both tags when locating drawing elements.

Pattern A (simple two-element): Flex logo left + text center
```html
<div class="flex items-center gap-4">
  <div class="header-logo"></div>
  <div class="header-text"></div>
</div>
```

Pattern B (three-column with identities): Grid RTL aware
```html
<div class="grid" style="grid-template-columns: 1fr auto 1fr; gap: 20px;">
  <div class="left-col">Identitas Kiri (RTL =视觉上 right)</div>
  <div class="center-col">Kop Surat Center</div>
  <div class="right-col">Identitas Kanan (RTL =视觉上 left)</div>
</div>
```

⚠️ **CRITICAL:** When using `dir="rtl"` on wrapper div, first child aligns to RIGHT, not LEFT. For logo-left layout:
- Use `dir="ltr"` on identity containers  
- Or use explicit order via CSS `order: 1/2/3` on flex children
- Or keep header separate from identity blocks (original pattern worked better)
## Tools Used in Session

- `/tmp/render_live.py` — Playwright render of live data for quick iteration
- `/tmp/measure.py` — Print-media section diagnostics (measures sheet/table/tfoot heights)
- `google-chrome --headless --screenshot` — Full-page screenshot capture
- Python/PIL — Image analysis (pixel counts, cropping, comparison canvas)
- DocX ZIP parsing — Extract structure and formatting from Word source
- **Docker exec** — Verify served files inside container before assuming build failure (see references/docker-frontend-debugging.md)

## When to Save as Skill Pattern

- Layout debugging took >1 hour of iteration
- Multiple CSS overrides conflicted before resolving
- Print overflow required systematic measurement rather than guessing
- Reference photo was distorted/noisy, requiring fallback to source XML

Save this workflow under `print-layout-match` so future sessions start knowing these pitfalls.