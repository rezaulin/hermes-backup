# RTL Flexbox Logo Order - v35 Session Notes (2026-08-25)

## Problem Pattern: Logo Position Confusion in Arabic Raport Layout

### Root Cause
Agent repeatedly misplaces logo LEFT/RIGHT due to misunderstanding how RTL (`dir="rtl"`) interacts with flexbox.

**WRONG ASSUMPTION**: "RTL should reverse visual order, so text on right, logo on left"

**REALITY**: With default `flex-direction: row` and `dir="rtl"`:
- Element 1 (first in DOM) → KIRI (left side of paper)
- Element 2 (second in DOM) → KANAN (right side of paper)

This is counter-intuitive but CORRECT behavior for RTL flex containers.

### Evidence from User Feedback Loop

**Session 2026-08-25 Debugging:**
1. Initial attempt: Logo RIGHT ❌
   - User: "Logo raport lo bos yang dimaksud... sekarang logo ada dikanan seharusnya dikiri"
   
2. First fix: Swapped HTML order ✅
   - Moved `<img>` BEFORE `<div class="header-text">`
   - Result: Logo LEFT ✓

3. Verification pattern established:
   ```html
   <!-- ✅ CORRECT: Image first = kiri -->
   <div dir="rtl" class="flex">
       <img src="/logo.png">    <!-- First element = LEFT -->
       <div class="text">...</div>  <!-- Second element = RIGHT -->
   </div>
   ```

### Why This Mistake Happens
Agent's mental model assumed: "RTL = flip everything horizontally so text aligns right margin"

But CSS Flexbox + RTL works differently:
- Text alignment inside elements respects RTL (content flows right-to-left)
- BUT **element positions within flex container** respect DOM order
- No automatic flipping happens unless you use `direction: ltr` on parent or explicit transforms

### User Correction Signals
When user says:
- "Sekarang malah gak bisa login" (side effect of wrong edit)
- "Kamu koq ngeyel to" (repeated failure after correction)
- "Harusnya dikiri yang bener" (explicit position correction)
- "Bos kamu ngerjain apa sih" (workflow frustration)

**ACTION**: Immediately verify which element is FIRST in HTML source before `<div dir="rtl">`. If `<div class="text">` comes first, logo will appear LEFT — swap order!

### Reference Screenshots from Session
User uploaded screenshot showing:
- Logo HITAM PUTIH di KIRI (circular crest with mosque/stars)
- Text Arab center/right aligned
- HR line below school name

### Fix Applied
**Template change**: Move logo IMG tag before text DIV:
```diff
<div class="flex items-center pb-3 mb-2 text-biru">
-   <div class="header-text">...</div>
+   <img src="/logo-raport-bw-v5.png" class="header-logo">
-   <img>
+   <div class="header-text">...</div>
</div>
```

### Verification Checklist
After any header edit:
1. ✅ Check DOM order in HTML source (`grep -A 5 'flex items-center'`)
2. ✅ Preview shows logo on LEFT side (not right!)
3. ✅ Text content center-aligned within its container
4. ✅ HR line width correct (70% vs 90%)
5. ✅ Spacing compact (mb-2, not mb-3+)

### Related Skills
- `rapot-print-layout` - Full implementation guide
- `arabic-print-layout` - General Arabic typography rules

---

Source: Session 2026-08-25 SIM Mubtadiat rapport layout debugging (v34-v35 iterations)