---
name: pesantren-absensi
description: Complete project knowledge for Pesantren Absensi web app - deployment, backup, architecture, and common tasks
category: software-development
---

# Pesantren Absensi - Project Knowledge

## Overview
Sistem absensi santri pesantren berbasis web (Node.js + Express + JSON database).
Deploy: VPS Ubuntu, PM2, Nginx reverse proxy, Cloudflare DNS/SSL.

## Architecture
- **Backend:** Express.js, JWT auth, bcrypt password, PDFKit for PDF export
- **Database:** JSON file (`data.json`) per client instance
- **Frontend:** Single-page app in `public/index.html` (vanilla JS, no framework)
- **Deploy:** One-click via `deploy-client.sh`

## Repo Structure (3 Repos)
- `origin` → `rezaulin/pesantren-absensi` (personal/source code)
- `deploy` → `rezaulin/pesantren-deploy` (deploy/sales)
- `release` → `rezaulin/vps-deploy` (production/sales - legacy)
- **ALWAYS push to BOTH active repos:** `git push origin main && git push deploy main`

## VPS Info
- IP: 157.245.200.128
- Domain: reviewtechno.me
- Specs: 4vCPU, 8GB RAM, 155GB disk
- PM2 for process management

## Deployment
```bash
# Deploy new client
bash /root/pesantren-absensi/deploy-client.sh <nama> <port> <domain>

# Flow: clone from vps-deploy repo → npm install → init data.json → PM2 → Nginx
```

## Cloudflare R2 Backup
- Config: `/root/.r2-config` (source it for credentials)
- Bucket: `pesantren-backup`
- Backup script: `backup-r2.sh` (cron every 6 hours)
- Scans ALL folders in `/var/www/*/` with `data.json`
- Restore: `restore.sh <client-name> [--r2]`

## DNS Template
See `DNS-TEMPLATE.md` in repo for full checklist:
1. Add domain to Cloudflare
2. Update nameservers at registrar
3. A Record → 157.245.200.128
4. Create Origin Certificate
5. Run deploy script

