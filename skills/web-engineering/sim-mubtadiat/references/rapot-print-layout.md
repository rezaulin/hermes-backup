# Raport Print Layout — owner spec (IMPLEMENTED Aug 2026)

Implemented & deployed (commit series ending 2026-08-22). Owner's photo-annotated
mockup was the source of truth. Keep this file as the layout contract — future
raport changes must not regress these specs.

## Owner spec (verbatim) — ALL CONFIRMED

| Mockup color | Font | Size | Applied to |
|---|---|---|---|
| Hijau (green) | Times New Roman | 14pt | Latin identity labels, signature names. ~~all grade digits~~ — SUPERSEDED: grade digits moved to KFGQPC (see `.td-num` note in implementation map; TNR lacks Arabic-Indic glyphs) |
| Oranye (orange) | KFGQPC Uthman Taha Naskh | 18, **Bold** | Report title, semester title, tfoot total row, البيان label, أيام التأخر header, المدير/المدرس labels |
| Biru (blue) | KFGQPC Uthman Taha Naskh | 16pt | Madrasa name line, tahun line, table headers, kitab & funun cells, Arabic identity values |

Owner answers to the 3 confirmation questions (2026-08-22):
1. Title `كشف الدرجات الدراسية` → **Uthman Taha** (18 Bold), NOT TNR.
2. Grade numbers → **Arabic-Indic digits** (keep `toArabicDigits`).
3. Footer = **signature block** (المدير + المدرس), keep existing logic.
   **Nama mudaris MUST come from the mustahiq assigned to the santri's bagian** —
   backend (fixed 2026-08, commit 29f82d2): `models/laporan.go` query on
   `mustahiq_bagian mb JOIN pengajar p ON mb.pengajar_id = p.id WHERE
   mb.bagian_id = $1 ORDER BY mb.tahun_ajaran DESC LIMIT 1`, picking
   `COALESCE(NULLIF(p.nama_arab,''), p.nama)` → `nama_mudarris` JSON field.
   (The ORIGINAL query used `pengajar_bagian WHERE peran='mustahiq'` — that
   table has ZERO such rows, so mudarris was always dots. Do not reintroduce.)
   Owner spec: the raport MUST show the ARABIC name (nama_arab) — hence the
   COALESCE priority. Related: every pengajar edit silently disabled the
   pengajar (`is_active` Go zero-value in UpdatePengajar, commit 6cd097a),
   which is why owner-filled nama_arab seemed to "disappear" and the raport
   showed Indonesian names — see SKILL.md gotchas for that pattern.

