# SIM Mubtadiat — Academic Domain Model (kuartal / semester / absensi / penilaian)

Discovered by tracing code in `/opt/simmubtadiat`. Update this file when rules change.

## Core structure

```
kalender_kuartal (per tahun_ajaran, unique on (kuartal, tahun_ajaran))
  K1 tgl_mulai → tgl_selesai  ┐
  K2 tgl_mulai → tgl_selesai  ┘ Semester 1
  K3 tgl_mulai → tgl_selesai  ┐
  K4 tgl_mulai → tgl_selesai  ┘ Semester 2
```

- **4 kuartal per tahun ajaran. Semester 1 = K1+K2, Semester 2 = K3+K4.** `SemesterDariKuartal()` in `models/penilaian_lock.go`: kuartal ≤ 2 → semester 1, else 2.
- Kuartal odd (K1/K3) = **Tamrin** (practice/exam-1 phase); kuartal even (K2/K4) = **Ujian**.
- Calendar admin UI (`frontend/src/js/settings.js`): admin enters only the **START date** of each kuartal + year-end date. `tgl_selesai` auto = start of next kuartal − 1 day; last kuartal runs to year-end. Validation: K1 < K2 < K3 < K4 starts; year-end ≥ last kuartal start. Saved via POST /api/kalender (array upsert).

## Date-driven semester binding (the key logic)

Attendance and penilaian never ask "which semester?" — it's derived from the DATE:

1. On attendance input (`InputAbsensiSesi`, models/absensi.go): look up `kalender_kuartal WHERE tahun_ajaran=$ta AND $tanggal BETWEEN tgl_mulai AND tgl_selesai` → get kuartal → `SemesterDariKuartal()` → check `IsSemesterLocked()`; reject if locked.
2. After saving attendance rows, same lookup gets `kuartal_id` → `RecalculateRekapAbsensiTx()` for every santri in the bagian, counting izin/sakit/alpha from `absensi_perizinan` within `[tgl_mulai, tgl_selesai]`, upsert into `rekap_absensi (santri_id, kuartal_id)`.
3. Consequence: **the attendance date alone decides the semester.** If a date falls outside all kuartal ranges → no lock check and no rekap (silent skip). If `kalender_kuartal` is empty, ALL attendance skips rekap binding.
4. Editing kuartal dates retroactively re-buckets historical attendance — pair date changes with a rekap recalc plan.

## Penilaian (grading)

- Mapel has `aktif_kuartal` jsonb int array (default `[1,2,3,4]`; validated 1..4, min 1 in `handlers/mapel.go`).
- Per-semester Khos rules (`models/penilaian_dasar.go` comments are authoritative):
  - Mapel active in BOTH semester kuartals → Khos = (tamrin + ujian) / 2.
  - Active in only the odd kuartal (tamrin) → Khos = tamrin value directly.
  - Active in only the even kuartal (ujian) → Khos = ujian value directly.
  - If tamrin (K1/K3) empty but active in both → Khos = ujian / 2.
  - If the active kuartal has no scores yet, mapel is NOT calculated (no Khos saved).
