# SIM Mubtadiat — mobile UI patterns, penilaian signal features & search/nav architecture (2026-08)

Owner-driven mobile cleanup session (commit 6be51ad and the penilaian signal commits). These are conventions the owner actively enforces — follow them for ANY new page/feature.

## Mobile table card pattern (table-responsive + data-label)

- `frontend/style.css` (~line 195) defines a `.table-responsive` media-query block: on small screens each `td` renders as a labeled row via `td::before { content: attr(data-label) }` — the table becomes a vertical card list, no horizontal scroll.
- To "match alumni's look" on any list page: add `table-responsive` to the `<table>` class AND add `data-label="..."` to every `<td>` in the JS row template. Reference pages already using it: alumni.html, santri.html, pengajar-purna.html. Applied 2026-08: pengajar.html (daftar pengajar) + catatan.html (pelanggaran/prestasi).
- Gotcha: header `<th>` count must match the cells — catatan.html originally had 3 th but 4 td (the Aksi column); add the missing th when applying the pattern.
- JS renders rows via `createElement('tr')` + innerHTML (pengajar.js renderTable) or `tableBody.innerHTML +=` (catatan.js renderRows) — patch the template strings, then `node --check` the JS.

## Vertical tabs on mobile

- Pattern (applied to profil-santri.html detail tabs): `nav class="-mb-px flex flex-col md:flex-row md:space-x-6"` — stacked on mobile, one row on desktop; buttons get `text-left md:text-center`, `py-3 md:py-4`. Drop the `overflow-x-auto` wrapper when converting. Owner phrasing: "dibuat menurun bukan menyamping".

## Bottom nav per role (BOTTOM_NAV)

- Single source of truth: `BOTTOM_NAV` object in `frontend/src/js/xss.js` (roles: default, admin, keamanan, muroqib, mustahiq). Rendered at runtime by `window.renderBottomNav(role)` after /api/me resolves; the FAB spacer is auto-inserted at index 2 and an existing FAB element is preserved.
- **Edit BOTTOM_NAV, never the per-page static `<nav>` HTML** — that markup is only the initial paint; renderBottomNav rewrites it per role.
- Owner decision (2026-08): muroqib nav cut from 6 items to 3 — Santri, Absen, Pelanggaran. Other menus stay reachable via the sidebar.

## Global search (FAB 🔍 + Ctrl+K)

- Frontend: search modal injected by `frontend/src/js/xss.js` on DOMContentLoaded (if not already inline), wired to `#btn-mobile-search` FAB + `#btn-global-search`; results from `GET /api/search?q=`; badge/link resolution in `searchBadgeFor(item)` (tipe → color/label/href/subtext). tipe `pengajar` opens a modal via `openGlobalDetailPengajar`; everything else links to a page.
- Backend sources in `models/pencarian.go GlobalSearch` (each LIMIT 10):
  1. santri aktif/pengabdian (role-scoped EXISTS for non-global roles)
  2. alumni/arsip — for pimpinan/admin/keamanan: `status NOT IN ('aktif','pengabdian')` — 2026-08 fix: previously hardcoded `IN ('lulus','boyong','keluar')` which MISSED cuti santri; now aligned with GetArsipSantri's "everything non-aktif" semantics
  3. pengajar aktif
  4. pengajar_purna (added 2026-08)
  5. dewan_harian
- Deep-link pattern: search result links to `page.html#<id>`; target page parses `location.hash` AFTER its data loads and auto-opens the detail modal (see `openDetailFromHash()` in pengajar-purna.js). Reuse this for any new searchable entity.
- Smoke test without login: `curl -s -o /dev/null -w '%{http_code}' .../api/search?q=x` → 401 means routed; exercise GlobalSearch via a throwaway pgxpool script (same recipe as tmp_batch_regen).

## Penilaian UI signals (frontend/src/js/penilaian.js + frontend/style.css)

Threshold-driven visual signals, all owner-approved; frontend thresholds MUST stay in sync with backend (penilaian_dasar.go maxNilaiKuartal / GenerateNilaiKhos / GenerateAlBayan):

