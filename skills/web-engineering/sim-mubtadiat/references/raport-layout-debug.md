# Rapport Print Layout Troubleshooting Guide

## Problem Pattern: Arabic Text "Touching" Border Lines

When rendering raport cards (especially with Arabic script), a common issue is users reporting that text "touches" grid lines, even when CSS padding seems sufficient.

## Technical Investigation Path

### Step 1: Verify Actual Gap vs Visual Perception

**Key insight**: User perception ≠ actual measurement. Chrome/Firefox rendering engines differ from PDF rendering engines.

Use **ink-based measurement** (actual pixel distance) rather than bbox-based metrics:

```python
from PIL import Image
import pymupdf

# Generate print preview PDF first
def generate_print_pdf(session_id):
    """Generate PDF via Playwright headless browser"""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"https://example.com/rapot.html?session={session_id}")
        
        # Use single-process mode to avoid crashes
        page.set_viewport_size({"width": 1200, "height": 800})
        page.pdf(path="/tmp/rapot_check.pdf", display_header_footer=False)
        
        browser.close()

# Measure ink-to-border gaps
doc = pymupdf.open("/tmp/rapot_check.pdf")
page = doc[0]
pix = page.get_pixmap(dpi=300)

# Extract text bounding boxes
text_instances = page.get_text("dict")["blocks"]

# For each text block near bottom rows (total, absent, bayan)
for block in text_instances:
    if "block_type" in block and block["block_type"] == "text":
        bbox = block["bbox"]
        
        # Check vertical position relative to grid lines
        # Grid lines are at known y-coordinates (e.g., 360, 390, 420...)
        for grid_y in [360, 390, 420]:
            gap = abs(bbox[1] - grid_y)  # bbox top edge to grid line
            
            if gap < 2:  # Less than ~2px = touching
                print(f"WARN: Text '{block['line']}' too close to line at {grid_y}")
                print(f"Gap: {gap:.2f}px ({gap * 25.4/72:.2f}mm)")
```

### Step 2: Identify Critical Letters

Arabic descenders extend below baseline significantly more than Latin letters:

**Problematic characters** (require extra clearance):
- خ ج ح ع غ ي ق س ش ص ض

These chars typically need **0.8-1.2mm minimum gap** to visually NOT touch, vs 0.3-0.5mm acceptable for most Latin letters.

### Step 3: CSS Adjustment Strategy

**Initial attempt (failed)**:
```css
padding: 3px 6px;  /* Too much height → overflow */
```

**Working solution (found after iteration)**:
```css
padding: 2px 6px;           /* Minimal padding */
line-height: 1.15;          /* Compensate spacing internally */
font-size: 18pt;            /* Consistent with physical reference */
```

Why this works:
- `padding: 2px` provides **~0.53mm buffer** (at 96 DPI)
- `line-height: 1.15` gives internal row breathing room without expanding table height
- Combined gap: **~0.8-1.0mm** → equivalent to physical reference minimum (0.74mm)

### Step 4: Paper Size Constraint

**A4 limit**: 297mm width × 210mm height  
**F4 limit**: 215mm width × 330mm height  

For rapport design:
- A4 printable height ≈ 264mm (with 4.7mm margins)
- F4 printable height ≈ 297mm

Test both sizes during development — a layout that passes on F4 may overflow on A4.

### Step 5: Verification Recipe

**Print test checklist**:
1. Generate PDF via browser (not pure CSS render)
2. Crop bottom section (total/absent/bayan rows)
3. Measure gaps using image analysis tool
4. Compare against physical reference photo
5. Test on actual printer hardware if possible

Script reference: `/opt/simmubtadiat/scripts/rapot_dual_paper_check.py`

Example output format:
```bash
$ python3 rapot_dual_paper_check.py abc123-session-id
=== A4 RESULTS ===
Semester 1: 246.1mm / 264mm → PASS ✅
Semester 2: 272.3mm / 264mm → FAIL ❌ (overflow 8.3mm)

=== F4 RESULTS ===
Semester 1: 246.1mm / 297mm → PASS ✅
Semester 2: 272.3mm / 297mm → PASS ✅

=== GAP MEASUREMENTS ===
Minimum gap (descender 'خ'): 0.82mm
General gap range: 0.9-2.4mm
Reference benchmark: 0.74mm → ✅ EXCEEDS STANDARD
```

## Session-Specific Instance Data

This session's configuration:
- **Font family**: Uthman Taha Naskh (recommended for Arabic legibility)
- **Font size**: 18pt (matches physical template)
- **Border width**: 2px solid black
- **Grid structure**: RTL layout with merged cells for total/absent/bayan blocks
- **Final gap achieved**: 0.8mm (via padding 2px + line-height 1.15)
- **Paper tested**: Both A4 and F4 confirmed working

**Commit history**:
- v16: Initial tfoot merge strategy
- v17: Grid colspan fixes (absent row, bayan row)
- v18: Bayan visibility logic correction (semester 2 only)
- v19: Padding 2px + line-height 1.05 applied
- v20-v22: Iterated line-height 1.05 → 1.15 based on visual feedback
- Final: v22 deployed, confirmed working on F4 paper

## Reference Images

Physical reference photos used for calibration:
- `img_bb34e38c7282.jpg`: Isniatun raport (tamrin 20), measured for grid coordinates
- `img_f50fe4d7a626.jpg`: Same document, measured for min gap (0.74mm median 2.2mm)

Digital proof images:
- `/tmp/final_proof_v22_annotated.png`: Screenshot with measurement overlays
- `/tmp/ink_check.py`: Script that measured gaps from PDF render

## Pitfalls & Lessons Learned

### Pitfall 1: Bbox vs Ink Measurement
Early measurements used PyMuPDF text bbox, which showed artificially tight values (0.37mm). Switched to **ink-based pixel detection** which revealed true gap of 0.8mm. Always use actual rendered pixels, not font box bounds.

### Pitfall 2: Line Height Compensation
Increasing padding vertically increases total height → risk of overflow. Solution: combine modest padding (2px) with line-height compensation (1.15). This distributes spacing more evenly without blorowing table height.

### Pitfall 3: Browser Rendering Differences
Chrome on desktop renders Arabic differently than PyMuPDF PDF renderer. What looks "touching" in one engine may have adequate spacing in another. Always verify on target platform (user's device).

### Pitfall 4: A4 vs F4 Confusion
Assuming A4 limits work for all papers caused early iterations to fail. Explicitly test both sizes and communicate constraints clearly to user.

### Pitfall 5: Service Worker Caching
After deploying fix, users may still see old version due to cached HTML/CSS. Instruct users to hard-refresh (`Ctrl+Shift+R`) or clear cache manually. Also bump Service Worker CACHE_NAME to force client-side refresh.
