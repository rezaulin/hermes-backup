---
name: pesantren-absensi-maintenance
description: Patterns and gotchas for maintaining the FAONSI/pesantren-absensi single-file monolithic web app (Express backend + single index.html frontend).
triggers:
  - pesantren-absensi feature changes
  - FAONSI app modification
  - absen.reviewtechno.me update
  - single-file monolith HTML/JS editing
---

# Pesantren Absensi (FAONSI) Maintenance Guide

## Project Structure
- **Path:** `/root/pesantren-absensi/`
- **Frontend:** `public/index.html` (~1000 lines, 55KB, single-file monolith)
- **Backend:** `server.js` (~500 lines, endpoints for absensi/santri/kamar/kegiatan/pengumuman/pelanggaran/raport/settings/export)
- **Database:** `data.json` (flat-file JSON, gitignored, backed up to `backup-data` branch)
- **Process:** PM2 (`pesantren-absensi`)
- **URL:** `https://absen.reviewtechno.me` (nginx + Cloudflare SSL)
- **Auth:** admin / admin123
- **Deploy tools:** `deploy-client.sh`, `docker-compose.yml`, `ecosystem.config.js`, `backup.sh`, `DEPLOY.md`

## Editing the Monolithic index.html

### Approach: Python execute_code for batch edits (3+ changes)
For **single targeted edits**, `patch` tool works fine — use it directly.

For **3+ changes**, don't use sequential `patch` calls — the file is too large and string matches may not be unique. Use Python `execute_code` instead:

```python
with open('/root/pesantren-absensi/public/index.html', 'r') as f:
    html = f.read()

# Make ALL changes
html = html.replace(old1, new1)
html = html.replace(old2, new2)
html = html.replace(old3, new3)

# Verify changes applied
assert new1 in html
assert new2 in html

with open('/root/pesantren-absensi/public/index.html', 'w') as f:
    f.write(html)
```

**Why this works better than patch:**
- Single read/write cycle (avoids race conditions)
- Can verify all changes before saving
- `patch` tool struggles with non-unique matches in large files
- `write_file` historically fails on files >45KB

### After editing: ALWAYS validate JS syntax
```bash
cd /root/pesantren-absensi && node -e "
const fs=require('fs');
const html=fs.readFileSync('public/index.html','utf8');
const m=html.match(/<script>([\s\S]*?)<\/script>/);
try{new Function(m[1]); console.log('JS syntax: OK')}
catch(e){console.log('JS syntax ERROR:', e.message); process.exit(1)}
"
```

### Then restart:
```bash
pm2 restart pesantren-absensi && curl -s -o /dev/null -w "%{http_code}" https://absen.reviewtechno.me
```

## Architecture Gotchas

### 1. Sidebar Nav ≠ Grid Menu (5 locations to update)
The sidebar nav items and grid menu items have DIFFERENT structures:
- **Sidebar:** `{id, icon, label}` — no highlight property
- **Grid menu:** `{id, icon, label, highlight: true/false}`
- **Ustadz grid menu** also exists separately from admin grid menu

When adding a new feature, update ALL FIVE locations:
1. Sidebar nav items (line ~429)
2. Admin grid menu (line ~454)
3. Ustadz grid menu (line ~469)
4. `allowed` array for ustadz role (line ~437)
5. `loadPageData()` function (line ~509)

If any one is missed, the feature silently won't appear in that context.

### 2. Kegiatan Auto-Add Pattern
Don't rely on empty-DB init for new default kegiatan. Use this pattern in `server.js`:

```javascript
// Ensure kegiatan array exists
if (!db.kegiatan) db.kegiatan = [];
// Init defaults only on fresh DB
if (db.kegiatan.length === 0) {
  db.kegiatan = [
    { id: 1, nama: 'Ngaji Pagi', ... },
    // ... defaults without newest ...
  ];
}
// Auto-add specific kegiatan if missing (runs every boot)
if (!db.kegiatan.find(k => k.nama.toLowerCase().includes('sekolah'))) {
  db.kegiatan.push({ id: nextId(db.kegiatan), nama: 'Sekolah Formal', created_at: new Date().toISOString() });
}
saveDB(db);
```

This ensures:
- Fresh DB gets all defaults
- Existing DB gets new kegiatan added without duplicates
- Restart-safe (checks by name, not by ID)

### 3. Filter API supports these query params on /api/santri:
`kamar_id`, `kelas_diniyyah`, `kelompok_ngaji`, `kelompok_ngaji_malam`, `kelas_sekolah`, `jenis_bakat`

## Roles: Admin, Ustadz, Wali Santri
Three roles with different access levels:

| Feature | Admin | Ustadz | Wali |
|---|---|---|---|
| Dashboard | Full stats | Full stats | Anak cards + rekap per kegiatan |
| Absensi (input) | ✅ | ✅ | ❌ (403 blocked) |
| Data Santri | CRUD | Read-only | ❌ |
| Kamar/Kegiatan/Users | CRUD | ❌ | ❌ |
| Rekap Absensi | Full | Full | Anak only |
| Catatan Guru | CRUD + hapus | Create/edit | Read anak only |
| Pelanggaran | CRUD | Read | ❌ |
| Raport | Full | Full | Anak only |
| Pengumuman | CRUD | Read | Read |
| Pengaturan | ✅ | ❌ | ❌ |

### Wali-specific API endpoints
- `GET /api/wali/anak` — returns santri where `wali_user_id === req.user.id`
- `GET /api/wali/rekap` — absensi filtered to wali's children only
- `GET /api/dashboard` — returns `{role:'wali', anak:[...], rekap_kegiatan:{}, ...}` when role=wali

### Wali frontend pattern
Wali gets a **completely different UI** — separate pages, grid menu, and nav:
- `page-walidashboard` — anak cards with attendance stats
- `page-walirekap` — attendance recap with anak filter
- `page-walicatatan` — read-only catatan guru for their children

### Adding wali write restriction
In any POST/PUT/DELETE endpoint, add at the top:
```javascript
if (req.user.role === 'wali') return res.status(403).json({ message: 'Wali tidak bisa mengubah data' });
```

### Wali role in user form
Add `<option value="wali">Wali Santri</option>` to the role `<select>` in the user modal.

### Santri ↔ Wali linking
Santri has `wali_user_id` field (nullable). When editing santri, populate a `<select id="mWali">` with users filtered by `role==='wali'`.

## Catatan Guru Feature Pattern
### Backend
- CRUD at `/api/catatan`
- `created_by` set from `req.user.id` (JWT) — **auto-detect, never from request body**
- Wali filter: only see notes where `santri_id` matches their children
- Integrated into `/api/raport/:santri_id` response as `catatan_guru` array
- Integrated into raport PDF

### Frontend
- Modal form: santri select, date, kategori dropdown (perilaku/akademik/kesehatan/lainnya), judul, isi textarea
- Card-style list with guru_nama auto-displayed
- Filter by santri, kategori, date range

### Auto-detect creator pattern
```javascript
// Backend POST — NEVER accept created_by from body
const c = {
  id: nextId(db.catatan_guru), santri_id, tanggal, judul, isi, kategori,
  created_by: req.user.id,  // ← from JWT, not req.body
  created_at: new Date().toISOString()
};
```

## Adding New Feature: 6-Location Checklist (Updated with Wali)
When adding a new page/feature, there are SIX places to update in index.html. Missing any one = feature silently absent in that context:

1. **Sidebar nav items** (~line 529) — `{id, icon, label}` (no highlight)
2. **Admin grid menu** (~line 565) — `{id, icon, label, highlight}`
3. **Ustadz grid menu** (~line 575) — `{id, icon, label, highlight}`
4. **Wali grid menu** (~line 583) — if wali should see it
5. **`allowed` array for ustadz role** (~line 538) — add the id string
6. **`loadPageData()` function** (~line 630) — add `if(page==='xxx')loadXxx()`

Plus: HTML page section, JS functions, sidebar nav must use same ordering as grid menus.

For wali-specific pages (prefix `wali`), add to:
- Wali sidebar nav items (`waliItems` array)
- Wali grid menu (`waliMenu` array)
- `loadPageData()` with `if(page==='waliXxx')loadWaliXxx()`
- `switchTab()` redirect if needed (e.g., wali home → walidashboard)

## Known Bug Patterns

### Variable Naming: camelCase vs snake_case (sesiId/sesi_id)

**Bug (2026-04-20):** `POST /api/absensi/bulk` crashed with `ReferenceError: sesiId is not defined` because the destructured variable from `req.body` is `sesi_id` (snake_case) but the code referenced `sesiId` (camelCase).

```javascript
// WRONG — sesiId never declared, ReferenceError crash:
const { tanggal, kegiatan_id, kelompok_id, sesi_id, jam_sesi, items } = req.body;
// ... later in sesiMatch callback:
if (sesiId) return s.id === parseInt(sesi_id);  // ← BUG: sesiId undefined

// CORRECT — use sesi_id consistently:
if (sesi_id) return s.id === parseInt(sesi_id);  // ← FIXED
```

**Symptom:** Every save triggers 500 error, nothing saved, error log shows `ReferenceError: sesiId is not defined at sesiMatch (server.js:463:5)`.

**Prevention:** When destructuring from `req.body`, the variable names MUST match exactly what you reference later. If you destructure `sesi_id`, use `sesi_id` everywhere (not `sesiId`). This pattern can happen in any endpoint — always verify variable names match their destructured form.

### Sesi Not Linked to Absensi Records

**Bug (2026-04-20):** After creating a new `absensi_sesi` record, the absensi rows were inserted with `sesi_id: null` instead of the new sesi's ID. This broke session tracking — the sesi existed but absensi records weren't linked to it.

```javascript
// WRONG — sesi created but absensi gets sesi_id: null
const newSesi = { id: nextId(db.absensi_sesi), ustadz_username: req.user.username, ... };
db.absensi_sesi.push(newSesi);
// later...
db.absensi.push({ ..., sesi_id: sesi_id ? parseInt(sesi_id) : null, ... });
//                                          ↑ sesi_id from body is undefined, always null

// CORRECT — track current sesi ID and use it
let currentSesiId;
if (oldSesi) {
  currentSesiId = oldSesi.id;
} else {
  const newSesi = { id: nextId(db.absensi_sesi), ... };
  db.absensi_sesi.push(newSesi);
  currentSesiId = newSesi.id;
}
// later...
db.absensi.push({ ..., sesi_id: currentSesiId, ... });  // ← linked!
```

**Pattern:** Whenever creating a parent record and child records in the same request, capture the parent's ID and use it on children. Don't rely on `req.body` to carry the ID if it's auto-created server-side.

### Kegiatan ↔ Kelompok Auto-Sync (tipe KEGIATAN)

**Problem (2026-04-20):** Kegiatan table and kelompok table are separate. Adding a kegiatan didn't create a kelompok tipe `KEGIATAN`, so the new absensi dynamic form (which uses kelompok) didn't show the kegiatan.

**Fix pattern — auto-sync in all CRUD endpoints:**

