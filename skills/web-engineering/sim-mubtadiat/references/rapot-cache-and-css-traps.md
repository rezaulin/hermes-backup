# Raport: SW-cache + CSS-specificity traps, identity/Al-Bayan display rules (2026-08-27)

## "belum berubah" on rapot.html — Service-Worker PRECACHE trap (NOT deploy/CF failure)

When the owner says a rapot.html CSS/layout change "gak berubah / belum live" even in **Incognito**,
the usual Cloudflare / `docker cp` culprits are NOT it. Root cause 2026-08-27:
`frontend/public/sw.js` listed `/rapot.html` AND `/dist/rapot.html` in `urlsToCache` (precache list).
The service worker cached the page HTML at install and served that stale copy forever. **Bumping
`CACHE_NAME` alone does NOT help** while the URL stays in the precache list — the fresh SW just
re-precaches the same paths.

**Fix:** remove page-HTML entries from `urlsToCache` (keep only static shell assets:
`/index.html`, `/style.css`, logo, favicon) AND bump `CACHE_NAME`. After that rapot.html is
network-first fresh.

Diagnostic ladder for "gak berubah" on ANY page, in order:
1. `curl -s "https://reviewtechno.me/rapot.html?nc=$(date +%s)" | grep '<your-new-css>'` — cache-bust
   query defeats CF + SW; confirms the server truly serves new bytes.
2. `docker exec simmubtadiat-app-1 md5sum /app/public/dist/rapot.html` vs `curl … | md5sum` — equal =
   served correctly, problem is 100% client-side.
3. CF headers: `cf-cache-status: DYNAMIC` + `cache-control: no-cache` on the .html = CF is NOT caching;
   suspect SW next.
4. **Grep `sw.js` `urlsToCache` for the page path.** Present → precache trap. Remove + bump CACHE_NAME.
5. Owner reload recipe: Incognito is the definitive test (no SW/cache). Clear a stuck SW in a normal
   tab: DevTools → Application → Service Workers → Unregister → Clear site data → reload. On phone/PWA:
   clear site data or uninstall + reinstall the PWA.

## CSS specificity: `.rapot-sheet td` beats per-cell padding on the identity table

The sheet-wide rule `.rapot-sheet th, .rapot-sheet td { padding: 1px 8px 3px 6px }` (and
`text-align:center`) OVERRIDES any `padding-left`/`text-align` set on `.st-left`/`.st-right`/`.st-*`
cells — even with `!important` when the target selector is less specific. Symptom: owner asks to
"geser kolom identitas kanan (No.Tamrin/Bagian) biar sejajar kolom kutubu dirosah" and
`.st-right { padding-left: Npx !important }` does NOTHING visible.

**Fix:** shift the INNER table via `margin-left`, not the td padding:
`.student-table .st-right > table { margin-left: 65px !important }`. margin-left on the nested table
cannot be clobbered by the td padding rule.

General rule: to move/align an identity sub-block, act on `.student-table .st-* > table` (margin),
not on the `td` (padding). Owner-accepted value for the right identity column = **65px** (guessed
60→130→220 first and overshot; owner eyeballs the pixel value because Chromium auto-render OOMs on the
2GB VPS — expect 2-4 iterations, ask "kurang dikit / kejauhan" each round to converge fast).

## Raport identity + Al-Bayan display rules

- **Kelas field = `<kelas_nama> <tingkatan_nama>`** e.g. "1 Tsanawiyah" / "3 Aliyah". Backend
  `GetLaporanRaport` already returns `kelas_nama` + `tingkatan_nama` separately; concat in rapot.js
  `renderSheet` (decodeEntities both). Owner wants tingkatan appended after the kelas number.
- **All mapel of the year show in BOTH semesters.** The `aktif_kuartal` filter in the raport display
  query (laporan.go) was disabled via `OR TRUE` (kept `$4/$5` params so placeholders stay valid).
  Mapel taught only 1 kuartal / 1 semester still appear; khos/am cells render `-` in the non-taught
  semester (`fmtNilai(khos) || '-'` in rapot.js). Mapel spread in DB: most `[1,2,3,4]`, plus `[4]`,
  `[3,4]`, `[1,2]`, `[1,2,3]`.
- **Al-Bayan رديء (rodli', ≤5) prints as المثبت (Musbat) on the RAPORT CETAK ONLY.** Data + Penilaian
  menu keep `الرديء` unchanged — transform is display-only in rapot.js sem-2 block:
  `if (decodeEntities(bayan).includes('الرديء')) bayanLabel='المثبت'`, still red. Owner rule: "rodli'
  sudah dipastikan musbat".

## Header (kop) & footer Arab labels need explicit KFGQPC font-family

`.header-text` and its `h2/h3/p` do NOT inherit the Arabic font from the sheet — default falls back to
Times New Roman which lacks proper Arabic glyphs. Any Arab header text (كشف الدرجات, semester title,
nama madrasah, tahun) must get `font-family: 'KFGQPC Uthman Taha Naskh','Amiri',serif` on the rule
itself. Same trap for footer cells بإذن / بغيره: they used `.text-biru` (Times New Roman) → switch to
`td-arab text-biru` to pick up Uthman. Rule: for ANY Arabic text cell on the raport, verify it carries
an Uthman font class or explicit font-family; `.text-biru` / `.text-hijau` / `.ft-tnr` are Times New
Roman and mangle Arabic. Logo↔header gap tuned via `.header-text { margin-left: 90px }` (logo 3cm≈113px;
owner wanted it "mepet").

## Import Santri: partial mode + placeholder-count bug

- `ImportSantriBatch` (models/santri.go) is PARTIAL: commits per row so valid rows land and failed rows
  are skipped and collected in `res.Errors` (baris, nama, alasan). Handler returns `sukses`, `gagal`,
  `errors` with 200 even when some rows fail. Frontend renders a colored table (Baris | Nama | Alasan)
  + a 📋 Salin button (tab-separated to clipboard, with execCommand fallback).
- Bug found while testing: the INSERT had 19 columns but placeholders `$1..$18` with a literal `'aktif'`
  mid-list → "INSERT has more expressions than target columns" made import ALWAYS fail. Fixed to
  `$1..$17` + `'aktif'`. When touching this INSERT, re-count columns vs placeholders.

## Assign santri manual → langsung masuk kelas

Frontend `santri.js` add-form must send `bagian_awal_id` inside the POST `/api/santri` body. Backend
`CreateSantri(ctx, s, bagianAwalID)` already sets `bagian_id` + inserts `riwayat_bagian` in ONE
transaction. The old code sent no `bagian_awal_id` then did a SECOND call to
`/api/perpindahan/naik-kelas` which left santri stuck in "belum di kelas". Removed the second call.

## Absensi Pengajar Kuartal (replaces monthly S/I/T)

Table `absensi_pengajar_kuartal` (pengajar_id, tahun_ajaran, kuartal_1, kuartal_23, kuartal_4 INT
default 0). Endpoint `/api/absensi-pengajar-kuartal` GET (filter tingkatan_id/kelas_id/tahun_ajaran,
LEFT JOIN so teachers with no record still show) + POST (batch upsert). Input & Rekap tabs both use it;
input cells blank before a record exists (`id>0` check, not literal 0). Old `absensi_manual_pengajar_bulanan`
dropped by migration 049.
