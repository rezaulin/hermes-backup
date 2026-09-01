# Image-Based Layout Debugging Flow (2026-08-25)

## When to Use

Owner reports visual issues based on screenshots: "gap terlalu jauh", "garis gak muncul", "text menyentuh border", or any print-layout mismatch described via photo.

## NEVER Start With CSS Guessing

Don't add padding, don't change line-height — these guesses failed during 2026-08-25 session progress: 5 pages → 4 → 3 → 2 only worked after MEASUREMENT.

## Step-by-Step Workflow

### 1. Render Actual Output First

**Tool**: Playwright in print mode OR `/tmp/render_live.py` script

```python
# Playwright example
await browser.newPage({ viewport: { width: 215.9*96/25.4, height: 330.2*96/25.4 } })
await page.goto('https://reviewtechno.me/rapot.html')
await page.emulateMedia({ media: 'print' })
await page.screenshot(path='/tmp/current_rapot.png', fullPage=True)
```

Or use existing ready script: `/tmp/render_live.py <santri_id> --semester <N>`

### 2. Measure Gaps Directly

**Tool**: `/scripts/detect_table_grid.py <reference_photo.jpg>`

This scans reference photos for horizontal row-separator lines + per-band vertical lines to detect colspan/rowspan merges from pixel positions.

Expected output shows X-coordinates where borders appear:
```
Horizontal lines at Y: [45mm, 78mm, 112mm, ...]
Vertical lines in data band at X: [55px, 162px, 240px, 354px, 511px]
```

Compare measured vs actual rendered output gap = (actual_line_Y - text_bottom_px).

### 3. Apply Surgical Fixes

Only after measurement, know EXACTLY what's oversized:

**Common culprits discovered 2026-08:**
- tfoot padding: `1.27cm` → `1px 6px 4px 6px` (saved ~68mm per row)
- Line-height: `1.22` → `1.1` for table cells (saved ~10mm total rows)
- Min-height tuning: `285mm` → `270mm` gave headroom for rounding errors
- Logo size: `width: 3cm` → `60px` (overflow fix)

**Key insight**: Font descenders (خ ج ح ع غ ي ق) extend below baseline — asymmetric padding (`padding-top: 2px; padding-bottom: 4px`) handles this better than symmetric values.

### 4. Re-Measure & Iterate

Run detection again on new screenshot. Compare measured gaps against reference photo. If still off by >0.5mm, adjust ONE value at a time and re-test.

**Never make multiple CSS changes without verification** — you won't know which one fixed it.

## Vision Tool Failure Triage

When vision tool fails (timeout, quota, no model configured):

### Level 1: Fix Config First
```bash
hermes config set auxiliary.vision.provider fireworks
hermes config set auxiliary.vision.model "accounts/fireworks/models/kimik3"
```

### Level 2: OCR Fallback
Install system packages:
```bash
apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-ind tesseract-ocr-ara
pip3 install pytesseract
```

Use ready script: `/root/.hermes/skills/web-engineering/sim-mubtadiat/scripts/ocr_tool.py <image_path> --lang="eng,ind,ara"`

Works on screenshots with Arabic text, raport tables, forms. Confidence scores provide quality feedback (~56% on blurry, higher on clean renders).

### Level 3: FFmpeg Video Analysis
For video uploads:
```bash
ffmpeg -i video.mp4 -vf select='gt(scene,0.05)',metadata=print metadata
```

Cuts timestamps + motion density per second (score >0.5 = hard cut; many small events/sec = dancing/spinning).

### Level 4: PIL Annotation Detection
When owner says "yang saya lingkari": scan for saturated pen pixels (red `r>140, r-g>40, r-b>40`; also yellow/blue bands), report count + bbox + density-per-band to LOCATE the circles.

## Common Pitfalls

1. **Anti-aliasing effects**: Monitor display smoothens edges, making text visually "closer" to borders than pixel measurements show
2. **Rendering engine differences**: PyMuPDF/300DPI render ≠ Chrome desktop browser ≠ mobile Chrome
3. **Hardware scaling**: Phone screens have different DPI than desktop monitors
4. **Cloudflare cache trap**: CF serves stale `.png` files even after container restart — always check filename has `-vN` suffix or use direct curl to bypass cache

## Session Learnings (2026-08-25)

**Trilemma discovered**: Cannot satisfy both "text never touches grid lines" AND "fits exactly 1 page A4". Measured from reference photo: initial v19 had only 0.37mm gap (text visually touching), but increasing padding/line-height to fix gap caused overflow (>264mm A4 limit).

**Resolution**: Use F4 paper (limit 297mm) → sem2 = 272.3mm fits comfortably with improved gap (~0.8-1mm visual). If A4 is mandatory, accept ~0.8mm gap as meeting physical reference standard (min gap in reference photo = 0.74mm).

## Tools & Scripts Created

| Script | Path | Purpose |
|---|---|---|
| `render_live.py` | `/tmp/` | Renders live data to PDF/image for comparison |
| `detect_table_grid.py` | `/root/.hermes/skills/web-engineering/sim-mubtadiat/scripts/` | Scans reference photos for grid structure |
| `measure.py` | `/tmp/` | Measures section heights (thead/tbody/tfoot/signature) |
| `photo_gap_check.py` | `/root/.hermes/skills/web-engineering/sim-mubtadiat/scripts/` | Measures exact pixel gaps between text and borders |
| `ocr_tool.py` | `/root/.hermes/skills/web-engineering/sim-mubtadiat/scripts/` | Extracts text from images using tesseract |
| `rapot_dual_paper_check.py` | `/root/.hermes/skills/web-engineering/sim-mubtadiat/scripts/` | Verifies both A4 and F4 layouts side-by-side |

Use these directly — they're battle-tested from 2026-08 sessions.

## Quick Reference

**Owner complaint** → **First action**
- "Gap terlalu jauh" → Measure actual rendered output (Playwright screenshot)
- "Garis gak muncul" → Check print-mode CSS + verify with render script  
- "Text menyentuh border" → Count mm of descender space needed, measure current font metrics
- "Tumpah jadi 5 halaman" → Measure each section's height in mm, find the outlier
- "Warna background hilang" → Check overlay opacity (<0.65 required), verify Cloudflare cache status
- "Vision tool timeout" → Switch to tesseract OCR fallback

**Always ask**: "Lo mau gua analisa apa sama gambarnya?" before starting diagnosis. Never assume visual issues = print layout bugs.