```javascript
// POST /api/kegiatan — auto-create kelompok
app.post('/api/kegiatan', authenticate, requireAdmin, (req, res) => {
  const { nama } = req.body;
  const k = { id: nextId(db.kegiatan), nama, ... };
  db.kegiatan.push(k);
  // Auto-create kelompok tipe KEGIATAN
  if (!db.kelompok.find(kl => kl.nama === nama && kl.tipe === 'KEGIATAN')) {
    db.kelompok.push({ id: nextId(db.kelompok), nama, tipe: 'KEGIATAN', created_at: ... });
  }
  saveDB(db); res.json(k);
});

// PUT — sync nama if renamed
app.put('/api/kegiatan/:id', authenticate, requireAdmin, (req, res) => {
  const k = db.kegiatan.find(x => x.id == req.params.id);
  const oldNama = k.nama;
  // ... update k ...
  if (req.body.nama && req.body.nama !== oldNama) {
    const kl = db.kelompok.find(x => x.nama === oldNama && x.tipe === 'KEGIATAN');
    if (kl) kl.nama = req.body.nama;
  }
  saveDB(db);
});

// DELETE — cascade delete kelompok + relasi
app.delete('/api/kegiatan/:id', authenticate, requireAdmin, (req, res) => {
  const k = db.kegiatan.find(x => x.id == req.params.id);
  if (k) {
    const kelompokIds = db.kelompok.filter(kl => kl.nama === k.nama && kl.tipe === 'KEGIATAN').map(kl => kl.id);
    if (kelompokIds.length) {
      db.kelompok = db.kelompok.filter(kl => !kelompokIds.includes(kl.id));
      db.santri_kelompok = db.santri_kelompok.filter(sk => !kelompokIds.includes(sk.kelompok_id));
    }
  }
  db.kegiatan = db.kegiatan.filter(x => x.id != req.params.id);
  saveDB(db);
});
```

**Backfill on boot** — for existing kegiatan that don't have kelompok:
```javascript
// After loadDB(), before server start:
db.kegiatan.forEach(k => {
  if (!db.kelompok.find(kl => kl.nama === k.nama && kl.tipe === 'KEGIATAN')) {
    db.kelompok.push({ id: nextId(db.kelompok), nama: k.nama, tipe: 'KEGIATAN', created_at: ... });
  }
});
saveDB(db);
```

### Rekap Page: Kelompok Filter When Tipe Selected

**Problem (2026-04-20):** When selecting a kelompok tipe in rekap, the filter area was hidden (`display:none`), so there was no way to drill down to a specific kelompok.

**Fix pattern:**
1. Add a `<select id="rekapKelompok">` dropdown (hidden by default)
2. On tipe change → populate from `/api/kelompok?tipe=X` → show dropdown, hide old filters
3. On loadRekap → append `&kelompok_id=X` if dropdown has value

```javascript
async function rekapOnTipeChange(){
  const tipe = $('rekapTipe').value;
  const kelompokSel = $('rekapKelompok');
  if(tipe){
    const kelompok = await api('/api/kelompok?tipe='+tipe);
    kelompokSel.innerHTML = '<option value="">Semua Kelompok</option>';
    if(kelompok) kelompok.forEach(k => {
      const o = document.createElement('option');
      o.value = k.id; o.textContent = k.nama;
      kelompokSel.appendChild(o);
    });
    kelompokSel.style.display = '';
    // Hide old kegiatan-based filters
    $('rekapKamar').style.display = 'none';
    $('rekapFilter').style.display = 'none';
  } else {
    kelompokSel.style.display = 'none';
    $('rekapKamar').style.display = '';
  }
  loadRekap();
}

async function loadRekap(){
  const tipe = $('rekapTipe').value;
  if(tipe){
    let url = '/api/rekap?kelompok_tipe='+tipe;
    if($('rekapKelompok').value) url += '&kelompok_id='+$('rekapKelompok').value;
    // ... fetch + render ...
  }
}
```

### editSantri: GET /api/santri/:id does not exist
There is NO `app.get('/api/santri/:id', ...)` route in server.js. The frontend must fetch ALL santri then filter by ID (same pattern as `editKamar`):

```javascript
// CORRECT:
function editSantri(id){api('/api/santri').then(data=>{const s=data.find(x=>x.id===id);if(s)showModal('santri',s)})}
// WRONG (silently fails, 404):
function editSantri(id){api('/api/santri/'+id).then(s=>{if(s)showModal('santri',s)})}
```

### Dynamic Filter: Keyword Match Order Matters
When mapping kegiatan names to filter types, use an **ordered array** (NOT object map). "Ngaji Malam" contains both "ngaji" and "malam" — if "ngaji" is checked first, it matches wrong filter (Kelompok Ngaji instead of Kamar).

```javascript
// CORRECT — ordered array, specific rules first
const filterRules = [
  {match:'malam', field:'kamar_id', label:'Kamar'},        // FIRST (catches "Ngaji Malam")
  {match:'bakat', field:'jenis_bakat', label:'Jenis Bakat'},
  {match:'madrasah', field:'kelas_diniyyah', label:'Kelas Diniyyah'},
  {match:'sekolah', field:'kelas_sekolah', label:'Kelas Sekolah'},
  {match:'ngaji', field:'kelompok_ngaji', label:'Kelompok Ngaji'},  // LAST (catches "Ngaji Pagi", "Ngaji Qur'an")
];
```

### Kegiatan Auto-Add on Boot
Default init only runs when `db.kegiatan` is empty. For new kegiatan added later, use a separate ensure-check AFTER the init block:

```javascript
if (!db.kegiatan) db.kegiatan = [];
if (db.kegiatan.length === 0) { /* init defaults */ }
// Auto-add new kegiatan if missing (runs every boot, name-based check)
if (!db.kegiatan.find(k => k.nama.toLowerCase().includes('sekolah'))) {
  db.kegiatan.push({ id: nextId(db.kegiatan), nama: 'Sekolah Formal', ... });
}
saveDB(db);
```

## Version & Git
- **Current version:** 2.0.0 (in package.json)
- **Repo:** `github.com/rezaulin/pesantren-absensi` (private)
- **Latest commits:** 5c6de41 (Catatan Guru), 61867b6 (Wali Santri)
- After changes: `git add -A && git commit -m "msg" && git push origin main`

## Browser Testing Workarounds

### Sidebar click timeouts
The sidebar overlay sometimes causes `browser_click` to timeout (30s). Workarounds:
1. Press Escape first: `browser_press(key='Escape')`
2. Then click the target element
3. If still fails, navigate via JS console: `browser_console(expression="switchTab('pageId')")`

### Reliable page navigation via JS console
Always works, faster than clicking UI elements:
```javascript
switchTab('absensekolah')  // Absen Sekolah Formal
switchTab('santri')        // Data Santri
switchTab('kegiatan')      // Kelola Kegiatan
switchTab('absensi')       // Absensi Harian
switchTab('rekap')         // Rekap Absensi
```

### Toast verification
After saving via UI, look for `text: Tersimpan` or `text: [action] tersimpan` in the snapshot output as confirmation.

### Page navigation via JS console
More reliable than clicking UI elements:
```javascript
switchTab('absensekolah')  // navigate to Absen Sekolah
switchTab('santri')        // navigate to Data Santri
switchTab('kegiatan')      // navigate to Kelola Kegiatan
```

## Known Bug Patterns

### editSantri: GET /api/santri/:id does not exist
There is NO `app.get('/api/santri/:id', ...)` route in server.js. If you see `editSantri` calling `api('/api/santri/'+id)`, it will silently fail (404) and the modal won't populate with data.

**Correct pattern** (same as editKamar):
```javascript
function editSantri(id){api('/api/santri').then(data=>{const s=data.find(x=>x.id===id);if(s)showModal('santri',s)})}
```

This fetches ALL santri then filters by ID client-side. If you ever add a GET-by-id route, you could simplify, but the fetch-all approach works fine with <1000 records.

### Why edit modal appears empty
If you click ✏️ and the modal opens but fields are empty: check the browser console for 404 on `/api/santri/:id`. The fix is above.

## Adding New Features Checklist
1. Update `server.js` (API endpoints, schema, init defaults)
2. Update `index.html` (use Python execute_code, break into 2-3 scripts if many changes):
   - Add HTML page section (after existing similar pages)
   - Update table/modal if data schema changed
   - Add to sidebar nav items (~line 429)
   - Add to admin grid menu (~line 454)
   - Add to ustadz grid menu (~line 469)
   - Add to `allowed` array for ustadz (~line 437)
   - Add to `loadPageData()` (~line 509)
   - Add JS functions (after similar existing functions)
3. Validate JS syntax (node -e check)
4. Restart PM2 + verify HTTP 200
5. Browser test: login → sidebar → grid menu → feature page → save test
6. Git commit with descriptive message

### Python execute_code: split if many changes
If 5+ string replacements, break into 2-3 separate `execute_code` calls (each doing read→replace→write) to avoid context overflow. Verify each batch before proceeding.

## ⚠️ CRITICAL: File Corruption Pitfall

**Never use `write_file` on `index.html` directly.** Multiple failed `write_file` attempts can wipe the file to 0 bytes. If this happens:

```bash
cd /root/pesantren-absensi && git checkout HEAD -- public/index.html && pm2 restart pesantren-absensi
```
**Confirmed:** This happened on 2026-04-17 — repeated failed `write_file` calls wiped index.html to 0 bytes. Git restore worked perfectly. Never use `write_file` on this file.

**Safe editing methods (in order of preference):**
1. `patch` tool — for 1-2 targeted edits (works reliably)
2. `execute_code` Python script — for 3+ batch edits (read→replace→write)
3. `cat > file << 'EOF'` via terminal — last resort for full rewrites

**Never use:** `write_file` on files >45KB (historically fails/glitches)

## Data Schema: Santri
```javascript
{
  id: number,
  nama: string,
  kamar_id: number,
  status: 'aktif' | 'nonaktif' | 'lulus',
  kelas_diniyyah: string,        // e.g. "1A", "2B", "3A"
  kelompok_ngaji: string,        // e.g. "Juz 1", "Juz 28", "Tahsin"
  kelompok_ngaji_malam: string,  // e.g. "Ust. Ahmad", "Ust. Hasan"
  jenis_bakat: string,           // e.g. "Tahfidz", "Kaligrafi", "Futsal"
  kelas_sekolah: string,         // e.g. "7A", "8B", "9A"
  wali_user_id: number | null,   // links to users.id where role='wali'
  created_at: ISO string
}
```

## Data Schema: Catatan Guru
```javascript
{
  id: number,
  santri_id: number,
  tanggal: string,               // "YYYY-MM-DD"
  judul: string,                 // optional title
  isi: string,                   // note content (required)
  kategori: 'perilaku' | 'akademik' | 'kesehatan' | 'lainnya',
  created_by: number,            // auto-set from JWT, NOT from request body
  created_at: ISO string
}
```

Filter santri by: `kamar_id`, `kelas_diniyyah`, `kelompok_ngaji`, `kelompok_ngaji_malam`, `kelas_sekolah`, `jenis_bakat`

**Note (2026-04-19):** Flat fields kept for backward compat but new system uses `kelompok` + `santri_kelompok` pivot tables. New filtering via `kelompok_id`, `kelompok_tipe`, `sesi_id` on absensi endpoints.

## Dynamic Filter Per Kegiatan (Absensi Page)

The attendance page filter dropdown changes dynamically based on selected kegiatan tab. Use an **ordered array** (NOT an object map) because keyword matching order matters:

```javascript
// CORRECT: Ordered array - "malam" checked before "ngaji"
const filterRules=[
  {match:'ngaji malam',field:'kelompok_ngaji_malam',label:'Kelompok Ngaji Malam'},  // MOST SPECIFIC first
  {match:'malam',field:'kelompok_ngaji_malam',label:'Kelompok Ngaji Malam'},
  {match:'bakat',field:'jenis_bakat',label:'Jenis Bakat'},
  {match:'madrasah',field:'kelas_diniyyah',label:'Kelas Diniyyah'},
  {match:'diniyyah',field:'kelas_diniyyah',label:'Kelas Diniyyah'},
  {match:'sekolah',field:'kelas_sekolah',label:'Kelas Sekolah'},
  {match:'qur\'an',field:'kelompok_ngaji',label:'Kelompok Ngaji Al-Qur\'an'},
  {match:'ngaji',field:'kelompok_ngaji',label:'Kelompok Ngaji Al-Qur\'an'},  // LAST (catches "Ngaji Pagi", "Ngaji Qur'an Siang")
];

// WRONG: Object map - iteration order not guaranteed for keyword overlap
// "Ngaji Malam" would match "ngaji" (Kelompok Ngaji) instead of "malam" (Kamar)
```

**Bug this prevents:** "Ngaji Malam" kegiatan showing "Filter: Kelompok Ngaji" instead of "Filter: Kelompok Ngaji Malam" because "ngaji" matched first. The "ngaji malam" rule MUST come before plain "malam" or "ngaji".

**Auto-sync pattern:** Filter dropdowns must refresh santri data on EVERY call (not cache-once). This ensures when admin adds a new santri with kelompok="Ust. Baru", it appears in the filter immediately without page reload. Pattern: rebuild dropdown options + preserve current selection each time `buildFilterDropdown()` or `loadAbsenMalam()` or `loadAbsenSekolah()` is called.

### Filter Dropdown Pattern
```javascript
async function buildFilterDropdown(kegNama){
  const filter = getFilterForKegiatan(kegNama);
  const sel = $('absensiFilter');
  sel.innerHTML = '<option value="">Semua</option>';
  if(!filter){sel.style.display='none'; return}
  sel.style.display = '';
  // ALWAYS refresh santri cache for auto-sync (not just first call)
  allSantriCache = await api('/api/santri')||[];
  if(filter.field === 'kamar_id'){
    // Kamar is a separate table, fetch it
    const kamar = await api('/api/kamar');
    if(kamar) kamar.forEach(k => { /* add options */ });
  } else {
    // Other fields are on santri object directly
    const vals = [...new Set(allSantriCache.map(s => s[filter.field]).filter(Boolean))].sort();
    vals.forEach(v => { /* add options */ });
  }
}
```

### Backend: Universal Filter Pattern for Absensi/Rekap/Export
```javascript
// In GET /api/absensi, /api/rekap, /api/export/pdf:
const santriFilters = ['kamar_id', 'kelas_diniyyah', 'kelompok_ngaji', 'kelompok_ngaji_malam', 'jenis_bakat', 'kelas_sekolah'];
santriFilters.forEach(f => {
  if (req.query[f]) {
    const santriIds = db.santri.filter(s => String(s[f]) === String(req.query[f])).map(s => s.id);
    list = list.filter(a => santriIds.includes(a.santri_id));
  }
});
```
This replaces the old single `if (req.query.kamar_id)` block and works for all santri attribute filters.

## V2 Project: Vanilla CSS SPA (`/root/pesantren-v2/` on VPS2)

A separate project — same backend logic, **vanilla HTML/CSS/JS** frontend (NOT Tailwind).

### Project Structure
- **Path:** `/root/pesantren-v2/` (on VPS2: `172.237.138.149`)
- **Frontend:** `public/index.html` (~3200+ lines, single-file monolith)
- **Backend:** `server.js` (~1800 lines, Express, flat-file JSON DB)
- **Database:** `data.json` (backup: `data.json.backup.YYYYMMDD_HHMMSS`)
- **PM2:** `pesantren-v2` on port 3001
- **URL:** `https://absensi-v2.reviewtechno.me` (or direct `http://IP:3001`)
- **Login:** admin/admin123
- **SSH:** `sshpass -p 'jancoK123@a' ssh -o StrictHostKeyChecking=no root@172.237.138.149`

### Editing Remote VPS2
All edits go through SSH. Pattern for each change:
```bash
sshpass -p 'jancoK123@a' ssh -o StrictHostKeyChecking=no root@172.237.138.149 "COMMAND"
```
For file edits, use `patch` tool (works via local terminal that SSHs to VPS2). For 3+ changes on the monolith HTML, use `execute_code` Python script.

### After Editing VPS2: Always restart
```bash
sshpass -p 'jancoK123@a' ssh -o StrictHostKeyChecking=no root@172.237.138.149 "cd /root/pesantren-v2 && node --check server.js && pm2 restart pesantren-v2"
```

### Adding a New Module/Page to Vanilla SPA (Phase 1-4 Pattern)

When adding a new feature page (like Kelompok management), there are **6 locations** to update:

1. **HTML page div** — add `<div class="page" id="page-{name}">` in the content section (after similar pages)
2. **Sidebar nav items** in `buildNav()` — add `{id, icon, label}` to items array
3. **Admin grid menu** in `buildGridMenu()` — add to appropriate group (Data Master, Operasional, etc.)
4. **`loadPageData()`** — add `if(page==='xxx')loadXxx()`
5. **JavaScript functions** — add `loadXxx()`, `renderXxxTable()`, `saveXxx()`, `showModal('xxx')` handler
6. **`hapus()` function** — add `if(type==='xxx')loadXxx()` for delete callback

#### Code Organization Pattern (for large monoliths)
```javascript
/* ================= PHASE 1: KELOMPOK MASTER ================= */
// API Functions
async function fetchKelompok(tipe) { ... }
async function loadKelompok() { ... }

// Render Functions
function renderKelompokTable(data) { ... }
function selectKelompokTipe(tipe) { ... }

// CRUD
function editKelompok(id) { ... }
async function saveKelompok(id) { ... }

/* ================= PHASE 2: SANTRI_KELOMPOK ================= */
// Detail Panel
async function showKelompokDetail(id, nama) { ... }
async function loadKelompokAnggota() { ... }

// Bulk Add
async function showBulkAddModal() { ... }
async function doBulkAdd() { ... }

// Deactivate
async function deactivateAnggota(santriId, kelompokId) { ... }
```

#### Tipe Filter Tabs Pattern (reusable)
```javascript
const KELOMPOK_TIPES=[
  {value:'KAMAR',label:'🏠 Kamar',color:'#3b82f6'},
  {value:'KEGIATAN',label:'📚 Kegiatan',color:'#0d9488'},
  // ...
];
let selectedKelompokTipe='';

async function loadKelompok(){
  if(!$('kelompokTabs').innerHTML){
    let tabs='<div class="kegiatan-tab '+(selectedKelompokTipe===''?'active':'')+'" onclick="selectKelompokTipe(\'\')">Semua</div>';
    KELOMPOK_TIPES.forEach(t=>{
      tabs+='<div class="kegiatan-tab '+(selectedKelompokTipe===t.value?'active':'')+'" onclick="selectKelompokTipe(\''+t.value+'\')">'+t.label+'</div>';
    });
    $('kelompokTabs').innerHTML=tabs;
  }
  const url=selectedKelompokTipe?'/api/kelompok?tipe='+selectedKelompokTipe:'/api/kelompok';
  const data=await api(url);
  renderKelompokTable(data);
}
```

#### Bulk Add Modal Pattern (multi-select with "Select All")
```javascript
async function showBulkAddModal(){
  const allSantri=await api('/api/santri');
  const anggota=await api('/api/santri-kelompok?kelompok_id='+currentKelompokId+'&status=aktif');
  const anggotaIds=new Set((anggota||[]).map(a=>a.santri_id));
  const available=allSantri.filter(s=>s.status==='aktif'&&!anggotaIds.has(s.id));
  // Render checkboxes with "Select All"
  let html='<div><label><input type="checkbox" id="bulkSelectAll" onchange="toggleBulkSelect()"> <b>Pilih Semua</b></label></div>';
  available.forEach(s=>{
    html+='<label><input type="checkbox" class="bulk-check" value="'+s.id+'"> '+s.nama+'</label>';
  });
  // ...
}
function toggleBulkSelect(){
  const all=document.getElementById('bulkSelectAll').checked;
  document.querySelectorAll('.bulk-check').forEach(c=>c.checked=all);
}
```

### Backend: Adding Unified Absensi Filters
When adding kelompok_id/sesi_id support to existing absensi endpoint:
```javascript
app.get('/api/absensi', authenticate, (req, res) => {
  let list = db.absensi;
  if (req.query.tanggal) list = list.filter(a => a.tanggal === req.query.tanggal);
  // NEW: Filter by kelompok_id
  if (req.query.kelompok_id) list = list.filter(a => a.kelompok_id == req.query.kelompok_id);
  if (req.query.sesi_id) list = list.filter(a => a.sesi_id == req.query.sesi_id);
  // NEW: Filter by kelompok tipe
  if (req.query.kelompok_tipe) {
    const kelompokIds = db.kelompok.filter(k => k.tipe === req.query.kelompok_tipe).map(k => k.id);
    list = list.filter(a => kelompokIds.includes(a.kelompok_id));
  }
  // Backward compat: old filter still works
  if (req.query.kegiatan_id) list = list.filter(a => a.kegiatan_id == req.query.kegiatan_id);
  // ... existing santri attribute filters ...
});
```

### Migrating Old Tables to Unified (absen_malam + absen_sekolah → absensi)
In bulk POST endpoints (absen-malam/bulk, absen-sekolah/bulk):
1. Find kelompok by name (e.g., "Absen Malam" or "Ngaji Malam")
2. Write to unified `absensi` table with `kelompok_id`
3. Also clean old table for backward compat
4. Create/update `absensi_sesi` with `kelompok_id`

In GET endpoints: read from unified `absensi` table filtered by kelompok_id, fall back to old table if kelompok not found.

### Desktop Responsive Pattern (Tailwind)

The app uses Tailwind breakpoint classes (not CSS media queries):

| What | Mobile | Desktop (md: / lg:) |
|---|---|---|
| Sidebar | Hidden, slides in on toggle | `md:static` — always visible |
| Hamburger menu | Visible | `md:hidden` — hidden |
| Bottom nav | Fixed bottom | `md:hidden` — hidden |
| Content margin | No margin | `md:ml-64` — offset for sidebar |
| Menu grid (icons) | Visible (quick access) | `md:hidden` — sidebar has them |
| Data widgets | Hidden | `hidden md:block` — show stats/tables |
| Stats grid | 2 cols | `grid-cols-2 md:grid-cols-4` |
| Content container | Full width | `max-w-6xl mx-auto` — centered |

**Philosophy:** Mobile = quick access buttons (layar sempit). Desktop = data & tables (layar luas).

```html
<!-- Menu grid: mobile only -->
<div class="md:hidden">...</div>

<!-- Data widgets: desktop only -->
<div class="hidden md:block">...</div>

<!-- Stats: 2 cols mobile, 4 cols desktop -->
<div class="grid grid-cols-2 md:grid-cols-4 gap-3">...</div>

<!-- Content: max-width centered -->
<div class="max-w-6xl mx-auto">...</div>
```

