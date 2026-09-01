---
title: SIM Mubtadiat Raport Print Layout
name: sim-mubtadiat-rapot-print
description: Arabic typography, font specs, print layout guidelines for raport PDF generation
tags: [arabic-typography, print-layout, docker-deployment]
author: AI Agent (2026-08-25)
session_ref: 2026-08-25
---

# SIM Mubtadiat Raport Print Layout Specs

## Typography (Arabic-Indic Digits Only)

### KFGQPC Uthman Taha Naskh (required for Arabic digits)
- **Header Titles**: 18pt bold
  - "كشف الدرجات الدراسية"
  - "فصل الدراسة الثانية"
- **Sub-header**: 16pt regular
  - Nama sekolah: "المدرسة الابتدائية للبنات هداية المبتدئات كديري ليربيا"
  - Tahun ajaran
  - Jabatan tanda tangan: "المدرس", "المدير"
- **Table Headers**: 18pt bold
  - "النمرة", "الكتب الدراسية", "الفنون"
  - "أرقام الدرجات الخاصة والعامة"
  - "جملة أرقام الدرجات الدراسية"
- **Isi Tabel**: 14pt regular
  - Angka nilai khos/am (٤, ٧, ٨, ٩, ٩٥...)
  - Nomor urut (١ sampai ١٥)

### Times New Roman / System Fonts
- **Identitas Santri**: 14pt regular (TIDAK BOLD)
  - Label dan value semua normal weight
  - Spasi setelah titik dua: `Nama : Isniatun` (perhatikan spasi)

## Critical Pitfalls

### 1. **Arabic-Hindi Digits Require Special Fonts**
Times New Roman TIDAK punya glyph angka Arab-Hindi (٠١٢٣٤٥٦٧٨٩). Browser fallback ke font acak → tampilan tidak konsisten. **Solusi**: Gunakan KFGQPC Uthman Taha Naskh untuk semua angka dalam tabel.

### 2. **Table Header Line-Break Control**
- "أرقام الدرجات الخاصة والعامة" harus tetap di 1 baris dengan `white-space: nowrap; font-size: 16pt;`
- Tanpa ini akan terpecah jadi 2 baris saat print preview

### 3. **Bold vs Normal Weight by Context**
- ✨ Header/Jabatan nama terang: **BOLD**
- ✨ Identitas santri (nama/stambuk/kelas): **REGULAR** (tidak bold!)
- ✨ Angka nilai di tabel: **REGULAR** (tidak bold!)
- ❌ Kesalahan umum: semua dicetak bold → tampilannya berantakan

## Layout Structure

### Header Section
```html
<!-- Logo kiri saja -->
<div class="flex items-center">
    <img src="/logo-raport-bw-v5.png" alt="Logo Raport BW">
    <div class="header-text">
        <h1 class="ft-uth-18">كشف الدرجات الدراسية</h1>
        <h1 data-field="semester-title" class="ft-uth-18">فصل الدراسة الثانية</h1>
        <h2 data-field="madrasah-line" class="ft-uth-16">المدرسة الابتدائية للبنات...</h2>
    </div>
</div>

<!-- Garis pembatas dekat dari header (margin 2px) -->
<hr style="border:none;height:1px;margin:2px auto;width:90%;">

<!-- Tahun ajaran centered -->
<div class="text-center mb-3">
    <p class="hdr-tahun ft-uth-16">سنة : <span>١٤٤٧ - ١٤٤٨ هـ / ٢٠٢٦ - ٢٠٢٧ م</span></p>
</div>
```

### Table Header (Two-row with colspan)
```html
<tr>
    <th rowspan="2">النمرة</th>
    <th rowspan="2">الكتب الدراسية</th>
    <th rowspan="2">الفنون</th>
    <th colspan="2" style="white-space: nowrap;">أرقام الدرجات الخاصة والعامة</th>
</tr>
<tr>
    <th>الخاصة</th>
    <th>العامة</th>
</tr>
```

## Deployment Checklist

1. **Before Deploy**: Check disk space (`df -h /`)
   - If >95% used → clean up first!
   
