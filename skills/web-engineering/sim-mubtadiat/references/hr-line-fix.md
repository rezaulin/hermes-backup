# Horizontal Line Styling Fixes (raport HTML)

## Pattern: Header separator line too long / not visible in print preview

### Root Cause
HR element styling conflicts with parent container borders + CSS print media query defaults.

### Symptoms
- Line extends almost touching logo (width too large)
- Spacing to year text too far (margin bottom insufficient)
- Not visible in browser print preview (print-color-adjust missing)

### Fix Template (2026-08-25 rapport.html)

**BEFORE:**
```html
<hr style="border:none;height:1px;background-color:#000;margin:3px auto;width:75%;">
```

**AFTER:**
```html
<!-- 1. Width reduction: 75% → 55% + min-width fallback -->
<hr style="border:none;height:2px;background-color:#000;margin:2px auto 8px auto;width:55%; min-width: 120px;">
```

**CSS adjustments:**
- `height: 2px` (not 1px) → more visible when printed
- `margin: 2px auto 8px auto` → top gap minimal, bottom gap to tahun ajaran increased
- `width: 55%` with `min-width: 120px` → prevents overflow on wide screens

---

### Critical Addition: Print Media Query Visibility

If line still missing in print preview, add explicit print rules:

```css
@media print {
    .rapot-sheet hr {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
        display: block !important;
    }
}
```

**Why needed:** Browser print renderer can strip inline styles on decorative elements. The `-webkit-print-color-adjust: exact` forces the background color to render even if it's normally considered "non-print" content.

---

### Verification Checklist

1. **Count HR tags**: `grep -c '<hr' rapot.html` should match expected count (raport = 1, after school name only)
2. **Check parent borders**: Look for `border-b-*` classes on wrapper divs that visually mimic extra lines
3. **Print test**: Navigate to `/rapot.html`, Ctrl+P, verify line appears between sekolah name and year text
4. **Actual print**: F4 paper size, margin 2.5cm top / 1.5cm sides / 2cm bottom (matches spec)

---

### Common Pitfalls

#### Extra Lines Bug
Owner reports "garis ada 2" or "gak ada garis" — check BOTH:
- `<hr>` element count (inline tag)
- Parent container border styles (`border-b-4`, `border-black`)

Visual output ≠ element count. A thick border on a flex wrapper creates same visual as an HR line.

#### Alignment Issues
Line centered via `margin: ... auto` assumes parent has consistent width. If wrapping flex container has `justify-content: space-between`, the line may appear left/right instead of center. Use `text-align: center` on parent OR keep line as block element with explicit `display: block`.

---

### Related Patterns
- See `print-layout-measurement.md` for full screenshot comparison workflow
- See `line-count-pitfall.md` for diagnosis when owner reports mismatched visual vs DOM
- Parent skill `sim-mubtadiat` → "Header Structure v29-v31" section for logo positioning bugs
