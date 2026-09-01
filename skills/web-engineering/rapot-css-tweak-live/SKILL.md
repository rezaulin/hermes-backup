---
name: rapot-css-tweak-live
description: Adjust pixel/spacing/positioning CSS on the SIM Mubtadiat raport print page (rapot.html) and make the change actually appear for the owner. Covers the Service-Worker precache trap that silently serves stale rapot.html, the CSS-specificity trap where `.rapot-sheet td` padding overrides `.st-*` cell padding, and the measure-can't-run (Chromium OOM) reality on the 2GB VPS. Load for ANY "geser/lurusin/rapikan px" request on the raport identity block, table columns, header, or signatures.
---

# Membenahi PX / posisi CSS di Raport Cetak SIM Mubtadiat (live)

Owner sering minta geser/luruskan elemen di raport cetak ("geser ke kanan biar sejajar",
"masih kurang", "kejauhan"). Tantangan sebenarnya BUKAN nulis CSS-nya — tapi (1) bikin
perubahan benar-benar MUNCUL di layar owner, dan (2) memilih properti CSS yang tidak
ditimpa aturan lain. Dua jebakan ini menghabiskan banyak ronde kalau tidak diantisipasi.

File: `/opt/simmubtadiat/frontend/rapot.html` (CSS + markup), `frontend/src/js/rapot.js`
(isian data), `frontend/public/sw.js` (service worker cache).

## ATURAN #0 — sebelum ubah apa pun, verifikasi ini bukan masalah cache

Owner bilang "gak berubah" TIDAK berarti file salah. Urutan diagnosa:

1. Cek file yang di-serve server SUDAH benar:
   ```bash
   curl -s "https://reviewtechno.me/rapot.html?nc=$(date +%s)" | grep -o 'margin-left: 65px'
   docker exec simmubtadiat-app-1 sh -c "md5sum /app/public/dist/rapot.html"
   curl -s https://reviewtechno.me/rapot.html -o /tmp/x && md5sum /tmp/x   # md5 harus SAMA
   ```
   Kalau server benar tapi owner tetap lihat lama → 100% cache browser/SW, bukan server.
