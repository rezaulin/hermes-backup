# Batch import, DB verification, view consistency & mapel display (2026-08-27)

## SQL INSERT placeholder-vs-literal mismatch = every row fails silently
Found in `ImportSantriBatch` (models/santri.go). The VALUES list mixed bound `$N`
with a SQL literal `'aktif'`, but placeholder numbering still ran `$1..$18` while
only 17 args were passed → `ERROR: INSERT has more expressions than target columns
(SQLSTATE 42601)` on EVERY row. Import was all-or-nothing, so the whole feature had
been silently dead.

RULE: when a VALUES list mixes bound `$N` and SQL literals (`'aktif'`,
`CURRENT_DATE`, `EXTRACT(...)`), recount — placeholders must run `$1..$K` where
K = number of args passed, and each literal occupies its own column slot WITHOUT
consuming a `$N`. `go build` will NOT catch this; only Postgres does at runtime.
Always exercise a batch INSERT against the real DB after editing it.

## Verifying model funcs against the production DB without a Go toolchain in the app image
The final app image has no Go toolchain. Build a throwaway runner exactly like
`Dockerfile.regen`:
- `golang:alpine` builder compiles `./tmp_test_<x>`, alpine runner runs it.
- Add `!tmp_test_<x>` to `.dockerignore` (blanket `tmp_*` ignore + `!tmp_batch_regen`
  negation already present).
- In the runner call `config.ConnectDB()` (reads DB_* env), then:
  ```
  docker run --rm --network simmubtadiat_default \
    -e DB_HOST=db -e DB_PORT=5432 -e DB_NAME=mubtadiaat_db -e DB_USER=mubtadiaat \
    -e DB_PASS="$(grep DB_PASS .env|cut -d= -f2)" <img>
  ```
- Clean up: `rm -rf tmp_test_<x> Dockerfile.<x>`, `docker rmi`, `git checkout .dockerignore`.
This proved the placeholder fix (Sukses=1 Gagal=2 with per-row reasons).

## Batch-import UX (owner pref): PARTIAL, not all-or-nothing
Owner wants valid rows committed and only non-conforming rows skipped + reported so
they know "data siapa yang tidak sesuai".
- Backend: per-row commit (own tx per row, rollback only that row on error), collect
  `{baris, nama, pesan}`, ALWAYS return 200 with `sukses`/`gagal`/`errors` (never a
  422 that discards everything). `humanizeDBError` maps unique-violation → friendly text.
- Frontend: green "Berhasil: N" + red "Dilewati: M" badges, a red `Baris|Nama|Alasan`
  table, and a **📋 Salin** button copying failures tab-separated (clipboard API +
  `execCommand` textarea fallback) so they paste to Excel, fix, re-upload.

## Attendance month-range must be IDENTICAL across all 3 views
Views: Input Manual, Rekap, Detail Santri (Riwayat Akademik). Bug: Detail Santri took
the Hijri YEARS from the calendar and looped all 12 months × 2 years = 24 rows, while
Input Manual/Rekap iterate the calendar's start-month→end-month
(`mulai_bulan_hijri`→`selesai_bulan_hijri`, e.g. Syawal 1447 → Sya'ban 1448 = 11 months).
Owner: "di input manual sudah sesuai tahun aktif, di rekap malah 2 tahun utuh".

FIX: fetch `/api/kalender/hijri-semester?tahun_ajaran=`, find earliest
`{mulai_thn,mulai_bln}` + latest `{selesai_thn,selesai_bln}` across semesters, walk
month-by-month `while (y*12+m <= end)`. Empty months still render (owner: value **0**
for detail-santri grid, not `-`). NEVER derive the range from "years present in data"
— always from the calendar's start/end months (mirror `buildBulanListTA`).

## Mapel display: Arab vs Indonesia split (migration 050)
`mata_pelajaran` stores `nama_mapel` (fann, Arab) + `nama_kitab` (Arab) + `urutan`;
migration 050 added `nama_indo` (admin-typed Indonesian).
- RAPORT PRINT stays Arab (`nama_kitab`).
- Riwayat Akademik + Penilaian + wali view show `nama_indo`; when empty, fall back to
  **Arab as-is** (owner: "tampilkan arab") — do NOT auto-translate via
  `kitab-translate.js` (lossy kamus, leaks Arab for unmapped kitab; owner rejected it
  as source of truth).
- Riwayat mapel order = `ORDER BY m.urutan` to match the raport.
- Kelola Mapel form (kelas.html/kelas.js) carries the `nama_indo` input; CRUD in
  handlers/mapel.go must SELECT/INSERT/UPDATE the column.

## Absensi pengajar = KUARTAL model (migration 049), NOT monthly S/I/T
Table `absensi_pengajar_kuartal` (pengajar_id, tahun_ajaran, kuartal_1/kuartal_23/
kuartal_4 INT). Old `absensi_manual_pengajar_bulanan` dropped. Input page (Absensi
Manual → tab Pengajar) + Rekap (tab Pengajar) both use
`GET/POST /api/absensi-pengajar-kuartal` filtered by tingkatan/kelas/tahun_ajaran;
teachers with no record still appear (LEFT JOIN, blank not 0 before first save).
PITFALL: migration column names MUST match the Go struct (`kuartal_1`/`kuartal_23`/
`kuartal_4`) — an earlier draft used `nilai_k1` and silently mismatched.

## Rapot header Arabic font + logo gap (owner 2026-08-27)
`.header-text` h2/h3/p (كشف الدرجات, semester, nama madrasah, tahun) AND the
بإذن/بغيره footer cells MUST carry `font-family: 'KFGQPC Uthman Taha Naskh','Amiri',serif`
— `.text-biru` alone is Times New Roman and renders Arab via fallback. For بإذن/بغيره
use `td-arab text-biru` (Uthman + blue). Logo↔text gap tuned via `.header-text
margin-left` (120px too far; 90px mepet for a 3cm logo). Owner wanted header weight
"biasa" (not forced 18pt bold).

## Mobile table fit (owner 2026-08-27)
Attendance grids that "harus geser" on phone → convert from fixed `w-NN` px columns to
`table-fixed` + `<colgroup>` percentage widths, cells `break-words`, inputs `w-full` +
`inputmode="numeric"`. Owner pref: numeric input cells render EMPTY before first save,
not `0`.
