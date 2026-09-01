# Gap Measurement Methodology for Arabic Typography

## Problem Context

Arabic script contains **descender letters** that extend significantly below the text baseline:
خ ج ح ع غ ي (and forms of س ش ص ض)

These require **extra bottom clearance** to prevent visual "touching" of horizontal grid lines/borders.

## Reference Benchmark from Physical Photos

Measured from user-provided raport reference photos (Isniatun/Iswatun sheets):

```
Bottom gap (tinta ke garis bawah):  median 2.2mm, min 0.74mm
Top gap (garis atas ke tinta):      median 1.5mm
```

**Rule:** Text should have minimum **~0.7mm clearance** from horizontal borders. User explicitly accepts "nyentuh dikit gak masalah" — visual proximity ~0.5mm is tolerable, hard-touching is not.

## Pixel-to-Millimeter Conversion

At screen DPI ~96: `1px ≈ 0.26mm`. So 2px padding ≈ 0.53mm (tight), 4px ≈ 1.05mm (safe).

## Rendering Discrepancy (critical pitfall)

PyMuPDF/Playwright renders ≠ Chrome browser print preview. Browser anti-aliasing makes gaps appear **tighter** than CSS metrics indicate. If user reports "masih nyentuh" from a real browser photo even though PDF measurement showed 0.8mm gap → trust the user, increase clearance. Measure from the USER'S actual browser screenshot, not your PDF render.

## Strategy Selection

| Current gap | Target | Solution | Risk |
|---|---|---|---|
| ≤0.53mm | ≥0.7mm | Asymmetric padding | Low |
| 0.7-0.8mm | ≥0.7mm | Small line-height bump | Very low |
| ≥0.9mm | — | No fix | None |

## Implementation Patterns

```css
/* NOT recommended — symmetric, tight for descenders */
padding: 2px 6px;

/* RECOMMENDED — asymmetric, more space below */
padding: 1px 8px 4px 6px;

/* BEST — combined, no overflow risk */
padding: 1px 8px 4px 6px;
line-height: 1.22;

/* Page vs element margins — don't confuse them */
@page { size: F4; margin: 2.5cm 1.5cm 2cm 1.5cm; }
.header-container { margin-top: 1.27cm; }
```

## CSS Validity Pitfall

`margin-bottom` on `tfoot th` is invalid/ignored in table layout and breaks Vite/PostCSS build ("Missed semicolon" cascade when combined with a dangling `font-family:`). Use `padding` inside table cells; run `npm run build` in frontend/ BEFORE docker compose up to catch syntax errors early — docker build failure surfaces at `RUN npm run build` with a truncated message.

## Verification Commands

```bash
cd /opt/simmubtadiat/frontend && npm run build   # catch CSS syntax errors fast
docker compose -f /opt/simmubtadiat/docker-compose.yml up -d --build app
curl -s https://reviewtechno.me/sw.js | grep -o 'mubtadiaat-cache-v[0-9]*'
```

## Validation Checklist

- [ ] No text touching borders in user's actual browser preview (not your PDF)
- [ ] Gap ~0.7-1.0mm minimum at descenders
- [ ] Content fits one page (F4: sem1+sem2 each ≤297mm)
- [ ] Header exact match to reference spelling (الكتب المدرسية NOT الدراسية)
- [ ] Footer merged-cell structure intact
- [ ] SW cache bumped