- **Low-score red = TWO thresholds (owner-confirmed 2026-08-23, commit 6879aa1):** Al-Bayan cells red for **≤ 5**; tamrin/kuartal + semester/raport (khos) cells red for **≤ 4**. Discriminate sections by `data-bayan-cell` (present on both Bayan branches, incl. readonly) — NOT `data-nilai-display` (that's on every display cell and wrongly swept khos into the ≤5 rule — owner correction). Cell gets `.nilai-rendah` (red text + pink bg); the row's name gets `.nama-rendah`. Unmarked live once the value crosses back over the threshold, no save/reload. Helpers: `NILAI_RENDAH_AMBANG = 5`, `refreshRendahMarks()` — call it from any new input wiring; initial call at the end of `renderSpreadsheet()` marks stored values on load.
- **Absence-impact name marks**: red = already cutting a score; amber (`.nama-warning`) = ≥ 75% of threshold ("almost"). Thresholds in `ABSENSI_AMBANG`: per semester izin ≥ 20 / alpha ≥ 6 → Akhlaq −1 (rendered per Raport section with that semester's absensi); per year izin ≥ 15 / alpha ≥ 5 → Bayan −1 (Bayan section). Helpers: `alasanAbsensi(ab, ambang, targetLabel)` → {red[], warn[]} and `markNamaDariAlasan()`. Reasons go into the `title` tooltip; `refreshRendahMarks()` merges absence + low-score reasons into one tooltip.
- **Real-time score clamping**: `clampNilaiInput(inp)` snaps any value past min/max back to the bound + `.flash-batas` flash; `maxNilaiKuartalMapel(m)` mirrors backend maxNilaiKuartal — max 10 umum, max 8 for al_quran/akhlaq/akhlaq_perilaku (owner: "batas qur'an tetep"). Covers typed input AND Excel paste, because the paste handler dispatches an `input` event per cell. Khos clamp 4–9, Bayan 5–9. Backend validators (BulkInputNilaiKuartal/Khos/Bayan) remain the second line of defense — never remove them when touching frontend clamps.
- CSS classes (style.css, dark-mode variants included): `.nilai-rendah`, `.nama-rendah`, `.nama-warning`, `.flash-batas`.

## Canonical attendance grid (Absensi Manual + Rekap, commit 0a8b790, 2026-08)

Owner provided a reference photo and spec: "masukin absensi persantri satu satu rekap juga satu satu tapi tampilan seluruh bulan muncul". Implemented in `absensi-manual.js` + `rekap.js` — do NOT revert to the old one-month-at-a-time picker:

- Layout: rows = ALL Hijri months of the TA (from `buildBulanListTA()`, driven by `kalender_semester_hijri` via `/api/kalender/hijri-semester`; falls back to both years of the Hijri pair when the calendar is unset), columns = **S | I | T**.
- **T = Alpha ("tanpa keterangan"). Hadir/H column is REMOVED** from input and rekap by owner decision; `total_hadir: 0` is still sent in payloads; backend deletes rows where all four totals are 0.
- One santri/pengajar per screen: `◀`/`▶` buttons + index counter; state vars `currentSantriIdx`/`currentPengajarIdx`/`rekapSiswaIdx`; per-person data keyed `"tahun:bulan"` in `santriGridData`/`pengajarGridData`/`rekapSiswaData`.
- "Simpan & Lanjut ▶" saves the visible santri's rows then auto-advances. Load fetches `/api/absensi-manual/santri?bagian_id=&tahun_hijri=` once PER Hijri year in the TA (1 TA spans 2 Hijri years).
- Rekap siswa is the read-only twin: same grid, summary cards without Hadir, reuses the raw manual-absensi endpoint (not the aggregate `/api/rekap/absensi-siswa`).
- Month dropdowns (`sel-bulan-hijri`, `filter-bulan-hijri-siswa`) are `hidden`, not deleted.

## Reference-photo analysis workflow (when owner sends a screenshot/spec)

Vision tool may be unavailable (no provider configured) — OCR via tesseract is the fallback, and it has REAL limits:

1. `tesseract img.jpg out -l ind+eng`, then retry with `--psm 6`/`--psm 11`, grayscale + `ImageOps.autocontrast`/invert + 3–5× upscale via PIL. Read words WITH coordinates via the `tsv` output (`awk -F'\t' ... {print $7,$8,$12}`) to reconstruct layout.
2. OCR reliably reads row text but often CANNOT read header cells with icons/low-contrast text (in the attendance spec, the column-header block returned empty across every preprocessing attempt).
3. So: extract what you can, present your reconstruction back to the owner, and ASK targeted questions for the unreadable parts (e.g. "kolom T itu Alpha? kolom Hadir dihapus?"). Owner tolerated the OCR attempt but pushed back ("Apa ocr mu mati?") when the summary kept asking questions that OCR could have answered — squeeze the OCR harder (crop per-region, upscale more) BEFORE asking the owner.
4. When the image is a PATTERN/ORNAMENT/design asset with no readable text, switch to PIL pixel analysis: size/mode, dominant colors (Counter over a downsized pixel list), average brightness, horizontal mirror-difference (symmetry/pattern detection), edge density, and per-band (top/mid/bottom) average colors. That's enough to characterize it ("blue-white Islamic ornament, high detail density") and design around it without vision.
5. When the owner sends a design asset to USE (e.g. hero background): `cp /root/.hermes/cache/images/<img>.jpg frontend/public/<name>.jpg`, optimize (PIL save quality=85, optimize, progressive), reference via `url('/<name>.jpg')` in style.css, and ALWAYS layer a semi-transparent gradient overlay in the app palette so overlaid text stays readable. Verify after deploy: `curl -s -o /dev/null -w '%{http_code} %{size_download}' .../<name>.jpg` → 200 + expected size, and grep the built CSS bundle for the filename.

## Deploy note

All of the above ships through the same Vite multi-stage Docker build — after patching frontend files, verify inside the container (`docker exec simmubtadiat-app-1 sh -c 'grep -c <marker> /app/public/dist/assets/<page>*.js'`); minification renames function names, so grep for STRING markers (class names, tooltip fragments like "hari lagi memotong"), not function identifiers.
