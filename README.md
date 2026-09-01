# Hermes Agent Profile Backup + Source (v0.18.0)

Profil Hermes + source code (bukan latest, versi **v0.18.0** yang udah teruji).  
Restore ke VPS baru — **Hermes versi yang sama persis** dengan yang di-backup.

## Install di VPS Baru

```bash
git clone https://github.com/rezaulin/hermes-backup.git ~/hermes-backup
cd ~/hermes-backup
bash install.sh        # Hermes source + profile restore dalam 1 perintah
```

Setelah selesai:

```bash
1. Edit ~/.hermes/.env — isi API keys
2. hermes — langsung jalan, versi v0.18.0
```

## Yang di-backup
- `hermes-src.tar.gz` — source Hermes v0.18.0 (tanpa venv/node_modules — dibangun ulang pas install)
- `config.yaml` — konfigurasi hermes
- `SOUL.md` — personality agent
- `skills/` — 327 skill
- `memory/` — MEMORY.md + USER.md
- `.env.example` — template API keys

## Setelah install
1. `hermes profiles list` — cek profile
2. `hermes skills list` — cek 327 skill siap pakai
3. `hermes` — mulai ngobrol!
