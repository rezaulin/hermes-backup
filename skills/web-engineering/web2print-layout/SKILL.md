---
name: web2print-layout
category: web-engineering
description: Web-to-print layout engineering — precise HTML/CSS positioning for print-ready reports, avoiding browser print bugs.
---

# Web Print Layout Engineering

Class of tasks: Achieving pixel-perfect print layouts from HTML/CSS in browsers (Chrome/Edge PDF). Focus: position-controlled layouts where visual fidelity matters (reports, invoices, official documents).

## When to use this skill

- User needs print-ready HTML that matches a physical reference (Word doc, PDF, paper)
- Layout involves logos, headers, signatures, or other fixed-position elements
- Browser print preview shows cropping, overflow, or element displacement
- RTL (Arabic text) interferes with left-aligned elements like logos

## Core principles

### 1. Page sizing: @page vs inline dimensions

Use BOTH:

```css
@media print {
    @page {
        size: 215.9mm 330.2mm; /* F4 example */
        margin: 15mm;
    }
}
.raport-sheet {
    width: 215.9mm;
    min-height: 330.2mm;
    padding: 2.5cm 1.5cm 2cm 1.5cm;
}
```

Don't rely on screen-only min-height — print needs explicit page-break rules:

```css
.raport-sheet {
    page-break-after: always;
    page-break-inside: avoid;
    break-inside: avoid;
}
```

### 2. Logo positioning: absolute > flexbox for left-alignment

Problem: Flexbox wraps with RTL direction, causing logos to flip right instead of stay left.

**Solution:** Use `position: absolute` for left-fixed elements:

```css
.header-wrapper {
    position: relative;
    width: 100%;
    min-height: 80px;
}

.header-logo {
    position: absolute;
    left: 0;
    top: 0;
    width: 90px;
    height: auto;
}

.header-text {
    margin-left: 120px; /* Push text past logo */
    text-align: center;
    direction: rtl;
}
```

This keeps logo locked LEFT regardless of RTL text direction inside same container.

### 3. Horizontal lines: background-color hack

Don't use `<hr>` alone — sometimes renders invisible or inconsistent. Use:

```css
.year-line {
    width: 60%;
    height: 0.3mm;
    background-color: #000;
    margin: 3px auto 2mm auto;
}
```

Thin heights (0.3–0.35mm) render crisper in PDF than thick borders.

### 4. Student data layout: flex-row + nowrap

For label-value pairs that shouldn't wrap:

```css
.student-row {
    display: flex;
    align-items: baseline;
    white-space: nowrap;
}

.student-label {
    width: 75px;
    text-align: right;
    margin-right: 6px;
}
```

This prevents wrapping across lines when printed.

### 5. Color control: hard black

For official docs, lock everything to pure black (#000000). Don't use theme colors or gradients.

## Common pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Logo jumps to right side | Flexbox + RTL interaction | Use `position: absolute; left: 0` instead |
| Print preview shows only half-page | Missing `@page` size or overflow | Add explicit `@page` + `overflow: visible` |
| Horizontal line invisible | Using `<hr>` without border | Use `background-color` div with thin height |
| Footer sign-off on wrong page | min-height too large | Reduce sheet min-height below printable area |
| Label-value wrapped across lines | No whitespace control | Add `white-space: nowrap` to rows |
| Bold values look gray | Theme color applied | Force `color: #000000 !important` |

## Verification steps

1. **Check print preview FIRST** before committing any output
2. Look for: logo position (left?), full page visible (not cropped)?, all content fits?
3. If half-page visible → increase min-height OR reduce margins
4. If logo displaced → switch to absolute positioning
5. Test with actual printer after browser PDF works

## Tools

- Chrome DevTools → Print → Preview
- `window.getComputedStyle(el)` to inspect computed sizes in mm
- Measure physical paper with ruler if exact reproduction needed
- Reference Word .docx files as gold standard — reverse engineer their layout

## References

- [Web2Print HTML Reference](references/web2print-html.md)
- [F4 Paper Specifications](references/f4-paper-spec.md)
- [SIM Mubtadiat Report Card Example](references/simmubtadiat-rapot-layout.md)