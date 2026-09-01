# Common Arabic Text Corrections — SIM Mubtadiat Raport Template

Based on Word source verification + photo reference cross-check.

## Fixed Typos (verified against docx gold standard)

| Wrong | Correct | Context |
|-------|---------|---------|
| فصل الدراسية الأولى | فصل الدراسة الأولى | Semester title (baris kop) |
| المدرسة العالية للبنات | المدرسة الابتدائية للبنات | School name (jenjang SD/ibtida'iyah) |
| ليربيا كديري | كديري ليربيا | City order (location format) |
| ١٤٤٦ - ١٤٤٧ هـ / ٢٠٠٥ - ٢٠٠٦ م | ١٤٤٧ - ١٤٤٨ هـ / ٢٠٢٦ - ٢٠٢٧ م | Year range (Hijri → Gregorian, correct order) |

## Pattern Matching for Other Jenjangs

When building raport for a different jenjang, adapt the school-name prefix (this is done dynamically in rapot.js `madrasahLine()`):

| Jenjang | Arabic Prefix | Latin Name |
|---------|---------------|------------|
| SD/Ibtida'iyah | المدرسة الابتدائية | Primary School |
| SMP/Tsanawiyah | المدرسة الإعدادية | Middle School |
| SMA/Aliyah | المدرسة الثانوية | High School |
| Aliyah (default in code) | المدرسة العالية | Senior/High |

## Year Conversion Formula

Hijri ≈ Gregorian − 579 (the SIM code uses −579 for calendar alignment, not −622):

```python
def convert_year(gregorian_m1, gregorian_m2):
    hijri_m1 = gregorian_m1 - 579
    hijri_m2 = gregorian_m2 - 579

    ar_map = '٠١٢٣٤٥٦٧٨٩'
    def to_arab(num):
        return ''.join(ar_map[int(d)] for d in str(num))

    return f"{to_arab(hijri_m1)} - {to_arab(hijri_m2)} هـ / {to_arab(gregorian_m1)} - {to_arab(gregorian_m2)} م"

# Example: "2026/2027" → "١٤٤٧ - ١٤٤٨ هـ / ٢٠٢٦ - ٢٠٢٧ م"
```

## Source of Truth Priority

1. **Word (.docx) file** — Gold standard; parse `word/document.xml` directly.
2. **PDF export** — Acceptable fallback; some raster distortion.
3. **Photo reference** — Last resort; tolerance ±1–2mm due to angle/lighting.

⚠️ Never trust photos alone for Arabic text — always verify against the original Word/PDF source when available. Raster distortion flips/misaligns columns.
