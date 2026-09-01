# Import Santri dari Excel — mode PARTIAL + matching wilayah toleran (2026-08)

Endpoint: `POST /api/santri/import` (multipart `file`). Handler
`handlers/santri_import.go`, batch `models.ImportSantriBatch`, resolusi wilayah
`models/wilayah.go`. Frontend `frontend/src/js/santri.js` (modal import).

## Mode PARTIAL (owner decision)
`ImportSantriBatch` commit PER BARIS (tx per row) — baris valid MASUK, baris gagal
di-SKIP dan dikumpulkan di `res.Errors` (baris, nama, alasan). BUKAN all-or-nothing.
Handler balikin `{sukses, gagal, errors[]}` baik di 200 (partial) maupun 422
(parse/validasi gagal sebelum sentuh DB).

**Bug klasik yang pernah ada:** query INSERT punya 19 kolom tapi placeholder `$1..$18`
+ literal `'aktif'` tidak sinkron → error "INSERT has more expressions than target
columns" → SEMUA baris gagal. Kalau import santri gagal total dgn error SQLSTATE 42601,
audit jumlah kolom vs placeholder INSERT DULU.

## Frontend laporan (santri.js)
Tampilkan hasil sebagai badge (✅ Berhasil N / ⚠️ Dilewati M) + tabel merah
`Baris | Nama | Alasan` + tombol 📋 Salin (tab-separated ke clipboard, fallback
`execCommand`). KRITIS: JANGAN `throw` hanya karena `!res.ok` — respons 422 juga bawa
struktur `errors[]`. Guard: `const hasStruct = data && (typeof data.gagal==='number' ||
typeof data.sukses==='number' || Array.isArray(data.errors)); if (!res.ok && !hasStruct) throw ...`.
Kalau throw di 422, tabel detail hilang → owner cuma lihat "Gagal mengimpor" (= "gak ada keterangan").

## Matching wilayah toleran (penyebab "semua baris gagal")
Data referensi DB pakai prefix ("KABUPATEN ROKAN HULU", "Kepulauan Bangka Belitung"),
file Excel owner tanpa prefix ("ROKAN HULU", "BANGKA BELITUNG"). Exact-match gagal semua.

`findWilayahCandidates` / `findWilayahFleksibel` (wilayah.go) mencocokkan bertingkat:
1. exact `LOWER=LOWER`
2. normalisasi kedua sisi via `normalizeWilayahNama` (strip prefix admin
   kabupaten/kota/kab/kecamatan/kec/provinsi/prov/kepulauan + buang titik + rapatkan spasi),
   bandingkan sama persis
3. contains dua arah pada bentuk ternormalisasi; kandidat diurut dari nama TERPENDEK
   (paling spesifik) agar deterministik.

**Ambiguitas KOTA vs KABUPATEN** (mis. "TEGAL" → ada KABUPATEN TEGAL & KOTA TEGAL):
`ResolveKabupatenKecamatan(provinsiKode, kabNama, kecNama)` ambil SEMUA kandidat kab,
lalu pilih yang benar-benar MEMUAT kecamatan yang ditulis. "TEGAL"+"TEGAL TIMUR" →
KOTA TEGAL (kecamatan Tegal Timur ada di Kota, bukan Kabupaten). Handler pakai fungsi ini,
bedakan pesan error: `kab.Kode==""` → "Kabupaten tidak ada di provinsi"; else → "Kecamatan
tidak ada di <kab>".

## Format file Excel yang diterima (template UjiCoba.xlsx)
Kolom (0-based): NIK, Stambuk, NISN, Nama, Nama Wali, "Tempat, Tanggal Lahir" (pisah koma,
tanggal `DD-MM-YYYY`/`YYYY-MM-DD`/`DD/MM/YYYY`), No HP Wali, Provinsi, Kabupaten/Kota,
Kecamatan, Desa/Kelurahan, Alamat Tambahan, Kamar. Wajib: NIK + Nama. Sheet pertama = data.

## Verifikasi (Chromium OOM → pakai curl, bukan browser)
Session cookie manual: `INSERT INTO sessions (id,user_id,expired_at,created_at) VALUES
(gen_random_uuid(), 1, NOW()+INTERVAL '1 hour', NOW()) RETURNING id;` (user 1 = pimpinan,
is_password_changed sudah true). Lalu `curl -s --cookie "session_id=$SID" -X POST
-F "file=@/tmp/uji.xlsx" .../api/santri/import -w "\nHTTP=%{http_code}\n"`. Bersihkan
santri uji + session sesudahnya. CATATAN: `curl ... -F` kadang di-false-reject terminal
heuristic → tulis flag ke file dulu bila perlu, atau retry.

## SW POST trap (lihat skill rapot-css-tweak-live)
Kalau upload gagal "Failed to fetch" padahal server 200 & curl sukses: Service Worker
menyegat POST. Fix: guard `if (event.request.method !== 'GET') return;` di sw.js fetch handler.
