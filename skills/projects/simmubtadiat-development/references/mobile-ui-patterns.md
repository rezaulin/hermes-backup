# SIM Mubtadiat — Mobile UI patterns & owner UI decisions (2026-08)

Owner-directed mobile cleanup. Reuse these patterns verbatim; they are the house style now.

## Card-table pattern ("disamakan dengan alumni/santri")

Pages whose lists look good on HP share ONE mechanism:
- `<table class="... table-responsive">` in the HTML
- `data-label="<Column Name>"` on every rendered `<td>` (in the JS render function)
- CSS in `frontend/style.css` (~line 159, inside a max-width media query) turns each row into a stacked card: thead hidden, `td { display:flex; justify-content:space-between }`, `td::before { content: attr(data-label) }`, plus `.table-responsive td > div:not(.text-xs) { display:inline-flex; flex-direction:column; align-items:flex-end }`.

Applied to: alumni.html, santri.html, pengajar-purna.html, pengajar.html (2026-08), catatan.html (2026-08). To align any other page: add the class + data-labels. Header column count must match td count (catatan.html was missing an Aksi th — fixed).

**Sibling-div pitfall:** because every direct child div of a card td becomes an `inline-flex`, MULTIPLE sibling divs inside one td (e.g. dewan-harian's several jabatan rows) end up SIDE BY SIDE instead of stacked. Fix: wrap the siblings in ONE container div `<div class="flex flex-col w-full text-left" style="align-items:flex-start">…</div>` — the inline style guards against the CSS rule's `align-items:flex-end`.

Badges inside a card cell (pengajar Mustahiq/Mufattish/Munawwib): put name + badge group in a `<div class="flex flex-col md:flex-row md:items-center gap-1 md:gap-2">` so they stack below the name on HP and sit beside it on desktop.

## Tabs go vertical on HP

Detail santri tabs: `nav class="-mb-px flex flex-col md:flex-row md:space-x-6"`, buttons `text-left md:text-center py-3 md:py-4`. Owner request: "urutan fitur dibuat menurun bukan menyamping".

## Absensi manual & rekap: monthly-grid layout (owner design, screenshot-based)

The owner's reference image = rows are ALL Hijri months of the tahun ajaran top-to-bottom, columns S | I | T. Implemented 2026-08 in absensi-manual.js (santri + pengajar tabs) and rekap.js (read-only):
- Month list built from the academic calendar (`buildBulanListTA` / kalenderRange): Smt-1 start month → Smt-2 end month (11 months for TA 2026/2027).
- **S = Sakit, I = Izin, T = Alpha ("tanpa keterangan")**. The HADIR column was REMOVED from input and rekap by owner decision — old total_hadir data stays in the DB untouched, it's just never shown or edited anymore.
- Input is ONE person at a time: `◀ 01. NAMA ▶` header with counter, fill all months, "Simpan & Lanjut ▶" saves and auto-advances to the next santri/pengajar (loops). Data loads per tahun_hijri — a TA spans TWO Hijri years, so fetch BOTH years and merge.
- Rekap siswa: same grid read-only + summary cards WITHOUT any Hadir card; rows with alpha get a faint red bg.
- Detail santri (profil_santri.js, tab Riwayat Akademik): per-TA "Rekap Absensi" is the same monthly grid — ALL months shown including empty ones (owner: "bulan kosong tetep tampil"), TOTAL as the last row instead of the old 3 big cards. Backend `RiwayatAbsensi` now carries `tahun_hijri` so months of both Hijri years can be laid out in order.

## Dashboard = role-based menu launcher (stats removed entirely)

Owner 2026-08: dashboard shows NO statistics, NO charts, NO teacher schedule ("hapus total", jadwal guru "tidak"). Instead: `renderMenuGrid(roles)` in main.js renders icon tiles filtered by `MENU_ACCESS` (xss.js) — same menu set as the sidebar, per role. Registry `DASH_MENU` maps route → {label, lucide icon, gradient classes}. The data-health watchdog (pimpinan/admin) still renders below it — that's a notification, not a statistic. When owner asks for more dashboard changes, do NOT resurrect stats/charts.

**Later iterations (commits ab36ed9 → 578dd20, 2026-08):**
- **Tabs** "Menu Utama | Semua Menu": Menu Utama is a FIXED list of 6 core menus (Santri, Penilaian, Absensi, Raport, Pelanggaran, Rekap) — owner chose a fixed list over a configurable setting ("tentukan"); don't add settings UI for it. Tabs auto-hide when Menu Utama has < 3 items (restricted roles).
- **Hero background is never plain**: owner sent an Islamic blue-white ornament → `frontend/public/hero-pattern.jpg` (copy from /root/.hermes/cache/images, PIL-optimize q85). `.hero-pattern` (style.css) = layered background-image: teal gradient overlay (135deg, rgba(15,110,119,.88) → rgba(18,162,168,.72)) OVER `url('/hero-pattern.jpg')`, cover+center. The overlay keeps white hero text readable; tune opacity if owner feedback says pattern too hidden/too loud.
- **Premium icon style** (owner: flat lucide tiles felt "template"): 3-stop gradient (via-), colored glow shadow per hue, glass sheen overlay div, stroke-width 2.25, tiles inside ONE rounded-3xl backdrop-blur card, hover lift + scale, grid 4 (mobile) / 5 (sm) / 7 (lg) cols. Standing rule for this app: backgrounds never plain (patterns/ornaments), icons never template-looking — fresh & premium.

## Bottom nav (xss.js `BOTTOM_NAV`)

Per-role arrays, spacer+FAB inserted automatically at index 2. Muroqib was cut from 6 items to 3 (Santri, Absen, Pelanggaran) by owner decision; other menus stay reachable via the top sidebar.

## Search (xss.js FAB + /api/search)

`GlobalSearch` (models/pencarian.go) sources as of 2026-08: santri aktif+pengabdian; alumni = ALL statuses NOT IN ('aktif','pengabdian') — i.e. the arsip set, incl. cuti (was only lulus/boyong/keluar); pengajar active; **pengajar_purna** (added 2026-08, badge in `searchBadgeFor`); dewan_harian. When the owner says search misses something, check these filters first. Pengajar-purna detail: `pengajar-purna.html#<id>` deep-link opens a read-only modal (works for pimpinan too, who only sees Edit/Hapus when canWrite).

## Vite bundle names are camelCase

When verifying deployed bundles, `ls /app/public/dist/assets/` — filenames are `dewanHarian-*.js`, `absensiManual-*.js`, `rekap-*.js`, `profilSantri-*.js`, `main-*.js` (not kebab-case). Cloudflare caches ~4h (`max-age=14400`, cf-cache-status HIT) but hashed filenames change per build, so new bundles bust the cache; tell the owner to Ctrl+F5 for the HTML shell.
