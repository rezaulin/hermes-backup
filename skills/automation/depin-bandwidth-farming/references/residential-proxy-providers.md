# Residential proxy providers for bandwidth-farming (researched 2026-08-29)

When a DePIN/bandwidth app (EarnApp etc.) rejects the VM's datacenter egress (`ip_type.dch`), the fix is residential/ISP egress via a proxy per device. This is the provider landscape for that job. Prices scraped from vendor homepages; **re-verify before buying** — they drift.

## Quick picks by scenario

| Need | Pick |
|---|---|
| Cheapest pay-per-GB + API for auto-swap | **ProxyCheap** (~$0.78/GB) |
| Free test of the whole architecture | **Webshare** free plan: 10 static proxies, full API |
| Most developer-friendly API (list/rotate/delete) | **Webshare** paid |
| Clean IP pool / enterprise anti-ban | **IPRoyal**, **Smartproxy (Oxylabs)** |
| Very large scale, US state targeting | **SOAX** (volume tiers down to ~$0.5/GB) |
| Already has balance | **9Proxy** (the operator's current choice) |

## Provider table

| Provider | ~Price | Model | Extract API | Notes |
|---|---|---|---|---|
| **ProxyCheap** | $0.78/GB | pay-per-GB, sticky sessions | ✅ (API docs site) | cheapest, big US pool, good farm fit |
| **Webshare** | $1.40/GB (monthly), $2.75 | plan-based, static + rotating | ✅ full API | **free tier = 10 proxies** (great for dry-run); API lets you list/rotate/delete per-proxy |
| **IPRoyal** | ~$1.75–2/GB | pay-per-GB | ✅ | stable, US ok |
| **Smartproxy (Oxylabs)** | ~$2–2.25/GB | pay-per-GB | ✅ | enterprise anti-block, pricier |
| **SOAX** | $0.5–2.2/GB (volume) | pay-per-GB | ✅ | US state/city targeting, scaling discounts |
| **Rayo (Rayobyte)** | ~$0.30–0.50/GB | pay-per-GB / packages | ✅ | residential + datacenter mixes |
| **PacketStream** | ~$0.10/GB | pay-per-GB, rotating | ⚠️ limited | cheapest by far but IPs are **shared/dirty → many already banned**; EarnApp-grade apps will struggle |
| **NetNut** | enterprise quote | — | — | ISP-based; overkill/expensive for farming |

Price scrape detail (2026-08-29): Webshare homepage shows `$1.4`/GB + "unlimited" plans; Smartproxy `$2`–`$2.25`/GB; Rayobyte residential ~`$0.30–0.50`; SOAX pricing page shows volume tiers `$5.00` → `$0.50`/GB (bigger = cheaper); PacketStream `$0.10`/GB mention. Try `curl -sL <site> | grep -oE '\$[0-9.]+ ?/ ?GB'` as a quick scrape.

## Selection rules for EarnApp-like apps

- **Don't pick the cheapest.** PacketStream-grade shared IPs are pre-banned on IP-sensitive platforms. Clean-pool providers (Webshare free tier first, then ProxyCheap/IPRoyal) beat raw cost.
- **US region is table stakes** — all of these do US; 9Proxy/SOAX/Webshare add US state/city targeting if ever needed.
- **API availability decides the watchdog** — the auto-swap watchdog needs an extract endpoint (`?num=N&country=US&t=1` style). Providers without one force manual rotation.
- **Sticky vs rotating matters:** for "1 device = 1 IP for as long as possible", prefer sticky/static per-port proxies (9Proxy model); rotating-backends that change IP mid-session are wrong for node farming.

## Free trials / free tiers (scraped live 2026-08-29 — nearly all are global, NOT region-locked)

| Provider | Free offer | Credit card? | Verdict for farm dry-run |
|---|---|---|---|
| **Webshare** | **10 proxies free, permanent**, 1GB/mo | ❌ | best free dry-run (but 1GB cap vanishes fast — the 402 `bandwidthlimit` signature) |
| **ProxyCheap** | **7-day trial** (static residential & DC) | ? | best for a full week of validation before paying |
| **Bright Data** | free trial | ❌ | big but sales-heavy onboarding |
| **Oxylabs** | free trial (datacenter) + "free proxies" | — | trial GB small |
| **Smartproxy** | **free trial per product** | ? | several GB free |
| **PacketStream** | trial | — | IPs dirty — skip for EarnApp-grade |
| **Rayobyte / ProxyRack** | free trial | — | ok for validation |
| **ScrapingAnt** | 10,000 credits/mo free | ❌ | scraping API, not general proxy — skip |
| **ZenRows** | 5,000 credits/mo free | ❌ | scraping API — skip |
| **9Proxy** | **NO trial** (must buy; only BF-spin-win promos) | — | use ProxyCheap 7-day or Webshare free for validation instead |

Key takeaway: trials are global, not region-dependent — pick by provider policy (ProxyCheap 7-day > Webshare perm-free > Smartproxy). For a 10–20 device farm the validated architecture then runs on a paid By-IPs package (see SKILL.md).

## Site-reachability probe (2026-08-29, from this box)

`iproyal.com` → HTTP 403 (Cloudflare bot-wall; scrape via other routes), all others (`9proxy.com`, `webshare.io`, `proxy-cheap.com`, `proxy-sale.com`, `packetstream.io`, `soax.com`, `netnut.io`, `smartproxy.com`, `rayobyte.com`) → 200.
