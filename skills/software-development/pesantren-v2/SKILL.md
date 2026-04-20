---
name: pesantren-v2
description: Project knowledge for Pesantren Absensi V2 — architecture, data flow patterns, and common pitfalls learned during development.
category: software-development
---

# Pesantren Absensi V2

Single-file monolith Express app (`server.js`) + single `index.html` frontend. JSON file database (`data.json`).

**Location:** `/root/pesantren-v2/`  
**PM2:** `pesantren-v2` (port 3001)  
**GitHub:** `rezaulin/pesantren-v2` (origin) + `rezaulin/pesantren-deploy` (deploy)  
**Login:** admin/admin123  

## Git Push

Always push to BOTH remotes:
```bash
git push origin main && git push deploy main
```

## Architecture: Unified Absensi Table

V2 uses a **unified `absensi` table** with `kelompok_id` to differentiate types. NOT separate tables like v1.

### Data Flow: Absen Sekolah

1. **Kelompok SEKOLAH must exist** (tipe: 'SEKOLAH', nama: 'Sekolah')
2. `POST /api/absen-sekolah/bulk` → saves to `db.absensi` with `kelompok_id` = SEKOLAH kelompok ID
3. `GET /api/rekap?tipe=absen_sekolah` → reads from `db.absensi` filtered by SEKOLAH kelompok_id
4. `GET /api/rekap` (Semua) → merges absensi + absen_malam + absen_sekolah (all from unified table)

### PITFALL: Kelompok SEKOLAH Missing

If no kelompok with `tipe === 'SEKOLAH'` exists:
- `kelompokId` is null
- Records save to `absensi` with `kelompok_id: null`
- Rekap can't find them (filters by kelompok_id)
- Data appears invisible

**Fix:** Auto-create SEKOLAH kelompok on server startup:
```javascript
if (!db.kelompok.find(k => k.tipe === 'SEKOLAH')) {
  db.kelompok.push({ id: nextId(db.kelompok), nama: 'Sekolah', tipe: 'SEKOLAH', kegiatan_nama: 'Sekolah', created_at: new Date().toISOString() });
  saveDB(db);
}
```

### PITFALL: Kelas Grouping in Rekap

For Sekolah records, `kelompok_nama` should show `santri.kelas_sekolah` (e.g., "7A"), NOT the kelompok name ("Sekolah"):
```javascript
const isSekolah = sekolahKelompok && a.kelompok_id === sekolahKelompok.id;
kelompok_nama: isSekolah ? (s?.kelas_sekolah || '-') : (kl?.nama || '-')
```

## Performance Optimizations

### Debounced Save (500ms)

`saveDB()` does NOT write to disk immediately. Instead:
- Sets `_pendingSave = true`
- `setInterval` at 500ms checks and flushes
- Graceful flush on SIGINT/SIGTERM/exit

This prevents disk thrashing with 40+ `saveDB` calls per request cycle.

### Compression

`compression` npm package — 70% smaller responses.

### Static Caching

`express.static` with `{ maxAge: '1h', etag: true }`.

### Pagination (optional)

`GET /api/santri?page=1&limit=20` — backward compatible (no page = full list).

## Import Excel: Santri + Auto-Create Wali

`POST /api/santri/import-excel` — multipart file upload.

Excel columns: `Nama | Alamat | Wali` (baris 1 = header, atau A/B/C fallback).

For each row:
1. Generate username from wali name: `wali_budisantoso` (lowercase, no spaces)
2. If duplicate: append `_2`, `_3` etc.
3. Create user with role `'wali'`, password `wali123`
4. Create santri with `wali_user_id` linking to wali user
5. Store `wali_nama` on santri as fallback for raport

Frontend: `showImportExcel()` modal → `doImportExcel()` with FormData fetch.

## Kelompok System

Kelompok has `tipe` field that determines behavior:
- `KAMAR` — room-based groups
- `SOROGAN` / `SOROGAN_MALAM` — recitation groups
- `BAKAT` — talent groups
- `SEKOLAH` — school attendance (special handling)
- `KEGIATAN` — generic activity groups
- Custom tipe names (e.g., 'Ngaji subuh') for pokok kegiatan

## Card Grid UI (Manage Pages)

Kelola Kamar and Kelas use `.manage-grid` + `.manage-card` CSS:
```html
<div id="kamarGrid" class="manage-grid"></div>
```
Cards show icon, title, stat badges, action buttons. Responsive grid (auto-fill, 200px min).

## Frontend: Kelas Filter for Sekolah Rekap

When "Absen Sekolah" card is selected, show kelas picker cards (NOT hide kelompok section):

1. Add `let rekapSelectedKelasSekolah=null;` variable
2. In `selectRekapKegiatanCard`: when `val==='absen_sekolah'`, show kelompok section, call `loadRekapKelasCards()`
3. `loadRekapKelasCards()`: fetch `/api/kelas-sekolah`, render picker cards with `selectRekapKelasCard` handler
4. `selectRekapKelasCard(kelasNama)`: set `rekapSelectedKelasSekolah`, highlight card, call `loadRekapData()`
5. In `loadRekapData`: pass `kelas_sekolah` param when absen_sekolah selected

**PITFALL: Card highlighting** — element IDs use `k.id` (numeric), but selection uses `k.nama`. Cannot do `$('rekap-kelas-'+kelasNama)`. Use text content matching instead:
```javascript
document.querySelectorAll('#rekapKelompokCards .picker-card').forEach(c=>{
  if(c.textContent.includes(kelasNama))c.classList.add('selected');
});
```

## Data Migration Pattern: absen_sekolah → unified absensi

When consolidating separate tables into unified absensi:
1. Create the target kelompok (e.g., SEKOLAH)
2. In `data.json`, migrate records: add `kelompok_id` to each record, push to `db.absensi`
3. Clear the old table (`db.absen_sekolah = []`)
4. Update all GET endpoints to read from `db.absensi` filtered by kelompok_id
5. Update bulk POST to use the kelompok_id

## Dual Remote Push

Project has 2 remotes — always push to both:
```bash
git push origin main && git push deploy main
```
- `origin` → `rezaulin/pesantren-v2` (private, development)
- `deploy` → `rezaulin/pesantren-deploy` (jualan)
