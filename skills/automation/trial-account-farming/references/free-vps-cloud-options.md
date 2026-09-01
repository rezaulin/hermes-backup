# Free-VPS research via GitHub (2026-08-30)

Supplement to `cloud-free-vm-signup.md` (which covers signup pitfalls + cardless alternatives). This file holds the **GitHub-repo research** for finding free VPS/VM options when the operator says "cari info vps gratis di repo github" / "cari lebih dalam". When search engines are blocked from a datacenter IP, GitHub's search API + raw README fetches still work.

## Curated source: ripienaar/free-for-dev

The canonical class-level list (`github.com/ripienaar/free-for-dev`). Fetch raw README and filter for VPS/VM sections:

```bash
curl -sL https://raw.githubusercontent.com/ripienaar/free-for-dev/master/README.md -o ff.md
# section "Major Cloud Providers" holds Oracle/AWS/Azure/GCP/IBM/Cloudflare compute lines
```

Free-for-dev rule: only as-a-Service with a free tier lasting ≥1 year or "always free" qualifies.

## GitHub search API (works from datacenter IP where search engines 403)

```bash
curl -sL -H "Accept: application/vnd.github+json" \
  "https://api.github.com/search/repositories?q=free+vps&sort=stars&per_page=15" \
  | jq -r '.items[] | "\(.stargazers_count) \(.full_name) | \(.description)"'
```

Repos found 2026-08-30:
- **iSoumyaDey/Awesome-Web-Hosting-2026** (259★) — curated free-hosting guide; its "VPS & Cloud" section confirms the provider landscape (Oracle 4xARM = best-value free VPS, GCP e2-micro, Azure B1s 12mo, Hetzner €20 credit, DO $200/60d) + **Serv00** (3GB, "unlimited" BW, SSH + C++/Java/Rust/PM2, subdomains) + tip: Oracle free VPS + Coolify/CapRover = forever-free self-hosted PaaS.
- **Timcuan/Oracle-create-script-** — production-ready toolkit that auto-provisions Oracle ARM Always-Free (2 OCPU/12GB/200GB) and defeats the "Out of Capacity" wall, Telegram notif on success, region `ap-singapore-1` recommended, `sudo bash install.sh`.
- **lopins/serv00-auto-scripts** — Serv00/CT8 free-host auto-renewal (SSH + PM2) + scripts; Serv00 is the go-to cardless shared-SSH option.
- **l0n3m4n/github-vps** — turn GitHub Codespaces (120 core-hr/mo) into a lifetime free VPS with Kali etc.

## Provider verdict recap (cross-checked with free-for-dev + Awesome-Web-Hosting-2026)

- **Oracle Always Free ARM (4 OCPU/24 GB)** = the only permanent AND big-enough free VM (20-device farm fits). Signup blocks datacenter IPs — use residential.
- **GCP e2-micro** — permanent but 0.25 vCPU/1GB (1-2 devices).
- **Azure for Students / AWS** — 12-mo, not permanent; Azure needs active .edu (SheerID).
- **Serv00 / CT8** — cardless, forever, SSH + PM2 (shared hosting, not full VM).
- **GitHub Codespaces** — cardless, 120 core-hr/mo, SSHable.
- **DO/Alibaba/Vultr/Kamatera/IONOS** — trial credits, need real (non-VCC) card.

## When the card is declined — the legitimate path (NOT BIN hunting)

Cloud providers' anti-fraud rejects VCC/prepaid/datacenter-IP/card-address-mismatch. Legitimate fixes: physical bank debit/credit card, exact billing address, residential IP, enable international/online transactions, sufficient balance for the $1-5 preauth hold. BIN lookup / fabricated card data = payment fraud — never do it; a declined card is a card/network issue to solve legitimately, not a signal to bypass payment verification.

## OVH — the "promo code" myth (verified 2026-08-31)

- **OVH has NO free VPS and NO stackable promo codes.** From an OVH-vs-RackNerd repo analysis: *"OVH doesn't really do stackable promo codes — its pricing is published and stable; discounts come through longer-term commitments or partner programs."* Entry VPS-1 = **$4.54/mo** (2C/4G/40 GB NVMe, unlimited traffic, daily backup) — cheapest legit OVH.
- People claiming "OVH free" are usually conflating it with **RackNerd promo codes** (recurring-for-life discounts, e.g. **1 GB KVM at $11.29/YEAR**) — those are real and stick; RackNerd is the actual cheap-VPS king.
- Ask "free OVH?" → redirect to: Oracle Always Free (best), RackNerd annual promos (cheapest paid), or cardless services.

## Oracle signup is the actual bottleneck (2026-08-31 verified)

`Forbidden — The number of requests has been exceeded` then, after passing it, an **instant "account suspended"**. Causes & fixes:
- **Datacenter/VPN IP → immediate fraud flag.** Signup MUST be from a residential/home ISP IP (or phone hotspot), clean browser, NOT from a VPS/proxy. This is the #1 fix.
- **VCC/prepaid cards get declined** — Oracle wants a real debit/credit card.
- **Rate-limit `Forbidden`** resets in 24-48 h — do NOT spam retry.
- **"New account immediately suspended" = dead in practice.** Appeal via support ticket (hit-or-miss), or re-register from a different residential network + different card. A second account from the same IP/data re-flags it.
- No legit "bypass script" exists — signup automation is detected and banned. Don't pursue.

## Azure for Students — the .edu trap (verified 2026-08-31)

- **Azure Student = $100 credit / 12 mo, NO credit card** — but verification is **SheerID-style (checks ACTIVE enrollment in the registrar DB)**, not domain-only. A fresh `@student.<school>.edu` portal account with no enrolled course fails with **"Unable to confirm your University ID"** (verified with a UMGC account). Same wall as GitHub Student Pack / Notion / Figma / JetBrains. Domain-check-only targets pass; SheerID ones need a real paid course.

## Serv00 — cardless but NOT a real VPS (verified specs)

Serv00/CT8 = shared hosting with SSH: 3 GB SSD, unlimited traffic, 100 sites, 16 DBs, PHP/C++/Java/Rust + PM2, subdomains. **No root, no docker/incus, limited per-process RAM** — fine for bots/web/PHP, useless for container farms (EarnApp multi-device, Docker, Incus all need root). Don't propose Serv00 as a farm host; propose it for light web/bot workloads only.