### Alpine.js Modal Patterns

#### 1. x-cloak style is REQUIRED
Without it, modals flash visible before Alpine initializes:
```html
<style>[x-cloak] { display: none !important; }</style>

<div x-show="searchOpen" x-cloak ...>...</div>
```

#### 2. Auto-focus input on modal open
Use `x-effect` with `$nextTick`:
```html
<div x-show="searchOpen" x-cloak
     x-effect="if(searchOpen) $nextTick(() => $refs.searchInput?.focus())">
  <input x-ref="searchInput" ...>
</div>
```

#### 3. Don't mix x-data with Alpine.data()
The app uses inline `x-data` on the app shell div. If you also use `Alpine.data()` for components, the scopes conflict — functions from `Alpine.data()` won't be accessible from inline handlers. **Solution:** Use global functions called via `window.funcName()` or inline expressions only.

#### 4. Escape to close + click outside
```html
<div @keydown.escape.window="searchOpen = false"
     @click.self="searchOpen = false">
```

#### 5. Debounced input search
```html
<input @input.debounce.300ms="fetchResults()" ...>
```

### Backend Search API Pattern

Added `?search=` query param to `/api/santri`:
```javascript
if (req.query.search) {
  const q = req.query.search.toLowerCase();
  list = list.filter(s => {
    const kamar = db.kamar.find(x => x.id === s.kamar_id);
    return (s.nama||'').toLowerCase().includes(q)
      || (s.nis||'').toLowerCase().includes(q)
      || String(s.id) === q
      || (kamar?.nama||'').toLowerCase().includes(q);
  });
}
```

### Debugging: Alpine State Missing (Empty Template Bindings)

**Symptom:** Page renders but x-text/x-show bindings show empty/zero values despite API returning data.

**Root cause:** Template references variables (`dashboardData`, `user`, `role`) not defined in `x-data` on the body. Alpine silently evaluates undefined vars as empty string.

**Diagnosis via browser console:**
```javascript
// 1. Check what's actually in x-data
document.querySelector('[x-data]')?.getAttribute('x-data')

// 2. Check if specific binding elements exist and their text
Array.from(document.querySelectorAll('[x-text*="dashboardData"]')).map(el => ({
  text: el.textContent,
  expr: el.getAttribute('x-text')
}))

// 3. Verify API actually works
fetch('/api/dashboard', {headers: {'Authorization': 'Bearer ' + localStorage.getItem('token')}})
  .then(r => r.json()).then(d => console.log(d))
```

**Fix pattern — expand x-data on body to include ALL referenced state + methods:**
```html
<body x-data="{
    page: 'login',
    token: localStorage.getItem('token'),
    user: null,
    role: '',
    dashboardData: { total_santri: 0, hadir_hari_ini: 0, izin_sakit: 0, alfa: 0 },
    loadDashboard() {
        fetch('/api/dashboard', { headers: { 'Authorization': 'Bearer ' + this.token } })
        .then(r => r.json()).then(d => { this.dashboardData = d; });
    },
    loadMe() {
        fetch('/api/me', { headers: { 'Authorization': 'Bearer ' + this.token } })
        .then(r => r.json()).then(d => { this.user = d; this.role = d.role; this.loadDashboard(); });
    },
    login(username, password) {
        fetch('/api/login', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username, password}) })
        .then(r => r.json()).then(d => {
            if(d.token) { this.token = d.token; localStorage.setItem('token', d.token); this.page = 'home'; this.loadMe(); }
        });
    },
    init() { if (this.token) { this.page = 'home'; this.loadMe(); } }
}">
```

**Key rules:**
1. Every variable used in `x-text`, `x-show`, `x-bind`, `@click` MUST be declared in `x-data`
2. Login must call `loadMe()` → `loadDashboard()` chain (not just set `page='home'`)
3. `init()` auto-restores session on page reload if token exists
4. Initialize `dashboardData` with default empty values to prevent undefined errors before API loads

### Global Search Modal (Header)

Pattern: magnifying glass icon in header → modal overlay from top → live search with debounce → results list with avatar + name + kamar.

```html
<!-- Header button -->
<button @click="searchOpen = !searchOpen">🔍</button>

<!-- Modal -->
<div x-show="searchOpen" x-cloak ...>
  <input @input.debounce.300ms="
    if(searchQuery.length >= 2) {
      fetch('/api/santri?search='+encodeURIComponent(searchQuery), ...)
    }
  " placeholder="Cari santri...">
  <!-- Results list -->
</div>
```

Alpine state needed: `searchOpen`, `searchQuery`, `searchResults`, `searchLoading`.

### V2 CRUD Page Pattern (Alpine.js + Tailwind)

When building CRUD pages for the V2 Alpine.js frontend, each page is a self-contained `x-data` component with its own state, load, save, delete functions.

### Template: CRUD Page with Modal

```html
<div class="page" x-show="page === 'PAGE_NAME'" x-data="{
    list: [],
    showModal: false,
    editId: null,
    form: { field1:'', field2:'' },
    load() {
        fetch('/api/ENDPOINT', { headers:{'Authorization':'Bearer '+token} })
        .then(r=>r.json()).then(d=>{ this.list=d; });
    },
    openAdd() { this.editId=null; this.form={field1:'',field2:''}; this.showModal=true; },
    openEdit(item) { this.editId=item.id; this.form={field1:item.field1||'',field2:item.field2||''}; this.showModal=true; },
    save() {
        const url = this.editId ? '/api/ENDPOINT/'+this.editId : '/api/ENDPOINT';
        const method = this.editId ? 'PUT' : 'POST';
        fetch(url, { method, headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body:JSON.stringify(this.form) })
        .then(r=>r.json()).then(()=>{ this.showModal=false; this.load(); });
    },
    del(id) {
        if(!confirm('Hapus?')) return;
        fetch('/api/ENDPOINT/'+id, { method:'DELETE', headers:{'Authorization':'Bearer '+token} })
        .then(()=>this.load());
    },
    init() { this.load(); }
}">
    <!-- Header + Tambah button -->
    <div class="flex justify-between items-center mb-4">
        <h2 class="text-2xl font-bold">Title</h2>
        <button @click="openAdd()" class="bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg font-semibold">+ Tambah</button>
    </div>
    <!-- Table -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-x-auto">
        <table class="w-full text-sm">
            <thead class="bg-gray-50 dark:bg-gray-700">
                <tr><th class="px-3 py-2 text-left">No</th><!-- columns --><th class="px-3 py-2 text-left">Aksi</th></tr>
            </thead>
            <tbody>
                <template x-for="(item,i) in list" :key="item.id">
                    <tr class="border-t dark:border-gray-700">
                        <td class="px-3 py-2" x-text="i+1"></td>
                        <!-- data cells -->
                        <td class="px-3 py-2">
                            <button @click="openEdit(item)" class="text-blue-500 hover:underline mr-2">✏️</button>
                            <button @click="del(item.id)" class="text-red-500 hover:underline">🗑️</button>
                        </td>
                    </tr>
                </template>
                <tr x-show="list.length===0"><td colspan="N" class="px-3 py-4 text-center text-gray-400">Tidak ada data</td></tr>
            </tbody>
        </table>
    </div>
    <!-- Modal -->
    <div x-show="showModal" x-cloak class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click.self="showModal=false">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md p-6">
            <h3 class="text-lg font-bold mb-4" x-text="editId?'Edit':'Tambah'"></h3>
            <!-- form fields -->
            <div class="flex justify-end gap-2 mt-4">
                <button @click="showModal=false" class="px-4 py-2 border rounded-lg dark:border-gray-600">Batal</button>
                <button @click="save()" class="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700">Simpan</button>
            </div>
        </div>
    </div>
</div>
```

### Critical: Nested x-data Token Access

**WRONG** — `this.$data.token` does NOT access parent scope in Alpine 3:
```javascript
// BROKEN — this.$data refers to child component's own data, token is undefined
fetch('/api/santri', { headers:{'Authorization':'Bearer '+this.$data.token} })
```

**CORRECT** — nested x-data inherits parent properties, use `token` directly:
```javascript
// WORKS — token is inherited from body x-data scope
fetch('/api/santri', { headers:{'Authorization':'Bearer '+token} })
```

In Alpine 3, child `x-data` components automatically inherit all parent scope properties. Inside methods, reference them by name (`token`, `user`, `role`) — NOT via `this.$data`.

### Sidebar Visibility Pattern (Tailwind)

**WRONG** — `:class` binding overrides Tailwind responsive classes:
```html
<aside class="sidebar ... md:static" :class="{ 'hidden': !sidebarOpen }">
<!-- Bug: sidebarOpen=false → hidden class applied → overrides md:static on desktop -->
```

**CORRECT** — use `hidden md:block` base + `!important` override:
```html
<aside class="sidebar fixed md:static ... hidden md:block" :class="{ '!block': sidebarOpen }">
```

- `hidden md:block` = hidden on mobile, always visible on desktop
- `!block` (with `!` = Tailwind important modifier) = when sidebarOpen=true on mobile, override hidden

### Alpine State Initialization Pattern

The body `x-data` must declare ALL state used across the app. Login must chain `loadMe()` → `loadDashboard()`:

```javascript
x-data="{
    page: 'login',
    token: localStorage.getItem('token'),
    user: null,
    role: '',
    dashboardData: { total_santri: 0, hadir_hari_ini: 0, izin_sakit: 0, alfa: 0 },
    loadDashboard() {
        fetch('/api/dashboard', { headers: { 'Authorization': 'Bearer ' + this.token } })
        .then(r => r.json()).then(d => { this.dashboardData = d; });
    },
    loadMe() {
        fetch('/api/me', { headers: { 'Authorization': 'Bearer ' + this.token } })
        .then(r => r.json()).then(d => {
            this.user = d; this.role = d.role;
            this.loadDashboard();  // ← MUST call after user loaded
        });
    },
    login(username, password) {
        fetch('/api/login', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username, password}) })
        .then(r => r.json()).then(d => {
            if(d.token) {
                this.token = d.token;
                localStorage.setItem('token', d.token);
                this.page = 'home';
                this.loadMe();  // ← MUST call loadMe, not just set page
            }
        });
    },
    init() { if (this.token) { this.page = 'home'; this.loadMe(); } }
}"
```

**Common mistakes:**
1. Login sets `page='home'` but never calls `loadMe()` → dashboard shows empty stats
2. `dashboardData` not initialized with defaults → undefined errors before API loads
3. `init()` doesn't check existing token → logged-out on page reload

### Pages Built for V2 (as of 2026-04-19)
- Dashboard: greeting, stats cards, menu grid (4 groups: Operasional, Data Master, Laporan, Lainnya)
- Data Santri: table + CRUD modal (nama, kamar dropdown, kelompok_ngaji, bakat, kelas_diniyyah, kelas_sekolah, status)
- Data Kamar: table + CRUD modal (nama, kapasitas)
- Data Kegiatan: table + CRUD modal (nama, hari, jam_mulai, jam_selesai)
- Pengguna: table + CRUD modal (nama, username, password, role: admin/ustadz/wali)

### Pages Still Placeholder (need building)
- Absensi, Absen Malam, Absen Sekolah, Catatan Guru, Rekap Absensi, Raport, Rekap Ustadz, Laporan, Pelanggaran, Pengumuman, Sensus, Pengaturan

