---
name: batch-pdf-zip-export
description: Generate multiple PDFs server-side with PDFKit and package into ZIP download with archiver. Includes Express route ordering rules and authenticated download pattern.
category: software-development
---

# Batch PDF Export as ZIP

Generate multiple PDFs server-side and package them into a ZIP download. Common use case: "download all reports" feature.

## Prerequisites

```bash
npm install pdfkit archiver
```

## Critical: Express Route Order

**This is the #1 pitfall.** Parameterized routes MUST come AFTER literal routes.

```javascript
// ✅ CORRECT — literal route first
app.get('/api/raport/download-all', authenticate, handler);
app.get('/api/raport/:santri_id', authenticate, handler);
app.get('/api/raport/:santri_id/pdf', authenticate, handler);

// ❌ WRONG — parameterized route catches "download-all" as :santri_id
app.get('/api/raport/:santri_id', authenticate, handler);
app.get('/api/raport/download-all', authenticate, handler);  // NEVER REACHED
```

Express matches routes top-to-bottom. `/api/raport/:santri_id` matches ANY path like `/api/raport/download-all`, treating `download-all` as the `santri_id` param.

## Pattern: PDFKit to Buffer (Promise wrapper)

PDFKit streams data asynchronously via events. To get a complete buffer before adding to ZIP, wrap in Promise:

```javascript
function generatePDFBuffer(data) {
  return new Promise((resolve) => {
    const doc = new PDFDocument({ size: 'A4', margin: 40 });
    const chunks = [];
    doc.on('data', chunk => chunks.push(chunk));
    doc.on('end', () => resolve(Buffer.concat(chunks)));

    // ... build PDF content ...

    doc.end();  // triggers 'data' events, then 'end'
  });
}
```

## Pattern: ZIP with archiver

```javascript
const archiver = require('archiver');

app.get('/api/download-all', authenticate, (req, res) => {
  res.setHeader('Content-Type', 'application/zip');
  res.setHeader('Content-Disposition', 'attachment; filename=reports.zip');

  const archive = archiver('zip', { zlib: { level: 5 } });
  archive.pipe(res);
  archive.on('error', (err) => { console.error('ZIP error:', err); res.status(500).end(); });

  // MUST use async/await since PDF generation is promise-based
  (async () => {
    for (const item of itemsList) {
      const buffer = await generatePDFBuffer(item);
      const safeFilename = item.nama.replace(/[^a-zA-Z0-9\u00C0-\u024F]/g, '-') + '.pdf';
      archive.append(buffer, { name: safeFilename });
    }
    archive.finalize();
  })();
});
```

⚠️ **Do NOT use forEach** — it doesn't await. Use `for...of` with async.

## Frontend: Authenticated PDF/ZIP Download

`window.open()` does NOT send auth headers. Use fetch + blob:

```javascript
async function downloadAll() {
  toast('Mempersiapkan...');
  const res = await fetch('/api/download-all?dari=...&sampai=...', {
    headers: { 'Authorization': 'Bearer ' + token }
  });
  if (!res.ok) { const e = await res.json(); toast(e.message); return; }
  const blob = await res.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'reports.zip';
  a.click();
  URL.revokeObjectURL(a.href);
}
```

## Pitfalls

1. **Route order** — Literal routes before parameterized. Most common bug.
2. **Sync vs async** — PDFKit `doc.end()` triggers async events. Buffer not ready immediately after `doc.end()`. Always use Promise.
3. **forEach doesn't await** — Use `for...of` loop for sequential PDF generation.
4. **Filename sanitization** — Strip non-ASCII chars for ZIP filenames: `.replace(/[^a-zA-Z0-9\u00C0-\u024F]/g, '-')`
5. **Memory** — Each PDF is held in memory. For 100+ PDFs, consider streaming to temp files instead of buffers.
6. **Timeout** — Large ZIPs may hit HTTP timeout. Consider progress indicator or async job pattern for 50+ reports.
