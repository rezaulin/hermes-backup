# Rapot render toolchain + owner font spec (session 2026-08-26)

## PITFALL: `docker cp` of rapot.html alone BREAKS the page JS

`frontend/rapot.html` (source) references dev module paths like
`<script type="module" src="/src/js/rapot.js">` and `/src/js/xss.js`. Vite
rewrites those to hashed `/assets/rapot-XXXX.js` **only during the Docker
multi-stage build**. If you `docker cp` the raw source HTML straight into
`/app/public/dist/rapot.html`, the browser requests `/src/js/rapot.js`, the
server returns `text/html` (404 fallback), and the module load fails with:

```
Failed to load module script: Expected a JavaScript-or-Wasm module script
but the server responded with a MIME type of "text/html".
```

Consequence: **all page JS silently dies** — `filter-tahun-ajaran` never
populates (0 options), "Tampilkan Santri" renders nothing, and any
Playwright render/measure script hangs on `.btn-print-single` /
`wait_for_selector` timeouts. This looks like a Playwright/session bug but it
is NOT — it's the dev-path 404.

**Rule:** CSS-only tweaks to rapot.html can be `docker cp`'d for a quick look
ONLY if you don't need the JS (you won't — the raport is JS-rendered). To
actually render/measure, you MUST full-rebuild:
`sh -c 'docker compose up -d --build app'`. Verify the served HTML references
`assets/rapot-*.js` (built) not `/src/js/rapot.js` (dev):
`docker exec simmubtadiat-app-1 sh -c "grep -oE 'assets/rapot-[^\"]*\.js' /app/public/dist/rapot.html"`.

## Chromium render flakiness on this low-RAM VPS

The box is ~1.9 GB RAM with heavy swap usage. Chromium (`/tmp/render_live.py`,
already using `--single-process --no-zygote --no-sandbox --disable-dev-shm-usage`)
still dies/EGL-crashes intermittently and leaves zombie processes that starve
the next run. Reliable pattern:
1. `pkill -9 -f chromium` before each render run (clears stale procs).
2. Retry once on timeout — transient OOM often clears on the second try.
3. Run the render script via `> /tmp/rl.log 2>&1; echo rc=$?` then grep the log
   (the terminal backgrounding heuristic sometimes truncates long inline output).

## Test-session recipe (auth Playwright/curl against 127.0.0.1:8080)

Cleaner than the temp-user + bcrypt dance for read-only rendering: reuse the
admin user (id=1, `is_password_changed=true`) and INSERT a session row.
`sessions` schema = `(id uuid, user_id int, expired_at timestamptz, created_at)`.

```sql
INSERT INTO sessions (id, user_id, expired_at, created_at)
VALUES (gen_random_uuid(), 1, NOW() + INTERVAL '2 hours', NOW())
RETURNING id;
```
Write the returned uuid to `/tmp/sid.txt`; render_live.py reads it and sets
cookie `session_id`. Verify: `curl -s -o /dev/null -w '%{http_code}\n' --cookie "session_id=$SID" http://127.0.0.1:8080/api/me` → 200.
Filters populate from `/api/settings/umum` (tahun_ajaran_aktif) + `/api/kalender/tahun`;
santri list from `/api/santri/by-bagian/<id>`; raport data from
`/api/laporan/raport/<santriId>?semester=N&tahun_ajaran=YYYY/YYYY`.
Known-good demo filter for TA 2026/2027: tingkatan=1, kelas=12, bagian=31 (santri Ruqoyyah, id 110).

## Owner font/layout spec — CONFIRMED via color-coded reference photo (2026-08-26)

Owner sends a color-legend annotated reference. Mapping:
| Color | Font | Applies to |
|---|---|---|
| 🟢 Hijau | Times New Roman 14pt | student identity (Nama/Stambuk/Kelas/Tamrin/Bagian) + numeric grade values |
| 🟠 Orange | KFGQPC Uthman Taha Naskh 18pt **BOLD** | table header (thead), footer total rows, signature NAMES |
| 🔵 Biru | KFGQPC Uthman Taha Naskh 16pt | Arabic table cell text (kitab/funun), jabatan المدير/المدرس |

Layout constants (F4): `@page { size: 215.9mm 330.2mm; margin: 2.5cm 1.5cm 2cm 1.5cm; }`
(Top 2.5 / Left 1.5 / Bottom 2 / Right 1.5 cm). Logo target = **3×3 cm**
(≈113px @96dpi) — NOT the old 90px. WARNING: bumping logo to 3cm previously
pushed the sheet to 3 pages; re-measure with render_live.py after any logo/font
size change (overflow lives in cumulative vertical spacing, trim header/table
margins to reclaim — see the overflow-fix history in SKILL.md).

**thead nuance:** owner wants thead at 18pt bold, but the combined column
header `أرقام الدرجات الخاصة والعامة` must stay 16pt + `white-space:nowrap` or it
wraps to two lines. Raise the single-word headers to 18pt, keep the long phrase 16pt.

**"Header from top 1.27cm / Footer from bottom 1.27cm" is a MS-Word print
concept, NOT CSS-controllable.** In browser printing that band is the browser's
own header/footer (URL/date) region, set in the print dialog ("Margins: Custom"
/ disable "Headers and footers") — not something to encode in CSS. Explain this
to the owner rather than trying to fake it with padding.

## Signature names: NO parentheses (owner correction 2026-08-26)

Mudir & Mudarris signature names in rapot.html must render **without** wrapping
`( )`. Earlier template had `(<span data-field="sig-mudir-nama">…</span>)` —
owner: "seharusnya gak pakai kurung". Removed for both `sig-mudir-nama` and
`sig-mudarris-nama`. Applies whether the name is filled or shows the dotted
placeholder. Verify built file has zero `(<span data-field="sig-`.

## Mudarris / Mudir sourcing — code is CORRECT, data may be empty (confirmed)

- Nama Mudarris: `laporan.go` reads `mustahiq_bagian JOIN pengajar` (nama_arab
  fallback nama), `ORDER BY tahun_ajaran DESC LIMIT 1`, **no TA filter**. So a
  bagian with only an old-TA assignment shows that old mudarris; a bagian with
  no assignment shows dots. As of 2026-08-26 all 9 mustahiq_bagian rows are TA
  2024/2025 — none for the active 2026/2027 → names are stale/empty until owner
  re-assigns for the active TA.
- Nama Mudir (semester-2 signature): reads `mudir_tingkatan` via the bagian's
  tingkatan (managed in Settings), fallback `settings.nama_kepala`. All
  tingkatan had empty `nama_mudir` → signature blank until filled in Pengaturan.
  Both are input-data gaps, not code bugs.
