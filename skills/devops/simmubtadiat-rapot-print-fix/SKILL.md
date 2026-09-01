---
name: simmubtadiat-rapot-print-fix
version: 1.0
created: 2026-08-25
domain: simmubtadiat
tags: [print, raport, arabic-text, layout]
description: Fix print layout issues in SIM Mubtadiat raport by matching reference Word documents exactly
---

# Fix Print Layout Issues for SIM Mubtadiat Raport

Fixes Arabic text layout issues in raport print preview by matching reference Word document exactly.

## Context
SIM Mubtadiat generates report cards (raport) with Arabic text in RTL format. The print layout must exactly match reference `.docx` files uploaded by user — no improvisation allowed.

## Common Issues & Fixes

### Issue 1: Table Header Stacking Vertically
**Symptom:** `أرقام الدرجات الخاصة والعامة` stacks across 2+ rows instead of spanning horizontally

**Root Cause:** Using `rowspan="2"` on main columns breaks header structure

**Fix:**
```html
<!-- WRONG -->
<th rowspan="2">الكتب الدراسية</th>
<th rowspan="2">الفنون</th>
<th colspan="2">أرقام الدرجات الخاصة والعامة</th>

<!-- CORRECT: keep rowspan=2, add padding for spacing -->
<th rowspan="2" style="padding-bottom: 8px;">أرقام الدرجات<br>الخاصة والعامة</th>
```

**Alternative (preferred):** Keep original colspan structure:
```html
<th colspan="2" style="font-size: 16pt; padding-bottom: 8px;">
  أرقام الدرجات الخاصة والعامة
</th>
```

### Issue 2: Header Structure Changes
**Rule:** NEVER redesign header based on theory. User provides Word reference as GOLD STANDARD.

**Golden Rules:**
- Logo MUST appear left & right in header
- Title = Uthman Taha Naskh 18pt bold
- School name = Uthman Taha Naskh 16pt  
- Semester = Uthman Taha Naskh 18pt bold
- Horizontal line after school name (margin-top: 8px)
- Year = centered below separator

## Verification Steps

1. **Compare against reference Word file** - screenshot side-by-side
2. **Check table header columns** - verify `colspan` vs `rowspan` count matches
3. **Measure vertical spacing** - ensure Arabic descenders don't clip borders
4. **Test actual print** - screen preview ≠ physical output

## File Locations
- HTML template: `/opt/simmubtadiat/frontend/rapot.html`
- JavaScript generator: `/opt/simmubtadiat/frontend/src/js/rapot.js`
- Reference docs: `~/.hermes/cache/documents/*.docx`

## Deployment
```bash
cd /opt/simmubtadiat
docker compose down app
docker compose build app  # Rebuilds frontend static assets
docker compose up -d app
curl -s https://reviewtechno.me/rapot.html | grep "أرقام"  # Verify changes
```

## Pitfalls to Avoid
❌ Don't change existing structure just because "looks wrong"  
❌ Don't assume Arabic font metrics without testing  
❌ Don't use inline styles that override @page margins  
❌ Don't remove logo elements even if reference unclear  

✅ DO match reference .docx pixel-for-pixel  
✅ DO test on F4 paper dimensions (215.9×330.2mm)  
✅ DO use KFGQPC Uthman Taha Naskh font only for Arabic  
✅ DO preserve tbody/thead semantic structure

## Related Skills
- `sim-mubtadiat` - overall system operations
- `print-layout-match` - general print verification workflow