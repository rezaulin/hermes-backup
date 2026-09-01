# Raport Deployment Checklist & V24-V26 Lessons

## Complete Fix Summary

**Session goal:** Match raport layout to physical reference photos, fix text-touching-borders issue, ensure proper header/footer spacing per spec.

**Reference specs extracted from photo:**
- Paper size: F4 (215.9mm × 330.2mm)
- Page margins: Top 2.5cm, Right 1.5cm, Bottom 2cm, Left 1.5cm
- Header from top edge: 1.27cm
- Footer from bottom: 1.27cm
- Logo dimensions: 3×3 cm
- Fonts: Orange/Bold = Uthman Taha Naskh 18pt; Blue/Regular = 16pt; Green/Body = Times New Roman 14pt
- Column headers (RTL): الرقم | الكتب المدرسية | الفنون | الخاصة | العامة

## Version History & Fixes

### v23 Baseline
- Padding: `2px 6px` symmetric ❌
- Line-height: `1.15` ❌
- Books column header: **"الكتب الدراسية"** (wrong term) ❌
- Issues detected by user: "masih nyentuh" — text touching borders

### v24 Gap Fix (Strategy #3 - Combined)
**Changes:**
- Padding → `1px 8px 4px 6px` (asymmetric, more bottom space)
- Line-height → `1.22` (+6%, minimal safe increase)
- Books header corrected → **"الكتب المدرسية"** ✅
- **Result:** Gap improved from ~0.53mm to ~0.8-1.0mm ✅

### v25 Layout Spacing Fixes Attempted
**Issues discovered during patching:**
1. Invalid CSS on `tfoot th`: used `margin-bottom: 1.27cm` (ignored in table cells) + dangling `font-family:` 
2. Vite/PostCSS build failed with "Missed semicolon" error cascade
3. Need asymmetric approach for footer padding applied correctly

**Correct fix:** Changed to valid CSS using `padding: 1.27cm 6px` instead of margin.

### v26 Final Working Deploy
**Applied all fixes correctly:**
- ✅ Asymmetric cell padding works
- ✅ Footer padding properly specified
- ✅ Header margin-top: 1.27cm (not mepet logo anymore)
- ✅ Books column header spelling corrected
- ✅ Service Worker cache bumped to v24
- ✅ All builds pass, Docker deploys successfully

## Deployment Flow

```bash
# Step 1: Patch HTML files
patch /opt/simmubtadiat/frontend/rapot.html ...

# Step 2: Verify CSS syntax locally before Docker
cd frontend && npm run build   # catches PostCSS errors early

# Step 3: If build passes, update cache version
sed -i 's/mubtadiaat-cache-v23/mubtadiaat-cache-v24/' public/sw.js

# Step 4: Commit
git add frontend/rapot.html frontend/public/sw.js
git commit -m "rapot v24: gap fix + combined strategy"

# Step 5: Push
git push origin main

# Step 6: Deploy via Docker
docker compose -f docker-compose.yml up -d --build app

# Step 7: Verify live cache
curl -s https://reviewtechno.me/sw.js | grep -oE 'v\d+'
```

## Common Pitfalls & Solutions

### Pitfall 1: Using margin on table elements
❌ `tfoot th { margin-bottom: 1.27cm; }`
✅ `tfoot th { padding: 1.27cm 6px; }`

### Pitfall 2: Symmetric padding doesn't account for descenders
❌ `padding: 2px 6px;`
✅ `padding: 1px 8px 4px 6px;`

### Pitfall 3: CSS syntax error breaks Docker build
When you see `[vite:css] [postcss] ... Missed semicolon` in docker build logs → check line numbers in stylesheet. The error points to `rapot.html?html-proxy` which means it's parsing inline styles from HTML file. Look for:
- Dangling property declarations
- Missing semicolons before `}`
- Incorrect property order breaking cascade parser

**Fix:** Run `npm run build` locally first to catch errors fast, then deploy.

### Pitfall 4: Wrong Arabic terminology in column headers
Reference photo uses **"الكتب المدرسية"** (school books), not "الكتب الدراسية". Must match exactly for "plek ketiplek" requirement.

### Pitfall 5: PyMuPDF render vs browser discrepancy
If PDF measurement shows adequate gap but user screenshot shows touching → trust user! Browser anti-aliasing makes gaps appear tighter. Adjust anyway.

## Verification Commands After Deploy

```bash
# Check if SW cache updated
curl -s https://reviewtechno.me/sw.js | grep -oE 'v\d+'

# Inspect live HTML
curl -s https://reviewtechno.me/rapot.html | grep -E '(line-height|padding|Books)'

# Test print preview locally (Docker container)
docker exec simmubtadiat-app-1 bash -c "echo '<script>window.print()</script>' > /app/public/test.html && open http://localhost:8080/test.html"
```

## Files Modified in Session

| File | Changes |
|------|---------|
| `/opt/simmubtadiat/frontend/rapot.html` | Cell padding, line-height, header text, footer styling |
| `/opt/simmubtadiat/frontend/public/sw.js` | Cache version bump v23→v24 |

## Proof Artifacts Created

- `/tmp/v23_before_gap_comparison.png` — Tight gap visual
- `/tmp/v24_after_gap_comparison.png` — Improved gap visual  
- `/tmp/v23_vs_v24_side_by_side.png` — Side-by-side comparison
- `/root/.hermes/cache/images/img_*.jpg` — User's reference raport photos

## User Communication Style Notes

User expects:
- ✅ Direct, no fluff explanations
- ✅ Visual proof/screenshots generated automatically
- ✅ Technical reasoning ("why we chose this fix")
- ✅ Multiple solution options with trade-offs presented
- ✅ "Gas" command when ready to deploy

**Response template:**
> "Gue analisa dulu... Oke found the issue! Solution: X (quick explanation). Here's proof: [screenshots]. Ready to deploy? Gas."

---

**Document Created:** 2026-08-25  
**Session Context:** Raport v24-v26 deployment cycle  
**Next Action Items:** None — task complete, user confirmed OK after visual verification