## Key Features
- Absensi kegiatan (Ngaji Pagi, Qur'an Siang, Bakat, Diniyyah, Malam, Sekolah)
- Fast absensi UI: "Semua Hadir" button, search, real-time counter
- Santri CRUD with dynamic filters
- Role: admin, guru, wali (read-only parent dashboard)
- Catatan guru (auto-detect creator, goes to raport)
- Raport + PDF export
- Rekap absensi
- Auto-backup hourly (GitHub) + every 6h (R2)

## Common Tasks
- **Update UI:** Edit `public/index.html` (single file, CSS + JS inline)
- **Add API:** Edit `server.js`
- **Restart:** `pm2 restart pesantren-absensi` (or `absensi-<client-name>`)
- **Check logs:** `pm2 logs <name> --lines 50`
- **Backup now:** `bash backup-r2.sh`
- **Restore:** `bash restore.sh <client-name> [--r2]`

## Session-Based Attendance Tracking (absensi_sesi)
When ustadz saves absensi, system creates a "session" record. If same (ustadz, kegiatan, tanggal) exists, replace old data.

**Schema:** `absensi_sesi` = `{id, ustadz_username, kegiatan_id, kegiatan_nama, tanggal, created_at}`

**Pattern (replace, NOT upsert):**
```js
// 1. Check if sesi exists for this ustadz+kegiatan+tanggal
const oldSesi = db.absensi_sesi.find(s => s.ustadz_username === req.user.username && s.kegiatan_id == kegiatan_id && s.tanggal === tanggal);
if (oldSesi) {
  // 2a. Delete ONLY this ustadz's old absensi (not other ustadz's!)
  db.absensi = db.absensi.filter(a => !(a.kegiatan_id == kegiatan_id && a.tanggal === tanggal && a.recorded_by === req.user.id));
  oldSesi.created_at = new Date().toISOString(); // update timestamp
} else {
  // 2b. Create new sesi
  db.absensi_sesi.push({ id: nextId(db.absensi_sesi), ustadz_username: req.user.username, kegiatan_id: parseInt(kegiatan_id), tanggal, created_at: new Date().toISOString() });
}
// 3. Insert fresh data (NOT upsert)
items.forEach(item => {
  db.absensi.push({ id: nextId(db.absensi), santri_id: item.santri_id, ... });
});
```

**Gotcha:** For absen-malam/sekolah (no kegiatan_id), use `kegiatan_nama` field instead for matching. Always filter by `recorded_by === req.user.id` to avoid deleting other ustadz's data.

**Rekap Ustadz:** Count sesi records, not rows. `total_sesi` = number of sessions = number of teaching days.

## Raport 4-Zone Layout
Professional monthly report with 4 zones, works on web + PDF + print.

**Zona 1 — Kop Surat:** 3-column invisible table (15%-70%-15%)
- Kolom kiri: Logo (from Settings)
- Kolom tengah: Nama Pesantren (biggest) → Judul Laporan (medium) → Alamat lembaga (small)
- Kolom kanan: Empty (balance)
- Full-width double border line

**Zona 2 — Identitas:** 6-column invisible table for aligned colons
- Label | : | Value || Label | : | Value
- Makes `:` perfectly aligned vertically

**Zona 3 — Inti Laporan:**
- Blok A: Attendance table (padding generous, header background, bold TOTAL line)
- Blok B: Discipline notes (indent descriptions 15px from date)
- Blok C: Development narrative (bordered box, min-height 60px)

**Zona 4 — Pengesahan:** 3 columns
- Kiri: Orang Tua/Wali (auto from `wali_user_id`)
- Tengah: Wali Kelas (empty, for manual signature)
- Kanan: "Kendal, 18 April 2026" → "Kepala Yayasan" → signature space → bold name
- Empty data → dotted line `......................................`

**Data fields needed:** `settings.alamat_lembaga`, `settings.kepala_nama`, `santri.alamat`, `santri.wali_user_id`

## Navigation Pattern (SPA)
The app uses `navigateSidebar(page)` / `switchTab(tab)` for page switching. `goTo()` does NOT exist.

**Cross-page navigation with auto-load:**
```js
// Don't use: goTo('raport'); setTimeout(...)
// Use flag pattern:
function openRaportFor(id, nama) {
  navigateSidebar('raport');
  window._raportAutoLoad = {id, nama};
}
// In loadPageData:
if(page==='raport') {
  const a = window._raportAutoLoad;
  window._raportAutoLoad = null;
  loadRaportForm(a ? a.id : null, a ? a.nama : null);
}
```

## Print CSS for Raport
```css
@media print{
  @page{size:A4;margin:15mm}
  body{background:#fff!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}
  body *{visibility:hidden}
  #raportCanvas,#raportCanvas *{visibility:visible}
  #raportCanvas{position:absolute;left:0;top:0;width:100%;border-radius:0!important;box-shadow:none!important}
  #raportActions,.sidebar,.bottom-nav,.header-bar,#modalBg{display:none!important}
}
```

## Kegiatan Kategori (Pokok/Tambahan)
Master kegiatan now has `kategori` ('pokok'/'tambahan') and `urutan_tampil` (number) fields.
Used for sorting columns in rekap ustadz pivot tables — Pokok first, then Tambahan by urutan.

**DB schema:** `kegiatan` = `{id, nama, kategori, urutan_tampil, created_at}`
**API:** POST/PUT `/api/kegiatan` accepts `kategori` and `urutan_tampil`

## Rekap Ustadz PDF (Pivot Table)
Dynamic pivot: scan active kegiatan in period → columns, count sessions per ustadz per kegiatan.
Landscape A4, 3-col kop surat, auto-sizing columns, rotate 90° if narrow, repeat header on new pages.
Endpoint: `GET /api/rekap-ustadz/pdf?dari=&sampai=`

## Bulk Raport Download (ZIP)
Download all student raports as single ZIP file. Each PDF has full kop surat + identitas + rekap.
Endpoint: `GET /api/raport/download-all?dari=&sampai=`
Uses `archiver` package. PDFs generated sequentially via Promise wrapper.
**CRITICAL:** Route must be BEFORE `/api/raport/:santri_id` route (Express route order).

## Excel Export
Two endpoints, both with Sheet 1 (Formal with kop surat/logo/merge cells) + Sheet 2 (Raw Data):
- `GET /api/export/excel` — Rekap absensi (pivot: santri × kegiatan)
- `GET /api/rekap-ustadz/excel` — Rekap ustadz (pivot: ustadz × kegiatan)
Uses `exceljs` package. Logo injected from `settings.logo` (base64).

## UI: Stat Cards with Colors
```css
.stat-card.blue{background:linear-gradient(135deg,#e8f4fd,#fff);border-color:#b3d9f2}
.stat-card.green{background:linear-gradient(135deg,#e8f8e8,#fff);border-color:#a8d8a8}
.stat-card.orange{background:linear-gradient(135deg,#fff8e8,#fff);border-color:#f0d68a}
.stat-card.red{background:linear-gradient(135deg,#fdecea,#fff);border-color:#f0a8a8}
.stat-card .icon{position:absolute;right:8px;top:8px;font-size:1.8rem;opacity:.15}
```

## UI: Mobile-First Responsive Design (Native App Feel)
Single-file SPA needs aggressive CSS overrides to feel like a native app on phone.

**Breakpoint strategy:** mobile-first with 3 tiers:
- `<992px` — mobile (phones, small tablets)
- `600-991px` — tablet
- `≥992px` — desktop (sidebar permanent)

**Mobile must-haves (<992px):**
```css
@media(max-width:991px){
  /* Header compact ala native app */
  .header{padding:.5rem .75rem;min-height:48px}
  .header-title{font-size:.95rem}
  .header-icon{width:32px;height:32px;font-size:1.1rem}
  .profile-pic{width:30px;height:30px;font-size:.8rem}

  /* Sidebar: overlay 85% width, NOT push */
  .sidebar{left:-100%;width:85%;max-width:320px;z-index:200;box-shadow:4px 0 20px rgba(0,0,0,.2)}
  .sidebar.open{left:0}

  /* Content full-width, minimal padding */
  .content{padding:.6rem .75rem;margin-left:0}
  .header{margin-left:0}

  /* Welcome banner compact */
  .welcome-banner{padding:.8rem 1rem;border-radius:14px;margin-bottom:.7rem}
  .welcome-banner h3{font-size:.92rem}

  /* Stats 2x2 kecil & padat */
  .stats{grid-template-columns:repeat(2,1fr);gap:.45rem}
  .stat-card{padding:.6rem .5rem}
  .stat-card .num{font-size:1.2rem}
  .stat-card .label{font-size:.6rem}

  /* Quick actions 4 kolom kecil */
  .quick-action{padding:.55rem .2rem}
  .quick-action .qa-icon{font-size:1.25rem;width:38px;height:38px}
  .quick-action .qa-label{font-size:.58rem}

  /* Feed cards compact (pengganti tabel) */
  .feed-card{padding:.55rem .7rem}
  .feed-card .feed-name{font-size:.8rem}

  /* Bottom nav native feel */
  .bottom-nav{height:56px;padding-bottom:env(safe-area-inset-bottom,0)}
  .nav-item{font-size:.58rem;padding:.35rem .4rem}

  /* Tables compact */
  table{font-size:.75rem}
  th{padding:.45rem .5rem;font-size:.65rem}

  /* Desktop-only elements hidden */
  .desktop-table{display:none!important}
  .card-feed{display:flex}
}

/* Tablet: 4-col stats, 2-col absensi */
@media(min-width:600px) and (max-width:991px){
  .stats{grid-template-columns:repeat(4,1fr)}
  .absensi-grid{grid-template-columns:1fr 1fr}
}

/* Desktop: sidebar permanent, hide bottom nav, card→table swap */
@media(min-width:992px){
  .sidebar{left:0;box-shadow:none;border-right:1px solid var(--border);z-index:10}
  .sidebar.open{left:0}
  .overlay{display:none!important}
  .sidebar-header button{display:none}
  .content{margin-left:280px}
  .header{margin-left:280px}
  .header-left .header-icon{display:none}
  .bottom-nav{display:none!important}
  body{padding-bottom:0}
  .card-feed{display:none}
  .desktop-table{display:block!important}
  .stats{grid-template-columns:repeat(4,1fr)}
}
```

**Dashboard layout (mobile):**
1. Welcome banner (compact greeting)
2. Stats 2x2 grid (Total Santri, Hadir, Izin/Sakit, Alfa)
3. Quick Actions — 4 shortcut harian (Absen Kelas, Absen Malam, Data Santri, Input Pelanggaran)
4. Widget cards: Alfa list as card feed (NOT table), Pengumuman
5. Bottom nav: Beranda, Absen, Rekap, Menu, Lainnya (→ sidebar drawer)

**Bottom nav pattern:**
- 5 items max (thumb zone)
- "Lainnya" opens sidebar drawer (not a page)
- `safe-area-inset-bottom` for notched phones
- Hidden on desktop via `display:none!important`

**Card feed vs table swap:** Render BOTH in HTML, use CSS media queries to show/hide:
```html
<div class="card-feed">...mobile cards...</div>
<div class="desktop-table" style="display:none">...<table>...</div>
```

**Common pitfall:** If sidebar shows on mobile, check that `.content` and `.header` don't have `margin-left:280px` leaking outside the `@media(min-width:992px)` block.

## UI: Menu Grouping (3 Blocks)
Menu items grouped by category with `.menu-group-title` headers:
- 📋 Operasional Harian (Absensi, Absen Malam, Sekolah, Pelanggaran, Catatan)
- 📁 Data Master (Santri, Kamar, Kegiatan, Pengguna, Sensus)
- 📊 Laporan & Rekap (Rekap, Raport, Rekap Ustadz, Laporan, Export)
Rendered via `buildGridMenu()` with `groups` array structure, 4-column grid.

## V2 Frontend (Alpine.js + Tailwind)
Second version at `/root/pesantren-v2/` using Alpine.js 3 + Tailwind CSS (CDN).
Same `data.json` format and API endpoints as v1. Runs on port 3001, domain: `v2.reviewtechno.me`.

**Repo:** `rezaulin/pesantren-v2` on GitHub. Push BOTH repos after changes.

**Architecture:** Single `public/index.html` with Alpine.js `x-data` on `<body>`.
Server: `server.js` with Express, same APIs as v1.

### Copying FAONSI Source to V2
User prefers the original FAONSI design (from `pesantren-absensi`) over Grok-generated code. To sync:
```bash
cp /root/pesantren-absensi/public/index.html /root/pesantren-v2/public/index.html
cp /root/pesantren-absensi/server.js /root/pesantren-v2/server.js
```
**PORT GOTCHA:** v1 server defaults to port 3000, but nginx for `v2.reviewtechno.me` proxies to **3001**. After copying, restart with:
```bash
cd /root/pesantren-v2 && PORT=3001 pm2 restart pesantren-v2 --update-env
```
Without `PORT=3001`, you get 502 Bad Gateway because the server listens on 3000 while nginx hits 3001.

### Alpine.js Pitfalls (Learned the Hard Way)

**1. Nested x-data scope access:**
```html
<!-- Body x-data has `token` -->
<body x-data="{ token: '...', page: 'home', ... }">
  <!-- Child x-data can access parent `token` directly -->
  <div x-data="{ list: [], load() { fetch('/api/...', {headers:{'Authorization':'Bearer '+token}}) } }">
```
- Use `token` directly, NOT `this.$data.token` (doesn't work in Alpine 3)
- Child components inherit parent scope properties
- Works for both template expressions AND methods

**2. Page name consistency:**
- Dashboard buttons: `@click="page='absenmalam'"`
- x-show condition: `x-show="page === 'absenmalam'"`
- Must match EXACTLY (hyphens matter: `absen-malam` ≠ `absenmalam`)
- Common mismatches: `absen-malam`→`absenmalam`, `absen-sekolah`→`absensekolah`, `settings`→`pengaturan`, `laporan`→`rekap`

**3. Double-escaped HTML from patch tool:**
When patching Alpine.js x-data with complex JS, the tool may produce `\\\"` instead of `"`.
Symptom: ALL pages render at once, raw JS visible as text.
Fix: `sed -i 's/\\\\"/"/g' public/index.html` or use Python string replace.

**4. Sidebar visibility on desktop:**
```html
<!-- BAD: hidden by default on all screens -->
<aside :class="{ 'hidden': !sidebarOpen }">

<!-- GOOD: visible on desktop, hidden on mobile -->
<aside class="hidden md:block" :class="{ '!block': sidebarOpen }">
```

**5. Dark mode toggle:**
```js
// In x-data state:
darkMode: localStorage.getItem('darkMode') !== 'false',
// Toggle button in header:
<button @click="darkMode = !darkMode; document.documentElement.classList.toggle('dark', darkMode); localStorage.setItem('darkMode', darkMode)">
  <span x-text="darkMode ? '☀️' : '🌙'"></span>
</button>
```

### Page Pattern (CRUD with Modal)
Every data page follows this Alpine.js pattern:
```html
<div x-show="page === 'xxx'" x-data="{
    list: [],
    showModal: false,
    editId: null,
    form: { field1:'', field2:'' },
    load() { fetch('/api/xxx',{headers:{'Authorization':'Bearer '+token}}).then(r=>r.json()).then(d=>{this.list=d;}); },
    openAdd() { this.editId=null; this.form={...}; this.showModal=true; },
    openEdit(item) { this.editId=item.id; this.form={...}; this.showModal=true; },
    save() {
        fetch(url, {method, headers:{'Content-Type':'application/json','Authorization':'Bearer '+token}, body:JSON.stringify(this.form)})
        .then(r=>r.json()).then(()=>{this.showModal=false;this.load();});
    },
    del(id) { if(!confirm('Hapus?')) return; fetch('/api/xxx/'+id,{method:'DELETE',headers:{'Authorization':'Bearer '+token}}).then(()=>this.load()); },
    init() { this.load(); }
}">
```

## WebSantri (Next.js on VPS2)
Separate app from v1/v2 — modern Next.js 14 stack.

**Access:**
- VPS2: `172.237.138.149` (root/jancoK123@a)
- SSH: `sshpass -p 'jancoK123@a' ssh -o StrictHostKeyChecking=no root@172.237.138.149 "command"`
- App path: `/root/websantri/`
- Domain: `websantri.reviewtechno.me`
- Port: 3002, PM2 name: `websantri`
- Login: admin/admin123, ustadz/ustadz123, wali/wali123

**Tech stack:** Next.js 14 (App Router), TypeScript, Prisma 5.22, SQLite, next-auth, vanilla CSS
**Libraries:** jspdf, jspdf-autotable, xlsx (all already in package.json)

**Deploy after changes:**
```bash
sshpass -p 'jancoK123@a' ssh -o StrictHostKeyChecking=no root@172.237.138.149 "cd /root/websantri && npm run build && pm2 restart websantri"
```

**Prisma gotcha:** SQLite doesn't support enums — use String fields. Don't use Prisma 7 (use 5.22). Remove `prisma.config.ts` if present (Prisma 7 artifact).

**Grok sub-agent pattern for VPS2:** Use `delegate_task` with `acp_command='grok'` and `toolsets=['terminal']`. All SSH commands must use the sshpass prefix. Max iterations 80-100 for complex tasks.

**Features built:**
- Absensi with status buttons (Hadir/Izin/Sakit/Alpa), summary bar, mobile card view
- Perizinan with search, status/jenis/date filters, PDF+Excel export
- Jadwal grouped by hari, filter per hari
- Dashboard with stat cards, sidebar with sections (Menu Utama/Data Master/Operasional)

## V2 Kelompok System (Many-to-Many Groups)

V2 introduces `kelompok` (groups) with `santri_kelompok` pivot table for flexible grouping.

**DB Schema:**
```
kelompok = {id, nama, tipe, kegiatan_nama, created_at}
santri_kelompok = {id, santri_id, kelompok_id, status: 'aktif'|'inactive', created_at}
absensi_sesi = {id, ustadz_username, kegiatan_id, kelompok_id, tanggal, jam_sesi, created_at}
absensi = {..., kelompok_id, sesi_id}  // linked to kelompok + sesi
```

### Tipe System (Dynamic, NOT Hardcoded)

Tipe values come from 3 sources (endpoint: `GET /api/kelompok-tipes`):
1. **Built-in:** KAMAR, SEKOLAH, SOROGAN, BAKAT, SOROGAN_MALAM
2. **Pokok kegiatan:** tipe = kegiatan name (e.g., "Madrasah Diniyyah")
3. **Tambahan kegiatan:** tipe = "KEGIATAN" (sub-grup system)

**Frontend:** Fetch from API, cache in `KELOMPOK_TIPES` array. Must call `loadKelompokTipes()` before using.

### Kegiatan ↔ Kelompok Auto-Sync

When creating/editing/deleting kegiatan, kelompok records auto-sync based on kategori:

**Pokok (main activity):**
```js
// POST /api/kegiatan with kategori='pokok'
// → creates kelompok with tipe = kegiatan nama
kelompok.push({ id: nextId(), nama: kegiatan.nama, tipe: kegiatan.nama, kegiatan_nama: kegiatan.nama });
```
- Appears as its own tipe in absensi/rekap dropdowns
- Sub-groups use same tipe (e.g., "Kelas 1A" under tipe "Madrasah Diniyyah")
- Rename kegiatan → rename all kelompok with matching tipe
- Delete kegiatan → delete all kelompok with matching tipe + their santri_kelompok

**Tambahan (additional activity):**
```js
// POST /api/kegiatan with kategori='tambahan'
// → creates kelompok with tipe = 'KEGIATAN'
kelompok.push({ id: nextId(), nama: kegiatan.nama, tipe: 'KEGIATAN', kegiatan_nama: kegiatan.nama });
```
- Appears under "Kegiatan Tambahan" tipe
- Sub-groups created with tipe='KEGIATAN' + kegiatan_nama = parent name
- In absensi dropdown, grouped by `kegiatan_nama` using `<optgroup>`

### Duplicate Check Pattern

Kelompok uniqueness = `nama + tipe + kegiatan_nama`:
```js
if (db.kelompok.find(k => k.nama.toLowerCase() === nama.toLowerCase() && k.tipe === tipe && (k.kegiatan_nama || '') === (kegiatan_nama || '')))
  return res.status(400).json({ message: 'Duplikat' });
```
This allows same sub-group name under different kegiatan (e.g., "Kelas 1A" under both "Madrasah Diniyyah" and "Ngaji Pagi").

### Frontend Cache Invalidation

**Critical pattern:** When kegiatan is added/edited/deleted, clear `KELOMPOK_TIPES` cache AND reset dropdown options:
```js
async function saveKegiatan(id) {
  // ... save ...
  KELOMPOK_TIPES = [];
  resetTipeDropdowns();
}
function resetTipeDropdowns() {
  // Remove all options except first from each dropdown
  const aSel = $('absensiTipe'); if(aSel) { while(aSel.options.length > 1) aSel.remove(1); }
  const rSel = $('rekapTipe');  if(rSel) { while(rSel.options.length > 1) rSel.remove(1); }
  const kTabs = $('kelompokTabs'); if(kTabs) kTabs.innerHTML = '';
}
```
Without this, new kegiatan won't appear until page refresh.

### Dynamic Dropdown Grouping (optgroup)

For KEGIATAN tipe, group kelompok by `kegiatan_nama` in dropdowns:
```js
if (tipe === 'KEGIATAN') {
  const groups = {};
  data.forEach(k => {
    const key = k.kegiatan_nama || 'Lainnya';
    if (!groups[key]) groups[key] = [];
    groups[key].push(k);
  });
  Object.keys(groups).forEach(gName => {
    const optgroup = document.createElement('optgroup');
    optgroup.label = '📋 ' + gName;
    groups[gName].forEach(k => {
      const o = document.createElement('option');
      o.value = k.id; o.textContent = k.nama;
      optgroup.appendChild(o);
    });
    $('dropdown').appendChild(optgroup);
  });
}
```

### Absensi Dinamis (Single Form for All Types)

V2 replaces 3 separate absensi pages with 1 dynamic form:
- Step 1: Select tipe (dropdown from `/api/kelompok-tipes`)
- Step 2: Select kelompok (filtered by tipe, with optgroup for KEGIATAN)
- Step 3: List santri with H/I/S/A buttons + counter bar

**Submit:** `POST /api/absensi/bulk` with `{tanggal, kelompok_id, items}`

**sesi_id Bug Fix:** In `POST /api/absensi/bulk`, variable was destructured as `sesi_id` (snake_case) but code referenced `sesiId` (camelCase) → ReferenceError crash. Always match variable names:
```js
const { tanggal, kelompok_id, sesi_id } = req.body;
// Use sesi_id consistently, NOT sesiId
const sesiMatch = (s) => {
  if (sesi_id) return s.id === parseInt(sesi_id);  // ✓ correct
  // if (sesiId) return ...  // ✗ BUG: sesiId not defined
};
```

**Link absensi to sesi:** Track `currentSesiId` when creating/updating sesi, use it in absensi inserts:
```js
let currentSesiId;
if (oldSesi) { currentSesiId = oldSesi.id; }
else { const newSesi = {...}; db.absensi_sesi.push(newSesi); currentSesiId = newSesi.id; }
items.forEach(item => {
  db.absensi.push({ ..., sesi_id: currentSesiId });  // NOT null
});
```

### Kamar Anggota Management

Uses `santri.kamar_id` (many-to-one, NOT pivot table). Different pattern from kelompok:

```js
// Count anggota per kamar
const anggotaCount = {};
santri.forEach(s => { if (s.status === 'aktif') anggotaCount[s.kamar_id] = (anggotaCount[s.kamar_id] || 0) + 1; });

// Load anggota for detail panel
const data = await api('/api/santri?kamar_id=' + kamarId);

// Bulk add: update kamar_id on each santri
for (const sid of selectedIds) {
  await api('/api/santri/' + sid, { method: 'PUT', body: JSON.stringify({ kamar_id: currentKamarId }) });
}

// Pindah kamar: show dropdown of other kamar, then PUT
await api('/api/santri/' + santriId, { method: 'PUT', body: JSON.stringify({ kamar_id: targetKamarId }) });
```

## Important Notes
- Data.json contains ALL data (users, santri, absensi, etc.)
- Default admin: admin / admin123 (change after deploy!)
- JWT secret auto-generated per deployment
- Port allocation: start from 3001 for clients (3000 is main/testing)
- Always restart PM2 after backend changes: `pm2 restart pesantren-v2`

## VPS Migration
```bash
# Di VPS lama:
bash backup-vps.sh   # Backup semua ke R2

# Di VPS baru:
# 1. Install awscli, setup ~/.r2-config
# 2. Download dari R2:
aws --endpoint-url $R2_ENDPOINT s3 cp s3://pesantren-backup/vps-migration/vps-backup-XXXX.tar.gz .
# 3. Restore:
bash restore-vps.sh vps-backup-XXXX.tar.gz
# 4. Update DNS A Record ke IP baru
```
