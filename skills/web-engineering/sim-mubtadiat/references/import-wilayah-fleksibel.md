# Import Santri: Matching Wilayah Fleksibel & SW POST Guard (2026-08)

## Masalah 1 — Nama wilayah tidak cocok → semua baris gagal

Data Excel owner sering pakai nama tanpa prefix administratif:
- "ROKAN HULU" (DB: "KABUPATEN ROKAN HULU")
- "TEGAL" (DB: "KOTA TEGAL" & "KABUPATEN TEGAL" — ambigu)
- "BANGKA BELITUNG" (DB: "Kepulauan Bangka Belitung")

Query exact-match `LOWER(nama)=LOWER($2)` gagal semua.

### Solusi — `models/wilayah.go`

**`normalizeWilayahNama()`** — strip prefix + titik, lowercase:
```
"KABUPATEN ROKAN HULU" → "rokan hulu"
"KOTA TEGAL"           → "tegal"
"Kepulauan Bangka Belitung" → "bangka belitung"
```
Regex: `(?i)^(kabupaten|kota|provinsi|kepulauan|kab\.?|kec\.?)\s+`, lalu buang `.`, rapatkan spasi.

**`findWilayahFleksibel()`** — matching bertingkat:
1. exact LOWER match (existing)
2. normalisasi kedua sisi → sama persis
3. contains dua arah pada bentuk ternormalisasi (pilih kandidat nama terpendek)

**`ResolveKabupatenKecamatan()`** — selesaikan ambiguitas Kota vs Kabupaten:
- "TEGAL" → cocok ke KOTA TEGAL & KABUPATEN TEGAL
- Kalau kecNama diberikan ("TEGAL TIMUR"), coba semua kandidat kab/kota
- Pilih yang benar-benar memuat kecamatan → KOTA TEGAL menang

Handler (`handlers/santri_import.go`) panggil `ResolveKabupatenKecamatan()` satu kali
untuk kabupaten + kecamatan sekaligus. Hindari panggilan berantai `FindKabupaten` lalu
`FindKecamatan` karena bisa salah pilih kabupaten dulu.

## Masalah 2 — "Failed to fetch" saat upload di browser

Gejala: owner upload via UI gagal "Failed to fetch", server sehat (health 200),
`curl` POST langsung SUKSES. Server logs TANPA POST /api/santri/import.

Penyebab: `sw.js` fetch handler menyegat SEMUA request (GET + POST). Untuk POST
multipart, `respondWith(fetch(event.request))` refetch dengan body stream yang sudah
ke-consume di intercept pertama → gagal.

Diagnosa: tes Incognito (tanpa SW) — kalau upload jalan, 100% SW.

Fix: `frontend/public/sw.js` — tambah guard di awal fetch handler:
```js
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return; // POST/PUT/DELETE → native browser
  ...
});
```
Bump `CACHE_NAME` setelah fix.

## Masalah 3 — Frontend "gak ada keterangan apapun"

Handler import kembalikan 422 saat semua baris gagal di tahap parsing. Tapi `santri.js`
di jalur `!res.ok` cuma `throw new Error(data.message)` — `data.message` undefined di
422, jadi error kosong. Tabel detail nggak muncul.

Fix: jangan throw hanya karena `!res.ok` — periksa apakah respons punya field
`sukses`/`gagal`/`errors` terstruktur:
```js
const hasStruct = data && (typeof data.gagal === 'number' || ...);
if (!res.ok && !hasStruct) throw new Error(...);
```
Dengan ini, tabel merah + tombol Salin tetap render di jalur 422 & 200.
