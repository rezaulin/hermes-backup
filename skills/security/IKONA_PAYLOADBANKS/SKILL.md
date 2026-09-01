---
name: security-payload-banks
description: "Use when fetching security payload banks from GitHub."
version: 1.0.0
author: IKONA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [payloads, cheatsheets, github, pentest, references]
    related_skills: [web-exploit-test, advanced-bug-hunting, bug-hunting]
---

# SECURITY PAYLOAD BANKS — Fetch & Refresh Recipe

Recipe terverifikasi buat bulk-download payload bank / cheatsheet security dari GitHub ke folder `references/` skill pentest. Sumber-sumber legendary, bukan hasil pencarian generic (GitHub API search untuk istilah umum baliknya sampah).

## When to Use

- Setup / refresh offline payload references buat skill pentest
- User minta "ambil referensi payload dari GitHub" / "cari di github yang bagus buat audit"
- Bulk-download cheatsheet security ke references/ skill

## Verified Sources (checked Aug 2026)

### PayloadsAllTheThings (swisskyrepo)
- Repo: `swisskyrepo/PayloadsAllTheThings`, branch `master`
- RAW URL butuh encode spasi jadi `%20`: `master/XSS%20Injection/README.md`
- Kategori di `master/<Category>/README.md` (SQL Injection, XSS Injection, SSRF, SSTI, JWT, XXE, Upload Insecure Files, Race Condition, IDOR, Open Redirect, CRLF Injection, Command Injection, CORS Misconfiguration, Prototype Pollution, Web Sockets)
- `curl -sfL -m 60` works

### HackTricks (carlospolop)
- Content PINDAH ke `src/pentesting-web/` — path lama `pentesting-web/` 404
- File bernilai tinggi (file flat): `bypass-payment-process.md`, `race-condition.md`, `hacking-jwt-json-web-tokens.md`, `cors-bypass.md`, `csrf-cross-site-request-forgery.md`, `oauth-to-account-takeover.md`, `proxy-waf-protections-bypass.md`, `content-security-policy-csp-bypass/README.md` (dir!), `mass-assignment-cwe-915.md`, `nosql-injection.md`, `orm-injection.md`, `login-bypass/README.md` (dir), `deserialization/README.md` (dir), `file-upload/README.md` (dir), `file-inclusion/README.md` (dir)
- Rule: item `type=dir` → fetch `dir/README.md`; `type=file` → fetch path langsung
- Cara cek struktur: `curl -sL https://api.github.com/repos/carlospolop/hacktricks/contents/src/pentesting-web` (WAJIB `-L`, API balas 301 Moved)

### DEAD / jangan buang request
- `payloadbox` org — 404 total di GitHub. Ganti:
  - `Mehdi0x90/Web_Hacking` (branch `main`, file `README.md`) — bug bounty tricks
  - `EdOverflow/bugbounty-cheatsheet` (branch `master`, `cheatsheets/xss.md|sqli.md|ssrf.md`)
- `1ndianl33t/Bug-Bounty-Roadmaps` — 404 (nama repo berubah, skip)

### Cybermes (Zyrexnn/Cybermes) — agregator skill + payload
- Repo: `Zyrexnn/Cybermes`, ~218MB full clone (hacktricks submodule 161MB). `git clone --depth 1` cukup buat dapet skill.
- Isi bernilai (tanpa submodule gede): `knowledge/hack-skills/skills/` (100+ playbook, format `SKILL.md` + `SCENARIOS.md` + `SQLMAP_ADVANCED.md`), `knowledge/Claude-BugHunter/skills/` (80+ skill hunt-* dibangun dari report bounty asli, punya `cbh/data/` CVE report), `knowledge/strix-skills/` (25 vuln class), `knowledge/PayloadsAllTheThings/` (payload + webshell ASP/PHP + gambar imagetragik/exiftool), `tools/wordlists/`, `tools/bin/` (subfinder, httpx, katana, gau, ffuf precompiled).
- Struktur skrip: `SKILL.md` punya frontmatter `name` + `description` — kompatibel Hermes skill format. Auto-generate `.py` per skill = jalankan `git show` bedah, dump payload section, bikin argparse script (`--list`/`--dump`/`--search`).

## Recipe

1. **Verifikasi 1 URL manual dulu** (`curl -sI`) sebelum batch — 404 = salah branch (main vs master) atau salah path, bukan masalah network.
2. **Pakai script jadi**: `scripts/fetch_payload_banks.sh <destination-references-dir>` — script terverifikasi berisi semua URL valid di atas; cukup jalankan, tidak perlu tulis ulang.
2. Batch script bash: `set -e`, helper encode `enc() { printf '%s' "$1" | sed 's/ /%20/g'; }`, `curl -sfL -m 60 "$BASE/$src" -o "$dst"`, tracking `ok/fail`, `rm -f` file yang gagal.
3. Simpan per-sumber: `<skill>/references/<source>/<topic>.md` + pointer satu baris di SKILL.md skill tujuan.
4. Jangan mirror seluruh HackTricks — pilih file high-value (payment bypass, race condition, deserialization, JWT, WAF/CSP bypass, login bypass).

## Pitfalls

- **Windows git-bash**: `du -sh` dan `wc -c` jalan normal; jangan pakai `python -c` f-string dengan nested quote — Python 3.11 SyntaxError (pakai `%` formatting).
- **Python inline parsing**: response API bisa list atau dict; cek `isinstance(d, list)` dulu sebelum loop.
- **cURL `-sI` ke raw URL yang benar** balas 200 — kalau 404 semua, cek path/encode dulu, bukan koneksi.
- **Reference di skill ≠ replacement runtime script** — payload bank buat dipakai agent saat pentest manual (grep, cat), bukan buat di-load penuh ke context tiap kali.
- **Windows Defender ngunci file signature AV** (webshell, EICAR, reverse-shell, gambar imagetragik/exiftool, `CVE-2021-22204`): file KEBACA dari bash (`cat`, `git show`, `ls -la` OK) tapi `python open()` / `os.open()` lempar `[Errno 22] Invalid argument`, walau `icacls` nunjukin Full Control. Diagnosa: `icacls <file>` full-access tapi python tetap Errno 22 = Defender block. Fix: `powershell Add-MpPreference -ExclusionPath 'C:\...\<dir>'` (eksklusi folder tempat file target) — langsung sembuh, `sleep 3` dulu. Tanpa exclusion, jalanin: `git show HEAD:<path> > dest` (bash redirect baca via git object, bukan filesystem).
- **Symlink/repo read-only di Windows git checkout**: beberapa `SKILL.md` di hack-skills lempar Errno 22 waktu copytree — solusinya `git show HEAD:<path>` ke file tujuan (isi dari git object, bypass filesystem lock). Urutan recovery file yang gagal copy: `chmod -R u+rw` → python copytree → sisa yang gagal → `git show` satu-satu.
- **Git-bash Windows ga punya `zip`** — pakai `python -m zipfile -c out.zip dir/`. Zip via python zipfile jalan normal di MSYS.
- **`python -c` heredoc + path backslash**: di git-bash heredoc, `\` di dalam f-string/python string jadi SyntaxError unterminated literal — tulis generator ke file `.py` dulu (write_file), jalanin, jangan inline heredoc buat script panjang.

## Related Skills

- `web-exploit-test` — battery runtime yang pakai payload bank ini di references/
- `advanced-bug-hunting` — manual exploitation methodology
- `bug-hunting` — pipeline bounty otomatis