2. Minta owner tes di **Incognito** (nol cache, nol SW) atau URL cache-bust `?nc=123`.
   - Incognito BERUBAH → fix jalan, tinggal beresin cache tab normal + SW.
   - Incognito TIDAK berubah → BUKAN cache. CSS-nya yang salah/ketimpa (lihat Aturan #2).

## ATURAN #1 — Service Worker precache trap (penyebab "gak berubah" paling sering)

`frontend/public/sw.js` punya `urlsToCache`. Dulu berisi `/rapot.html` + `/dist/rapot.html`
→ SW simpan salinan rapot.html saat install dan SELALU sajikan versi itu, bikin deploy baru
tak pernah terlihat walau server sudah benar. FIX PERMANEN (sudah diterapkan): keluarkan
rapot.html dari `urlsToCache` sehingga selalu network-fresh. urlsToCache sekarang cukup:
`['/index.html','/logo.jpg','/favicon.svg','/style.css']`.

SETIAP kali ubah rapot.html/CSS, WAJIB bump `CACHE_NAME` di sw.js (mis. `mubtadiaat-cache-v34`
→ `v35`) supaya SW lama di device owner ter-invalidate. Tanpa bump, SW lama tetap aktif.

Owner mengaktifkan SW baru: Ctrl+Shift+R; kalau bandel → DevTools > Application >
Service Workers > Unregister + Clear site data; di HP → hapus data situs / uninstall PWA.

### SW POST/upload trap → "Failed to fetch" (app-wide, 2026-08)

Gejala: owner upload (import Excel santri) atau aksi POST/PUT lain gagal dengan
**"Failed to fetch"** di browser, PADAHAL server sehat (health 200) & `curl` POST
langsung SUKSES. Ini BUKAN server down. Penyebab: `sw.js` fetch handler menyegat
SEMUA request (termasuk POST multipart) lalu `respondWith(fetch(event.request))`.
Body request POST itu stream sekali-pakai — saat SW me-refetch, body sudah ke-consume
→ gagal; Cache API juga tak mendukung POST. Diagnosa cepat: minta owner tes di
Incognito (tanpa SW) — kalau di sana upload jalan, 100% SW.

FIX PERMANEN (sudah diterapkan): guard di awal fetch handler, hanya tangani GET —
biarkan browser handle POST/PUT/DELETE sendiri:
```js
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return; // jangan respondWith → native
  ...
});
```

## ATURAN #2 — CSS specificity trap pada sel identitas

Blok identitas = `.student-table` dengan `.st-left`/`.st-right` td, tiap sisi punya tabel
dalam berisi baris `.st-label | .st-colon | .st-value`. Ada aturan sheet-wide
`.rapot-sheet th, .rapot-sheet td { padding: 1px 8px 3px 6px; text-align:center }`
yang MENIMPA `padding`/`text-align` di `.st-*` (specificity `.rapot-sheet td` ≥ `.st-right`).

Akibatnya: `.st-right { padding-left: 220px !important }` bisa TIDAK nendang (bahkan di
incognito) karena kalah spesifisitas / ketimpa padding td. Gejala: server benar, incognito
pun tak berubah.

SOLUSI ANDAL untuk menggeser kolom kanan (No. Tamrin/Bagian) horizontal — pakai
**margin-left pada TABEL-DALAM**, bukan padding pada td:
```css
.st-right { width: 50%; }
.student-table .st-right > table { margin-left: 65px !important; }
```
`margin-left` pada `<table>` tidak disentuh aturan `td { padding }` manapun → pasti nendang.
Untuk per-cell alignment di dalam identitas, selalu scope `.student-table .st-*` + `!important`
(catatan skill sim-mubtadiat: sheet-wide center cascade meng-override .st-*).

## ATURAN #3 — kalibrasi angka via mata owner (Chromium OOM)

VPS cuma 2GB (~250MB free); Playwright/Chromium untuk auto-measure KONSISTEN kena SIGKILL
(exit -9), jadi tak bisa ukur px presisi dari server. Kalibrasi lewat feedback owner:
- Minta estimasi arah+besar: "kurang dikit / kurang banyak / kejauhan / lewat jauh".
- Owner sering tahu angka pastinya sendiri ("kayaknya di range 65px"). Percayai itu.
- Jangan naik 10px-10px; lompat besar dulu (60→130→220) untuk cari batas, lalu owner sebut
  angka final. Kasus nyata: 60→130→220 (lewat jauh) → owner "65px" → pas.

## Workflow lengkap (tiap iterasi)

1. Edit CSS di `frontend/rapot.html` (pakai margin-left tabel-dalam untuk geser horizontal).
2. Bump `CACHE_NAME` di `frontend/public/sw.js`.
3. Deploy: `sh -c 'docker compose up -d --build app' 2>&1 | tail -3` (background=true,
   notify_on_complete=true; heuristik terminal false-reject `docker compose up` tanpa `sh -c`).
4. Verifikasi live: `curl -s "https://reviewtechno.me/rapot.html?nc=$(date +%s)" | grep -o 'margin-left: 65px'`
   + cek SW version: `curl -s https://reviewtechno.me/sw.js | grep CACHE_NAME`.
5. Minta owner tes di Incognito / `?nc=timestamp`, kasih feedback arah.
6. Ulang 1-5 sampai pas. Baru commit + push setelah owner ACC ("mantap"/"oke").

## Isian data raport (rapot.js) — referensi cepat

- Identitas: `set('nama')`, `set('stambuk')`, `set('kelas')`, `set('tamrin')`, `set('bagian')`.
- Semua mapel setahun tampil di kedua semester (mapel 1-kwartal/1-semester nilainya `-`
  di semester lain): filter `aktif_kuartal` di query raport laporan.go dinonaktifkan (`OR TRUE`).
  (backend GetLaporanRaport kirim `kelas_nama`, `tingkatan_nama`, `bagian_nama`).
- Sel nilai kosong tampil "-": `fmtNilai(khos) || '-'`.
- Al-Bayan: data & menu Penilaian tetap `الرديء` (rodli ≤5); di RAPORT CETAK saja diubah
  ke `المثبت` (Musbat) — transform di rapot.js, bukan di DB.
- البيان & ttd Mudir hanya semester 2.

## Pitfalls
- **Signature-box flex collapse (sem 1 ttd nempel kiri, 2026-08):** `.signature-box`
  pakai `display:flex; justify-content:space-between` dengan 2 blok (المدير kiri, المدرس
  kanan). Di SEMESTER 1 blok المدير disembunyikan (`display:none`) → tinggal 1 item →
  flex naruh dia di KIRI. Owner mau ttd المدرس tetap di KANAN (konsisten dgn sem 2).
  FIX: `style="margin-left:auto"` pada blok المدرس → terdorong ke kanan walau sendirian.
  Aturan umum: kalau layout flex dengan 1 anak ter-hide, sisa anak berpindah posisi —
  pin dengan `margin-left:auto` (dorong kanan) atau `margin-right:auto` (dorong kiri).
- **Font Arab wajib KFGQPC Uthman Taha, bukan Times New Roman.** Header, biidzni/bighoirihi
  (`td-arab`), DAN angka jumlah khos/'am + absen di tfoot (`.text-hijau`) + keterangan bayan
  (`[data-field=bayan-value]`) semua harus Uthman. `.text-hijau` default-nya jatuh ke Times
  New Roman (tak punya glyph Arab-Hindi bagus) — override eksplisit:
  `.rapot-sheet .text-hijau, .rapot-sheet [data-field="bayan-value"] { font-family:'KFGQPC Uthman Taha Naskh','Amiri',serif }`.
- **biidzni (بإذن) / bighoirihi (بغيره) TIDAK bold** (owner 2026-08). Buang `font-weight:bold`
  dari kedua `<td>`, sisakan `text-align:right; padding-right:8px`.
- Jangan `docker cp` source html ke dist sebagai preview — memecah module-script Vite (lihat
  skill sim-mubtadiat). Selalu full rebuild.
- Setelah ACC, WAJIB commit + push (`git push origin main`) dan verifikasi push landed.