Paper geometry:
- F4 (215.9 × 330.2 mm) — now the DEFAULT in `kertas-selector` (A4 second)
- Margins (owner RE-CONFIRMED 2026-08-25 "ikuti saja yang digambar semua",
  reverted to the spec photo): Top **2.5 cm**, Left 1.5 cm, Bottom 2 cm,
  Right 1.5 cm. History: 2.5cm → 1.27cm on 2026-08-22 ("header terlalu ke
  bawah") → back to **2.5cm** on 2026-08-25. THREE places must carry the same
  top value or preview/print drift: the `#page-style` @page, the
  `updatePageSize()` template string, AND `.rapot-sheet` screen padding-top.
- Footer-pin `min-height` follows the top margin: **285mm** for F4 top-2.5cm
  (330.2 − 25 − 20 = 285.2). Was 263mm under the 1.27cm era. Recompute this
  whenever the top margin changes or signatures float mid-page.

### GRADES-TABLE COLUMN CONTRACT (measured from reference photo, 2026-08-25)
Reference vertical grid lines sit at px 55·162·240·354·476·511 (RTL:
right→left = الرقم | الكتب | الفنون | الخاصة | العامة). Widths are NOT equal —
the two value columns differ:
| Column (RTL) | width |
|---|---|
| الرقم | 8% |
| الكتب **الدراسية** | 27% |
| الفنون | 25% |
| الخاصة (khos) | **17%** |
| العامة (umum) | **23%** — wider than khos |
- Header text = **`الكتب الدراسية`** (د-ر-ALIF = "studi"), NOT `الكتب المدرسية`
  (م-د = "sekolah"). Verified letter-by-letter on an 8× zoom crop — the tell is
  a tall standing alif after د-ر. A prior version had the wrong word.
- أيام التأخر sub-rows (بإذن/بغيره): day count goes in the الخاصة column ONLY;
  the العامة cell must be an EXPLICIT empty `<td></td>` so its divider runs
  straight down and lines up with the rows above. Omit it and the grid breaks.
- Logo 3×3 cm (`object-fit: contain`) — **raport uses `/logo-raport-bw-v5.png`:
  the owner's OFFICIAL MONOCHROME EMBLEM rendered HD** (owner spec 2026-08-22:
  "harusnya seperti ini bos lambangnya bisa gak" + photo of the official
  black-on-white version, then "logonya dibuat hd dulu biar gak pecah", then
  "kalau ini bagaimana, sudah hd belum" with a cleaner 1181×1331 PNG source).
  **Version history:** v3 = flood-fill B/W of the 710×800 JPEG emblem photo;
  v4 = potrace HD render of that same JPEG emblem (commit 57e97b1);
  v5 = potrace HD render of the owner's LATER cleaner PNG source (commit
  dcb3fc4). NOTE: v5 is a DIFFERENT artwork variant from v4 (content aspect
  0.89 vs 1.04, IoU only 37%) — the owner's latest source always wins.
  History & lesson: v1/v2 were THRESHOLD CONVERSIONS of the colored
  `/logo-v3.png` — pixel-similarity to the official emblem was only ~28%, i.e.
  the colored app logo is a DIFFERENT artwork from the official monochrome
  seal. RULE: when the owner shows a reference photo of how an asset "should"
  look, USE THAT SOURCE ARTWORK DIRECTLY (process it) instead of deriving it
  programmatically from a different asset. Version-suffix rename mandatory
  each rebuild (Cloudflare 4h static cache: v2 was cached under an earlier
  filename). The REST of the app stays on the colored `/logo-v3.png`.
  `onerror` falls back to logo-v3.png.

  **HD pipeline (v4, commit 57e97b1) — potrace vectorization, not upscaling:**
  the owner's Telegram source is only 710×800 JPEG; naive upscaling adds no
  detail, and binary-threshold edges stay jagged. True HD = convert to vector:
  1. `PIL`: load grayscale → `MedianFilter(3)` denoise → `GaussianBlur(0.6)`
     (kills JPEG ringing) → crop to inverted bbox → `point(lambda x: 0 if x<128
     else 255, '1')` → paste onto +4px white border (so potrace doesn't trace
     to the image edge) → save `.pbm`.
  2. `potrace file.pbm -s -o out.svg --turdsize 25 --alphamax 1.0
     --opttolerance 0.2` (potrace 1.16, `apt-get install potrace`) → clean
     black-path SVG (~31KB), edges become smooth curves.
  3. Render the SVG at ANY resolution via headless Chrome: `page.goto(file://svg)`,
     set explicit width/height attrs, `page.locator('svg').screenshot(omit_background=True)`
     → RGBA PNG with perfect anti-aliasing. v4 = **3000×2867 px = ~2540 DPI at
     the 3cm header** (print standard needs 300).
  4. potrace caveat: it traces BLACK ONLY — the emblem's internal white areas
     become transparent. For a print header on white paper that renders
     correctly (white shows through), and matches the official seal look.
  **Fidelity check after rebuild — do NOT trust raw pixel IoU.** Measured IoU
  of the vector render vs the source photo was only 24–38% — misleading,
  caused by hairline strokes and sub-pixel alignment, NOT wrong artwork.
  Correct checks: (a) connected-component census — component SIZES scale by a
  constant factor (e.g. exactly 5.7× at the rendered resolution) and the
  count matches → same topology; (b) center-of-mass nearly identical;
  (c) IoU WITH 2px dilation tolerance jumps to ~84%. Partial-alpha pixel
  percentage (~1.5%) confirms smooth edges.

