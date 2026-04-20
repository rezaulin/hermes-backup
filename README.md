# Hermes Agent Profile Backup

Profil Hermes untuk reza. Auto-restore ke VPS baru.

## Install di VPS Baru

```bash
git clone https://github.com/rezaulin/hermes-backup.git ~/hermes-backup
cd ~/hermes-backup
bash install.sh
```

## Yang di-backup
- `config.yaml` — konfigurasi hermes
- `SOUL.md` — personality agent
- `skills/` — semua skill
- `memory/` — memory files
- `.env.example` — template API keys

## Setelah install
1. Edit `~/.hermes/.env` — isi API keys
2. Jalankan `hermes`

## Update backup
```bash
cd ~/hermes-backup
bash update.sh
git add -A && git commit -m "update" && git push
```
