---
name: solana-meme-scanner
description: Scan & rank trending Solana meme token pools via GeckoTerminal free API. Score oportunitas + heuristik honeypot/rug risk. Bisa push notif Telegram. Basis untuk degen dashboard.
---

# Solana Meme Token Scanner (Degen Dash)

## Trigger
Jalanin saat user mau monitor meme token Solana, cari peluang entry, atau bangun notif signal Telegram.

## Struktur
- `/root/degen-dash/src/scanner.py` — scanner utama (rank + risk filter)
- `/root/degen-dash/data/last_scan.json` — snapshot hasil terakhir
- `/root/degen-dash/logs/` — log

## API (Gratis, no key)
- Trending: `GET https://api.geckoterminal.com/api/v2/networks/solana/trending_pools?page=N`
- Search pool: `GET .../search/pools?query=<symbol>&network=solana`
- Detail pool: `GET .../networks/solana/pools/<addr>`
- Basis quote ada di `attributes.base_token_price_usd`, volume `volume_usd.h24`, txns `transactions.h24.{buys,sells}`.

## Run
```bash
cd /root/degen-dash && python3 src/scanner.py 15
```

## Key konsep (penting, sampaikan ke user)
- **Winrate 90% itu mitos marketing.** Fokus net profit (RR/asymetric), bukan winrate. 50% win + RR 1:3 = untung.
- Skor = vol24 × buy_ratio × (0.5 + turnover). Warnings = konteks, BUKAN oracle: mcap<1M, micro-price, sell/buy>0.9 (dump pressure), tanpa data tx.

## RugCheck (honeypot/risk) — gratis no key
- `GET https://api.rugcheck.xyz/v1/tokens/<MINT>/report/summary` → `score_normalised`, `lpLockedPct`, `risks[{name,level: danger|warn}]`, `tokenType`.
- Verdict logic di scanner: danger batre → DANGER; lp<60 → LP-LOW; score_n>5000 → RISKY; else OK.
- **Rate limit ketat (~429 cepat sekali). WAJIB cache per-mint** ke `data/rugcheck_cache.json` + jeda 0.3s antar panggilan. Run kedua bareng cache = 0.1s vs 30s pertama.

## Pitfall
- Birdeye butuh API key (401 tanpa key). GeckoTerminal gratis.
- Robinhood public endpoint di-restrict (quote kosong) — jangan andalkan; pakai GeckoTerminal/alt source buat data harga.
- `market_cap_usd` sering null/"0.0" — guard dengan usd() lalu fallback 0.
- **Mint token ADA di `relationships.base_token.data.id` (format `solana_<ADDRESS>`), strip prefix.** BUKAN `attributes.base_token.address` (null).
- API agak lambat (1-2 detik/panggil) — jangan loop ketat; cache snapshot ke file.

## Next (belum dibangun)
- Honeypot detector beneran (butuh RPC/CPI — Butuh key Solana RPC atau pakai RugCheck API).
- Auto-sniper launch (membutuhkan wallet + RPC).
- Notif Telegram (butuh bot token via @BotFather + chat id dari user).
- Dashboard web di VPS.