## Git Deploy Workflow (No SSH)
```bash
# On local machine
cd /root/pesantren-v2
git add -A && git commit -m "feat: description" && git push origin main

# On VPS (user must do manually)
cd /root/pesantren-v2 && git pull && pm2 restart pesantren
```

## Kegiatan ↔ Kelompok Auto-Sync (tipe KEGIATAN) + Hierarchical Grouping

### Problem
Kegiatan table and kelompok table are separate. Adding a kegiatan didn't create a kelompok tipe `KEGIATAN`, so the dynamic absensi form (which uses kelompok) didn't show the kegiatan.

### Solution: 3-layer sync

**Layer 1: Auto-create kelompok on kegiatan CRUD (server.js)**

```javascript
// POST — auto-create kelompok with kegiatan_nama
app.post('/api/kegiatan', authenticate, requireAdmin, (req, res) => {
  const { nama } = req.body;
  const k = { id: nextId(db.kegiatan), nama, ... };
  db.kegiatan.push(k);
  if (!db.kelompok.find(kl => kl.nama === nama && kl.tipe === 'KEGIATAN')) {
    db.kelompok.push({
      id: nextId(db.kelompok), nama, tipe: 'KEGIATAN',
      kegiatan_nama: nama,  // ← links to parent kegiatan
      created_at: new Date().toISOString()
    });
  }
  saveDB(db); res.json(k);
});

// PUT — sync nama if renamed
app.put('/api/kegiatan/:id', ..., (req, res) => {
  const oldNama = k.nama;
  // ... update fields ...
  if (req.body.nama && req.body.nama !== oldNama) {
    const kl = db.kelompok.find(x => x.nama === oldNama && x.tipe === 'KEGIATAN');
    if (kl) kl.nama = req.body.nama;
  }
});

// DELETE — cascade: kelompok + santri_kelompok relasi
app.delete('/api/kegiatan/:id', ..., (req, res) => {
  const kelompokIds = db.kelompok
    .filter(kl => kl.nama === k.nama && kl.tipe === 'KEGIATAN')
    .map(kl => kl.id);
  db.kelompok = db.kelompok.filter(kl => !kelompokIds.includes(kl.id));
  db.santri_kelompok = db.santri_kelompok.filter(sk => !kelompokIds.includes(sk.kelompok_id));
});
```

**Layer 2: Backfill on boot (server.js, after loadDB)**

```javascript
db.kegiatan.forEach(k => {
  const existing = db.kelompok.find(kl => kl.nama === k.nama && kl.tipe === 'KEGIATAN');
  if (!existing) {
    db.kelompok.push({
      id: nextId(db.kelompok), nama: k.nama, tipe: 'KEGIATAN',
      kegiatan_nama: k.nama, created_at: new Date().toISOString()
    });
  } else if (!existing.kegiatan_nama) {
    existing.kegiatan_nama = k.nama; // backfill old records
  }
});
```

**Layer 3: `kegiatan_nama` field on kelompok POST/PUT (server.js)**

```javascript
app.post('/api/kelompok', ..., (req, res) => {
  const { nama, tipe, kegiatan_nama } = req.body;
  // Duplikat check includes kegiatan_nama (so "Kelas 1A" can exist under different kegiatan)
  if (db.kelompok.find(k =>
    k.nama.toLowerCase() === nama.toLowerCase() &&
    k.tipe === tipe &&
    (k.kegiatan_nama || '') === (kegiatan_nama || ''))
  ) return res.status(400).json({ message: 'Sudah ada' });
  const k = { id: nextId(db.kelompok), nama, tipe, kegiatan_nama: kegiatan_nama || null, ... };
});
```

### Frontend: Modal + Dropdown Patterns

**Modal — show kegiatan dropdown when tipe=KEGIATAN:**
```javascript
// In showModal('kelompok') — add dropdown
'<div id="mKegiatanGroup" style="'+(showKegiatan?'':'display:none')+'">'
  +'<label>Kegiatan</label>'
  +'<select id="mKegiatan"><option value="">-- Pilih Kegiatan --</option></select>'
+'</div>'

// onchange handler
async function kelompokTipeOnChange(tipe) {
  if (tipe === 'KEGIATAN') {
    $('mKegiatanGroup').style.display = '';
    // populate from /api/kegiatan
  } else {
    $('mKegiatanGroup').style.display = 'none';
  }
}

// saveKelompok — include kegiatan_nama
if (body.tipe === 'KEGIATAN') {
  body.kegiatan_nama = $('mKegiatan').value || null;
  if (!body.kegiatan_nama) return toast('Pilih kegiatan dulu');
}
```

**Absensi dropdown — optgroup by kegiatan:**
```javascript
if (tipe === 'KEGIATAN') {
  const groups = {};
  data.forEach(k => {
    const key = k.kegiatan_nama || 'Lainnya';
    if (!groups[key]) groups[key] = [];
    groups[key].push(k);
  });
  Object.keys(groups).forEach(gName => {
    const optgroup = document.createElement('optgroup');
    optgroup.label = '📚 ' + gName;
    groups[gName].forEach(k => {
      const o = document.createElement('option');
      o.value = k.id; o.textContent = k.nama + ' (' + k.jumlah_anggota + ' santri)';
      optgroup.appendChild(o);
    });
    $('absensiKelompok').appendChild(optgroup);
  });
}
```

Same optgroup pattern for rekap dropdown (`rekapKelompok` select).

### Kelola Kelompok Table — show Kegiatan column
```html
<thead><tr><th>No</th><th>Nama Sub-Grup</th><th>Kegiatan</th><th>Tipe</th><th>Anggota</th><th>Aksi</th></tr></thead>
```
```javascript
const kegiatanCol = k.kegiatan_nama || '-';
// render in table row
```

### UX flow
1. Admin adds kegiatan "Madrasah Diniyyah" → auto-creates kelompok (nama="Madrasah Diniyyah", tipe="KEGIATAN", kegiatan_nama="Madrasah Diniyyah")
2. Admin adds sub-groups: Kelas 1A, Kelas 2A (tipe="KEGIATAN", kegiatan_nama="Madrasah Diniyyah")
3. Absensi → tipe "Kegiatan" → dropdown shows grouped:
   ```
   ┌─📚 Madrasah Diniyyah──────┐
   │ Madrasah Diniyyah (5)     │  ← main group
   │ Kelas 1A (0)              │  ← sub-group
   │ Kelas 2A (0)              │  ← sub-group
   └───────────────────────────┘
   ```

## Rekap: Kelompok Filter When Tipe Selected

### Problem
When selecting a kelompok tipe in rekap, filter area was hidden (`display:none`), so no way to drill down to specific kelompok.

### Fix
1. Add `<select id="rekapKelompok">` (hidden by default) to filter area HTML
2. On tipe change → populate from `/api/kelompok?tipe=X`, show dropdown, hide old filters
3. On loadRekap → append `&kelompok_id=X` if dropdown has value

```javascript
async function rekapOnTipeChange() {
  const tipe = $('rekapTipe').value;
  const kelompokSel = $('rekapKelompok');
  if (tipe) {
    const kelompok = await api('/api/kelompok?tipe=' + tipe);
    kelompokSel.innerHTML = '<option value="">Semua Kelompok</option>';
    // Use optgroup for KEGIATAN tipe (same pattern as absensi dropdown)
    if (kelompok) kelompok.forEach(k => {
      const o = document.createElement('option');
      o.value = k.id; o.textContent = k.nama;
      kelompokSel.appendChild(o);
    });
    kelompokSel.style.display = '';
    // Hide old kegiatan-based filters
    $('rekapKamar').style.display = 'none';
    $('rekapFilter').style.display = 'none';
  } else {
    kelompokSel.style.display = 'none';
    $('rekapKamar').style.display = '';
  }
  loadRekap();
}

async function loadRekap() {
  const tipe = $('rekapTipe').value;
  if (tipe) {
    let url = '/api/rekap?kelompok_tipe=' + tipe;
    if ($('rekapKelompok').value) url += '&kelompok_id=' + $('rekapKelompok').value;
    // ... fetch + render ...
  }
}
```

**Backend already supports:** `GET /api/rekap?kelompok_tipe=X&kelompok_id=Y` — filters by kelompok type, then drills down by specific kelompok.

## Pokok vs Tambahan Kegiatan (Dynamic Tipe System)

### Concept
- **Pokok** kegiatan (e.g., Madrasah Diniyyah): appears as its own tipe in absensi (setara Kamar, Sekolah, Sorogan). Sub-grup dibuat dengan `tipe = nama kegiatan`.
- **Tambahan** kegiatan (e.g., English Club): uses sub-grup system (`tipe = "KEGIATAN"` + `kegiatan_nama` field).

### Data Model
```javascript
// Pokok: kelompok tipe = nama kegiatan langsung
{ id: 27, nama: "Madrasah Diniyyah", tipe: "Madrasah Diniyyah", kegiatan_nama: "Madrasah Diniyyah" }
{ id: 29, nama: "Kelas 1A", tipe: "Madrasah Diniyyah", kegiatan_nama: "Madrasah Diniyyah" }  // sub-grup

// Tambahan: kelompok tipe = "KEGIATAN", kegiatan_nama = parent
{ id: 30, nama: "English Club A", tipe: "KEGIATAN", kegiatan_nama: "English Club" }
{ id: 31, nama: "English Club B", tipe: "KEGIATAN", kegiatan_nama: "English Club" }
```

### Backend: Auto-create Logic (POST /api/kegiatan)
```javascript
if (k.kategori === 'pokok') {
  // Pokok: kelompok tipe = nama kegiatan (jadi tipe absensi tersendiri)
  if (!db.kelompok.find(kl => kl.tipe === k.nama)) {
    db.kelompok.push({ id: nextId(db.kelompok), nama: k.nama, tipe: k.nama, kegiatan_nama: k.nama, ... });
  }
} else {
  // Tambahan: kelompok tipe KEGIATAN (sub-grup system)
  if (!db.kelompok.find(kl => kl.nama === k.nama && kl.tipe === 'KEGIATAN')) {
    db.kelompok.push({ id: nextId(db.kelompok), nama: k.nama, tipe: 'KEGIATAN', kegiatan_nama: k.nama, ... });
  }
}
```

### Backend: Sync on Rename (PUT /api/kegiatan/:id)
```javascript
if (oldKategori === 'pokok') {
  // Pokok: update tipe on ALL kelompok with this tipe
  db.kelompok.filter(kl => kl.tipe === oldNama).forEach(kl => {
    kl.tipe = k.nama; kl.kegiatan_nama = k.nama;
  });
} else {
  // Tambahan: update kegiatan_nama on kelompok tipe KEGIATAN
  db.kelompok.filter(kl => kl.tipe === 'KEGIATAN' && kl.kegiatan_nama === oldNama).forEach(kl => {
    kl.kegiatan_nama = k.nama;
    if (kl.nama === oldNama) kl.nama = k.nama;
  });
}
```

### Backend: Sync on Delete (DELETE /api/kegiatan/:id)
```javascript
let kelompokIds;
if (k.kategori === 'pokok') {
  kelompokIds = db.kelompok.filter(kl => kl.tipe === k.nama).map(kl => kl.id);
} else {
  kelompokIds = db.kelompok.filter(kl => kl.tipe === 'KEGIATAN' && kl.kegiatan_nama === k.nama).map(kl => kl.id);
}
// cascade: kelompok + santri_kelompok
```