Student identity block — FINAL spec (owner reversed course 2026-08-23):
grid layout KEPT (flex row per field: fixed-width label 100px → colon `:`
aligned exactly across all rows → `.val` flex-1), but **plain**: the dotted
underline (`border-bottom: 1px dotted`) REMOVED and values NOT bold
(`<strong>` → `<span>`, `font-weight: normal`). Owner: "dibawah nama
dibawah kelas kenapa ada garis garisnya hilangkan saja" + "kolom isian
nama kelas dll jangan dibuat tebal". Do NOT reintroduce dotted underlines
or bold on identity values.

## Implementation map (what lives where)

- `frontend/public/fonts/UthmanTN.ttf` — the KFGQPC font (self-hosted; print
  output must not depend on a CDN). Loaded via `@font-face` in rapot.html under
  family name `'KFGQPC Uthman Taha Naskh'`, fallback `'Amiri'`.
- Font tier classes in `rapot.html` `<style>`: `.ft-tnr` (TNR 14pt),
  `.ft-uth-18` (Uthman 18pt bold), `.ft-uth-16` (Uthman 16pt); table cells use
  `.td-arab` (Uthman 16) / `.td-num` (**Uthman 14 bold** — changed from TNR
  2026-08-23, commit c4ca8d9: Times New Roman has NO Arabic-Indic digit
  glyphs (٠١٢٣٤٥٦٧٨٩) and the browser fallback font is inconsistent;
  the original "green tier = TNR 14pt for grade digits" mockup spec predates
  this finding — keep digits on KFGQPC). `tfoot th` = Uthman 18 bold.
- **Merged tfoot (plek ketiplek raport fisik, owner 2026-08-24, commits 874d911 + e24d1c1)**:
  total, absen & bayan ALL live in ONE tfoot of the main grades table (border
  columns continue straight down — NOT separate tables). Order:
  `جملة أرقام` row (label colspan=3) → `أيام التأخر` (**th colspan=2 rowspan=2**
  spanning الرقم+الكتب — detected from reference: vertical line at x476 ABSENT;
  single-column label overflows/clips at 18pt; sub-rows بإذن / بغيره —
  reference wording, formerly بغير إذن; day counts in الخاصة value column) →
  `البيان` row (**2 merged cells: label colspan=2 + value colspan=3** —
  reference shows only 3 vertical lines in this row; 5 separate cells = 3
  bogus extra lines). Grid ground truth method: detect vertical border lines
  per row band on the reference photo, missing line = colspan. **بيان is
  semester-2 ONLY** (rapor akhir tahun; owner re-confirmed 2026-08-24 after a
  brief wrong change to all-semesters — do NOT repeat that mistake). Direktur
  signature also sem2-only.
- **Text-to-border gap rule (owner 2026-08-24, commit aa5734c)** — "jangan
  sampai ada text menyentuh garis, terutama huruf yang arah penulisannya ke
  bawah" (descenders خ ج ح ع غ ي ق). Physical reference photo, measured on
  pixels (calibration: photo = full A4 → 1px ≈ 0.37mm): ink-to-line gap min
  ≈ 0.74mm, bottom-gap median ≈ 2.2mm, top-gap median ≈ 1.5mm. Current spec:
  `padding: 2px 6px` + `line-height: 1.05` → measured min ink gap 0.8mm,
  typical 1.0–2.4mm; sem2 content 259.3mm of the ~264mm A4 print area (4.7mm
  headroom). The earlier 1px / line-height 1.1 spec produced 0.08–0.14mm gaps
  = text visually TOUCHING the borders. If the gap spec changes again,
  re-measure with `scripts/rapot_gap_check.py` — see Testing notes.
- `.rapot-sheet`: on-screen = exact F4 white sheet (width 215.9mm,
  min-height 330.2mm, padding `1.27cm 1.5cm 2cm 1.5cm`, flex column).
