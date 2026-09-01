---
name: word-print-layout-fix
category: web-engineering
description: Fix Word .docx logo position in RTL layouts via header XML editing
---

# Word Print Layout Fix — Logo Position & Header Engineering

**Mission:** Fix Word .docx print layouts where elements (logo, header text) appear at wrong horizontal position due to RTL layout semantics.

**Trigger:** User reports logo/header appears RIGHT instead of LEFT in Arabic/RTL layout.

---

## Core Bug: RTL Element Order

With `dir='rtl'` (right-to-left), **element order = visual position**:
- First element → KANAN side  
- Last element → KIRI side

If header has single paragraph containing ONLY logo → logo appears kanan (first = right).

---

## Solution: Insert Empty Paragraph

Insert empty `<w:p>` BEFORE logo paragraph so logo becomes second element → kiri visually.

**XML transformation:**

```xml
<!-- BEFORE (logo first = kanan) -->
<w:hdr>
  <w:p w14:paraId="...">
    <w:r><w:drawing>LOGO</w:drawing></w:r>
  </w:p>
</w:hdr>

<!-- AFTER (logo second = kiri) -->
<w:hdr>
  <w:p>                    <!-- Para 0: EMPTY -->
    <w:pPr/>
    <w:r><w:t/></w:r>
  </w:p>
  <w:p>                    <!-- Para 1: LOGO -->
    <w:r><w:drawing>LOGO</w:drawing></w:r>
  </w:p>
</w:hdr>
```

---

## Implementation Steps

1. Backup original file
2. Parse header.xml from ZIP archive  
3. Find `<w:p>` containing drawing/logo element
4. Create empty `<w:p>` with minimal structure (`pPr` + `r` + `t`)
5. Insert empty para BEFORE logo para using `root.insert(index, new_elem)`
6. Rebuild ZIP preserving all other files
7. Write fixed document back
8. Verify visually

---

## Python Recipe

See `references/word-header-logo-fix.md` for complete executable code.

---

## Debug Checklist

- [ ] Check if drawing element uses `wp:inline` tag (Word format)
- [ ] Verify header XML is being read/written correctly
- [ ] Ensure ZIP rebuild doesn't corrupt other files (images, rels)
- [ ] Test on clean copy after each iteration
- [ ] Open document in Word or LibreOffice to verify rendering

---

## Related Skills

- `print-layout-match`: HTML/CSS print layout engineering alternative
- Web-based rapport systems often use similar RTL patterns

---

## References

- `references/word-header-logo-fix.md` — Complete Python implementation
