# Raport `البيان` (bayan) cell — styling, label mapping, verification

Session 2026-08-29. Owner request, verbatim: *"di raport cetak albayan harus bold, dan untuk almusbat jangan di kasih warna merah biar tetep hitam aja, coba cek"*.

## Where the cell lives

`frontend/rapot.html`, tfoot of the main value table (~line 637-641):

```html
<!-- Bayan/Decision (Semester 2 only) -->
<tr data-field="bayan-box" style="display:none;">
    <th colspan="2" style="font-weight:bold; text-align:center;">البيان</th>
    <td colspan="3" data-field="bayan-value" style="text-align:right; padding-right:20px;">-</td>
</tr>
```

Row visibility is toggled by JS: `bayan-box` is a `<tr>`, so show it with `display = ''` (table-row) — **never `'block'`**. `sig-mudir` (Direktur signature) uses `'block'`. Both only appear for semester 2.

## The two-file styling split (the actual trap)

| Property | Set in | Notes |
|---|---|---|
| font-family (`KFGQPC Uthman Taha Naskh`/`Amiri`) | `frontend/rapot.html` CSS block ~line 266 (shared with `.text-hijau`) | added 2026-08 so tfoot numbers/bayan aren't Times |
| **font-weight: bold** | same CSS block, own rule appended 2026-08-29 | this is the "albayan harus bold" fix |
| **color** | `frontend/src/js/rapot.js` inline `bayanTd.style.color = …` | **inline style beats the stylesheet** — adding `color:` to CSS has no effect |

So: weight/font → HTML CSS. Color → JS. Before diagnosing any raport print-style bug as CSS, run:

```bash
grep -n "\.style\." /opt/simmubtadiat/frontend/src/js/rapot.js
```

Every hit is a property the stylesheet cannot control.

## Current JS (post-fix)

```js
const isSem2 = String(semester) === '2';
if (isSem2) {
  let bayanLabel = data.bayan || '-';
  const isRodli = decodeEntities(bayanLabel).includes('الرديء');
  if (isRodli) bayanLabel = 'المثبت';
  set('bayan-value', bayanLabel);
  // Owner 2026-08-29: nilai البيان (termasuk المثبت) dicetak HITAM, tidak
  // pernah merah. Warna merah zona RODI dihapus — hanya di menu Penilaian.
  const bayanTd = sheet.querySelector('[data-field="bayan-value"]');
  if (bayanTd) bayanTd.style.color = '';
  ...
}
```

`isRodli` is still needed for the LABEL mapping, just no longer for color. Note `decodeEntities()` before the `includes('الرديء')` test — the API value can arrive HTML-escaped, and a raw `includes` on the escaped string misses.

## Label mapping rules (unchanged, keep intact)

- DB (`nilai_bayan.label_arab`) and the Penilaian menu keep `الرديء` (rodli', score ≤5).
- The **printed raport only** renders it as `المثبت` (musbat) — rodli' is already confirmed musbat/tetap.
- Do not "fix" this by changing the stored label; it's a print-time display substitution.

## Red-color policy (superseded rule)

Old behaviour: rodli'/musbat printed in `#dc2626`. **Removed 2026-08-29** — the printed raport is monochrome black for this field. Red zone highlighting is a Penilaian-menu affordance only. If a future session sees `style.color = isRodli ? '#dc2626' : ''` reappear, it's a regression.

## Deploy + verify

```bash
# 1. bump SW cache (mandatory for any raport cosmetic change)
#    frontend/public/sw.js -> const CACHE_NAME = 'mubtadiaat-cache-vNN';
# 2. full rebuild (docker cp of source html BREAKS page JS — see SKILL.md)
cd /opt/simmubtadiat && docker compose up -d --build app   # background + notify_on_complete
# 3. confirm the CSS actually shipped into dist
curl -s https://reviewtechno.me/rapot.html | grep -A2 'bayan-value'
curl -s https://reviewtechno.me/sw.js | head -1     # expect the new vNN
```

Visual check: render a semester-2 raport for a santri whose bayan ≤5 — the البيان value must read `المثبت`, bold, black. Semester 1 must not show the row at all.

## Verifying a font-weight/color change on the 2GB VPS (works when full render OOMs)

`/tmp/render_live.py` full-page renders repeatedly died `exit -9` (chromium OOM, ~230MB free). Two fallbacks, both cheap:

**1. Mini-page cascade probe** — extract the real `<style>` blocks + the real tfoot `<tr>` from `frontend/rapot.html`, render just those in a 900×400 page, read `getComputedStyle`. Confirms cascade/specificity without loading the app, the fonts CDN, or any JS. Script: `/tmp/verify_bayan_css.py`. Result here: `fontWeight 700`, `color rgb(0,0,0)`, `inlineColor (none)` in BOTH `screen` and `print` media.

**2. Ink-delta A/B** — render the same mini-page twice, second time with `font-weight:normal !important` injected, count dark pixels in the value column. `/tmp/ink_compare.py`. **Count glyph pixels only: skip any row whose dark-pixel run exceeds ~40% of width — those are table borders and they swamp the signal** (raw counts gave 1815 vs 1777 = +2.1%, looked like noise; border-filtered gave 195 vs 157 = **+24%**, unambiguous). A real bold change on this font is ~20-25% more ink; <5% means the rule isn't landing.

Note `@font-face` for `KFGQPC Uthman Taha Naskh` declares `font-weight: normal` only, so `bold` is **synthesized** by the browser — the weight difference is real but subtler than a true bold face. Don't conclude "bold didn't apply" from a thin-looking glyph; measure.

Full-page render, when RAM allows: pick the santri by DB lookup first
(`SELECT nb.santri_id,s.nama,nb.nilai_angka,s.bagian_id FROM nilai_bayan nb JOIN santri s ON s.id=nb.santri_id WHERE nb.nilai_angka<=5;`), map `bagian_id` → filters via `SELECT id,nama_bagian,tingkatan_id,kelas_id FROM bagian WHERE id=<n>`, then click the `.btn-print-single` whose ancestor contains the name. **The print buttons are NOT in `<tr>`s** — the santri list rows are `<div class="flex justify-between…">`, so `b.closest('tr')` returns null and a `closest('tr')`-only match silently falls back to the wrong santri (printed `المتوسط الثاني` instead of `المثبت`). Use `b.closest('tr')||b.closest('div')||b.parentElement`.

DB creds: `psql -U mubtadiaat -d mubtadiaat_db` (NOT `-U postgres`, that role doesn't exist). Column names: `kelas(id,nama)`, `tingkatan(id,nama,urutan)`, `bagian(id,kelas_id,tingkatan_id,nama_bagian)` — no `nama_kelas`/`nama_tingkatan`/`kelas.tingkatan_id`.

`pkill -9 -f chromium` inside a `terminal()` call kills the tool's OWN shell (the pattern matches the command string) → `exit -9` with empty output, indistinguishable from an OOM. Use `pkill -9 -f "[c]hromium"`.
