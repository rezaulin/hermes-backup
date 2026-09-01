# Raport Print Layout Font Specifications (2026-08-25 Final)

## Complete Typography Map

### **Times New Roman 14pt**
- **Student Identitas** (label + value, NOT BOLD):
  - Nama, No. Stambuk, Kelas, No. Tamrin, Bagian
- **All Arabic labels in table**: النمرة، الكتب الدراسية، الفنون، أرقام الدرجات الخاصة والعامة، etc.

### **KFGQPC Uthman Taha Naskh 18pt BOLD**
- **Header titles**:
  - `كشف الدرجات الدراسية` (judul besar)
  - Semester title: `فصل الدراسة الأولى/الثانية`
- **Tabel headers**:
  - Semua kolom tabel (النمرة, الكتب الدراسية, الفنون, أرقام الدرجات, خاصة, عامة)
  - Footer rows: جملة أرقام الدرجات, أيام التأخير, البيان
- **Tanda tangan nama terang**:
  - `<(...)` wrapper around names: Bakar, Shaykh 'Ata', etc.

### **KFGQPC Uthman Taha Naskh 16pt**
- **Kop & sub-header**:
  - Nama sekolah: `المدرسة الابتدائية للبنات هداية المبتدئات ليربيا كديري`
  - Tahun ajaran: `سنة : ... / ... م`
- **Jabatan tanda tangan**:
  - `المدرس`, `المدير` (before the parentheses)
- **Isi tabel values**: Angka nilai, angka nomer row

---

## Critical Pattern Notes

### **No Bold on Identitas Values**
```html
<!-- WRONG (old v28) -->
<p><span class="lbl">Nama</span>: <strong data-field="nama">...</strong></p>

<!-- CORRECT (v29+) -->
<p><span class="lbl">Naming</span>: <span data-field="nama">...</span></p>
```
**Reason**: Owner explicit requirement. Latin label:Bold doesn't match reference photo aesthetic.

### **Spacing After Colon**
Label-to-value MUST have space after colon (`:`), achieved via CSS `.lbl { width: 100px; margin-right: 8px }`. Never manually add spaces in HTML.

### **White-space: nowrap for Arabic Headers**
```html
<th colspan="2" style="white-space: nowrap; font-size: 16pt;">
  أرقام الدرجات الخاصة والعامة
</th>
```
**Purpose**: Prevents line break in long Arabic phrases → stays single line even with limited column width.

---

## Verification Checklist (per print test)

- [ ] Student identity data uses Times New Roman 14pt (not bold)
- [ ] Header text: judul besar (18pt), semester (18pt), sekolah (16pt) - all KFGQPC Uthman
- [ ] Table headers: semua 18pt Bold
- [ ] Footer summary rows: 18pt Bold (جملة, أيام التأخر, البيان)
- [ ] Jabatan: المدرس/Mudir = 16pt Normal
- [ ] Tanda tangan names: 18pt Bold (in parentheses)
- [ ] All Arabic text passes `white-space: nowrap` check (no wrapping in middle of phrases)

---

## Common Pitfalls

**❌ Using generic fonts** like Arial or Helvetica for Arabic → breaks Islamic typography standard

**❌ Mixing font weights inconsistently** (bold vs normal in wrong places)

**❌ Missing `white-space: nowrap` on multi-word Arabic headers** → splits into multiple lines

**❌ Forgetting italic variants don't exist in Uthman Taha Naskh** → fallback to Amiri serif if needed

**❌ Assuming Times New Roman has Arabic glyphs** → it DOESN'T for numbers (٠١٢٣...). Use KFGQPC Uthman for ALL Arabic including digits.

See parent skill `sim-mubtadiat` for full rapport workflow and deployment process.