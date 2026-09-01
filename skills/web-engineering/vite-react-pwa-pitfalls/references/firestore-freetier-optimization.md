# Firestore Free-Tier (Spark) Optimization — POS/offline-first apps

Kapan pakai: app offline-first (IndexedDB/Dexie) yang mau deploy ke Firestore
GRATIS (Spark) dengan data banyak (katalog besar, ratusan transaksi/hari) tanpa
jebol kuota. Terbukti di Omni POS (React+TS+Vite+Dexie).

## Limit Spark (per hari)
- Reads 50.000 / Writes 20.000 / Deletes 20.000 / Storage 1 GB / Egress 10 GB/bln
- Yang paling gampang jebol: reads (buka laporan naif = ribuan read sekali klik) & writes (transaksi naif = 10+ write).

## 3 pilar arsitektur (WAJIB semua)

### 1. Sync incremental berbasis `updatedAt` (bukan full-fetch, bukan onSnapshot)
- Tiap dokumen WAJIB punya `updatedAt: number` (epoch ms) + `deletedAt?: number` (soft delete).
- UI SELALU baca IndexedDB (source of truth di layar). Firestore disentuh HANYA oleh sync engine + write path.
- `pullChanges(coll)`: `query(coll, where('updatedAt','>', lastSync), orderBy('updatedAt','asc'))` → tulis ke IndexedDB, `deletedAt` → hapus lokal. 1000 dok, 3 berubah = 3 read.
- `lastSync` per koleksi disimpan di **localStorage** (0 read metadata), bukan Firestore.
- `list()` service cache-first: baca IndexedDB; full-fetch `getDocs(orderBy name)` HANYA saat `count()===0` (first run), set watermark `lastSync` = max updatedAt.
- Orkestrasi sync: boot + event `online` + interval LONGGAR (2.5 mnt utk 2-3 device), BUKAN tiap render. TIDAK ADA `onSnapshot` untuk list (charge read tiap perubahan tiap dokumen).
- Composite index wajib per koleksi: `(updatedAt ASC)` di `firestore.indexes.json`.

### 2. Agregat laporan harian (pembunuh-read #1 kalau salah)
- JANGAN baca koleksi `transactions` mentah buat laporan (5000 tx = 5000 read/klik).
- Dokumen counter `reports_daily/{YYYY-MM-DD}`: `{omzet, profit, txCount, itemsSold, perMethod{}, depositTopup, kasbonPaid, topProducts{cap 50}, updatedAt}`.
- Update INCREMENTAL tiap transaksi via `increment()` (Firestore FieldValue) — tak perlu read-dulu, aman konkuren. `topProducts` perlu read-modify-write (merge + cap 50).
- Laporan N hari = baca N dokumen. `getSummaryFromDaily(start,end)` rekonstruksi SalesSummary dari agregat.
- Terlaris dari `topProducts` agregat (cap 50/hari) — cukup utk chart, tak perlu query granular.
- Kas masuk non-penjualan (deposit topup, kasbon paid) ikut di-increment ke agregat.
- Backfill: fungsi sekali-jalan scan transaksi existing → bangun agregat (read besar SEKALI, bukan harian). Di demo, panggil saat seed/boot kalau agregat kosong.

### 3. Batch write minimal + soft delete
- 1 transaksi = 1 `writeBatch`/`runTransaction` commit (tx + decrement stok + agregat harian). Firestore transaction: SEMUA read dulu, baru write.
- JANGAN tulis inventory movement per-item ke Firestore (bisa +5 write/tx cuma buat log) — simpan lokal saja.
- `remove()` = soft delete (`deletedAt`+`updatedAt`), bukan `deleteDoc` — supaya sync incremental device lain ikut hapus tanpa full re-fetch.
- Statistik pelanggan (`totalSpent`/`transactionCount`) di-update dalam batch transaksi yang sama, jangan write terpisah.

## Pagination riwayat (hemat read data lama)
- `listCompletedTransactionsPaged(pageSize=50, beforeTs?)`: `orderBy('createdAt','desc') limit(pageSize+1)`, cursor = createdAt terakhir. UI "Muat lebih banyak". JANGAN pernah baca semua transaksi sekaligus.

## Estimasi (toko sibuk, 5 device, 200 tx/hari): writes ~1.350, reads ~900 — jauh di bawah limit.

## Multi-tenant vs 1-project-per-klien
- **1 Firebase project per klien** (model jual per-klien): tiap klien kuota gratis SENDIRI → beban per-project rendah. Security rules SINGLE-TENANT sederhana: `allow read,write: if request.auth != null`. TIDAK perlu field `storeId`/partitioning. Koleksi flat. Config `.env` per deploy → nyambung ke Deploy CLI `npx omni-pos setup`.
- Rules default-deny `match /{document=**} { allow read,write: if false }` di bawah semua match spesifik.

## Dual-path demo mode
- Semua fitur di atas WAJIB dual-path: `if (isDemoMode) { localStorage/IndexedDB; return }` sebelum sentuh Firestore. Agregat demo di localStorage key `omni_pos_reports_daily`, sync `pullChanges` return 0 di demo. Logika kebangun & ketes penuh di demo mode tanpa Firebase real; pas config dateng tinggal colok.

## Verifikasi
- Build zero-error + unit test agregat/sync (Vitest: `dayKey`, `txDelta` akumulasi, `getDailyReports` range filter, syncMeta roundtrip).
- Smoke browser demo: transaksi → laporan naik real-time (via `queryClient.invalidateQueries`), no macet.
- Staging Firestore real: Firebase Console → Usage, simulasi 20 tx + buka laporan 10× → cek read/write count sesuai estimasi.

## Setup Vitest di Vite+TS project (yang belum punya test runner)
- `npm i -D vitest jsdom`, `vitest.config.ts` (`environment: 'jsdom', globals: true, setupFiles`), script `"test": "vitest run"`.
- `tsconfig.app.json`: EXCLUDE `src/**/*.test.ts`, `src/**/*.spec.ts`, `src/test` supaya `tsc -b` build produksi tak ikut compile test (kalau tidak, build gagal / type test bocor).
