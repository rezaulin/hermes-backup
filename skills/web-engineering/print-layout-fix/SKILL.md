---
name: print-layout-fix
tags: [print, layout, html-css, docker]
version: 1.0
author: Qoder
last_updated: 2026-08-26
related_skills: [web-app-status-check, print-layout-verification]
description: Engineering print-ready HTML/CSS layouts matching physical references (raport, invoices) using table-based layout for stable alignment
---

# Print Layout Engineering for Documents

Class of task: Fix HTML/CSS print layouts that don't match physical references (raport, invoices, certificates). Focus on precision spacing, stable alignment, and avoiding browser print artifacts.

## Trigger Conditions
- User provides screenshot/scan of printed document as reference
- Report/rapot/certificate output doesn't match physical reference
- "Garis sudah rapi tapi X masih salah" type correction
- Frustration signals like 'hadeh', 'malah rusak', 'aku muak'

## Class Approach

### 1. Confirm Paper Size FIRST (critical!)
**F4** (Indonesia standard): 215.9mm × 330.2mm  
**A4**: 210mm × 297mm

Never guess — ask user or check their physical reference. Wrong size = partial print + pagination disaster.

```css
@page {
    size: 215.9mm 330.2mm; /* or 210mm 297mm */
    margin: 15mm;
}
```

### 2. Table Layout > Box Model for Print
Flexbox/grid breaks unpredictably in browser print mode. Tables give deterministic column alignment:

```html
<table class="student-table">
  <tr>
    <td class="st-left">...</td>
    <td class="st-right">...</td>
  </tr>
</table>
```

**Key properties:**
- `border-collapse: collapse` only if visible borders needed
- Fixed width cells (`width: 80px`, `text-align: right`)
- No padding conflicts (`padding: 0`, `vertical-align: top`)

### 3. Logo Positioning Trick
Don't use flex-wrap or justify-content — logo moves around. Use absolute positioning:

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
}
```

This locks logo LEFT while text can center independently.

### 4. Line Divider Placement
Common mistake: line under entire header block. Correct: line under title ONLY, before meta info:

```html
<h2>Title</h2>
<p>Madrassah Name</p>
<hr class="year-line">
<p>Year Info</p>
```

CSS:
```css
.year-line {
    width: 60%;
    height: 0.3mm;
    background-color: #000;
    margin: 3px auto 2mm auto;
}
```

### 5. Student Identity Block
Fixed-width labels ensure colon alignment across rows:

```css
.st-label {
    text-align: right;
    white-space: nowrap;
    width: 80px;
    padding-right: 6px;
}

.st-colon {
    width: 10px;
    text-align: center;
}

.st-value {
    padding-left: 4px;
}
```

Two columns split 50% each, separated by space.

### 6. Debug Workflow
1. Open print preview (Ctrl+P)
2. Check page dimensions match spec
3. Verify full content visible (no overflow/truncation)
4. Measure spacing visually (margin/padding in mm)
5. Iterate CSS → build → deploy → test cycle

## Pitfalls
- ❌ Using flexbox/grid for identity blocks (unreliable in print)
- ❌ Assuming A4 without confirmation (F4 is taller)
- ❌ Putting line under entire header instead of mid-header
- ❌ Forgetting Docker rebuild after CSS changes
- ❌ Browser caching old styles (use hard reload)

## User Preferences (Observed)
- Direct fixes first, explanations minimal
- Hard reload instruction if changes not visible
- Don't over-explain after successful fix
- When frustrated: STOP, confirm what's wrong, then execute

## Tool Stack
- Terminal: `docker compose build/up` for hot-reload
- Browser DevTools: Network tab disable cache, force reload
- Vision analysis: screenshot comparison for precision
- Git commit before pushing to production

## Related Skills
- web-app-status-check: verify deployment success
- hermes-agent-skill-authoring: encode learnings into reusable skills
- print-layout-verification: validate against physical reference