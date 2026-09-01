# Word Header Logo Fix — Complete Python Implementation

**Problem:** Logo appears RIGHT instead of LEFT in Word .docx with RTL layout.

## Root Cause

With `dir='rtl'` (right-to-left text flow), element order = visual order:
- **Element 1 (first) → KANAN side**
- **Element N (last) → KIRI side**

If header paragraph contains ONLY logo, it becomes first element → appears right.

---

## Solution Pattern

Insert empty paragraph BEFORE logo paragraph:

```xml
<!-- BEFORE (logo at pos 1 = kanan) -->
<w:hdr>
  <w:p>                    <!-- Para 0 -->
    <w:r><w:drawing>LOGO</w:drawing></w:r>
  </w:p>
</w:hdr>

<!-- AFTER (logo at pos 2 = kiri) -->
<w:hdr>
  <w:p>                    <!-- Para 0 (empty) -->
    <w:pPr/>
    <w:r><w:t/></w:r>
  </w:p>
  <w:p>                    <!-- Para 1 (logo) -->
    <w:r><w:drawing>LOGO</w:drawing></w:r>
  </w:p>
</w:hdr>
```

---

## Full Implementation

```python
import zipfile
from lxml import etree
import io
import shutil

def fix_word_logo_position(input_file):
    """Fix Word document where logo appears right instead of left."""
    
    # Backup original
    backup_path = input_file + '.backup'
    shutil.copy(input_file, backup_path)
    print(f"✓ Backup created: {backup_path}")
    
    # Read ZIP contents into memory first
    zip_file = zipfile.ZipFile(input_file, 'r')
    file_contents = {name: zip_file.read(name) for name in zip_file.namelist()}
    zip_file.close()
    
    # Parse header.xml
    header_xml_str = file_contents['word/header1.xml'].decode('utf-8')
    ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    
    root = etree.fromstring(header_xml_str.encode())
    
    # Find paragraph containing drawing/logo
    para_elem = None
    for child in root:
        if 'p' in str(child.tag).lower():
            para_elem = child
            break
    
    if para_elem is None:
        raise ValueError("No paragraph found in header")
    
    # Create empty paragraph
    empty_p = etree.Element(ns + 'p')
    empty_p.append(etree.Element(ns + 'pPr'))
    
    empty_r = etree.Element(ns + 'r')
    empty_t = etree.Element(ns + 't')
    empty_t.text = ''
    empty_r.append(empty_t)
    empty_p.append(empty_r)
    
    # Insert BEFORE logo paragraph
    idx = list(root).index(para_elem)
    root.insert(idx, empty_p)
    
    print(f"✓ Empty paragraph inserted at index {idx}")
    
    # Rebuild ZIP
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name in file_contents:
            content = file_contents[name]
            if name == 'word/header1.xml':
                zf.writestr(name, etree.tostring(root, pretty_print=True, encoding='UTF-8'))
            else:
                zf.writestr(name, content)
    
    # Write fixed file (overwrite original)
    with open(input_file, 'wb') as f:
        f.write(output.getvalue())
    
    print(f"✅ SUCCESS!")
    print(f"   Para 0 (empty) → RIGHT side")  
    print(f"   Para 1 (logo) → LEFT side ✓")
    return backup_path

# Usage
if __name__ == '__main__':
    import sys
    docx_file = sys.argv[1] if len(sys.argv) > 1 else 'document.docx'
    fix_word_logo_position(docx_file)
```

---

## Verification Steps

After running script:

1. Open `.docx` file in Word/LibreOffice
2. Check header section
3. Verify logo visually positioned on **LEFT** side
4. Empty space should appear on **RIGHT** side (but not visible when printed)

---

## Debug Tips

### Q: How do I find where drawing elements are?

```python
import re
from zipfile import ZipFile

with ZipFile('document.docx', 'r') as z:
    header_xml = z.read('word/header1.xml').decode('utf-8')

# Find all wp.inline tags
inline_matches = re.finditer(r'<wp:inline[^>]*>', header_xml, re.IGNORECASE)
for m in inline_matches:
    print(f"Found wp.inline at position {m.start()}")
    print(m.group(0)[:500])
```

### Q: Why isn't logo moving after fix?

Check these potential issues:

1. **Parent container overrides**: Look for explicit positioning in section properties
2. **Multiple header references**: Document may have multiple sections with different headers
3. **Cached preview**: Word may cache old version - try "Revert to Saved"
4. **Corrupt rebuild**: Verify ZIP structure with `zipfile.ZipFile('file.docx', 'r').testzip()`

### Q: What about body paragraphs with logos?

Same principle applies! Search `word/document.xml` for drawing elements:

```python
doc_xml = file_contents['word/document.xml'].decode('utf-8')
root = etree.fromstring(doc_xml.encode())

for i, p in enumerate(root.iter()):
    if 'p' in str(p.tag).lower():
        has_drawing = any('drawing' in str(c.tag).lower() or 
                         'inline' in str(c.tag).lower() 
                         for c in p.iterchildren())
        if has_drawing:
            print(f"Drawing found in paragraph at index {i}")
```

Then apply same insertion logic.

---

## Performance Notes

- Script processes entire ZIP in memory - fine for documents <100MB
- For large files, iterate stream-wise (advanced)
- Always backup before editing

---

## Related

See [`SKILL.md`](../SKILL.md) for overview and integration notes.
See [`print-layout-match`](../../print-layout-match/SKILL.md) for HTML/CSS alternatives.
