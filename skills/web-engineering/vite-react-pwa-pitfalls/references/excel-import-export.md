# Excel Import & Export (browser, no server) — Omni POS

Fitur reusable: import produk massal dari Excel (+ template generator) dan export
laporan penjualan multi-sheet yang rapi. Semua di browser, tanpa server.

## Library: pakai `exceljs`, JANGAN `xlsx`
- **`xlsx` (SheetJS) sudah TIDAK di-publish ke npm resmi** (ada CVE lama + mereka
  pindah distribusi ke CDN sendiri `cdn.sheetjs.com`). `npm install xlsx` bisa
  narik versi lama/rentan atau gagal. 
- **`exceljs`** masih aktif di npm, aman, dan formatting jauh lebih bagus: bold
  header, fill warna, `numFmt` currency, lebar kolom, merge cell, multi-sheet.
  Cocok untuk requirement "rapi".
- Install: `npm install exceljs`. Verifikasi cepat di node:
  `node -e "const E=require('exceljs'); console.log(new E.Workbook()?'ok':'')"`
- CATATAN: `npm install exceljs` bisa minta approval / makan waktu lama di環境 ini;
  jalankan dengan timeout longgar (300s) dan konfirmasi ke user dulu kalau ke-block.

## Pola Export (workbook multi-sheet)
```ts
import ExcelJS from 'exceljs'
const wb = new ExcelJS.Workbook()
const ws = wb.addWorksheet('Ringkasan')
ws.columns = [{ header: 'Omzet', key: 'total', width: 18 }, ...]  // set width di sini
// style header row
const row = ws.getRow(1)
row.eachCell(c => { c.fill = {type:'pattern',pattern:'solid',fgColor:{argb:'FF6D28D9'}}; c.font = {bold:true,color:{argb:'FFFFFFFF'}} })
// currency: set numFmt per-cell atau per-column
r.getCell('total').numFmt = '#,##0'
// download di browser (bukan fs):
const buf = await wb.xlsx.writeBuffer()
const blob = new Blob([buf], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
// downloadBlob() → createObjectURL + <a download> + revokeObjectURL
```
- `argb` format: `FF` (alpha) + hex RGB, mis. `FF6D28D9`.
- Laporan penjualan POS yang lengkap = 6 sheet: Ringkasan, Penjualan Harian,
  **Terlaris per Kategori** (group per kategori + subtotal), Metode Pembayaran,
  Riwayat Transaksi, Kas Masuk Deposit-Kasbon. (Sejalan Bug 11: audit semua sumber kas.)
- Produk terlaris per kategori: item transaksi biasanya TIDAK simpan categoryId →
  agregasi `Map<kategori, Map<productId, {qty,revenue,profit}>>` dari transactions,
  resolve kategori via productId lookup.

## Pola Import (template + parse + preview validasi)
1. **Template generator** (tombol "Download Template"): workbook dengan sheet
   Produk + sheet "Satuan Bertingkat" (multi-satuan/grosir) + sheet Panduan +
   sheet Daftar Satuan (referensi kode). Isi contoh baris biar user paham format.
   Satuan bertingkat: kolom SKU, Nama Satuan, Isi (ratio ke base), Harga Jual →
   integrasi ke tiered pricing (dus isi 20 = Rp60.000 → auto Rp3.000/pcs).
2. **Parse**: `wb.xlsx.load(await file.arrayBuffer())`. Baca cell defensif —
   ExcelJS cell value bisa berupa object (`{text}` untuk rich text, `{result}`
   untuk formula). Bikin helper `cellStr`/`cellNum` yang handle semua bentuk.
3. **Preview validasi SEBELUM commit**: kembalikan array baris dengan status
   `valid | duplicate | error` + array `messages` per baris. Tampilkan badge
   hitung (Baru/Sudah ada/Error) + list per baris.
4. **Pilihan duplikat**: kalau SKU sudah ada, kasih radio **Perbarui / Lewati**
   (user minta pilihan eksplisit, jangan asумsi). Kategori baru auto-buat.
5. Commit: loop baris valid → resolve/buat kategori → create/update produk.

## Pitfall
- Import/export ikut aturan demo-mode dual-path (Bug 4): create/update produk &
  list kategori harus `isDemoMode` aware.
- Selalu `.replace(',', '.')` untuk angka yang mungkin diketik dengan koma (id-ID).
- Baris kosong di Excel (user hapus contoh) → skip kalau nama & SKU dua-duanya kosong.
