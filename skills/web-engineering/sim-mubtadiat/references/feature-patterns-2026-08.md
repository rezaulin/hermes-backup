# Feature patterns (2026-08 session batch)

Domain-feature learnings from the absensi-kuartal / raport / import / assign work.
Consult before touching those areas.

## Grid "seluruh bulan TA" — ONE month-range source

Absensi Manual, Rekap Absensi, and Detail-Santri Riwayat all show a per-month
grid. They MUST derive the month list from the SAME source: kalender akademik
`kalender_semester_hijri` (table name — NOT `hijri_semester`), walked inclusively
from `{mulai_bulan_hijri, mulai_tahun_hijri}` → `{selesai_bulan_hijri,
selesai_tahun_hijri}` (helper pattern `buildBulanListTA`).

Fetch: `GET /api/kalender/hijri-semester?tahun_ajaran=...` → array of semesters,
each with mulai_*/selesai_* Hijri fields.

**PITFALL (Detail-Santri bug, owner: "di rekap malah tertampilkan 2 tahun utuh"):**
an impl that extracts only the *set of tahun_hijri* (e.g. `[1447,1448]`) then
loops all 12 bulan × each year renders **24 bulan (2 tahun utuh)** instead of the
real ~11-month span. Always iterate mulai-bulan → selesai-bulan, not full years.

Empty-month cells in santri absensi grids = **0** (owner pref, not `-`).

Verify span:
```sql
SELECT tahun_ajaran,semester,mulai_bulan_hijri,mulai_tahun_hijri,
       selesai_bulan_hijri,selesai_tahun_hijri FROM kalender_semester_hijri;
-- 2026/2027 = Syawal(10) 1447 → Sya'ban(8) 1448 = 11 bulan
```

## Absensi PENGAJAR = KUARTAL, not monthly S/I/T

Owner redesign 2026-08. Migration 049, table `absensi_pengajar_kuartal`
(cols `kuartal_1 / kuartal_23 / kuartal_4`, INT default 0). Input = 3 free
numeric columns per teacher (K1 | K2&3 | K4). Endpoint
`GET/POST /api/absensi-pengajar-kuartal` (write roles pimpinan/mufatish/muroqib).

GET returns ALL teachers — mustahiq (`mustahiq_bagian`) UNION munawwib
(`pengajar_bagian` peran='munawwib') — LEFT JOINed so teachers without records
still appear. Row with `id=0` = no record yet → render input BLANK (owner:
"sebelum diisi jangan diisi 0, cukup kosongkan"). Old
`absensi_manual_pengajar_bulanan` was dropped. Santri tab still uses monthly S/I/T.

## Assign santri langsung masuk kelas

`models.CreateSantri(ctx, s, bagianAwalID)` already sets `santri.bagian_id` AND
inserts `riwayat_bagian` in ONE tx; handler `RegisterSantri` decodes
`bagian_awal_id` from the POST body.

**PITFALL ("santri nyangkut di belum-dikelas"):** frontend omitted `bagian_awal_id`
from the `/api/santri` payload and fired a SECOND `/api/perpindahan/naik-kelas`
call (unreliable). Fix = include `bagian_awal_id` in the create payload, delete
the second call. Verify:
`SELECT bagian_id,(SELECT count(*) FROM riwayat_bagian WHERE santri_id=s.id) FROM santri s WHERE ...`
→ both non-zero.

## Raport mapel visibility: ALL mapel both semesters

`mata_pelajaran.aktif_kuartal` (jsonb `[4]`, `[1,2]`, `[1,2,3,4]`) governs which
kuartal a mapel is taught. Owner 2026-08: EVERY class mapel must appear in BOTH
Smt 1 & Smt 2 raport, empty (`-`) in the semester it isn't taught. The raport
query in `laporan.go` filtered `aktif_kuartal @> q1 OR @> q2` → Q4-only mapel
vanished from Smt 1. Fix = neutralize the filter (`... OR TRUE`, keep $4/$5
placeholders valid). khos/am are LEFT JOINed so untaught cells are NULL → render
`fmtNilai(khos) || '-'`.