2. **After Code Changes**:
   ```bash
   cd /opt/simmubtadiat
   docker compose down app
   docker compose build app  # or --no-cache for fresh build
   docker compose up -d app
   
3. **If Login Failed After Deploy**:
   - Check database health: `docker ps | grep simmu`
   - If DB status = "Restarting": check logs for errors
   - Common cause: `/` 100% full → database can't write lock file
   - Fix: delete large files, run `docker system prune -a -f`

4. **After Rebuild**: Verify print layout works
   - Open `https://reviewtechno.me/rapot.html`
   - Check browser console (F12) for JS errors
   - Test print preview before committing

## Known Issues & Fixes

| Problem | Root Cause | Solution |
|---------|-----------|----------|
| Logo appears twice | Left+right in code | Remove right logo img tag |
| Values print bold | Used `<strong>` instead of `<span>` | Change to `<span>` only |
| Arabic numbers display wrong | Using Times New Roman | Use KFGQPC Uthman Taha Naskh |
| Login fails after deploy | Database crash from disk full | Clean space, restart both containers |
| Header text breaks into 2 lines | Missing white-space: nowrap | Add inline style constraint |
| Header layout unbalanced | Logo left vs text right gap too wide | Use `.header-container` flex with spacer div on right side (75px) |
| Identity misaligned | Inline flex with `:` between label/value | Use `<table class="identity-table">` with fixed-width `td.lbl` (90px), `td.colon` (10px center) |

## Session Reference
- Date: 2026-08-25
- User correction: "nilai tidak cetak tebal" (after I made it bold by mistake)
- Correction: Set `font-weight: normal` for `.rapot-sheet td.td-num`

---

## Updated Layout Pattern (2026-08-26 Session)

### New Header Structure

**Before:** Logo left + text right with inline flex gap. Result: title visually off-center, logo separated.

**After:** `.header-container` flexbox with balanced spacer div:

```html
<div class="header-container">
  <img src="/logo-raport-bw-v5.png" alt="Logo Raport BW" class="header-logo">
  <div class="header-title">
    <h2>كشف الدرجات الدراسية</h2>
    <h3 data-field="semester-title">فصل الدراسة الثانية</h3>
    <p data-field="madrasah-line">المدرسة الابتدائية للبنات هداية المبتدئات كديري ليربيا</p>
  </div>
  <div style="width: 75px;"></div> <!-- Spacer to balance -->
</div>

<hr class="header-divider"> <!-- 2px thick, centered below title block -->

<div class="year-text">
  سنة : <span data-field="tahun-ajaran">١٤٤٧ - ١٤٤٨ هـ / ٢٠٢٦ - ٢٠٢٧ م</span>
</div>
```

CSS Rules:
```css
.header-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
}

.header-logo { width: 75px; height: auto; }
.header-title { text-align: center; flex-grow: 1; direction: rtl; }
.header-divider { border-top: 2px solid #000; margin: 10px 0 6px 0; }
.year-text { text-align: center; direction: rtl; font-size: 14px; font-weight: bold; }
```

### Student Identity Table

**Before:** Inline `<p>` with label: value using flex gap. Problem: `:` positions vary per row (label length differs).

**After:** Two separate tables, fixed-width columns:

```html
<table class="identity-table">
  <tr><td class="lbl">Nama</td><td class="colon">:</td><td class="val"><strong data-field="nama"></strong></td></tr>
  <tr><td class="lbl">No. Stambuk</td><td class="colon">:</td><td class="val"><strong data-field="stambuk"></strong></td></tr>
  <tr><td class="lbl">Kelas</td><td class="colon">:</td><td class="val"><strong data-field="kelas"></strong></td></tr>
</table>

<table class="identity-table">
  <tr><td class="lbl">No. Tamrin</td><td class="colon">:</td><td class="val"><strong data-field="tamrin"></strong></td></tr>
  <tr><td class="lbl">Bagian</td><td class="colon">:</td><td class="val"><strong data-field="bagian"></strong></td></tr>
</table>
```

CSS Rules:
```css
.identity-table { border-collapse: collapse; }
.identity-table td.lbl { width: 90px; }
.identity-table td.colon { width: 10px; text-align: center; }
.identity-table td.val { flex: 1; min-width: 20mm; }
```

Result: All `:` perfectly aligned vertically across rows.
