# SIM Mubtadiat Report Card Layout Specification

This is the exact layout for raport cetak in SIM Mubtadiat, reverse-engineered from Word .docx physical reference.

## Paper & Page Setup

- **Size**: F4 (215.9mm × 330.2mm)
- **Margins**: top 2.5cm, left/right 1.5cm, bottom 2cm
- **Page breaks**: avoid inside content blocks

## Header Structure (left-to-right visual)

```
[LOGO]          [Text Block - centered]
90px             Arabic: كشف الدرجات الدراسية
                   فصل الدراسة الأولى/الثانية
                   nama madrasah lengkap
                   ──────────────── (line)
                   سنة : ... هـ / ... م
```

### Implementation rules:

1. **Logo**: `position: absolute; left: 0` to prevent RTL flipping
2. **Text block**: `margin-left: 120px`, `text-align: center`, `direction: rtl`
3. **Line**: `background-color: #000` div, height 0.3mm, width 60%
4. **Font sizes**:
   - Judul Arab: 20pt normal
   - Semester title: 22pt bold
   - Madrasah line: 14pt
   - Year text: 9pt

## Student Identity Block

```
Nama       : [value]    No. Tamrin : [value]
No. Stambuk: [value]    Bagian     : [value]
Kelas      : [value]
```

### CSS rules:
- Flex rows with `white-space: nowrap` (no wrapping)
- Label width: 75px, aligned right
- Colon: 8px center
- Value: bold
- Gap between lines: 1mm

## Table Section

- Border thickness: 2px solid black
- Font: Uthman Taha Naskh 16pt for headers, Times New Roman 14pt for values
- Padding: 1px vertical, minimal horizontal

## Footer (Signatures)

- Mudir signature: left side (if available)
- Mudarris signature: right side
- Position: `margin-top: auto` at bottom of page

## Color Palette

- All text: #000000 (pure black)
- Background: white
- No gradients or theme colors

## Verification Checklist

- [ ] Logo fixed LEFT (not flipped by RTL)
- [ ] Full page visible in print preview (not cropped)
- [ ] Horizontal line under madrasah name only (before year)
- [ ] Student data no wrapping across lines
- [ ] All fonts render correctly (Uthman Taha installed?)
- [ ] Signature block positioned at bottom margin

## Reference Files

Physical Word .docx file serves as gold standard. Use browser print → PDF to compare against original. Measure printed output with ruler if needed.

## Known Issues

- Chrome sometimes scales small fonts (<8pt) inconsistently in print
- Absolute positioning can overlap if content too long → use min-height guard
- Arabic font fallback may look different than Word's specific font