- Nilai 'Am (`GenerateNilaiAm`, `models/penilaian_final.go`): per (bagian, mapel, semester); joins `nilai_kuartal` on `kuartal IN (q1,q2)` for that semester; respects `is_edited` overrides and pending Her (`is_her=true, nilai NULL`).
- Nilai dasar = average of Khos across all mapel of both semesters (`WHERE semester IN (1,2)`).
- Attendance rekap feeds penilaian via join `rekap_absensi ra JOIN kalender_kuartal kk ON ra.kuartal_id = kk.id` (semester derived from the kuartal's tahun_ajaran).

## Locking

- `penilaian_status (tahun_ajaran, semester)` — DRAFT → opened → LOCKED. Absensi is enforced against the semester lock of the date's kuartal (see binding above).

## TWO attendance tracks (critical — they bind differently)

The app has **two separate attendance systems** with different date bases and different semester binding:

| | Track 1: Absensi Sesi | Track 2: Absensi Manual Bulanan |
|---|---|---|
| File | `models/absensi.go` | `models/absensi_manual.go` |
| Date basis | **Masehi** (Gregorian date per session) | **Hijri** (tahun_hijri + bulan_hijri 1-12) |
| Granularity | per session (pertemuan 1/2) | totals per santri × month |
| Semester binding | automatic via `kalender_kuartal` date lookup | via `semester` column, month-OVERLAP rule against `kalender_semester_hijri` (since migration 047; migration 046's `hijri_semester_map` was DROPPED); day-15 heuristic replaced with overlap 2026-08; before 046 only tahun_ajaran |
| Feeds | `rekap_absensi` per kuartal (pertemuan counts) | penilaian directly (already in days) |

- Track 2 stores `tahun_ajaran` (from the active year at save time) on every row. Penilaian final (`penilaian_final.go`) sums BOTH tracks per tahun_ajaran for the annual score correction: izin ≥ 15 days → −1, alpha ≥ 5 days → −1 (izin from track 1 converted pertemuan→hari first).

## Absence-based score corrections — owner-confirmed rules (updated 2026-08 to MULTIPLIERS, verified live)

Owner confirmed these thresholds are the intended rules, and on 2026-08-23 changed from single-threshold to **MULTIPLIER** corrections ("1.ya bener 2.ya benar 3.ya"): every full multiple of the threshold = −1, floor(hari/ambang). Example: izin 55 hari/year → floor(55/15) = **−3** on Al-Bayan (previously only −1 regardless of amount).

| | Akhlaq (per semester) | Al-Bayan (annual) |
|---|---|---|
| Target | only mapel with kategori `akhlaq_perilaku`; other mapel NEVER touched. **PREREQUISITE: mapel must actually HAVE this kategori in DB** — prod shipped with all أخلاق mapel as `umum`, so the code ran but nothing was ever corrected. Owner (2026-08, option A): only mapel named **الأخلاق** = `akhlaq_perilaku`; **علم الأخلاق** (kitab) stays `umum`. Update with `ILIKE '%أخلاق%' AND NOT ILIKE '%علم%'` — exact-match `= 'الأخلاق'` misses Unicode variants (LENGTH 7 vs 8, hamza forms look identical) and only hit 4/10 rows | rata-rata ALL Khos, semesters 1+2, rounded |
| Izin | **floor(hari/20) per semester** → −1 per 20 days | **floor(hari/15) per year** → −1 per 15 days |
| Alpha | **floor(hari/6) per semester** | **floor(hari/5) per year** |
| Sakit | never counted | never counted |
| Stacking | izin & alpha corrections INDEPENDENT, both multiplier — can stack beyond −2 now (e.g. izin 55 + alpha 12 = −3 + −2) | same |
| Clamp | 4–9 | **NO LOWER BOUND** (owner decision 2026-08-23, picked "tanpa batas bawah" over floor 4/3/2): multiplier corrections apply in full — values CAN go below 5, even negative. Only the TOP is clamped (max 9). Labels are range-based now: ≥9=الجيد الأول, ≥8=الجيد الثاني, ≥7=المتوسط الأول, ≥6=المتوسط الثاني, **EVERYTHING ≤5=الرديء — WITH hamzah (owner correction: NOT الردي)**. Max 9 = Jayyid Awal; Mumtaz/الممتاز does not exist. Manual-input validation (`BulkInputNilaiBayan`) widened 5–9 → 0–9 to match |
| Code | `GenerateNilaiKhos` (models/penilaian_dasar.go) — `koreksiAkhlaq -= izinHari/20`, `-= alphaHari/6` | `GenerateAlBayan` (models/penilaian_final.go) — `koreksi -= izinHari/15`, `-= alphaHari/5` |
| Frontend mirror | `potonganAbsensi(hari, ambang)` in frontend/src/js/penilaian.js — used by `alasanAbsensi` (tooltip/warning text) AND the Bayan section koreksi calc; keep BOTH in sync with backend thresholds | same. Frontend hasilAkhir calc was `Math.max(5, Math.min(9, …))` — after removing the backend floor it must become `Math.min(9, …)` too, and the label map `bayanLabels` became a function `bayanLabel(v) => bayanLabels[v] || "RODI'"` so values outside 9..6 still get a label (owner's UI still shows the transliteration RODI' for ≤5) |
| Triggers | automatic in `penilaian_lock.go` finalization (all santri per semester; Bayan only after semester 2) + manual via POST /api/penilaian/generate-khos & /generate-bayan from spreadsheet save | same |

**Case study (the bug that exposed it, 2026-08):** Ainun (santri 116), izin 55 days (30 sem1 + 25 sem2) but Bayan only dropped 1 (9→8). Root cause: `if izinHari >= 15 { koreksi-- }` — single decrement. Fixed to floor-division multipliers in both backend files + frontend. After fixing, ALWAYS regen (stored values are snapshots — see "Recalculating stored scores" below).

**Case study 2 (clamp + hamzah, 2026-08-23):** Ahla (alpha 25/year) should drop 5 (9→4) but landed on 5 — the `if finalScore < 5 { finalScore = 5 }` clamp silently swallowed the multiplier. Owner verified the full expectation table by hand before approving (Ainun: akhlaq smt1 8→7 izin30, smt2 8→7 izin25, bayan 9→6 izin55; Ahla: akhlaq smt1 8→6 alpha15, smt2 8→7 alpha10, bayan 9→4 alpha25) — when the owner reports one santri's numbers, expect them to have hand-computed the WHOLE cohort; spot-check ALL their cases in the DB before claiming the fix works. Owner also chose NO lower bound over a floor, and the label الردي must be written **الرديء** (hamza) — Arabic label corrections come from the owner and are authoritative; grep every occurrence (`models/penilaian_final.go` auto path, `models/penilaian_dasar.go` manual path, frontend label map, test expectations) because labels are duplicated across backend auto + manual-input code.

Unit conversion: track-1 `rekap_absensi` stores PERTEMUAN; `PertemuanKeHari(p) = (p+1)/2` (2 pertemuan = 1 day, round up). Track-2 manual rows already in days. Sum BOTH tracks first, convert once at semester/year level, THEN apply thresholds.

RESOLVED (2026-08): the old frontend-max-9 vs backend-max-10 mismatch is fixed. Then SUPERSEDED 2026-08-23: `GenerateAlBayan` and `BulkInputNilaiBayan` now have NO lower bound (top clamp 9 only); manual input validates 0–9; no Mumtaz case anywhere. grep confirms zero `الممتاز` references in active code. Verified live via the runtime-verifier: all-high scores clamp to 9 = الجيد الأول. DB has no CHECK constraint, existing data maxes at 9, so no migration was needed for either change.

Al-Bayan UI (commit 960b9d2, owner request "kolom dikurangi"): `renderBayanSection` in frontend/src/js/penilaian.js renders 3 content columns — **Al-Bayan Asli | Keterangan | Al-Bayan Akhir** (old Izin/Alpha/Keterangan-Asli/Keterangan-Akhir columns removed). Keterangan shows the reduction reason verbatim — `Dikurangi 1 (izin 20 hari)`, `Dikurangi 2 (izin 16 hari + alpha 5 hari)` (red text), `Tidak ada pengurangan`, or `Override manual` — and the Jayyid label moved to a `title` tooltip on the nilai-akhir input. `dirtyBayan` tracking preserves manual overrides on save.

## Penilaian UI rules — low-score marking & input caps (owner-confirmed 2026-08, commit 0755867)

Feature arrived as "Kita diskusi dulu" → audit current state → present options + 3 targeted questions → owner answered by number ("1. Batas qur'an tetep / 2. diangka dan siswinya / 3. oke") → implement. Keep this flow for future UI custom requests (see SKILL.md Workflow step 2).

**1. Low-score red marking — TWO thresholds (final form 2026-08-23, commit 6879aa1, owner correction "di menu penilaian nilai tamrin nilai semester nilai raport yang merah mulai nilai 4, sedangkan di Al-Bayan nilai merah mulai nilai 5"):**
- **Al-Bayan section: red for ≤ 5** (`v <= NILAI_RENDAH_AMBANG` — 5 is the RODI zone). **Tamrin (kuartal) / semester / raport (khos) inputs: red for ≤ 4** (`v <= 4`; 4.5 is NOT red — "mulai nilai 4" means 4 ke bawah). Implementation in `refreshRendahMarks()`: `const isBayan = inp.hasAttribute('data-bayan-cell'); const low = isBayan ? v <= NILAI_RENDAH_AMBANG : v <= 4;` — keep this dual-threshold when refactoring.
- **THE PITFALL that caused the wrong first version (commit 5264e8e):** Bayan detection used `inp.hasAttribute('data-nilai-display')` — but `data-nilai-display` is attached to EVERY value-display cell (khos + kuartal readonly included, see renderRaportSection), so all khos inputs wrongly inherited the Bayan ≤5 rule and khos values of 5 lit up red. Owner caught it ("kesalahpahaman di penilaian bos"). **Never use a shared display attribute as a section discriminator.** The fix added a dedicated `data-bayan-cell` attribute on BOTH Bayan render branches (the disabled/readonly branch has NO `data-bayan`, so keying off `data-bayan` alone misses the readonly cell). Attribute map: kuartal=`data-k`, khos readonly=`data-nilai-display`, khos editable=`data-khos-sem`+`data-nilai-display`, Bayan readonly=`data-bayan-cell`, Bayan editable=`data-bayan`+`data-bayan-cell`.

**RODI-zone red is CROSS-PAGE — every page that shows Al-Bayan must mark it red (owner request "ya" 2026-08-23, commit 481b3dc).** Three display surfaces, two shapes of data:
| Page | Shows | Red rule | Implementation |
|---|---|---|---|
| Penilaian (spreadsheet) | numeric score | value ≤ 5 | `.nilai-rendah`/`.nama-rendah` classes via `refreshRendahMarks()` (penilaian.js) |
| Raport print (sem 2 only) | Arabic label | label contains الرديء | `bayanTd.style.color = decodeEntities(label).includes('الرديء') ? '#dc2626' : ''` on `[data-field="bayan-value"]` (rapot.js — inline style, not a class, because print CSS owns that sheet) |
| Profil santri (riwayat) | Arabic label | label contains الرديء | conditional Tailwind `text-red-600 dark:text-red-400` on the Al-Bayan div (profil_santri.js) |
Rules differ by data shape: numeric surfaces test ≤5; label surfaces test `.includes('الرديء')`. When adding ANY new Al-Bayan display surface, add its red rule too — grep `grep -rn "bayan" frontend/src/js/` to find them all. Rekap page does NOT display Al-Bayan (checked 2026-08-23). Note the backend sends the LABEL string (nilai_label/label_arab) for raport & riwayat APIs but the NUMBER for the spreadsheet.

- Style: number red + light-red cell background, AND the student's NAME cell turns red while any value in the row is below threshold. Returns to normal live the moment a value is raised past the threshold (input event — no save/reload).
- Scope: kuartal tables (Tamrin/Ujian K1–K4), Raport Semester 1&2 (both editable khos inputs and read-only display inputs), Al-Bayan Akhir inputs. **Read-only Al-Bayan display cells are marked too** — the readonly branch carries `data-bayan-cell` (the 2026-08-23 fix moved from the overloaded `data-nilai-display` to this dedicated attribute — before that the disabled input was either never marked or wrongly swept into khos rules). The editable Bayan input is `min="0" max="9"` since the no-floor change (was `min="5"`).
- Mechanism (frontend/src/js/penilaian.js): `NILAI_RENDAH_AMBANG = 5`; rows tagged `data-mark-row`, name cells `data-nama`; khos/kuartal display cells tagged `data-nilai-display` (including disabled ones), BOTH Bayan branches tagged `data-bayan-cell` (editable one also `data-bayan` for save-tracking). `refreshRendahMarks()` walks all `tr[data-mark-row]` and toggles `.nilai-rendah` on inputs / `.nama-rendah` on the name cell; called once at render end and again on every khos/bayan input event. CSS lives in `frontend/style.css` as plain classes (`.nilai-rendah`, `.nama-rendah`, dark variants) — they are toggled imperatively via classList, do NOT replace with Tailwind utilities. **CSS location pitfall (hit 2026-08-23): there are TWO style.css files — `frontend/style.css` (repo root) is the real one carrying these classes (every page links it via `<link href="./style.css">`); `frontend/src/style.css` is the Vite-imported one that does NOT have them. Grepping `frontend/src/style.css` for `.nilai-rendah` returns 0 and produces false "CSS missing" conclusions — always grep `frontend/style.css` (root).**
- **Verifying a minified deployed bundle:** `grep -c pattern` counts LINES, and minified JS is one line — use `grep -o pattern | wc -l` for occurrence counts. Also minification renames constants (grep for `NILAI_RENDAH_AMBANG` in the bundle returns 0); grep for stable string/attribute fragments instead (e.g. `hasAttribute("data-nilai-display")` or the logic shape `?r<=U:r<U`).

**2. Input caps with real-time clamp:**
- Kuartal: umum max 10, Quran & Akhlaq max 8 (owner confirmed Quran stays 8). Frontend `maxNilaiKuartalMapel(m)` MIRRORS backend `maxNilaiKuartal(kategori)` in models/penilaian_dasar.go — if the backend caps ever change, update both.
- Input `max` attribute is dynamic per mapel; `clampNilaiInput(inp)` on the input event snaps out-of-range values back to the bound and flashes `.flash-batas` (red outline) for 600ms.
- The Excel-paste handler (container-level 'paste' listener) sets `inp.value` then dispatches `new Event('input')` — so clamp + Jml/Rata² recalc + red marking all fire on pasted cells. PASTE BYPASSES the `max` attribute; never rely on it alone.
- Backend is the second defense: `BulkInputNilaiKuartal` rejects <0, > cap, non-0.5 multiples; `BulkInputNilaiKhos` rejects outside 4–9; bayan inputs 0–9 (was 5–9 until the floor was removed 2026-08-23). The frontend clamp exists so owners never hit those save-time errors.
- **General rule for this app:** any user-editable score input needs backend validation PLUS a frontend real-time clamp wired to both typing AND the paste path.

## Recalculating stored scores after a logic change (audited 2026-08)

Stored `nilai_khos` / `nilai_bayan` rows are SNAPSHOTS — a backend logic fix does NOT retroactively update them. Two regen paths, and **there is no separate "Generate" button in the UI** (owner caught the agent inventing one — never tell the user a button exists without grepping the HTML/JS first):
- **UI path**: Penilaian spreadsheet `saveAll()` (frontend/src/js/penilaian.js, "Simpan Semua") sequentially: save kuartal → POST /api/penilaian/generate-khos per santri × semesters 1&2 → apply ONLY user-edited (dirty) khos overrides → generate-am per bagian/semester → generate-bayan per santri → apply only dirty bayan overrides. So "make old stored values conform to new logic" = open Penilaian per bagian → Simpan Semua. Manual overrides survive because they are re-applied AFTER generation.
- **Batch path**: `lockAndGenerate` in models/penilaian_lock.go (semester finalization) regenerates Khos for all active santri and Bayan after semester 2.
- **Batch path outside the app** (owner-approved 2026-08): throwaway `main.go` in `tmp_batch_regen/` calling the REAL model functions (`models.GenerateNilaiKhos` ctx, santriID, semester, ta + `models.GenerateAlBayan`) for every `status='aktif'` santri, wired via `config.DB = pgxpool`.
  **How to RUN it (updated 2026-08-23 — `go run` NO LONGER WORKS):** the deployed app image is `alpine:latest` with no Go toolchain (`docker compose run app ... go run` → `go: not found`), and the host may lack Go too. The working recipe is a dedicated throwaway Docker image — template: `templates/Dockerfile.regen` in this skill:
  ```bash
  cd /opt/simmubtadiat
  docker build -f Dockerfile.regen -t sim-regen:latest .   # golang builder → alpine runner
  source .env && docker run --rm --network simmubtadiat_default \
    -e DB_HOST=db -e DB_PORT=5432 \
    -e DB_USER="${DB_USER:-mubtadiaat}" -e DB_PASS="${DB_PASS:-mubtadiaat_secret}" \
    -e DB_NAME="${DB_NAME:-mubtadiaat_db}" sim-regen:latest
  ```
  Two pitfalls hit this session:
  1. `.dockerignore` has `tmp_*` which EXCLUDES `tmp_batch_regen/` from the build context (`stat /app/tmp_batch_regen: directory not found`). Add a negation line `!tmp_batch_regen` after `tmp_*` (already present as of 2026-08-23 — keep it).
  2. Use `--network simmubtadiat_default` + `DB_HOST=db` (compose service name resolves inside the network). The old DB-IP-inspect dance also works but the compose network is simpler.
  **Manual-override safety check before any batch regen**: grep for an update endpoint (`grep -rn "UPDATE nilai_am\|UpdateNilai" handlers/ models/`) and audit the `is_edited` flag. As of 2026-08-23: `is_edited` is only ever WRITTEN (false) in the nilai_am insert and never read, and there is NO manual score-edit endpoint — all stored values are pure generated output, so batch regen can never clobber a user edit. The real override protection lives in the frontend `saveAll()` path (dirty khos/bayan overrides re-applied AFTER generation). If a manual-edit feature is ever added, re-audit this before running batch regens.
- **Do NOT trust "Khos OK=N, error=0" as proof corrections landed.** A batch can run clean yet apply nothing if the binary is stale (go build cache) or the prerequisite is missing (e.g. no mapel with kategori akhlaq_perilaku yet). ALWAYS spot-check after regen: pick one santri with known attendance, query their actual current-class akhlaq mapel's nilai_khos, and compare against the expected base−correction. When a spot-check disagrees, re-run the SAME batch — a cache-stale run fixed itself on rerun (2026-08: batch showed 8.00, single-santri script showed 6.00, batch rerun then showed 6.00).
- **Verify against the santri's ACTUAL mapel IDs**: a santri who moved classes may have their akhlaq scores under the OLD class's mapel id (e.g. mapel 87 kelas 1, not 104 kelas 3). Querying by a remembered/wrong mapel id returns no rows or the wrong rows and produces false "correction didn't work" conclusions. Resolve the mapel id from `mata_pelajaran WHERE kelas_id=<bagian.kelas_id> AND kategori='akhlaq_perilaku'` first.
- Before recommending regen: audit which rows have attendance data (`GROUP BY` absensi_manual_bulanan where izin/alpha > 0) and flag NULL-semester rows (excluded from per-semester sums, only counted in annual Bayan) plus any manual overrides (they win, by design).

## Hijri academic calendar (kalender_semester_hijri, migration 047 — CURRENT design)

User requirement (iterated): manual (Hijri-based) attendance must bind to a semester, and ALL academic dates entered in Hijri. Design history: migration 046 first added a separate month→semester mapping table (`hijri_semester_map`) + its own UI card; owner then asked to MERGE it with the kuartal calendar into ONE card with Hijri semester ranges. Migration 047 implements that and DROPS `hijri_semester_map` — do not recreate it.

- Table `kalender_semester_hijri (tahun_ajaran, semester)` — Hijri start/end (tgl/bulan/tahun) + nullable `masehi_mulai/selesai` DATE columns. Frontend computes the Gregorian equivalents (Intl islamic-umalqura, WIB) before saving; conversion code + verified test cases live in skill `simmubtadiat-development`, references/hijri-calendar.md.
- On save, `kalender_kuartal` is rebuilt from the Masehi spans (each semester halved: tamrin half + ujian half), so the legacy absensi-sesi lock/rekap path keeps working unchanged.
- Absensi manual bulanan (santri & pengajar): nullable `semester` column, resolved at save via `SemesterDariBulanHijri()` (models/hijri_semester.go) — a month belongs to a semester when it OVERLAPS the semester range (ordinal compare `tahun*360 + bulan*30 + tanggal`, month start..end vs semester start..end). The earlier day-15 heuristic was buggy: any month containing the semester start mid-month (e.g. Smt 1 starts 17 Syawal) was rejected because day 15 < day 17. Deterministic backfill (MAX + LEFT JOIN) of both manual tables runs on EVERY calendar save.
- UI: Settings → single card "Kalender Akademik & Tahun Ajaran": Tahun Ajaran + Tahun Hijri aktif + Mulai/Selesai Smt 1 + Mulai/Selesai Smt 2, all Hijri inputs. API: `GET/POST /api/kalender/hijri-semester` (POST pimpinan/admin only).

## Forcing stray manual-attendance rows into the configured year (owner request, 2026-08)

Owner phrasing: "paksa data yang masih nyasar biar masuk ke tahun ajaran yang benar". Stray rows = `absensi_manual_bulanan` rows with NULL semester after the calendar exists. Two distinct causes — diagnose FIRST with:

```sql
SELECT am.santri_id, s.nama, t.nama AS tingkatan, k.nama AS kelas,
       am.bulan_hijri || '/' || am.tahun_hijri AS bulan,
       am.total_izin, am.total_alpha, am.total_sakit
FROM absensi_manual_bulanan am JOIN santri s ON s.id=am.santri_id
LEFT JOIN bagian b ON b.id=s.bagian_id LEFT JOIN kelas k ON k.id=b.kelas_id
LEFT JOIN tingkatan t ON t.id=b.tingkatan_id
WHERE am.tahun_ajaran='<TA>' AND am.semester IS NULL ORDER BY t.nama, k.nama, s.nama;
```

- **Cause A — mapping bug / mid-month semester start:** the month IS inside the TA range but unmapped (classic: the first month, when Semester 1 starts day 17). Fixed by the overlap-backfill itself; no data edit needed.
- **Cause B — Hijri-year typo at input time:** month number belongs to the year BEFORE the TA starts (e.g. Muharram/Rabiul Awal/Jumadil Akhir **1447** with TA starting 17 Syawal 1447 — those months are ~9 months earlier). The owner's intent is the SAME month in the second year (**1448**). Owner explicitly wants these force-shifted, not left in the annual-only bucket.

Recipe (applied safely on 2026-08):

1. **Backup first:** `CREATE TABLE backup_absensi_manual_<date> AS SELECT * FROM absensi_manual_bulanan;` (+ pengajar twin).
2. **Resolve unique-constraint collisions before shifting years:** both tables have `UNIQUE (santri_id|pengajar_id, tahun_hijri, bulan_hijri)`. Check `SELECT santri_id, bulan_hijri FROM ... WHERE tahun_hijri=<target_year>` — if a row already exists at the target, MERGE (SUM the four totals into the target row) then DELETE the source row; otherwise a plain UPDATE hits the unique key.
3. **Shift years:** `UPDATE absensi_manual_bulanan SET tahun_hijri=<target> WHERE tahun_ajaran='<TA>' AND tahun_hijri=<wrong> AND bulan_hijri IN (...)` — guarded with `NOT EXISTS` against the target.
4. **Re-run overlap backfill** (same SQL the app runs on calendar save):
   ```sql
   UPDATE absensi_manual_bulanan am SET semester = v.sem FROM (
     SELECT am2.id, MAX(CASE WHEN (am2.tahun_hijri*360 + am2.bulan_hijri*30 + 1)
            <= (ks.selesai_tahun_hijri*360 + ks.selesai_bulan_hijri*30 + ks.selesai_tanggal)
            AND (am2.tahun_hijri*360 + am2.bulan_hijri*30 + 30)
            >= (ks.mulai_tahun_hijri*360 + ks.mulai_bulan_hijri*30 + ks.mulai_tanggal)
            THEN ks.semester END) AS sem
     FROM absensi_manual_bulanan am2
     LEFT JOIN kalender_semester_hijri ks ON ks.tahun_ajaran = am2.tahun_ajaran
     GROUP BY am2.id) v WHERE am.id = v.id;
   ```
   Repeat for `absensi_manual_pengajar_bulanan` (same columns; pengajar rows carry semester too).
5. **Verify zero NULLs left:** `SELECT COUNT(*) FILTER (WHERE semester IS NULL) FROM absensi_manual_bulanan;` and report the per-semester/per-class distribution. Remind the owner that stored nilai_khos/nilai_bayan snapshots still need a regen (Penilaian → Simpan Semua per bagian) to reflect the corrected absensi.

Do NOT apply this to months that genuinely predate the school (e.g. the santri just enrolled) — ask the owner when ambiguous; when the same month exists one Hijri year later, the typo reading is almost always correct.

## Stale & duplicate scores after pindah bagian / naik kelas (audited 2026-08)

Santri who change bagian or move up a class leave a trail of orphaned score rows. This masquerades as "corrections don't work" / "nilai hilang" — always audit for it before blaming the correction logic.

Two distinct corruptions:

1. **Duplicate `nilai_bayan`** — RESOLVED structurally by **migration 048** (2026-08): unique key is now `UNIQUE (santri_id, tahun_ajaran)` (constraint `nilai_bayan_santri_tahun_unique`). The migration dedupes first (keeps highest id per santri+TA), then adds the constraint. Both bayan upserts (penilaian_dasar.go `BulkInputNilaiBayan`, penilaian_final.go `GenerateAlBayan`) conflict on `(santri_id, tahun_ajaran)`. `bagian_id` is still stored/updated but no longer part of uniqueness — a santri moving bagian just updates the existing row. If you ever need the old diagnostic query (find duplicates), it is now expected to return zero rows.

2. **Stale `nilai_khos` / `nilai_kuartal` bound to the OLD class's mapel** — mapel are keyed by `(kelas_id, tingkatan_id)`. Scores entered while the santri was in the old class stay linked to old-class mapel IDs; `GenerateNilaiKhos` reads the CURRENT class's mapel (which have no scores) → Khos comes out empty/wrong and Akhlaq corrections appear to do nothing. 2026-08 scale: 18/25 santri had stale khos (540 rows); 38/51 had kuartal scores for the wrong class (1322/1852 rows).
   ```sql
   -- detect: score rows whose mapel's class != santri's current class
   SELECT COUNT(DISTINCT nk.santri_id) santri, COUNT(*) rows
   FROM nilai_khos nk JOIN santri s ON s.id=nk.santri_id JOIN bagian b ON b.id=s.bagian_id
   JOIN mata_pelajaran mp ON mp.id=nk.mapel_id
   WHERE nk.tahun_ajaran='<TA>' AND (mp.kelas_id<>b.kelas_id OR mp.tingkatan_id<>b.tingkatan_id);
   -- (same query on nilai_kuartal for the deeper problem)
   ```
   Clean-slate regen recipe: backup (`CREATE TABLE backup_nilai_khos_bayan_<date> AS SELECT ...`), `DELETE FROM nilai_khos/nilai_bayan WHERE tahun_ajaran='<TA>'`, then re-run the batch verifier-style regen (`GenerateNilaiKhos` smt 1&2 + `GenerateAlBayan` for every active santri — working example `/opt/simmubtadiat/tmp_batch_regen/main.go`, run like the runtime-verifier).

RESOLVED (owner decision 2026-08, option A): **"nilai tetap di kelas lama"** — raw kuartal marks STAY bound to the old-class mapel, never relinked. Instead, the READERS were widened: `GenerateNilaiKhos` (models/penilaian_dasar.go) and the raport query (models/laporan.go) now select the current-class mapel **PLUS** any mapel where the santri has nilai_kuartal in the running TA:

```sql
WHERE ((m.kelas_id = b.kelas_id AND m.tingkatan_id = b.tingkatan_id)
       OR EXISTS (SELECT 1 FROM nilai_kuartal nk2
                  WHERE nk2.mapel_id = m.id AND nk2.santri_id = $santri AND nk2.tahun_ajaran = $ta))
```

This makes old-class scores visible again (Khos regenerates, Akhlaq corrections land) without moving any data. If the owner ever chooses option B (marks follow the santri), relink `nilai_kuartal.mapel_id` to the matching new-class mapel and drop this clause.

**Dedupe evolution for duplicate-input santri (owner decision, 2026-08)** — three iterations, keep only the FINAL rule:

1. **Option A alone (widen clause)** surfaced two rows of the same-named mapel (e.g. الأخلاق kelas 1 AND kelas 3) for the ~8 santri who have nilai_kuartal in TWO classes for ALL kuartals — genuine duplicate input, not a mid-year move.
2. **Option-2 dedupe v1 (FAILED, commit 0b2dfc5):** hide the old-class mapel only when the santri has scores for a SAME-NAMED mapel in the current class. Broken because Arabic mapel names are not stable keys — `التاريخ` exists in 7- and 8-char variants, `علم الصرف` in 3 variants (9/9/10 chars), `علم  النحو` has a double space where `علم النحو` has one. Old-class rows without a name-exact twin leaked through into Khos AND into the Bayan Asli average. Symptom: 4 santri (MAGFIROH/MAHYA ZAKIA/NASYWA/RIA RIFATUL) showed Bayan Asli **8 when it should be 9** — their current-class average alone is 8.87–8.91 (rounds to 9), but 10–12 leaked old-class rows averaging 8.6–8.85 pulled the all-rows average to 8.4 (rounds to 8).
3. **FINAL rule:** old-class mapel count ONLY when the santri has NO nilai_kuartal anywhere in their current class:
   ```sql
   WHERE ((m.kelas_id = b.kelas_id AND m.tingkatan_id = b.tingkatan_id)
          OR (NOT EXISTS (SELECT 1 FROM nilai_kuartal nk4
                          JOIN mata_pelajaran m4 ON m4.id = nk4.mapel_id
                          WHERE nk4.santri_id = $santri AND nk4.tahun_ajaran = $ta
                            AND m4.kelas_id = b.kelas_id AND m4.tingkatan_id = b.tingkatan_id)
              AND EXISTS (SELECT 1 FROM nilai_kuartal nk2
                          WHERE nk2.mapel_id = m.id AND nk2.santri_id = $santri AND nk2.tahun_ajaran = $ta)))
   ```
   Implemented in `GenerateNilaiKhos` mapel query + its opening cleanup DELETE (models/penilaian_dasar.go) and the raport query (models/laporan.go). Genuine-moved santri with scores ONLY in the old class (e.g. AINI) keep showing them. Audit for duplicate-class input: `SELECT nk.santri_id, COUNT(DISTINCT mp.kelas_id), STRING_AGG(DISTINCT mp.kelas_id::text, ',') FROM nilai_kuartal nk JOIN mata_pelajaran mp ON mp.id=nk.mapel_id WHERE nk.tahun_ajaran='<TA>' GROUP BY nk.santri_id HAVING COUNT(DISTINCT mp.kelas_id)>1;`

**Bayan Asli diagnostic** ("harusnya 9 tapi tertulis 8"-style reports): compare two averages per santri — all khos rows vs current-class-only khos:
```sql
-- all-rows avg vs current-class avg (run for suspect santri IDs)
SELECT nk.santri_id, ROUND(AVG(nk.nilai_akhir),3) AS rata_semua, COUNT(*) n
FROM nilai_khos nk WHERE nk.santri_id=ANY($ids) AND nk.tahun_ajaran='<TA>' AND nk.semester IN(1,2)
GROUP BY nk.santri_id;
-- then add JOIN mata_pelajaran mp ON mp.id=nk.mapel_id AND mp.kelas_id=<bagian.kelas_id> AND mp.tingkatan_id=<bagian.tingkatan_id>
```
`FLOOR(avg+0.5)` per variant = the expected Bayan Asli. If they differ, old-class rows are polluting the average (or the frontend/backend disagree on which rows they average). Note: the frontend computes Al-Bayan Asli itself in renderBayanSection from whatever khos keys the spreadsheet API returns (it does NOT read nilai_bayan for that column), so fixing the backend khos rows fixes both UI and stored bayan after a regen — but they must agree on row membership.

LESSON (cost real data, 2026-08): before ANY clean-slate `DELETE FROM nilai_khos/nilai_bayan` + regen, verify the generator can actually rebuild what you are deleting. The first from-scratch regen rebuilt only 203 of 748 khos rows because the generator (pre-option-A code) only read the santri's CURRENT-class mapel — the rest had to be restored from backup. Rule: backup table first → regen → compare row counts against the backup BEFORE calling it done.

Restore recipe (used to recover that regen; backup = flat rows `src, id, santri_id, ref_id=mapel_id|bagian_id, semester, tahun_ajaran, nilai`):
- khos: `INSERT INTO nilai_khos (santri_id, mapel_id, semester, tahun_ajaran, nilai_akhir, created_at, updated_at) SELECT santri_id::int, ref_id::int, semester::int, tahun_ajaran, nilai::numeric, now(), now() FROM backup_... WHERE src='khos' ON CONFLICT (santri_id, mapel_id, semester, tahun_ajaran) DO NOTHING;`
- bayan: insert ONLY rows whose `ref_id::int` equals the santri's CURRENT bagian_id (`AND ref_id::int = (SELECT bagian_id FROM santri s WHERE s.id = santri_id::int)`) so duplicates aren't recreated; derive label_arab AND nilai_label from the number (≥9=الجيد الأول, ≥8=الجيد الثاني, ≥7=المتوسط الأول, ≥6=المتوسط الثاني, ≤5=الرديء WITH hamzah). Column-count gotcha: nilai_bayan takes BOTH label_arab and nilai_label plus kategori_id — first restore attempt failed on expression count.

## Penilaian consumption points — per-semester vs annual (audited 2026-08)

LESSON: when a new dimension column lands on a fact table (here: `semester` on absensi_manual_bulanan), audit EVERY query that SUMs the table and decide per-consumer granularity. Don't assume all sums want the filter — and don't assume none do.

| Consumption point | File | Granularity | Filter |
|---|---|---|---|
| Raport (izin/alpha display) | models/laporan.go | PER SEMESTER | `AND semester = $N` |
| Khos akhlaq correction (izin ≥20, alpha ≥6 /semester) | models/penilaian_dasar.go | PER SEMESTER | `AND semester = $N` |
| Al-Bayan annual correction (izin ≥15, alpha ≥5 /year) | models/penilaian_final.go | ANNUAL by design | tahun_ajaran only |
| Penilaian spreadsheet | models/penilaian_spreadsheet.go | PER SEMESTER + annual Bayan aggregate | `GROUP BY semester`; rekap split via `kuartal IN (1,2)` vs `(3,4)` |
| Admin rekap view | models/rekap.go | per month/year filters | no semester filter needed |

Note: manual-attendance rows with NULL semester are EXCLUDED from per-semester sums until a calendar save backfills them. If a raport "misses" manual attendance, first check the calendar was saved for that tahun_ajaran.

LESSON (spreadsheet display bug, 2026-08): user reported an izin appearing in BOTH Raport Semester 1 AND Semester 2 sections. Root cause: `GetPenilaianSpreadsheet` returned ONE annual attendance map and the frontend (`penilaian.js` renderRaportSection) rendered that same map into both semester sections. Fix shape — backend returns `absensi` as `{"1": {...}, "2": {...}}` (per-semester maps, keyed by santri_id) PLUS `absensi_bayan` (annual aggregate for the Al-Bayan section, which stays annual by design); frontend passes `absensi['1']` / `absensi['2']` to each section and `absensi_bayan` to Bayan. General rule: when the same number shows in multiple UI sections, check whether one aggregate map is being rendered N times before suspecting the data.

School-year shape (owner-confirmed 2026-08): Semester 1 runs Syawal → Rabiul Awal, Semester 2 runs Rabiul Awal/Akhir → Sya'ban — so a tahun ajaran always SPANS TWO Hijri years (e.g. TA 2026/2027 = 1447→1448; Smt 1 start `17 Syawal 1447` → end `29 Rabiul Awal 1448`, Smt 2 `1 Rabiul Akhir 1448` → `4 Sya'ban 1448`). Months like Jumadil Akhir 1447 fall BEFORE the year starts → no semester → only counted in the annual Bayan aggregate.

## Tahun Hijri aktif is a PAIR (owner rule, 2026-08)

Owner: "1 tahun ajaran ada 2 — kayak Masehi 2025/2026, begitu juga Hijriyah 1447/1448". So `tahun_hijri_aktif` in settings is a **pair string** like `1447/1448` (one string value), and no UI should force gonta-ganti tahun settings mid-year — the point is setting it once per tahun ajaran.

Consumers (all frontend/src/js/):
- `absensi-manual.js`: `tahunHijriPair()` parses the pair (fallback: second = first+1). Month dropdowns (santri & pengajar) are built by `populateBulanDropdown()` with one `<optgroup>` per year; option value = `"<tahun>:<bulan>"`, decoded by `parseBulanSel()`. The year RIDES WITH the month choice, so load/save always use the selected month's own year. Never re-introduce a separate tahun picker for the manual attendance grid.
  - **Dropdown content is RANGE-DRIVEN (owner correction, 2026-08):** owner rejected a hardcoded 24-month list — "kan kita udah setting waktu mulai semester dan selesai semester, kenapa dropdown harus 24 bulan?". `loadKalenderRange()` fetches `GET /api/kalender/hijri-semester?tahun_ajaran=<aktif>` at init (BEFORE populating dropdowns — init order matters) and the dropdown only lists months from the earliest semester start month through the latest semester end month inclusive (TA 2026/2027: Syawal 1447 → Sya'ban 1448 = 11 months). Fallback to the full 2-year pair list ONLY when no calendar rows exist for the active tahun ajaran. General rule for this app: any month/period selector must derive its options from the saved calendar range — never offer choices outside the configured academic period.
- `rekap.js`: Hijri filter inputs are `type=number` — prefill only when the setting is a bare number (`/^\d+$/.test(...)`), else leave empty.
- `settings.js`: calendar-form year prefill takes the SECOND year of the pair (the running Hijri year).

PITFALL: any code doing `parseInt(tahun_hijri_aktif)` or binding it to a numeric input must handle the slash first — bare parseInt truncates/NaNs silently.

## Known state pitfall (as of 2026-08)

`kalender_semester_hijri` / `kalender_kuartal` were found EMPTY in production → attendance had never been bound to semesters/recaps. First fix for any "absensi/daftar hadir doesn't show up in semester X" report: check both tables are populated for the active tahun ajaran (`GetTahunAjaranAktif` falls back settings → current-date-in-kalender → latest kalender). Manual attendance rows carry NULL semester until a calendar is saved (backfill runs on save).

## Data-health watchdog (built 2026-08, owner-requested)

After the Bayan-Asli-8-vs-9 saga, owner asked "mungkin gak kedepan ada kasus begini lagi?" and chose an **in-app dashboard notification** over Telegram cron ("gak perlu cronjob ke telegram, cukup ke dashboard pimpinan pemberitahuannya"). Embedded as part of the app, checked every time pimpinan opens the dashboard.

- **Backend**: `GET /api/data-health` (pimpinan/admin via `RequireRoles`), handler `handlers/data_health.go`, model `models/data_health.go` → `GetDataHealthReport(ctx, ta)` returns `{tahun_ajaran, ada_masalah, issues[]}`. 4 checks:
  | kode | level | meaning | panic-fix? |
  |---|---|---|---|
  | `khos_kelas_lama` | bahaya | santri has scores in current class AND stale old-class khos rows | YES — re-run regen |
  | `bayan_kosong` | perhatian | active santri with no nilai_bayan for the TA | **NO** — legitimate when only kuartal 1 filled (Khos needs the ujian kuartal; verify `nilai_kuartal` kuartal coverage first) |
  | `absensi_belum_mapping` | bahaya | manual attendance rows with semester NULL | YES — save calendar to trigger backfill |
  | `nilai_dobel_kelas` | perhatian | nilai_kuartal spanning >1 class | NO — informational; option-A rule already handles it (archive) |
- **Frontend**: `#dash-data-health` in `frontend/index.html` + `loadDataHealth()` in `main.js` (called only for pimpinan/admin roles). Red card = BUTUH TINDAKAN, amber = PERHATIAN, tiny green dot = bersih (silent). Each card shows count + up to 8 sample santri names + description.
- **Adding a check**: add the query to `GetDataHealthReport`, keep the level honest (bahaya = data wrong, perhatian = needs attention), and sample names are capped at `maxSample=8`.
- Endpoint smoke test without login: `curl -s -o /dev/null -w '%{http_code}' https://reviewtechno.me/api/data-health` → 401 means routed correctly. To exercise the checks directly, run the model via a throwaway pgxpool script (same recipe as tmp_batch_regen) — no auth needed.

## Migration checklist when adding constraints/upserts (lessons from 048)

When changing a unique key that code upserts against:
1. Write migration that first **dedupes** violating rows (keep newest: `DELETE ... a USING ... b WHERE a.id < b.id AND <same-key>`), THEN `ADD CONSTRAINT`. Migrations are one-shot — test the dedupe query read-only first.
2. Update EVERY `ON CONFLICT (...)` in Go to the new key (grep `ON CONFLICT (santri_id` etc.) — the app only breaks at runtime, not compile time.
3. `go build -o /tmp/simtest .` then deploy; migration runs on container start. Verify: `SELECT conname FROM pg_constraint WHERE conrelid='<table>'::regclass AND contype='u';`