- Print: `@page { size: 215.9mm 330.2mm; margin: 1.27cm 1.5cm 2cm 1.5cm; }` set
  in `#page-style` (default) and by `updatePageSize()`. Sheet padding is zeroed
  in `@media print` so @page margins own the positioning (1:1). Screen wrappers
  are ALSO zeroed in print: `main, #rapot-wrap, #print-area { padding: 0
  !important; margin: 0 !important; overflow: visible !important; }` — without
  this, the p-4/md:p-8 wrapper offset (~8.5mm) pushes each sheet down and the
  signature block spills onto an extra page.
- **Footer-pinning trick**: `.signature-box` has `margin-top: auto` (flex column
  sheet) + print `.rapot-sheet { min-height: <N>mm !important }` (`!important`
  is REQUIRED — the on-screen `.rapot-sheet { min-height: 330.2mm }` rule sits
  LATER in the file and would otherwise win the cascade) so signatures always
  sit at page bottom like a Word footer.

  **⚠️ FOOTER-PINNING OVERFLOW BUG — root cause found 2026-08-25.** After the
  top margin went back to 2.5cm the raport printed 5→4→3 pages instead of 2.
  Real content was only ~260mm yet each sheet measured ~284mm. TWO stacked
  dead-space bugs, both had to be fixed:
    1. `tfoot th { padding: 1.27cm 6px }` = 12.7mm vertical padding × 3 footer
       rows → tfoot ballooned to **101mm** (reference footer rows are ~8mm thin).
       Fix: `padding: 1px 6px 4px 6px` → tfoot ~33mm.
    2. `.signature-box { margin-top: 1.27cm !important }` was OVERRIDING the
       template's inline `style="margin-top:auto"` — the `!important` won the
       cascade, so footer-pinning NEVER actually worked and 12.7mm dead space
       was ADDED instead. Fix: DELETE `margin-top` from the `.signature-box` CSS
       rule entirely; the inline `margin-top:auto` then pins signatures to the
       sheet bottom for real.
  Diagnostic that nailed it: under `page.emulate_media("print")`, measure EACH
  child of `.rapot-sheet` (header / student-data / table / signature-box) — the
  gap between `sheet.offsetHeight` and the sum-of-children (or a child far
  taller than its ink) exposes the dead space. `min-height` alone can't shrink a
  sheet whose children carry hidden padding.

  **min-height needs HEADROOM below the F4 print area (285.2mm).** 285/282mm was
  too mepet — sub-pixel rounding spilled onto page 3. **270mm** is the safe
  value (content ~260mm; signatures land ~10mm above the bottom edge on F4,
  acceptable). Value history: 285.2mm (orig F4-2.5cm) → 297mm (F4-1.27cm) →
  263mm (2026-08-22, A4 content) → **270mm (2026-08-25, F4-2.5cm + real
  footer-pinning)**. Recompute + re-verify page count whenever the top margin
  changes. Keep ALL print sheet rules in the ONE `@media print` block at the top
  of the `<style>` — a second block once set `min-height: auto` and killed the
  pinning.
- `rapot.js` tbody row template uses `td-num` for digits & `td-left td-arab` for
  kitab/funun — keep these classes when editing the row template.

## ONE-PAGE-PER-SEMESTER FIX — deployed 2026-08-22 (commits 56953e8 → 8a1a3b0)

Reproduced headlessly (Playwright + system Chrome, real app flow, print-media
PDF with `prefer_css_page_size=True` — the page's own `@page` applies, so the
PDF is exactly what a printer sees). Re-runnable probe: `scripts/rapot_print_check.py <session_uuid>`
(measures sheet mm + counts PDF pages; 1 semester must = exactly 1 page).
Test subject: santri 110 Ruqoyyah (Ibtida'iyah kelas 6, bagian A; filters
tingkatan=1, kelas=12, bagian=31 on TA 2026/2027).

Pre-fix measurements: sem-1 sheet = 391.3mm, sem-2 = 407.2mm vs F4 total
330.2mm → PDF came out **4 pages for 2 semesters**; page 2 repeated thead +
rows 15–16 + tfoot + absensi + signatures (table split mid-table). Post-fix
(commit 8a1a3b0): content 248mm (sem 1) / 256mm (sem 2) → verified **2 pages
total** on BOTH F4 and A4 PDFs.