### Backend: Dynamic Tipe Endpoint
```javascript
app.get('/api/kelompok-tipes', authenticate, (req, res) => {
  const builtIn = [
    { value: 'KAMAR', label: '🏠 Kamar', color: '#3b82f6', kategori: 'built-in' },
    { value: 'SEKOLAH', label: '🏫 Sekolah', color: '#f97316', kategori: 'built-in' },
    { value: 'SOROGAN', label: '📖 Sorogan', color: '#8b5cf6', kategori: 'built-in' },
    { value: 'BAKAT', label: '🎨 Bakat', color: '#ec4899', kategori: 'built-in' },
    { value: 'SOROGAN_MALAM', label: '🌙 Sorogan Malam', color: '#6366f1', kategori: 'built-in' },
  ];
  const pokokKegiatan = db.kegiatan.filter(k => k.kategori === 'pokok');
  const dynamicTipes = pokokKegiatan.map(k => ({
    value: k.nama, label: '📚 ' + k.nama, color: '#0d9488', kategori: 'pokok'
  }));
  const tambahan = [{ value: 'KEGIATAN', label: '📋 Kegiatan Tambahan', color: '#0d9488', kategori: 'tambahan' }];
  res.json([...builtIn, ...dynamicTipes, ...tambahan]);
});
```

### Frontend: Dynamic KELOMPOK_TIPES (replaces hardcoded array)
```javascript
let KELOMPOK_TIPES = [];
async function loadKelompokTipes() {
  if (KELOMPOK_TIPES.length) return KELOMPOK_TIPES;
  const data = await api('/api/kelompok-tipes');
  if (data) KELOMPOK_TIPES = data;
  return KELOMPOK_TIPES;
}
// Every function that uses KELOMPOK_TIPES must call loadKelompokTipes() first:
async function loadKelompok() { await loadKelompokTipes(); /* then use KELOMPOK_TIPES */ }
async function initRekapTipeDropdown() { await loadKelompokTipes(); /* then build options */ }
async function showModal('kelompok') { await loadKelompokTipes(); /* then build tipeOpts */ }
```

### Frontend: Modal — Conditional Kegiatan Dropdown
```javascript
// kelompokTipeOnChange — show/hide based on selected tipe
async function kelompokTipeOnChange(tipe) {
  if (tipe === 'KEGIATAN') {
    $('mKegiatanGroup').style.display = '';
    // Populate only tambahan kegiatan (NOT pokok — pokok uses tipe=nama)
    const kegList = await api('/api/kegiatan') || [];
    kegList.filter(kg => kg.kategori === 'tambahan').forEach(kg => { /* add options */ });
  } else {
    $('mKegiatanGroup').style.display = 'none';
  }
}

// saveKelompok — include kegiatan_nama for KEGIATAN tipe
async function saveKelompok(id) {
  const body = { nama: $('mNama').value, tipe: $('mTipe').value };
  if (body.tipe === 'KEGIATAN') {
    body.kegiatan_nama = $('mKegiatan').value || null;
    if (!body.kegiatan_nama) return toast('Pilih kegiatan dulu');
  }
  // ... POST/PUT ...
}
```

### Frontend: Fallback for Unknown Tipe
```javascript
function getTipeInfo(tipe) {
  return KELOMPOK_TIPES.find(t => t.value === tipe) || { label: '📚 ' + tipe, color: '#0d9488' };
}
```

### Migration: Old KEGIATAN → Pokok Tipe
When existing kelompok has `tipe: "KEGIATAN"` but kegiatan is pokok, run one-time migration:
```javascript
db.kelompok.filter(k => k.tipe === 'KEGIATAN').forEach(k => {
  const keg = db.kegiatan.find(kg => kg.nama === k.kegiatan_nama);
  if (keg && keg.kategori === 'pokok') { k.tipe = k.kegiatan_nama; }
});
```

### UX Flow
- **Pokok:** Add kegiatan (pokok) → auto-creates kelompok (tipe=nama) → appears as tipe in absensi/rekap
- **Tambahan:** Add kegiatan (tambahan) → auto-creates kelompok (tipe=KEGIATAN) → appears in sub-grup dropdown grouped by kegiatan_nama

## Cache Invalidation for Dynamic Dropdowns

When data changes affect cached API responses (like KELOMPOK_TIPES), clear cache + reset dropdowns so next visit re-fetches fresh data.

### Pattern: Clear cache on save/delete
```javascript
// After saveKegiatan or delete kegiatan:
KELOMPOK_TIPES = [];  // clear cached tipe list
resetTipeDropdowns(); // force dropdowns to re-populate on next use

function resetTipeDropdowns() {
  // Remove all options except first (placeholder) from each dropdown
  const aSel = $('absensiTipe'); if (aSel) { while (aSel.options.length > 1) aSel.remove(1); }
  const rSel = $('rekapTipe'); if (rSel) { while (rSel.options.length > 1) rSel.remove(1); }
  const kTabs = $('kelompokTabs'); if (kTabs) kTabs.innerHTML = '';
}
```

### Why this matters
The `loadKelompokTipes()` function has `if (KELOMPOK_TIPES.length) return` guard — it only fetches once. Without clearing cache after CRUD operations, new entries (like a new pokok kegiatan) won't appear until page reload.