## Al-Bayan رديء → المثبت in RAPORT CETAK ONLY

Owner: "rodli' sudah dipastikan musbat". DB (`nilai_bayan.label_arab`/
`nilai_label`) and the Penilaian menu STAY الرديء. Only `rapot.js` transforms for
print: `if (decodeEntities(bayanLabel).includes('الرديء')) bayanLabel = 'المثبت'`,
keep red. Al-Bayan box + Mudir signature render sem-2 only.
Label scale (penilaian_final.go GenerateAlBayan): 9=الجيد الأول, 8=الجيد الثاني,
7=المتوسط الأول, 6=المتوسط الثاني, ≤5=الرديء.

## Excel/batch import: PARTIAL mode + per-row report

`ImportSantriBatch` commits PER ROW (own tx each) — valid rows land, bad rows
skipped and collected in `res.Errors[]{Baris,Nama,Pesan}`; handler returns
`sukses/gagal/errors` with HTTP 200 even when some fail (NOT all-or-nothing).
Frontend: colored badges + a red `Baris|Nama|Alasan` table + a 📋 Salin button
(tab-separated to clipboard, `execCommand` fallback for blocked clipboard API).

**PITFALL found while testing:** the INSERT had 19 columns but placeholders
`$1..$18` + a literal `'aktif'` in the column list → "INSERT has more expressions
than target columns (SQLSTATE 42601)" made EVERY import fail. When touching a
multi-column INSERT, COUNT columns vs placeholders — a literal in the column list
shifts every subsequent `$n`.

## Mapel bilingual: nama_indo column

Migration 050 adds `mata_pelajaran.nama_indo` (admin-typed via Kelola Mapel form,
`kelas.html`/`kelas.js`). Riwayat Akademik + Penilaian + wali view show `nama_indo`
when set, else FALLBACK to Arabic `nama_kitab` as-is (owner chose "tampilkan arab",
NOT the kitab-translate.js dictionary — dictionary is lossy/incomplete). Riwayat
mapel order MUST match raport: `ORDER BY m.urutan`. Raport cetak header stays
Arabic `nama_kitab`. Handler `handlers/mapel.go` SELECT/INSERT/UPDATE all carry
`nama_indo`.

## Raport header fonts + logo gap

`.header-text` + its h2/h3/p need explicit `font-family: 'KFGQPC Uthman Taha
Naskh'` — sheet default is Times New Roman (no proper Arabic glyphs), so header
Arabic (كشف الدرجات etc.) silently fell back. Same for بإذن/بغيره footer cells:
use class `td-arab` (Uthman), not `.text-biru` (Times New Roman). Logo↔text gap:
`.header-text margin-left` should roughly match logo width (3cm ≈ 113px → 90px
"mepet", 120px too far).

## Mobile-responsive grid tables

Plain `w-full` table with fixed-px columns overflows phone viewport → forces
horizontal scroll (owner: "masih harus geser"). Use `table-fixed` +
`<colgroup>` with %-widths (e.g. name 40%, three number cols 20% each), inputs
`w-full` inside cells, `inputmode="numeric"` for numeric keypad, `break-words`
on the name/text cell.

## Verifying frontend when Chromium render OOMs on the VPS

Playwright/screenshot on the 2GB VPS OOM-loops (exit -9 repeatedly) even with
`--single-process`. When render verification is impossible: verify via SERVED
HTML/DOM instead — `curl -s <url> -o /tmp/x.html` then search_files for the
changed selector/attribute, and `docker exec app grep` the hashed Vite bundle for
a logic fragment. Minification renames vars, so grep for STRING LITERALS
(`mulai_bulan_hijri`, `table-fixed`) not var names. Test-print from the owner's
phone is the final layout authority.
