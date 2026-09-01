# Migrasi server Digital Sekolah — bundle backup + restore sekali-jalan

Dibuat 2026-08-29 atas permintaan owner: *"backup semua data smartlms/digital sekolah buat pindah server, biar bisa langsung run sekali klik di server baru"*.

Script live di repo: `deploy/backup.sh` + `deploy/restore.sh` (commit `4f7d7f4`). Keduanya sudah teruji end-to-end di server sumber.

## Alur

```bash
# server LAMA
sudo bash deploy/backup.sh          # -> /root/ds-migrate/digitalsekolah-backup-<ts>.tar.gz (~9 MB)
scp /root/ds-migrate/*.tar.gz root@IP-BARU:/root/

# server BARU
tar xzf digitalsekolah-backup-<ts>.tar.gz && cd digitalsekolah-backup-<ts>
sudo bash restore.sh domain-baru.com
```

`restore.sh` 9 tahap: apt deps → source → runtime data/secrets → Postgres create+import → `go build` → frontend dist → nginx → PM2 (+`pm2 save`/`startup`) → certbot + verifikasi HTTP.

Env override: `APP_DIR`, `DB_NAME`, `DB_USER`, `DB_PASS`, `BACKEND_PORT`, `SSL_EMAIL`, `SKIP_SSL=1`, `KEEP_GIT=1` (backup), `VERIFY=1` (restore).

## Apa yang WAJIB masuk bundle (semua ini di-gitignore → hilang kalau cuma `git clone`)

| Item | Path | Catatan |
|---|---|---|
| Dump DB | `pg_dump --no-owner --no-privileges --clean --if-exists` | 20 MB db → 1.2 MB gz, 50 tabel |
| Uploads | `backend/uploads` | 3.8 MB, logo sekolah dll |
| QRIS cache | `backend/qris_codes` | PNG hasil render |
| **Sesi WhatsApp** | `wa-gateway/auth` | ~3600 file, 15 MB. Kalau tidak dibawa → wajib scan QR ulang |
| Secrets | `backend/ecosystem.config.js` | VAPID keys. Tanpa ini push-notif mati (restore.sh memperingatkan) |
| frontend dist | `frontend/dist` | dibawa jadi `npm install` di server baru tidak wajib |

## VERIFY=1 — uji bundle tanpa mengganggu server live

`VERIFY=1 APP_DIR=/tmp/ds-verify/smart-lms DB_NAME=smart_lms_verify bash restore.sh dummy.local`

Melewati apt, nginx, PM2, certbot, dan `npm install` wa-gateway. Tetap menjalankan ekstraksi + import DB ke database terpisah + `go build` sungguhan. Ini cara memvalidasi bundle di server sumber. Hasil uji: 50 tabel ter-import, binary 41 MB ter-build, dist ada. Bersihkan: `rm -rf $APP_DIR && sudo -u postgres dropdb $DB_NAME`.

## PITFALL — `set -o pipefail` + `tar -tzf | head -1` = exit 141 senyap

`EXTRACTED=$(tar -tzf big.tar.gz | head -1 | cut -d/ -f1)` membuat script MATI di tengah tanpa pesan error: `head` menutup pipe setelah 1 baris → `tar` kena SIGPIPE (141) → `pipefail` mempropagasi → `set -e` exit. Gejalanya script berhenti persis setelah langkah sebelumnya, exit code 141, tidak ada baris error. Ganti dengan `sed -n '1s#/.*##p'` (sed membaca sampai habis, tidak menutup pipe). Audit SEMUA `| head` / `| tail` dalam script ber-`pipefail` yang sumbernya arsip besar.

## PITFALL — `.git` bisa jauh lebih besar dari source-nya

Bundle pertama = **120 MB**; `source.tar.gz` sendiri 113 MB. Penyebabnya `.git/objects` menyimpan ~110 MB binary Go/`.exe` yang pernah ter-commit (8 blob 13-18 MB). Exclude `.git` → source 113 MB → **1.9 MB**, bundle jadi 9.1 MB. Riwayat tetap ada di GitHub. `KEEP_GIT=1` untuk memaksa ikut. Selalu cek isi arsip berdasarkan ukuran sebelum menyerahkan bundle:

