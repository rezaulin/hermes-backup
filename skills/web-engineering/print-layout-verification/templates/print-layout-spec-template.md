# Print Layout Spec Template

## Usage
Copy this template and fill in your project's layout specifications based on the physical reference document.

---

## Physical Reference Specifications

### Paper Size & Orientation
- **Size**: [ ] A4 | [ ] F4 | [ ] Letter | [ ] Other: ______
- **Dimensions**: ______ mm × ______ mm (width × height)

### Page Margins
```
Top:    ______ cm
Bottom: ______ cm  
Left:   ______ cm
Right:  ______ cm
```

### Header Positioning
- **From top edge**: ______ cm
- **Logo dimensions**: ______ cm × ______ cm
- **Logo position**: Top-left / Top-center / Top-right

### Footer Spacing
- **From bottom edge**: ______ cm

### Typography Requirements

| Element | Font Family | Size | Weight | Color | Notes |
|---------|-------------|------|--------|-------|-------|
| Headers | e.g., Uthman Taha Naskh | 18pt | Bold | Orange (#FFA500) | Arabic RTL text |
| Body | Times New Roman | 14pt | Regular | Green (#2E8B57) | English/Indonesian |
| Labels | KFGQPC Uthman | 16pt | Semi-bold | Blue (#4169E1) | Secondary info |

### Column Structure (for tables)
1. Column 1: _______________ | Width: ______
2. Column 2: _______________ | Width: ______
3. Column 3: _______________ | Width: ______
4. ...

**Header order (RTL)**: List from right to left, not left to right!

### Gap Tolerance
- **Minimum text-to-border clearance**: ~0.7mm (Arabic descenders may need up to 1.0mm)
- **Acceptable "visual touch" limit**: 0.5mm (not actual pixel contact)
- **Measurement method**: Use user's browser screenshots, NOT PDF renders

### Special Notes
- Column headers must match reference photo EXACTLY (spelling, word count)
- Arabic script requires asymmetric padding for descenders (خ ج ح ع غ ي)
- Always test via actual browser print preview (Chrome/Firefox), not just CSS metrics
- Cloudflare static cache = 4 hours → bump filename/version after ANY change

### Implementation Strategy

**For text touching borders:**
1. First try: Increase line-height slightly (+0.05-0.07)
2. If insufficient: Use asymmetric padding `padding: 1px 8px 4px 6px`
3. Best result: Combine both approaches

**Validation checklist:**
- [ ] No text visually touching horizontal grid lines
- [ ] Content fits within one page (check both A4 and F4 limits if needed)
- [ ] All column headers match reference exactly
- [ ] Footer structure preserved (merged cells intact)
- [ ] Service Worker cache bumped after deployment

---

**Document Created**: YYYY-MM-DD  
**Reference Photo**: [Path to user-provided image]  
**Status**: Verified ✅ / Needs Adjustment ⚠️
