-- Diagnostic: verify raport Mudarris (المدرس) + Mudir (المدير) sources.
-- Run: docker exec -i simmubtadiat-db-1 psql -U mubtadiaat -d mubtadiaat_db -v ON_ERROR_STOP=1 < this.sql
-- Replace :BID with the target bagian_id (e.g. 31). Code is in models/laporan.go GetLaporanRaport.

-- 1. Mudarris exactly as the raport query resolves it (no TA filter, latest TA wins)
SELECT '=== MUDARRIS (query raport persis) ===' AS info;
SELECT mb.bagian_id, mb.tahun_ajaran, mb.pengajar_id,
       COALESCE(NULLIF(p.nama_arab,''), p.nama) AS nama_dipakai,
       p.nama AS nama_latin, p.nama_arab
FROM mustahiq_bagian mb
JOIN pengajar p ON mb.pengajar_id = p.id
WHERE mb.bagian_id = 31          -- <-- ganti bagian_id
ORDER BY mb.tahun_ajaran DESC;

-- 2. Are there ANY mustahiq assignments for the active TA? (usual root cause of stale/empty mudarris)
SELECT '=== mustahiq_bagian per TA ===' AS info;
SELECT tahun_ajaran, COUNT(*) AS jml_penugasan
FROM mustahiq_bagian GROUP BY tahun_ajaran ORDER BY tahun_ajaran DESC;

-- 3. Mudir for a bagian (via tingkatan) — semester-2 signature
SELECT '=== MUDIR untuk bagian (sem-2 signature) ===' AS info;
SELECT b.id AS bagian_id, b.tingkatan_id,
       COALESCE(m.nama_mudir,'(KOSONG)') AS nama_mudir,
       CASE WHEN COALESCE(m.tanda_tangan,'')='' THEN 'no-ttd' ELSE 'ada-ttd' END AS ttd
FROM bagian b
LEFT JOIN mudir_tingkatan m ON m.tingkatan_id = b.tingkatan_id
WHERE b.id = 31;                 -- <-- ganti bagian_id

-- 4. Mudir settings for every tingkatan
SELECT '=== SETTINGS mudir_tingkatan (semua) ===' AS info;
SELECT t.id AS tingkatan_id, t.nama AS tingkatan,
       COALESCE(m.nama_mudir,'(KOSONG)') AS nama_mudir
FROM tingkatan t
LEFT JOIN mudir_tingkatan m ON m.tingkatan_id = t.id
ORDER BY t.id;
