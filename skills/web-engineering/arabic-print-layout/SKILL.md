---
name: arabic-print-layout
category: web-engineering
description: Engineer Arabic-language print layouts for Islamic school report cards, F4 margins, typography calibration, table header patterns, PDF/Word reference conversion
---

# Arabic Print Layout Engineering — Report Card / Islamic School Documents

Engineer HTML/CSS print layouts that match Arabic-language report cards and Islamic education documents pixel-perfectly. Specialized in:
- Arabic typography with KFGQPC Uthman Taha Naskh or Amiri fonts
- F4/A4 paper sizing with precise margins
- Multi-row table headers (colspan + rowspan patterns)
- Reference-based reproduction (PDF/Word → HTML/CSS)

## Trigger Conditions
Load this skill when:
- Converting Arabic/Islamic school report cards to HTML/CSS print layout
- Fixing multi-row table headers that break incorrectly
- Adjusting Arabic typography (font family, size, line-height)
- Reproducing physical document layouts from PDF/Word references

## Workflow Steps

### 1. Extract Reference Structure FIRST
**Never guess layout** — always analyze reference document first:
```bash
# Convert PDF pages to images for visual inspection
python3 -c "import pymupdf; doc = pymupdf.open('file.pdf'); doc[0].get_pixmap(dpi=150).save('page.png')"
# Or parse DOCX for paragraph/table structure
python3 -c "import docx; doc = docx.Document('file.docx')"
```

### 2. Identify Key Structural Elements
Extract these from reference:
- **Margins**: Top/bottom/left/right spacing (e.g., F4: 2.5cm top, 1.5cm sides, 2cm bottom)
- **Typography tiers**: Font sizes per element level (title vs. body vs. data)
- **Table schema**: Header row count, colspan/rowspan patterns
- **Header/footer zones**: Position relative to content boundaries
- **Signature placement**: Vertical positioning rules

### 3. Map to CSS Print Rules
```css
@page { 
    size: 215.9mm 330.2mm;  /* F4 */
    margin: 2.5cm 1.5cm 2cm 1.5cm; 
}

.ft-uth-18 { 
    font-family: 'KFGQPC Uthman Taha Naskh', 'Amiri', serif; 
    font-size: 18pt; 
    font-weight: bold; 
}

.ft-uth-16 { 
    font-family: 'KFGQPC Uthman Taha Naskh', 'Amiri', serif; 
    font-size: 16pt; 
}
```

### 4. Build Table Headers Carefully
**Pattern A** — Two-tier merged header (most common):
```html
<tr>
  <th rowspan="2">Column A</th>
  <th rowspan="2">Column B</th>
  <th colspan="2" style="white-space: nowrap;">Merged Title</th>
</tr>
<tr>
  <th>Sub1</th>
  <th>Sub2</th>
</tr>
```

**Critical fix**: Add `white-space: nowrap` to prevent long Arabic titles breaking into multiple lines:
```html
<th colspan="2" style="white-space: nowrap; font-size: 16pt;">أرقام الدرجات الخاصة والعامة</th>
```

### 5. Typography Calibration
| Element | Font Family | Size | Weight | Line-height |
|---------|------------|------|--------|-------------|
| Document title | KFGQPC Uthman Taha Naskh | 18pt | Bold | 1.15 |
| Section header | KFGQPC Uthman Taha Naskh | 16pt | Regular | 1.15 |
| Arabic table cells | KFGQPC Uthman Taha Naskh | 16pt | Regular | 1.1 |
| Numeric values | Times New Roman OR KFGQPC (for Arabic digits) | 14pt | Bold | 1.25 |
| Latin labels | Times New Roman | 14pt | Normal | 1.25 |

### 6. Validate Against Physical Reference
Compare side-by-side with printed PDF or Word document. Pay attention to:
- Vertical spacing between elements
- Text wrapping behavior
- Border thickness consistency
- Alignment rightness (RTL directionality)
- Footer pinning (use `margin-top: auto` on signature boxes)

## Pitfalls

### ❌ Don't trust default Tailwind line-height (1.5)
Arabic text needs tighter spacing:
```css
/* WRONG */
.rapot-sheet td { line-height: 1.5; }

/* CORRECT */
.rapot-sheet td { 
    padding: 1px 8px 3px 6px; 
    line-height: 1.1;  /* Tighter for Arabic */
}
```

### ❌ Don't let long headers break across lines
Always use `white-space: nowrap`:
```css
/* WRONG - might break */
<th>أرقام الدرجات الخاصة والعامة</th>

/* CORRECT - stays single line */
<th style="white-space: nowrap;">أرقام الدرجات الخاصة والعامة</th>
```

### ❌ Don't hardcode fixed margins with !important overrides
Use dynamic `margin-top: auto` for footer pinning:
```css
/* WRONG - breaks page height calculation */
.signature-box { margin-top: 1.27cm !important; }

/* CORRECT - flexible based on content height */
.signature-box { margin-top: auto; }
```

### ❌ Don't skip font glyph coverage
Times New Roman lacks Arabic-Hindi digits (٠١٢٣٤٥٦٧٨٩). Use KFGQPC for mixed content:
```css
td.td-num { 
    font-family: 'KFGQPC Uthman Taha Naskh', 'Amiri', serif; 
    font-size: 14pt; 
    font-weight: bold; 
}
```

## Verification Checklist
- [ ] All Arabic text renders with correct glyphs (no fallback to random fonts)
- [ ] Table headers don't wrap unexpectedly (`white-space: nowrap` applied where needed)
- [ ] Margins produce exact page layout without overflow
- [ ] Line-height allows full content within single F4 page
- [ ] Signature boxes pin to bottom edge consistently
- [ ] Numeric grades display correctly in Arabic-Hindi format
- [ ] RTL/LTR mixing handles alignment properly

## Tooling Support
- **PyMuPDF** (`pymupdf`) — Render PDF pages to PNG for visual inspection
- **python-docx** — Parse DOCX file structure (paragraphs, tables, alignments)
- **pdf2image** — Alternative PDF-to-image conversion if PyMuPDF unavailable

---

See `references/print-layout-spec.md` for detailed margin/typography specs.
See `templates/arabic-rapot.html` for starter template structure.