---
name: express-file-export
description: Patterns for Express.js file exports (PDF, Excel, ZIP) with authentication, including route ordering pitfalls and async stream handling.
category: software-development
---

# Express File Export Patterns

## Critical: Route Ordering

Express matches routes in definition order. A parameterized route `:id` catches ANY path segment, including static names like `download-all`.

### Pitfall
```javascript
// WRONG - /api/raport/download-all matches :santri_id first!
app.get('/api/raport/:santri_id', ...);       // line 10
app.get('/api/raport/download-all', ...);     // line 20 — NEVER REACHED
```

### Fix: Define static routes BEFORE parameterized ones
```javascript
// CORRECT
app.get('/api/raport/download-all', ...);     // line 10 — matched first
app.get('/api/raport/:santri_id', ...);       // line 20
app.get('/api/raport/:santri_id/pdf', ...);   // line 30
```

**Rule**: If you have multiple routes sharing a prefix, always put concrete/static paths before parameterized (`:param`) paths.

---

## Authenticated File Downloads (Frontend)

`window.open()` does NOT send Authorization headers. Use fetch + blob instead.

```javascript
// WRONG
window.open('/api/export/pdf?dari=2026-01-01', '_blank'); // 401 Unauthorized

// CORRECT
async function downloadFile() {
  const res = await fetch('/api/export/pdf?dari=2026-01-01', {
    headers: { 'Authorization': 'Bearer ' + token }
  });
  if (!res.ok) { /* handle error */ return; }
  const blob = await res.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'filename.pdf';
  a.click();
  URL.revokeObjectURL(a.href);
}
```

---

## Bulk PDF into ZIP (archiver + pdfkit)

PDFDocument emits data asynchronously. Must wrap in Promise and await sequentially.

```javascript
const archiver = require('archiver');
const PDFDocument = require('pdfkit');

function generatePDF(data) {
  return new Promise((resolve) => {
    const doc = new PDFDocument({ size: 'A4', margin: 40 });
    const chunks = [];
    doc.on('data', chunk => chunks.push(chunk));
    doc.on('end', () => resolve({ filename: 'file.pdf', buffer: Buffer.concat(chunks) }));
    // ... draw PDF content ...
    doc.end();
  });
}

// MUST use for...of with await, NOT forEach
(async () => {
  for (const item of itemsList) {
    const { filename, buffer } = await generatePDF(item);
    archive.append(buffer, { name: filename });
  }
  archive.finalize();
})();
```

---

## Excel Export with ExcelJS

### Pattern: Kop Surat + Logo + Formatted Table

```javascript
const ExcelJS = require('exceljs');

app.get('/api/export/excel', authenticate, async (req, res) => {
  const wb = new ExcelJS.Workbook();
  const ws = wb.addWorksheet('Sheet Name');

  // 1. Logo from base64 settings
  if (logoData && logoData.startsWith('data:')) {
    const ext = logoData.split(';')[0].split('/')[1];
    const imageId = wb.addImage({ base64: logoData.split(',')[1], extension: ext });
    ws.addImage(imageId, { tl: { col: 0, row: 0 }, ext: { width: 60, height: 60 } });
  }

  // 2. Kop Surat (merge cells)
  ws.mergeCells('C1:J1');
  ws.getCell('C1').value = 'Nama Lembaga';
  ws.getCell('C1').font = { bold: true, size: 16 };
  ws.getCell('C1').alignment = { horizontal: 'center' };

  // 3. Styled header row
  const headerRow = ws.getRow(7);
  headers.forEach((h, i) => {
    const cell = headerRow.getCell(i + 1);
    cell.value = h;
    cell.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2E86C1' } };
    cell.alignment = { horizontal: 'center' };
    cell.border = { top: { style: 'thin' }, bottom: { style: 'thin' }, left: { style: 'thin' }, right: { style: 'thin' } };
  });

  // 4. Send file
  res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
  res.setHeader('Content-Disposition', 'attachment; filename=export.xlsx');
  await wb.xlsx.write(res);
  res.end();
});
```

### Multi-Sheet Strategy
- **Sheet 1 "Formal"**: Kop surat, logo, merge cells, styled — for printing
- **Sheet 2 "Raw Data"**: Plain data — for filtering/pivot by user

---

## Packages
```bash
npm install pdfkit archiver exceljs
```
