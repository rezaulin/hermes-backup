# Raport Layout Reference - Column Alignment Patterns

## Physical Reference Photo Structure

**Student**: Isniatun / Iswatun  
**Stambuk**: 2805  
**Class**: I Aliyah E  
**Bagian**: E  
**Tamrin No.**: 20  

### Reference Source Images
- Primary: `/root/.hermes/cache/images/img_f50fe4d7a626.jpg` (Isniatun full report photo)
- Secondary: `/root/.hermes/cache/images/img_be7e06aae08e.jpg` (Iswatun layout variant)

## Column Header Structure (RTL Order)

Physical reference shows **5-column layout** with Arabic headers:

| # | Arabic Header | English Translation | Our Implementation | Status |
|---|---------------|---------------------|-------------------|--------|
| 1 | **الرقم** | Unit No. | `<th>الرقم</th>` | ✅ Match |
| 2 | **الكتب المدرسية** | School Books | `<th>الكتب المدرسية</th>` (v23+) | ✅ Fixed in v23 |
| 3 | **الفنون** | Subjects/Arts | `<th>الفنون</th>` | ✅ Match |
| 4 | (merged header) أرقام الدرجات الخاصة والعامة | Score numbers, private & general | Split into two columns | ✅ Match |
| 4a | **الخاصة** | Private scores | `<th>الخاصة</th>` | ✅ Match |
| 4b | **العامة** | General scores | `<th>العامة</th>` | ✅ Match |

### Key Terminology Notes

**Books column header correction (v23):**
- ❌ Old: `"الكتب الدراسية"` → incorrect terminology (used "study books")
- ✅ New: `"الكتب المدرسية"` → matches reference exactly ("school books")
- Commit message: `"rapot fix #4: books column header → 'الكتب المدرسية' (matches reference photo)"`

## Footer Row Structure (Merged Table)

Reference photos show footer with **3 merged rows** spanning all columns:

### Row 1: جملة أرقام الدرجات الدراسية (Total Scores)
```html
<tr>
  <th colspan="3">جملة أرقام الدرجات الدراسية</th>
  <td data-field="total-khos">90</td>
  <td data-field="total-am">90</td>
</tr>
```
- Label spans first 3 columns (No, Books, Subjects)
- Values appear in separate Private/General score columns
- Total typically 90 for both columns (based on reference data)

### Rows 2–3: أيام التأخر (Absent Days)
```html
<tr>
  <th colspan="2" rowspan="2">أيام التأخر</th>
  <td class="td-arab">بإذن</td>
  <td data-field="absen-izin">0</td>
  <td></td>
</tr>
<tr>
  <td class="td-arab">بغيره</td>
  <td data-field="absen-bizeen">0</td>
  <td></td>
</tr>
```
- Label spans 2 columns + rowspans 2 vertically
- Sub-labels use correct Arabic grammar:
  - ✅ `بإذن` = "with permission" (correct)
  - ❌ NOT `بغيره إذن` or other variants (incorrect)
- Numeric values appear only in private column (general is empty)

### Row 4: Bayan (Comment/Average) - Semester 2 Only
```html
<tr>
  <th colspan="2">البيان</th>
  <td colspan="3">المعدل: -- / 100</td>
</tr>
```
- **Business rule**: ONLY appears in semester 2
- Semantic: Average score calculation
- Label spans 2 columns, value spans remaining 3 columns
- Empty in semester 1 (verified by existing business logic)

## Merged Cell Pattern Summary

| Element | Colspan | Rowspan | Position | Purpose |
|---------|---------|---------|----------|---------|
| جملة أرقام | 3 | 1 | Top footer | Group total label |
| أيام التأخر | 2 | 2 | Middle-left | Vertical group header |
| bayan | 2 | 1 | Bottom | Comment section header |

## Border & Spacing Rules

### Grid Lines
- All cells: `border: 2px solid black`
- Borders must be **continuous** across merged cells (no breaks at cell boundaries)
- Corner joins must appear single-line, not double-thick

### Text Gap Requirements
- Minimum gap between text bottom edge and border line: **~0.7mm**
- For Arabic descender letters (خ ج ح ع غ ي): needs extra clearance below baseline
- Solution applied v24: asymmetric padding + minimal line-height increase

### Padding Guidelines (post-v24)
```css
padding: 1px 8px 4px 6px;
/*
  top:    1px  (minimal to save vertical space)
  right:  8px  (extra horizontal for RTL alignment)
  bottom: 4px  (extra for descenders)
  left:   6px  (standard spacing)
*/
```

## Column Width Distribution (Approximate)

Based on physical reference measurement at ~2.62 px/mm scale:

| Column | % of table width | px estimate | Notes |
|--------|------------------|-------------|-------|
| الرقم | 8% | ~150px | Narrow, numeric only |
| الكتب المدرسية | 35% | ~650px | Wide for book titles |
| الفنون | 12% | ~220px | Medium for subject names |
| الخاصة | 15% | ~280px | Numeric scores |
| العامة | 30% | ~550px | Scores + notes |

Total table width ≈ 1850px (fits standard A4/F4 printable area)

## Testing Checklist Against Reference

When validating new rapport builds, check:

- [ ] All 5 column headers match Arabic text EXACTLY (check spelling, no typos)
- [ ] Footer row 1: label colspan=3, not colspan=2 or other
- [ ] Footer row 2–3: days تأخر has rowspan=2, labels are `بإذن`/`بغيره`
- [ ] Footer final row: bayan ONLY in semester 2 (semester 1 should be absent)
- [ ] Merged borders appear continuous (no visible breaks at join points)
- [ ] Arabic text gap ≥0.7mm measured visually on print preview
- [ ] Descender letters خ ج ح ع غ ي have clear clearance from bottom borders
- [ ] Total page height fits F4 limit (<297mm) for both semesters when printed together
- [ ] Column widths proportional (books column widest at ~35%)

## Version History

| Version | Change | Reason | Status |
|---------|--------|--------|--------|
| v19–v22 | Initial symmetric padding (2px 6px), tight line-height (1.15) | First attempt at gap fix | ❌ Failed (0.37mm measured) |
| v23 | Fixed books column header terminology | Match reference terminology | ✅ Partial success |
| v24 | Combined strategy: asymmetric padding + line-height 1.22 | Solve descender touch issue | ✅ Live solution |

---
**Generated**: 2026-08-25  
**Last tested**: v24 deployment  
**Reference source**: Physical photos from Isniatun/Iswatun student records
