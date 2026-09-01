# 9Proxy pricing & cheap-acquisition playbook (verified from official site 2026-08-29)

How to source 9Proxy residential cheaply — and the real economics behind Shopee/Tokopedia resellers selling "100 proxy Rp70k". All data scraped from `9proxy.com/pricing` Next.js payload + official GitBook docs.

## Official pricing — Residential by IP (unlimited bandwidth, sticky per-port proxies)

| Package | USD | per IP |
|---|---|---|
| 100 IP | $24 | $0.240 |
| 500 IP | $72 | $0.144 |
| 1000 IP + 500 bonus | $126 | $0.084 |
| 2500 IP | $210 | $0.084 |
| 5000 IP | $360 | $0.072 |
| 15000 IP | $720 | $0.048 |
| 25000 IP | $863 | $0.035 |
| 50000 IP | $1438 | $0.029 |
| 100000 IP | $2300 | $0.023 |
| 500000 IP | $8625 | $0.018 |

Retail baseline: $0.24/IP (100-IP package). Volume pricing dominates — per-IP falls 10x from 100 → 500k.

## Reseller packages (`forReseller:true` — verified-reseller only, from pricing payload)

| Package | USD | std | discount |
|---|---|---|---|
| 100000 IP | $2300 | $10000 | 77% |
| 200000 IP | $4140 | $20000 | 79% |
| 500000 IP | $8625 | $50000 | 82% |

## Promo / event deals (site banners 2026-08-29)

- **Reseller Deal: 93% OFF** — "Mega IP Package", 999,999 IPs, "Limited Stock for Resellers Only", "Limited-time pricing for verified resellers only".
- **Spin & Win**: BIG PRIZE wheel, up to 50% OFF (event window 25/11–09/12), + free IPs/GB rewards at $500 spend.
- **Black Friday Mega-Sale**: IP+GB combo bundles, "Combo Pricing From Just $25".
- **Crypto payment bonus (permanent, docs)**: pay via CoinPayments (BTC/ETH/LTC/TRX/USDT/Doge/DAI/BCH) → **+5% IP bonus** on the order. Stackable with everything else.

## Affiliate program (THE reseller source)

- Commission tiers by cumulative referred volume: L1 5% (0–$14,999), L2 10% ($15k–$39,999), L3 15% ($40k+). Permanent link on all future purchases/renewals.
- **Convert commission balance → Residential IPs at fixed $0.20/IP** (docs: "Exchange your available commission balance into Residential Proxy IPs at a fixed rate of $0.20 per IP"). This is below the 100-IP retail per-IP ($0.24) but the real win comes after 93%-off events + commissions.
- Withdrawals: $100 min, crypto / wallet credit / convert-to-IP.
- 60-day hold applies to wallet-funded purchases; direct card/crypto payments credit immediately.

## Share Code (official resale/transfer mechanism)

- By-IP: generate code = N IPs (min **5 IP/code**); by-GB: min **1 GB/code**.
- Enterprise-package codes: **180 days validity counted from recipient redemption** (regular packages: remaining package duration only).
- Codes can be pre-assigned to a recipient email (only they can redeem) or left open.
- This is the legit pipeline behind "proxy resellers": buy big (or earn affiliate) → generate Share Codes → sell codes/accounts.

## The Shopee "100 proxy Rp70k" economics

70k IDR ≈ $4.4 per 100 IP = **$0.044/IP** — below even the 500k reseller rate ($0.018 takes 500k min). Sellers reach it by **stacking**:

1. Buy during 93%-off reseller deals (or Spin&Win up to 50%) on huge packs → per-IP collapses to ~$0.003–0.01.
2. Pay crypto → +5% more IPs.
3. Farm affiliate commission on their own network → convert at $0.20/IP (or re-invest in promo packs).
4. Resell via Share Codes or sub-accounts; margin 2–10x even at Rp70k.

**What to verify before buying from a reseller (Shopee/Tokopedia/Telegram):**
- Is it 9Proxy **Residential by IPs** (sticky per-port ~24h) or by-GB user-pass? Ask for host:port:user:pass format and test it.
- Region per proxy — a list that looks alive can be GB/ES/PT/JP mixed (exactly what happened with the Webshare list); EarnApp needs US residential.
- Fresh quota (Webshare free-tier lists ship pre-exhausted — signature: `X-Webshare-Reason: bandwidthlimit` / "Bandwidth limit reached. Please upgrade…").
- Enterprise 180-day code vs regular package with remaining-duration expiry (code expiry after redemption matters).
- Legit resellers are 9Proxy-authorized ({ToS §5: reseller validation}); scam signal = no refund, no test, "IP langsung aktif" without creds.

## Quick price scrape (site is Next.js SPA — parse the serialized flight data)

```bash
curl -sL https://9proxy.com/pricing -A "Mozilla/5.0" -o p.html
grep -oE 'totalIps\\\\":(\\d+),\\\\"totalPrice\\\\":(\\d+)' p.html   # package list
grep -oE 'forReseller\\\\":true' p.html                              # reseller-only packs
grep -oE 'reseller_deal_93_off[^"]*":"[^"]*"' p.html                 # promo labels
```
