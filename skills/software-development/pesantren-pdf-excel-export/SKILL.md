---
name: pesantren-pdf-excel-export
title: PDF & Excel Export Patterns
description: Patterns for generating PDFs (pivot tables, bulk ZIP), Excel exports with header/logo injection, and authenticated file downloads in Node.js/Express apps.
---

## Context
Used in `/root/pesantren-absensi/server.js` (Express + PDFKit + ExcelJS + Archiver). Applies to pesantren-absensi and similar Node.js attendance/SaaS apps.

## Key Lessons Learned

### 1. Express Route Order — CRITICAL
Parameterized routes (`:param`) match BEFORE literal routes. Always put specific routes BEFORE param routes:

```
❌ WRONG:
app.get('/api/raport/:santri_id', ...)      // matches "download-all" as santri_id!
app.get('/api/raport/download-all', ...)     // never reached

✅ CORRECT:
app.get('/api/raport/download-all', ...)     // specific first
app.get('/api/raport/:santri_id', ...)       // param after
app.get('/api/raport/:santri_id/pdf', ...)   // more specific param after
```

### 2. Authenticated File Downloads — Don't Use window.open()
`window.open()` doesn't send auth headers. Use fetch + blob:

```javascript
async function downloadFile(url, filename) {
  const res = await fetch(url, { headers: { 'Authorization': 'Bearer ' + token } });
  if (!res.ok) { const e = await res.json(); toast(e.message); return; }
  const blob = await res.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}
```

### 3. PDF to Buffer (for ZIP bundling)
PDFKit streams asynchronously. Use Promise + chunks:

```javascript
function generatePDFToBuffer(data) {
  return new Promise((resolve) => {
    const doc = new PDFDocument({ size: 'A4', margin: 40 });
    const chunks = [];
    doc.on('data', chunk => chunks.push(chunk));
    doc.on('end', () => resolve(Buffer.concat(chunks)));
    // ... build PDF content ...
    doc.end();
  });
}
```

### 4. Bulk ZIP — Must Await Each PDF Sequentially
```javascript
const archive = archiver('zip', { zlib: { level: 5 } });
archive.pipe(res);
for (const item of items) {
  const buffer = await generatePDFToBuffer(item);
  archive.append(buffer, { name: item.filename + '.pdf' });
}
archive.finalize();
```

### 5. ExcelJS — Header + Logo + Two Sheets Pattern
```javascript
const ExcelJS = require('exceljs');
const wb = new ExcelJS.Workbook();

// Logo from base64 settings
if (logoData.startsWith('data:')) {
  const base64 = logoData.split(',')[1];
  const ext = logoData.split(';')[0].split('/')[1];
  const imageId = wb.addImage({ base64, extension: ext });
  ws.addImage(imageId, { tl: { col: 0, row: 0 }, ext: { width: 60, height: 60 } });
}

// Merge cells for kop surat
ws.mergeCells('C1:J1');
ws.getCell('C1').value = appName;
ws.getCell('C1').font = { bold: true, size: 16 };
ws.getCell('C1').alignment = { horizontal: 'center' };

// Styled header row (blue bg, white text, borders)
const headerRow = ws.getRow(7);
headers.forEach((h, i) => {
  const cell = headerRow.getCell(i + 1);
  cell.value = h;
  cell.font = { bold: true, color: { argb: 'FFFFFFFF' } };
  cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2E86C1' } };
  cell.border = { top: { style: 'thin' }, bottom: { style: 'thin' }, left: { style: 'thin' }, right: { style: 'thin' } };
});

// Raw data sheet (for filtering)
const ws2 = wb.addWorksheet('Raw Data');
ws2.addRow(['Tanggal', 'Nama', 'Kamar', 'Kegiatan', 'Status', 'Keterangan']);

res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
await wb.xlsx.write(res);
res.end();
```

### 6. Dynamic Pivot Table for PDF
Detect columns from data, sort by category priority, auto-size:

```javascript
// Sort: Pokok first, then Tambahan, by urutan_tampil
kegiatanList.sort((a, b) => {
  if (a.kategori !== b.kategori) return a.kategori === 'pokok' ? -1 : 1;
  return a.urutan - b.urutan;
});

// Auto-size: fixed No/Name cols, elastic for activities
const colKeg = (totalWidth - fixedCols) / kegiatanList.length;

// Rotate 90° for narrow columns
if (colKeg < 35) {
  doc.save();
  doc.translate(xx + colW/2, yy + rowH/2);
  doc.rotate(-90);
  doc.text(header, -40, -3, { width: 80, align: 'center' });
  doc.restore();
}
```

## Packages
- `pdfkit` — PDF generation
- `exceljs` — Excel (.xlsx) generation
- `archiver` — ZIP file creation

## Gotchas
- ExcelJS: merge cells BEFORE setting cell values
- ExcelJS: logo extension must be png/jpg, NOT svg
- PDFKit: only built-in fonts (Helvetica) work without registration
- Archiver: `npm install archiver` required
- Always use `fetch+blob` not `window.open()` for authenticated downloads