**⚠️ MOBILE PRINT PREVIEW PAGINATES BY THE PRINTER'S PAPER SIZE — USUALLY A4.**
The page's `@page { size: F4 }` does NOT control the Android/iOS print preview;
the OS uses the selected printer's default paper. The first fix round (commit
56953e8) made the layout fit F4's 297mm area — owner tested on his PHONE and
said "belum berubah, masih jadi 2 halaman", because his printer = A4 (content
area only ~264mm). RULE: when the owner prints from his phone, ALWAYS verify
the PDF at A4 size too (`page.pdf(format="A4")`) and keep total content under
~260mm so both papers fit. Never declare a print fix done on F4 verification
alone.

Root causes fixed (fonts stayed per spec — spacing only):
1. **@page top margin 2.5cm vs 1.27cm screen** → printed header sat ~1.2cm
   lower than the on-screen preview ("margin atas terlalu kebawah"). Fixed:
   `@page` margin-top → 1.27cm in BOTH `#page-style` and `updatePageSize()`.
2. **Tailwind preflight `line-height: 1.5`** inflated every table row — the
   grades table alone was 221mm (16 mapel). Fixed: cell `line-height: 1.1` +
   padding 1px (table ~150mm), kop headers line-height 1.15, student-data
   line-height 1.25 + p margin-bottom 1px, header pb-3/mb-3, bayan mt-1,
   absensi mt-2, signature margin-top 8px. Result: sem-1 248mm, sem-2 256mm.
   (SUPERSEDED 2026-08-24 for table cells only: now `padding: 2px 6px` +
   `line-height: 1.05` — see the gap-rule bullet in the implementation map.)
3. **Two conflicting `@media print` blocks** — the second set `min-height: auto`
   and killed footer pinning. Merged into one block (see above).
4. **Screen wrapper offset** — `main`, `#rapot-wrap` (p-4/md:p-8), and
   `#print-area` padding shifted sheets ~8.5mm down, spilling signatures onto
   an extra page. All three zeroed with `!important` in print media.
5. **min-height cascade** — print `min-height` needs `!important` because the
   on-screen rule (330.2mm) comes LATER in the file and wins otherwise.
