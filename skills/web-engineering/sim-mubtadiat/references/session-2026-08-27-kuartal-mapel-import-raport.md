# Session 2026-08-27 — Absensi Kuartal, Mapel nama_indo, Import Partial, Raport tweaks

## Absensi Pengajar = model KUARTAL (bukan bulanan S/I/T)
- Migration 049 `absensi_pengajar_kuartal`: `pengajar_id, tahun_ajaran, kuartal_1, kuartal_23, kuartal_4 (INT), UNIQUE(pengajar_id, tahun_ajaran)`. DROP `absensi_manual_pengajar_bulanan`.
- **PITFALL**: kolom migrasi HARUS match struct Go (`kuartal_1/kuartal_23/kuartal_4`). Awalnya migrasi pakai `nilai_k1/nilai_k23/nilai_k4` → mismatch dengan model. Selalu cek `\d <tabel>` vs struct sebelum deploy.
- Model+handler `absensi_pengajar_kuartal.go`. Route `/api/absensi-pengajar-kuartal`: GET (semua role akademik), POST (pimpinan/mufatish/muroqib).
- GET = LEFT JOIN semua pengajar (mustahiq via `mustahiq_bagian` UNION munawwib via `pengajar_bagian WHERE peran='munawwib'`) filter tingkatan/kelas → pengajar tanpa catatan tetap tampil (rec id=0, nilai 0).
- Input: tab Pengajar `absensi-manual.html` (kolom K1 | K2&3 | K4, angka bebas tanpa keterangan). Rekap: tab Pengajar `rekap.html` (filter tingkatan+kelas; nomor-kelas → kelas_id via `allBagian.find`).

## Mapel: kolom `nama_indo` (migration 050)
- Raport CETAK tetap Arab (`nama_kitab`). Riwayat Akademik + Penilaian + tampilan wali (main.js) pakai `nama_indo`.
- Fallback bila `nama_indo` kosong = tampilkan Arab APA ADANYA (BUKAN translate kamus `kitab-translate.js` — owner ganti pendekatan dari kamus ke kolom manual).
- Form Kelola Mapel `kelas.html` + `kelas.js` punya field "Nama Indonesia" (kirim di CRUD, isi saat edit).
- `GetRiwayatAkademik` (riwayat_akademik.go): SELECT `COALESCE(m.nama_indo,'')` + `m.urutan`; sort mapel `sort.SliceStable(... urutan)` supaya urutan Riwayat = urutan raport. `mapel.go` CRUD handle `nama_indo`.

## Import santri = PARTIAL mode
- `ImportSantriBatch` (santri.go): commit PER BARIS (tx per row). Baris valid MASUK, gagal di-skip → `res.Errors[]{Baris,Nama,Pesan}`. Tidak rollback total lagi.
- Handler `santri_import.go`: balikin `{sukses, gagal, errors}` dengan status success (bukan 422) walau ada gagal.
- Frontend `santri.js`: badge hijau "✅ Berhasil" + merah "⚠️ Dilewati"; tabel merah `Baris|Nama|Alasan`; tombol 📋 Salin (clipboard tab-separated, fallback textarea+execCommand).
- **BUG LAMA DITEMUKAN**: INSERT punya 19 kolom target tapi `VALUES ($1..$18)` dengan `'aktif'` literal di tengah → total 19 ekspresi tapi placeholder cuma s/d $18 → "INSERT has more expressions than target columns (SQLSTATE 42601)" → import SELALU gagal total. Fix: placeholder `$1..$17` + `'aktif'` literal (17 param + 1 literal + 1 EXTRACT = 19). PELAJARAN: kalau ada literal/fungsi di tengah VALUES, hitung ulang jumlah kolom vs `$n` tertinggi.
- Verifikasi tanpa Go di image app: throwaway `Dockerfile.testimport` (golang-builder→alpine, pola sama `Dockerfile.regen`), `!tmp_test_import` di .dockerignore, `docker run --network simmubtadiat_default -e DB_HOST=db ...`, hapus file+image+data test setelahnya. Struct Santri pakai `*string` untuk Stambuk/NIK dll (pakai helper `sp := func(s string)*string{return &s}`).

