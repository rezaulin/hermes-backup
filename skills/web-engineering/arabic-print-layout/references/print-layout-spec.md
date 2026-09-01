# Print Layout Specification — SIM Mubtadiat Report Cards

This document consolidates all print layout specifications discovered during Arabic report card engineering sessions.

## Paper Sizes

| Format | Width | Height | Usage |
|--------|-------|--------|-------|
| F4 | 215.9mm | 330.2mm | Primary for SIM Mubtadiat raport |
| A4 | 210mm | 297mm | Alternative (adjustable via UI) |

## Margins (F4)

```css
@media print { @page { size: 215.9mm 330.2mm; margin: 2.5cm 1.5cm 2cm 1.5cm; } }
```

- **Top**: 2.5cm (header room for school name/title)
- **Left/Right**: 1.5cm (symmetric spacing)
- **Bottom**: 2cm (signature box clearance)

**Total vertical content height**: 330.2 - 2.5 - 2 = **305.7mm**

## Font Hierarchy

### Title Tier (oranye/red-orange visual in legacy docs)
- **Font**: KFGQPC Uthman Taha Naskh (self-hosted) OR Amiri fallback
- **Size**: 18pt
- **Weight**: Bold
- **Usage**: Document title "كشف الدرجات الدراسية", semester title "فصل الدراسة الثانية"
- **Line-height**: 1.15 (compressed vs Tailwind default 1.5)

### Section Tier (biru/blue visual in legacy docs)
- **Font**: KFGQPC Uthman Taha Naskh / Amiri
- **Size**: 16pt
- **Weight**: Regular or Bold depending on context
- **Usage**: School name "المدرسة الابتدائية للبنات هداية المبتدئات كديري", table headers
- **Line-height**: 1.1 (tighter for Arabic descender handling)

### Data Tier (hijau/green visual in legacy docs)
- **Font**: Times New Roman (for Latin labels) OR KFGQPC Uthman Taha Naskh (for Arabic digits)
- **Size**: 14pt
- **Weight**: Normal for labels, Bold for numeric values
- **Usage**: Student data fields (Nama, Stambuk), grade numbers in cells
- **Line-height**: 1.25

## Table Structure Patterns

### Two-Tier Header Pattern (most common)
```html
<thead>
  <tr>
    <th rowspan="2">Col A</th>
    <th rowspan="2">Col B</th>
    <th colspan="2" style="white-space: nowrap;">Merged Parent Title</th>
  </tr>
  <tr>
    <th>Sub Col 1</th>
    <th>Sub Col 2</th>
  </tr>
</thead>
```

**Critical CSS Rules**:
- `white-space: nowrap` on merged header to prevent text breaking
- `rowspan="2"` on static columns
- `colspan="2"` on parent header spanning sub-columns
- Padding: `1px 8px 3px 6px` (reduced from default to fit within page height)
- Line-height: `1.1` (not 1.5 — prevents text cutting across borders)

### Footer Row Patterns

**Summary Row** (total grades):
```html
<tr class="text-orange">
  <th colspan="3" style="text-align: center;">جملة أرقام الدرجات الدراسية</th>
  <td class="text-hijau" data-field="total-khos">0</td>
  <td class="text-hijau" data-field="total-am">0</td>
</tr>
```

**Absence Tracking** (rowspans):
```html
<tr>
  <th rowspan="2" colspan="2">أيّام التأخّر</th>
  <td class="text-biru" style="font-weight:bold; text-align:center;">بإذن</td>
  <td class="text-hijau">0</td>
  <td class="text-hijau">-</td>
</tr>
<tr>
  <td class="text-biru" style="font-weight:bold; text-align:center;">بغيره</td>
  <td class="text-hijau">0</td>
  <td class="text-hijau">-</td>
</tr>
```

**Bayan/Decision** (semester-2 only):
```html
<tr data-field="bayan-box" style="display:none;">
  <th colspan="2" style="font-weight:bold; text-align:center;">البيان</th>
  <td colspan="3" data-field="bayan-value" style="text-align:right; padding-right:20px;">-</td>
</tr>
```
Only rendered when `String(semester) === '2'`. Hidden via `style="display:none"` on non-matching semesters.

## Signature Box Pinning

**Footer-pinning technique**:
```css
.signature-box { 
    display: flex; 
    justify-content: space-between; 
    padding: 0 40px; 
    margin-top: auto !important; /* Pins to bottom of .rapot-sheet */
}
```

**Parent container requirement**:
```css
.rapot-sheet { 
    min-height: 270mm !important; /* Allows margin-top: auto to work */
    display: flex;
    flex-direction: column;
}
```

**Important**: Don't use fixed `margin-top: Xcm !important` overrides — they break the flex calculation and cause footer overflow to page 3.

## Logo Handling

**Reference analysis shows**: Physical report cards may include logos at different positions. Check reference PDF before deciding:
- Left-aligned logo + centered text + right-aligned logo (3-column layout)
- Centered text only (no logos) — matches many Word references
- Inline SVG/logos with fallbacks: `<img src="/logo-v3.png" onerror="this.src='/logo-fallback.png'">`

## Arabic Digit Rendering

**Problem**: Times New Roman lacks Arabic-Hindi digit glyphs (٠١٢٣٤٥٦٧٨٩). Only has Western-Arabic (0123456789).

**Solution**: Use KFGQPC Uthman Taha Naskh for any cell containing mixed script:
```css
td.td-num { 
    font-family: 'KFGQPC Uthman Taha Naskh', 'Amiri', serif; 
    font-size: 14pt; 
    font-weight: bold; 
}
```

**Alternative**: JavaScript conversion function:
```javascript
function toArabicDigits(value) {
  const map = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
  return String(value).replace(/[0-9]/g, d => map[Number(d)]);
}
```

## Page Break Control

**Single sheet isolation**:
```css
.rapot-sheet { 
    page-break-after: always; 
    page-break-inside: avoid; 
    break-inside: avoid; 
}

.rapot-sheet:last-child { 
    page-break-after: auto; 
}
```

**Fullscreen reset in @media print**:
```css
@media print {
    main, #rapot-wrap, #print-area { 
        padding: 0 !important; 
        margin: 0 !important; 
        overflow: visible !important; 
    }
    
    .rapot-sheet { 
        margin: 0 !important; 
        padding: 0 !important; 
        width: auto !important; 
        max-width: 100% !important; 
    }
}
```

## Color Coding (Legacy Visual Language)

These CSS classes exist in some templates but are no longer strictly necessary with modern typography hierarchy:

| Class | Hex Code | Visual Use |
|-------|----------|------------|
| `.text-orange` | #ff7f50 (approx) | Headers, titles (old designation) |
| `.text-biru` | #4682B4 (steelblue) | Section headers, table headers |
| `.text-hijau` | #2E8B57 (seagreen) | Numeric values, totals |

**Current approach**: Prefer font weight/styling over color for semantic distinction. Colors deprecated in favor of pure typography.

## References to Physical Documents

Always compare implementation against:
- `/root/.hermes/cache/documents/doc_*.docx` (Word references from user uploads)
- `/tmp/raport_ref_page_*.png` (rendered PDF pages for visual inspection)
- User screenshots with red circles highlighting specific issues

---

**Version**: Updated 2026-08-25 after SIM Mubtadiat rapport print layout fix session.
**Source**: Discovery during conversation with user "jarvis BALAP".