```bash
tar -xzOf bundle.tar.gz '<dir>/payload/source.tar.gz' | tar -tzv | awk '{print $3"\t"$NF}' | sort -rn | head -25
```

## PITFALL — Postgres MATI kalau disk 100% penuh: `FATAL: could not write init file`

Uji restore di server yang tinggal ~160 MB membuat `/` mencapai 100% → Postgres berhenti menerima koneksi dengan `could not write init file`, lalu `Connection refused`. **Bukan** masalah kredensial. Pemulihan: bebaskan disk lalu `systemctl start postgresql`. Sumber ruang yang aman dibersihkan di box ini, berurutan:

| Aksi | Dibebaskan |
|---|---|
| `journalctl --vacuum-size=200M` | **1.1 GB** — journal sistemd sempat 1.4 GB |
| `rm -rf /root/.cache/pip` | 124 MB |
| `go clean -cache` | 448 MB (akan terbentuk lagi saat build) |
| `/root/.cache/ms-playwright` | 1.3 GB (hapus HANYA kalau tidak butuh render raport) |

Docker build cache melaporkan 4.15 GB tapi `RECLAIMABLE 0B` — jangan berharap dari situ.

**Selalu cek `df -h /` SEBELUM menjalankan uji restore.** Butuh ≥500 MB bebas.

## Binary basi di `backend/` — cara membuktikan mana yang aman dihapus

Owner bertanya "yakin ini gak kepake semua?" — jawab dengan bukti kernel, bukan nama file:

```bash
PID=$(pm2 jlist | python3 -c "import json,sys;print([p['pid'] for p in json.load(sys.stdin) if p['name']=='smart-lms-backend'][0])")
ls -la /proc/$PID/exe          # -> binary yang BENAR-BENAR jalan
pm2 jlist | python3 -c "...pm2_env.pm_exec_path..."
file -b <kandidat>             # PE32+ = binary Windows, mustahil jalan di Linux
lsof <kandidat>                # ada yang membuka?
```

Dihapus 2026-08-29 (190 MB, semua gitignored, nol referensi di config/script/systemd/nginx): `test.exe`, `smart-lms.exe`, `smartlms-backend.exe`, `main.exe` (semua PE32+ Windows), `smart-lms-linux`, `smartlms-backend` (ELF build 8 Juli). Yang HIDUP: `backend/smart-lms` (41 MB, build 22 Agt) — dikonfirmasi via `/proc/PID/exe`.

**`backend/smart_lms.db` JANGAN langsung dihapus.** Terlihat seperti sampah dev (backend pakai Postgres karena `USE_SQLITE` tidak diset, `lsof` kosong) TAPI isinya 709 baris data nyata, dan bukan subset produksi: SQLite punya 4 `pembayarans` sementara Postgres cuma 1; data terakhir SQLite 7 Juli vs Postgres 10 Agt. Diarsipkan ke `/root/ds-migrate/arsip/smart_lms-dev-20260707.db`. Pola umum: sebelum menyebut file "sampah", HITUNG BARISNYA dan bandingkan dengan produksi.

## Verifikasi pasca-operasi (owner peduli app tetap hidup)

```bash
curl -s -o /dev/null -w "api:%{http_code} " -X POST http://localhost:8085/api/auth/login -H 'Content-Type: application/json' -d '{}'   # 401 = hidup
curl -s -o /dev/null -w "web:%{http_code}\n" https://rezaulin.tech/
curl -s -o /dev/null -w "sim:%{http_code}\n" https://reviewtechno.me/    # app lain di box yang sama — jangan sampai kena
PGPASSWORD='smart123' psql -h 127.0.0.1 -U smart_lms_admin -d smart_lms -At -c "SELECT count(*) FROM students;"
```

## Hal yang tidak otomatis di server baru

- **Sesi WA** ikut terbawa tapi Baileys sering tetap `connected:false` → cek `http://localhost:3001/status`, scan QR bila perlu.
- **DNS A record** harus sudah mengarah ke IP baru sebelum certbot; kalau belum, restore.sh melewati SSL dan mencetak perintah certbot untuk dijalankan nanti.
- Bundle berisi kredensial (password DB, VAPID, sesi WA, token ShopeePay) — mode `600`, kirim via kanal privat, hapus setelah dipakai.