## Assign santri manual langsung masuk kelas
- Backend `CreateSantri(ctx, s, bagianAwalID)` + handler `RegisterSantri` (decode `bagian_awal_id`) SUDAH set `bagian_id` + insert `riwayat_bagian` dalam 1 transaksi.
- Bug di FRONTEND `santri.js`: payload POST `/api/santri` tak menyertakan `bagian_awal_id`, lalu assign lewat panggilan KEDUA `/api/perpindahan/naik-kelas` yang tak reliable → santri nyangkut di "belum di kelas". Fix: sertakan `bagian_awal_id: parseInt(...)` di payload POST, hapus panggilan kedua.

## Raport display rules
- **Semua mapel setahun tampil di KEDUA semester**: filter `aktif_kuartal` di query raport laporan.go dinonaktifkan (`... OR TRUE`, $4/$5 tetap dikirim agar placeholder valid). Mapel yang hanya diajar 1-kuartal/1-semester tetap muncul; nilai kosong ditampilkan `-` di rapot.js (`fmtNilai(khos)||'-'`, `fmtNilaiAm(am)||'-'`).
- **Al-Bayan rodli' → Musbat di cetak**: label `الرديء` (≤5) di raport CETAK ditulis `المثبت` (Musbat), tetap merah. Data DB & menu Penilaian TETAP `الرديء`. Transform display-only di rapot.js block `isSem2`, deteksi `decodeEntities(bayan).includes('الرديء')`. GenerateAlBayan (penilaian_final.go) tidak diubah.
- **Kelas + tingkatan**: field Kelas raport = `kelas_nama` + " " + `tingkatan_nama` (mis. "1 Tsanawiyah"). Backend laporan.go sudah kirim `tingkatan_nama`.
- **Font header**: `.header-text` (h2/h3/p — كشف الدرجات, semester, nama madrasah, tahun) HARUS `font-family: KFGQPC Uthman Taha Naskh`. بإذن/بغيره: class `td-arab text-biru` (bukan `.text-biru` polos = Times New Roman, tak punya glyph Arab yang benar).
- **Logo↔teks**: `.header-text margin-left` 120px kejauhan → 90px (logo 3cm ≈ 113px).
- **Identitas kolom kanan** (No.Tamrin/Bagian) sejajar الكتب الدراسية: `.st-right { padding-left: 60px !important }`.

## Absensi grid konsisten lintas 3 tempat (Input Manual / Rekap / Detail Santri)
- Bangun daftar bulan dari kalender akademik `mulai_bulan→selesai_bulan` (inklusif, loop `y*12+m <= end`), BUKAN loop 12 bulan penuh × tiap tahun Hijri.
- Bug: detail santri (`profil_santri.js`) sempat ambil set `tahun_hijri` lalu render 12 bulan/tahun = 24 bulan utuh, padahal TA 2026/2027 cuma ~11 bulan (17 Syawal 1447 → 4 Sya'ban 1448).
- Sumber rentang: `GET /api/kalender/hijri-semester?tahun_ajaran=` (tabel `kalender_semester_hijri`; kolom mulai/selesai `_tahun_hijri`/`_bulan_hijri`/`_tanggal`). Ambil batas mulai paling awal & selesai paling akhir lintas semester (ordinal `y*360+m*30+d`).
- Bulan kosong tetap tampil; sel = 0 (rekap/detail) atau kosong "" (input manual sebelum diisi).

## Frontend responsif HP (grid input)
- `table-fixed` + `<colgroup>` proporsi %, JANGAN lebar px tetap (bikin harus geser).
- Input `w-full` + `inputmode="numeric"`; nama `break-words`.
- Sel input kosong sebelum diisi = value "" (jangan `0`); `0` hanya tampil kalau memang tersimpan.