6. **Stray backslash in kitab column**: `الخط \ الإملاء` (literal `\`), 10 rows
   in `mata_pelajaran.nama_kitab` — cleaned in DB → `الخط والإملاء` (transaction
   + backup `/root/backup_20260822_rapot.sql`). When hunting "stray string" in
   raport columns, grep DB for `position(E'\\' in ...)` and weird chars first.
   Also note: `isExcludedRow()` in rapot.js computes exclusions but its
   `included` result is DEAD CODE — excluded categories (Quran/khot/qiroah/
   akhlaq/hafadz) still render & count in totals. Owner has NOT decided whether
   to enforce it.

Note: A4 is now the BINDING constraint (~264mm area). If content ever grows
(more than ~18 mapel rows, or taller البيان/absensi), it will spill on A4
first — check the A4 PDF, not just F4.

## KFGQPC font sourcing (hard-won, keep it)

- Not on Google Fonts; Amiri is NOT a substitute the owner accepts.
- Canonical file: `UthmanTN_v2-0.ttf` (UthmanTN = Uthman Taha Naskh), TrueType,
  139,336 bytes, DSIG-signed, licensed 2008–2022 (KFGQPC original).
- Working source (verified 2026-08):
  `https://github.com/alhikmahtegal/font-arab-uthmani/raw/main/UthmanTN_v2-0.ttf`
- GitHub searches for "UthmanTN"/"uthman naskh" return 0 results; most KFGQPC
  repos host QCF page-glyph fonts (per-page mushaf rendering), not text fonts.

## Mockup analysis recipe (reuse for future "match this photo" tasks)

Vision/OCR couldn't read the Arabic mockup. Working approach: classify every
non-gray pixel per row into H (g>r,b) / O (r>g>b) / B (b>r,g), group rows into
segments, count per zone → produces a zone→color map; then mask-per-color PNGs
fed to `tesseract -l ara` for the text. Also: corner-pixel sampling for the
background color, dominant-color Counter for populations. Only ask the owner
after exhausting pixel analysis.

## Testing notes

- **Headless ground truth beats screenshots for print bugs** (established 2026-08):
  `pip install playwright pypdf`, run `scripts/rapot_dual_paper_check.py <session_uuid>`
  (verifies 1 page/semester on BOTH A4 and F4 — the preferred probe since the
  A4-trap discovery) or `scripts/rapot_print_check.py <session_uuid>` (single paper).
  Key technique: patch `window.print` out BEFORE clicking Cetak, drive the real
  filters via `select.value = x; dispatchEvent(new Event('change', {bubbles:true}))`
  (kelas/bagian options load asynchronously per change — wait ~300ms between),
  then `page.emulate_media('print')` + `page.pdf(..., prefer_css_page_size=True,
  margin=0)` — page.pdf then honors the page's own `@page` size/margins.
  `pypdf` page count = definitive overflow proof; `extract_text()` per page shows
  split tables (Arabic renders glyph-reversed — unreadable but fine for structure).
  `browser_console` in Hermes blocks fetch() and document.cookie expressions —
  for auth, INSERT a sessions row in the DB and use Playwright `add_cookies`.
- Print preview: in the browser print dialog choose margins = Default so the
  `@page` rule wins, and paper size F4. Owner tests on a real printer — ask for
  a photo of the printed page before calling it done next time.
- Arabic text in tesseract needs `-l ara` and high-res upscaled crops; OCR of
  the KFGQPC glyphs is unreliable — trust the pixel-color analysis instead.
- **Ink-gap probes (2026-08-24):** `scripts/rapot_gap_check.py <photo.jpg>`
  measures ink-to-border gaps on the PHYSICAL reference photo (calibration:
  photo = full A4 → 1px = 297/h mm; loose ink threshold 185 for faded scans;
  green pen circles excluded). `scripts/rapot_pdf_gap_check.py
  /tmp/rapot_check_f4.pdf` does the same on the headless-Chrome PDF output of
  the dual-paper check (rasterize 300dpi, scan dark pixels per row band —
  borders are 're' rectangles in get_drawings, NOT 'l' lines). Pass = min
  ink gap >= 0.74mm. NEVER use word bboxes for this: Arabic font metrics
  make bbox-to-border gaps read ~0.15pt regardless of actual spacing.
- **Chromium multi-process crash (2026-08-24):** Playwright/system Chrome crashes
  with "Page crashed" on real pages that load fonts/iframes — discovered during
  print verification. Workaround: pass `--single-process` flag to Chromium
  launch args. This was a critical blocker; without it, no reliable print
  verification possible. The crash persists even when blocking external
  resources (Tailwind CDN, Google Fonts) or using Playwright bundled Chromium.
  Command pattern for `rapot_dual_paper_check.py`: 
  ```python
  browser = await p.chromium.launch(args=[
      "--no-sandbox", "--disable-dev-shm-usage",
      "--disable-gpu", "--single-process"])
  ```
  Note: `set_content()` works fine but `goto()` crashes — the issue is specific
  to navigation/renderer process spawn, not HTML content itself.
- **Service Worker rebuild-after-edit trap:** Starting
  `docker compose up -d --build app` BEFORE finishing frontend edits ships STALE
  assets. After every rebuild verify the actually-served artifacts: curl
  `https://reviewtechno.me/rapot.html` and grep a fresh marker (e.g., the padding
  comment text); the hashed JS bundle lives at `/app/public/dist/assets/rapot-<hash>.js`\n  inside the container (Vite strips comments — grep code strings, not comments);\n  the served `sw.js` must show the bumped CACHE_NAME. Frontend is served from
  `/app/public/dist` (Go FileServer) — there is NO `/app/frontend` in the
  container. Always bump CACHE_NAME (v16→v17→...→v19) AND wait for container
  to fully restart before verifying deployed URLs. Cloudflare static cache
  normally ~4h but dynamic endpoints bypass it — still, SW needs explicit cache
  reset via version bump.