### Where to call resetTipeDropdowns()
1. After `saveKegiatan()` — new/edited kegiatan may add/change tipe
2. After `hapus('kegiatan')` — deleted kegiatan removes a tipe
3. NOT needed for kelompok CRUD (kelompok don't create new tipes)

## Search Filter in Bulk Add Modals

When showing a multi-select list of santri (for bulk add to kelompok/kamar), add a search input that filters visible items in real-time.

### Pattern
```html
<input type="text" id="bulkSearch" placeholder="🔍 Cari nama santri..."
  oninput="filterBulkList()" style="width:100%;padding:.5rem;border:1px solid var(--border);border-radius:8px;margin-bottom:.5rem">
```

```javascript
function filterBulkList() {
  const q = ($('bulkSearch').value || '').toLowerCase();
  document.querySelectorAll('#bulkSantriList label').forEach(el => {
    el.style.display = el.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}

// "Pilih Semua" should only toggle VISIBLE items:
function toggleBulkSelect() {
  const all = document.getElementById('bulkSelectAll').checked;
  document.querySelectorAll('#bulkSantriList label').forEach(el => {
    if (el.style.display !== 'none') el.querySelector('.bulk-check').checked = all;
  });
}
```

### Key details
- Use `el.textContent.toLowerCase().includes(q)` — matches anywhere in the label (name + kamar info)
- "Pilih Semua" checks `el.style.display !== 'none'` to only select visible (filtered) items
- Works for both kelompok bulk add (checkboxes with `.bulk-check`) and kamar bulk add (`.bulk-kamar-check`)

## Rekap "Lainnya" Fallback: Resolve from kelompok_id

When `absensi_sesi` records have `kegiatan_nama: null` and `kegiatan_id: 0` (orphaned from deleted kegiatan), resolve the display name from `kelompok_id` instead of showing "Lainnya".

### Pattern in rekap-ustadz API
```javascript
userSesi.forEach(s => {
  let namaKeg = 'Lainnya';
  if (s.kegiatan_nama) namaKeg = s.kegiatan_nama;
  else { const kg = db.kegiatan.find(k => k.id === s.kegiatan_id); if (kg) namaKeg = kg.nama; }
  // Fallback: resolve dari kelompok
  if (namaKeg === 'Lainnya' && s.kelompok_id) {
    const kl = db.kelompok.find(k => k.id === s.kelompok_id);
    if (kl) {
      if (kl.tipe === 'KEGIATAN') namaKeg = kl.kegiatan_nama || kl.nama;
      else namaKeg = kl.tipe + ': ' + kl.nama;  // e.g., "KAMAR: hurairah"
    }
  }
});
```

### Orphan cleanup pattern
Sesi referencing deleted kegiatan/kelompok should be cleaned on boot:
```javascript
// Remove sesi where both kegiatan and kelompok don't exist
db.absensi_sesi = db.absensi_sesi.filter(s => {
  if (s.kegiatan_nama) return true;
  if (s.kegiatan_id) { const kg = db.kegiatan.find(k => k.id === s.kegiatan_id); if (kg) return true; }
  if (s.kelompok_id) { const kl = db.kelompok.find(k => k.id === s.kelompok_id); if (kl) return true; }
  return false; // orphan — remove
});
```

## Deployment Toolkit (Multi-Client)

### Files
- `deploy-client.sh` — 1-command deploy: `<name> <port> <domain>`
- `docker-compose.yml` — Docker multi-client
- `ecosystem.config.js` — PM2 multi-instance
- `backup.sh` — Auto backup data.json to `backup-data` branch
- `backup-all.sh` — Backup all clients in `/var/www/pesantren-*`
- `DEPLOY.md` — Full deployment guide

### Deploy new client (1 command)
```bash
bash deploy-client.sh pondok-alfalah 3001 absensi.alfalah.sch.id
```
Auto: clone → npm install → init data.json → PM2 start → Nginx config.

### Environment Variables (server.js)
```javascript
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'pesantren-secret-key';
const DB_FILE = process.env.DATA_FILE || path.join(__dirname, 'data.json');
```

## Default Kegiatan (as of 2026-04-17)
1. Ngaji Pagi — filter: Kelompok Ngaji Al-Qur'an
2. Ngaji Qur'an Siang — filter: Kelompok Ngaji Al-Qur'an
3. Bakat — filter: Jenis Bakat
4. Madrasah Diniyyah — filter: Kelas Diniyyah
5. Ngaji Malam — filter: Kelompok Ngaji Malam (NOT kamar)
6. Sekolah Formal — filter: Kelas Sekolah (auto-added if missing via boot check)

**Important:** Filter mapping changed 2026-04-17. "Ngaji Malam" now filters by `kelompok_ngaji_malam` (the ustadz/group), NOT by `kamar_id`. Each santri's `kelompok_ngaji_malam` field (e.g. "Ust. Ahmad") determines which group they attend.

## Session-Based Attendance Tracking (absensi_sesi)

When an ustadz saves attendance, the system creates a **session record** (not just individual student rows). This enables accurate "1 sesi = 1 kehadiran mengajar" counting.

### Schema
```javascript
// New table in data.json
absensi_sesi: [
  {
    id: number,
    ustadz_username: string,     // from req.user.username
    kegiatan_id: number,          // 0 for Absen Malam/Sekolah
    kegiatan_nama: string,        // "Absen Malam" or "Sekolah Formal" for non-regular
    tanggal: string,              // "YYYY-MM-DD"
    created_at: ISO string
  }
]
```

### Replace Logic (in all 3 bulk endpoints)
When ustadz saves attendance for the same (username, kegiatan, tanggal):
1. Find existing sesi → delete old absensi for THIS ustadz only
2. Update sesi timestamp (or create new sesi)
3. Insert fresh absensi rows

**CRITICAL:** Delete only `recorded_by === req.user.id`, NOT all absensi for that kegiatan+tanggal. Otherwise other ustadz's data gets wiped.

```javascript
// In /api/absensi/bulk
const oldSesi = db.absensi_sesi.find(s =>
  s.ustadz_username === req.user.username &&
  s.kegiatan_id == kegiatan_id &&
  s.tanggal === tanggal
);
if (oldSesi) {
  // Delete ONLY this ustadz's absensi
  db.absensi = db.absensi.filter(a =>
    !(a.kegiatan_id == kegiatan_id && a.tanggal === tanggal && a.recorded_by === req.user.id)
  );
  oldSesi.created_at = new Date().toISOString();
} else {
  db.absensi_sesi.push({
    id: nextId(db.absensi_sesi),
    ustadz_username: req.user.username,
    kegiatan_id: parseInt(kegiatan_id),
    tanggal,
    created_at: new Date().toISOString()
  });
}
// Insert fresh (NOT upsert)
items.forEach(item => {
  db.absensi.push({ id: nextId(db.absensi), santri_id: item.santri_id, ... });
});
```

### Rekap Ustadz (Session-Based)
Counts sesi instead of rows. `per_kegiatan` is a simple count, not `{total, H, I, S, A}`:
```javascript
// API response
{ user_id, nama, username, role, total_sesi, aktif_days, per_kegiatan: { "Ngaji Pagi": 4, "Sekolah Formal": 2 } }
```

## Raport 4-Zone Layout (Bulanan)

### Web View Structure
- **Zona 1 (Kop Surat):** Logo + app_name from Settings, centered title
- **Zona 2 (Identitas):** 2-column grid — Left: nama, kamar, alamat. Right: kelas, wali, periode
- **Zona 3A (Rekap Absensi):** Table per kegiatan with H/I/S/A/Total + TOTAL row
- **Zona 3B (Kedisiplinan):** Pelanggaran table, or green positive message if none
- **Zona 3C (Perkembangan):** Catatan guru with left-border accent
- **Zona 4 (Pengesahan):** 3-column signature area: Orang Tua | Wali Kelas (kosong) | Kepala Yayasan

### Data Sources
- Orang Tua name: `santri.wali_user_id` → resolve from `/api/users`
- Kepala Yayasan: `settings.kepala_nama`
- Alamat: `santri.alamat`
- Periode: from `sampai` date → format "Bulan YYYY"

### Settings Extension
New field `kepala_nama` in Settings (API already supports arbitrary fields via spread):
```javascript
// In saveSettings frontend
await api('/api/settings', {method:'PUT', body:JSON.stringify({
  app_name: appName,
  kepala_nama: $('settingKepalaNama').value || ''
})});
```

## Print CSS Pattern (A4 Raport)

```css
@media print {
  @page { size: A4; margin: 15mm }
  body { background: #fff !important; -webkit-print-color-adjust: exact; print-color-adjust: exact }
  body * { visibility: hidden }
  #raportCanvas, #raportCanvas * { visibility: visible }
  #raportCanvas { position: absolute; left: 0; top: 0; width: 100%; border-radius: 0 !important; box-shadow: none !important }
  #raportActions, .sidebar, .bottom-nav, .header-bar, #modalBg { display: none !important }
  /* Optimize for B&W printing */
  #raportCanvas table { border-color: #333 !important }
  #raportCanvas table th, #raportCanvas table td { border-color: #333 !important; color: #000 !important }
  /* Anti-potong: signature area stays on same page */
  #raportCanvas .sig-area { page-break-inside: avoid }
}
```

Key trick: `body * { visibility: hidden }` then `#raportCanvas, #raportCanvas * { visibility: visible }` — hides everything except the raport without breaking layout.

## Navigation Bug: goTo() Doesn't Exist

The app uses `navigateSidebar(page)` or `switchTab(page)` for navigation. There is **NO** `goTo()` function.

```javascript
// WRONG — goTo() doesn't exist, silently fails:
onclick="goTo('raport'); setTimeout(()=>{...}, 100)"

// CORRECT — use navigateSidebar + flag pattern:
function openRaportFor(id, nama) {
  navigateSidebar('raport');
  window._raportAutoLoad = { id, nama };
}
// Then in loadPageData:
if (page === 'raport') {
  const a = window._raportAutoLoad;
  window._raportAutoLoad = null;
  loadRaportForm(a ? a.id : null, a ? a.nama : null);
}
```

### Why setTimeout Doesn't Work
`navigateSidebar` → `switchTab` → `loadPageData` → `loadRaportForm()` is async. If `loadRaportForm` clears values (e.g., `$('raportSearch').value = ''`), a `setTimeout` that sets values BEFORE `loadRaportForm` finishes will have its values overwritten.

**Solution:** Pass the target ID/nama as parameters to `loadRaportForm` and let it set values AFTER loading data.

## Searchable Dropdown Pattern

For santri selection (dashboard search, raport form), use a text input + hidden input + dropdown div:

```html
<div style="position:relative">
  <input type="text" id="raportSearch" placeholder="Ketik nama santri..."
    oninput="searchSantriRaport(this.value)" autocomplete="off">
  <input type="hidden" id="raportSantri">
  <div id="raportSearchResults" style="position:absolute;top:100%;...display:none;z-index:100"></div>
</div>
```

Always add click-outside handler:
```javascript
document.addEventListener('click', e => {
  if (!e.target.closest('#raportSearch') && !e.target.closest('#raportSearchResults')) {
    const d = $('raportSearchResults'); if (d) d.style.display = 'none';
  }
});
```

## Data Schema Updates (as of 2026-04-18)

### Santri — added fields
```javascript
{
  // ... existing fields ...
  alamat: string,       // NEW — alamat lengkap santri
  // ... existing fields ...
}
```

### Settings — added fields
```javascript
{
  app_name: string,
  logo: string,         // base64 data URL
  background: string,   // base64 data URL (login bg)
  dashboard_bg: string, // base64 data URL (menu bg)
  kepala_nama: string   // NEW — nama kepala yayasan untuk raport
}
```

### absensi_sesi — new table
See "Session-Based Attendance Tracking" section above.

## PDF Export Auth Fix (Critical Pattern)

**Problem:** `window.open('/api/raport/pdf')` doesn't send auth token → 401 error.

**Solution:** Always use `fetch()` with Authorization header + blob download:
```javascript
async function exportSomethingPDF() {
  const res = await fetch('/api/endpoint/pdf?params', {
    headers: { 'Authorization': 'Bearer ' + token }
  });
  if (!res.ok) { const e = await res.json(); toast(e.message || 'Gagal'); return; }
  const blob = await res.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'filename.pdf';
  a.click();
  URL.revokeObjectURL(a.href);
}
```

**Never use:** `window.open(url)` for authenticated endpoints. It opens a new tab without the JWT.

## Bulk ZIP Download (pdfkit + archiver)

For downloading multiple PDFs as a single ZIP file.

### Backend Pattern
```javascript
const archiver = require('archiver');

app.get('/api/raport/download-all', authenticate, (req, res) => {
  res.setHeader('Content-Type', 'application/zip');
  res.setHeader('Content-Disposition', 'attachment; filename=raport.zip');
  const archive = archiver('zip', { zlib: { level: 5 } });
  archive.pipe(res);
  archive.on('error', (err) => { console.error('ZIP error:', err); res.status(500).end(); });

  // CRITICAL: pdfkit generates data async via events, need Promise wrapper
  function generatePDF(data) {
    return new Promise((resolve) => {
      const doc = new PDFDocument({ size: 'A4', margin: 40 });
      const chunks = [];
      doc.on('data', chunk => chunks.push(chunk));
      doc.on('end', () => resolve({ filename: 'name.pdf', buffer: Buffer.concat(chunks) }));
      // ... build PDF content ...
      doc.end();
    });
  }

  (async () => {
    for (const item of itemsList) {
      const { filename, buffer } = await generatePDF(item);
      archive.append(buffer, { name: filename });
    }
    archive.finalize();
  })();
});
```

### Why Promise is needed
`doc.on('data')` is async — `Buffer.concat(chunks)` is empty until `doc.on('end')` fires. Without Promise, `archive.append(Buffer.concat(chunks))` would append empty buffers.

### Frontend Pattern
```javascript
async function downloadAllZip() {
  toast('Mempersiapkan ZIP...');
  const res = await fetch('/api/raport/download-all?dari=...&sampai=...', {
    headers: { 'Authorization': 'Bearer ' + token }
  });
  if (!res.ok) { /* handle error */ return; }
  const blob = await res.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'raport.zip';
  a.click();
}
```

### npm dependency
```bash
npm install archiver
```

## Rekap Ustadz PDF (Pivot Table, Landscape)

Dynamic pivot table with auto-detected columns from database.

### Key Design Decisions
- **Landscape A4:** `{ size: 'A4', layout: 'landscape' }` for wide tables
- **Dynamic columns:** Scan absensi_sesi for active kegiatan in date range → sort by kategori (pokok first, tambahan second) → use as column headers
- **Auto-sizing:** `colNo (5%) + colNama (20%) + colTotal (8%) + kegiatan (67% / N columns)`
- **Rotate headers 90°:** When `colKeg < 35px`, use `doc.save() → translate → rotate(-90) → text → restore()`
- **Repeat header on new pages:** Wrap header rendering in `function renderTableHeader(yPos)` called on page 1 and after each `doc.addPage()`
- **Empty cells:** Show `-` instead of `0` for cleaner look

### Kegiatan kategori column (for sorting)
Added `kategori` ('pokok'/'tambahan') and `urutan_tampil` (number) to kegiatan table. Dynamic, not hardcoded.

## Mobile-First CSS Overhaul Pattern

When converting a desktop-style web app to feel native on mobile:

### Key Principles
1. **Use `@media(max-width:991px)` for mobile** — not `min-width`. Mobile styles should be the BASE, desktop overrides on top.
2. **Compact everything** — smaller padding, smaller fonts, tighter gaps. Native apps don't waste space.
3. **Safe area insets for notched phones:**
   ```css
   @media(max-width:991px){
     body{padding-bottom:calc(72px + env(safe-area-inset-bottom,0px))}
     .bottom-nav{padding-bottom:env(safe-area-inset-bottom,0)}
   }
   ```
4. **Sidebar as overlay, not push** — on mobile, sidebar should be `width:85%; max-width:320px` sliding from left, NOT pushing content.
5. **Bottom nav native feel** — `height:56px`, `position:fixed; bottom:0`, items `min-width:48px` (touch target), active indicator dot/bar.
6. **Card feed instead of tables** — mobile users hate horizontal scroll. Use stacked cards with name + metadata rows.
7. **Header compact** — `min-height:48px`, smaller icons/spacing, search bar hidden on mobile (useless).
8. **Stats 2x2 grid** — `grid-template-columns:repeat(2,1fr)` on mobile, 4-col on desktop.
9. **Quick actions** — 4-icon grid row for daily shortcuts (like super-app bottom sheet).
10. **Three breakpoints**: mobile (<600px), tablet (600-991px), desktop (≥992px).

### Mobile CSS Template
```css
@media(max-width:991px){
  body{padding-bottom:calc(72px + env(safe-area-inset-bottom,0px))}
  .header{padding:.5rem .75rem;min-height:48px}
  .content{padding:.6rem .75rem;margin-left:0}
  .header{margin-left:0}
  .sidebar{left:-100%;width:85%;max-width:320px;z-index:200}
  .sidebar.open{left:0}
  .bottom-nav{height:56px;padding-bottom:env(safe-area-inset-bottom,0)}
  /* Compact everything: stat cards, widgets, tables, modals */
}
```

## Background Image Upload Bug Pattern

### Problem: CSS Variables Unreliable for Dynamic Images
Setting background via CSS variable (`document.documentElement.style.setProperty('--login-bg', 'url(...)')`) can fail silently. The variable may not resolve correctly, especially when the value contains special characters or when the variable isn't defined at initial paint.

**Solution: Use direct inline styles instead:**
```javascript
// WRONG — CSS variable, unreliable:
document.documentElement.style.setProperty('--login-bg', 'url('+s.background+')');

// CORRECT — inline style, always works:
$('loginPage').style.background = "url('"+s.background+"') center/cover no-repeat";
```

### Problem: Pseudo-elements Block Custom Background
When `.login-wrap` has `::before` and `::after` pseudo-elements (decorative overlays), they cover the custom background image set via inline style.

**Solution: Class toggle to hide pseudo-elements:**
```css
.login-wrap.has-custom-bg::before,
.login-wrap.has-custom-bg::after{display:none}
```
```javascript
// When applying custom bg:
$('loginPage').classList.add('has-custom-bg');
// When removing custom bg:
$('loginPage').classList.remove('has-custom-bg');
```

### Problem: Dashboard Background Targets Non-existent Element
Old code targeted `$('gridMenu')` which was renamed/removed. After restructuring, grid-menu elements use class `.grid-menu`, not ID.

**Solution: Use `querySelectorAll` for multiple containers:**
```javascript
document.querySelectorAll('.grid-menu').forEach(grid=>{
  grid.style.background = "url('"+s.dashboard_bg+"') center/cover no-repeat";
  // ...
});
```

### loadAppSettings Must Run After DOM Build
`loadAppSettings()` applies styles to `.menu-item`, `.grid-menu` elements. If called before `buildGridMenu()`, those elements don't exist yet. Fix init order:
```javascript
buildNav();
buildGridMenu();
loadAppSettings(); // AFTER buildGridMenu
switchTab('home');
```

## Dashboard Menu Grid with Filtering

When rendering the same menu groups to multiple containers with different filters:
```javascript
function renderGroups(container, excludePengaturan){
  let html='';
  groups.forEach(g=>{
    let items = g.items;
    if(excludePengaturan) items = items.filter(m=>m.id!=='pengaturan');
    if(!items.length) return;
    // ... render ...
  });
  $(container).innerHTML = html;
}
// Render to multiple targets
renderGroups('fullMenu', false);        // all menus (Semua Menu page)
renderGroups('dashboardMenuGrid', true); // dashboard without Pengaturan
```

## Many-to-Many Migration: Flat Fields → Kelompok + Pivot (2026-04-19)

### Problem
Santri had hardcoded flat fields (`kelas_diniyyah`, `kelompok_ngaji`, `jenis_bakat`, `kelas_sekolah`, `kelompok_ngaji_malam`) and 3 separate absensi tables (`absensi`, `absen_malam`, `absen_sekolah`). Adding new activities required schema changes.

### Solution: Dynamic Groups (Many-to-Many)

**New tables in data.json:**
```javascript
kelompok: [
  { id: number, nama: string, tipe: 'KAMAR'|'KEGIATAN'|'SEKOLAH'|'SOROGAN'|'BAKAT'|'SOROGAN_MALAM'|'LAINNYA', created_at: ISO }
]

santri_kelompok: [  // pivot table
  { santri_id: number, kelompok_id: number, status: 'aktif'|'inactive', created_at: ISO }
  // status=inactive = soft delete (preserves history)
]

absensi: [  // unified (replaces absen_malam + absen_sekolah)
  { id, santri_id, kegiatan_id?, kelompok_id?, sesi_id?, tanggal, status, keterangan, recorded_by, created_at }
  // sesi_id = distinguishes multiple sessions per kelompok per day (pagi vs siang)
]
```

### Migration Steps (migrate.js pattern)
1. Backup data.json
2. Create kelompok from kamar (tipe=KAMAR), kegiatan (tipe=KEGIATAN), unique flat field values
3. Create santri_kelompok from each santri's flat fields
4. Migrate absen_malam + absen_sekolah → unified absensi with kelompok_id
5. Update existing absensi rows: add kelompok_id from kegiatan_id mapping
6. Update absensi_sesi: add kelompok_id
7. Keep old tables as backup (don't delete)

### New API Endpoints
```
GET/POST/PUT/DELETE  /api/kelompok?tipe=KAMAR
GET/POST/DELETE      /api/santri-kelompok?kelompok_id=X&status=aktif
POST                 /api/santri-kelompok/bulk  {kelompok_id, santri_ids:[1,2,3]}
PUT                  /api/santri-kelompok/deactivate  {santri_id, kelompok_id}
GET                  /api/absensi?kelompok_id=X&kelompok_tipe=SEKOLAH&sesi_id=Y
GET                  /api/absensi/kelompok/:id?tanggal=2026-04-19  (get santri to absen)
POST                 /api/absensi/bulk  {kelompok_id, sesi_id, tanggal, items}
GET                  /api/rekap?kelompok_tipe=SEKOLAH&dari=X&sampai=Y
```

### Backward Compatibility
- `absen-malam` GET/POST → reads/writes from unified absensi (auto-maps to kelompok)
- `absen-sekolah` GET/POST → same
- `absensi?kegiatan_id=X` → still works

### Key Decisions
- Soft delete on santri_kelompok (status=inactive) preserves history
- sesi_id on absensi distinguishes pagi/siang sessions for same kelompok+ tanggal
- Old tables kept as backup after migration
- `extra` field on santri retained for personal data (alergi, ukuran seragam) — NOT for filtering/relasi

## Features as of 2026-04-18
- Absensi harian (6 kegiatan, dynamic filter per kegiatan, auto-sync from santri data)
- Absen Malam (H/A only, filter kamar + kelompok_ngaji_malam, both auto-sync)
- Absen Sekolah Formal (filter kelas_sekolah, auto-sync)
- Data Santri CRUD (with kelas_diniyyah, kelompok_ngaji, kelompok_ngaji_malam, kelas_sekolah, jenis_bakat, wali_user_id)
- Kamar, Kegiatan, Users management (roles: admin, ustadz, wali)
- Rekap Absensi (filter by date, kamar, kegiatan, all santri fields)
- Export PDF (rekap + raport with catatan guru)
- Pelanggaran Santri CRUD (jenis, keterangan, sanksi)
- **Catatan Guru CRUD** (auto-detect creator from JWT, kategori: perilaku/akademik/kesehatan/lainnya, integrated in raport)
- Raport Santri (select student + date range → rekap per kegiatan + pelanggaran + catatan guru, export PDF)
- **Wali Santri role** (dashboard anak, rekap absensi anak, catatan guru anak — read-only, no write access)
- Pengaturan (app name, logo, background login, kepala_nama)
- **Session-based ustadz tracking** (absensi_sesi, 1 sesi = 1 kehadiran mengajar, auto-replace)
- **Rekap Ustadz** (session-based counting, per kegiatan breakdown)
- **Rekap Ustadz PDF** (pivot table, landscape, dynamic columns by kategori, rotate headers, repeat header, tanda tangan)
- **Kegiatan kategori** (pokok/tambahan + urutan_tampil for column sorting)
- **Raport Bulanan** (4-zone layout: kop surat, identitas, rekap absensi, kedisiplinan, perkembangan, pengesahan)
- **Download Semua Raport** (ZIP bulk export, all active santri PDFs)
- **Print raport** (@media print CSS, A4, hide all except raportCanvas)
- **Dashboard search** (cari santri → kartu profil H/I/S/A → link ke raport)
- **Searchable dropdown** (raport form, click-outside close)
- PWA support
- Role-based access (Admin full, Ustadz limited, Wali read-only for their children)

## Variable Naming Conflict Pattern (When Adding New Features)

When adding new code to the monolith that uses similar variable names as existing code, **rename your new variables** to avoid JS "Identifier already been declared" errors that break the ENTIRE script:

```javascript
// EXISTING code (line ~1839):
let absensiData = {};  // old system — object {santriId: status}

// NEW code MUST use different name:
let absenDinamisData = [];  // new system — array [{santri_id, nama, status}]
```

**Symptom:** Login page shows but clicking "Masuk" does nothing. Browser console: `Identifier 'X' has already been declared` + `doLogin is not defined`.

**Root cause:** Duplicate `let` declaration in the same `<script>` block causes a parse error that prevents ALL subsequent function declarations from being defined.

**Prevention:** Before adding new functions, grep for existing variable names:
```bash
grep -n "let myVarName\|var myVarName\|const myVarName" public/index.html
```

**Brace validation (inline scripts):**
```bash
python3 -c "
import re
html = open('public/index.html').read()
scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
s = scripts[0]
print(f'Braces: {{ {s.count(\"{\")} vs }} {s.count(\"}\")} - diff {s.count(\"{\")-s.count(\"}\")}')
"
```
If diff != 0, the script won't parse. Find the line where depth goes negative.

## Dynamic Absensi Form Pattern (3-Step: Tipe → Kelompok → Santri)

Instead of separate absensi/absen-malam/absen-sekolah pages, use a single dynamic form:

**HTML structure:**
```html
<!-- Step 1: Tipe + Tanggal -->
<select id="absensiTipe" onchange="absensiOnTipeChange()">
  <option value="">-- Pilih Tipe --</option>
</select>
<!-- Step 2: Kelompok (shown after tipe selected) -->
<div id="absensiStep2" style="display:none">
  <select id="absensiKelompok" onchange="absensiOnKelompokChange()">
</div>
<!-- Step 3: Santri list (shown after kelompok selected) -->
<div id="absensiStep3" style="display:none">
  <div class="absensi-grid" id="absensiGrid"></div>
  <button onclick="simpanAbsensiDinamis()">💾 Simpan</button>
</div>
<!-- Placeholder -->
<div id="absensiPlaceholder">Pilih Tipe dan Kelompok...</div>
```

**JavaScript flow:**
```javascript
async function loadAbsensi() {
  // Populate tipe dropdown from KELOMPOK_TIPES constant
  KELOMPOK_TIPES.forEach(t => { /* add options */ });
  // Show placeholder, hide steps
}

async function absensiOnTipeChange() {
  // Fetch /api/kelompok?tipe=X → populate kelompok dropdown
}

async function absensiOnKelompokChange() {
  // Fetch /api/absensi/kelompok/:id?tanggal=X → get santri list
  // Build absenDinamisData array
  // Show step 3, render grid
}

async function simpanAbsensiDinamis() {
  // POST /api/absensi/bulk {kelompok_id, tanggal, items}
}
```

**Variable names must NOT clash with old system** (see naming conflict pattern above).

## Deployment Toolkit
- `deploy-client.sh` — 1-command deploy new client: `bash deploy-client.sh <name> <port> <domain>`
- `docker-compose.yml` — Docker multi-client
- `ecosystem.config.js` — PM2 multi-instance
- `backup.sh` — Auto backup data.json to `backup-data` branch (hash-based change detection)
- `backup-all.sh` — Backup all clients in `/var/www/pesantren-*`
- `DEPLOY.md` — Full deployment guide
- Crontab: `0 * * * * /root/pesantren-absensi/backup.sh`
- Env vars: `PORT`, `JWT_SECRET`, `DATA_FILE`
