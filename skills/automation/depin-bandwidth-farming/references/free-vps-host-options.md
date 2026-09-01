# Free VPS / cloud-host landscape for farm hosting (researched 2026-08-31)

When the farm needs a host (VPS dies / quota burned / need more nodes), this is the
verified landscape of free and ultra-cheap options. Prices/limits drift — re-verify
before committing, but the classification (permanent vs trial vs card-required) is stable.

## VPS sizing rule (verified from two deploys 2026-08-31)

| Host spec | Max devices (EarnApp farm) |
|---|---|
| 2C / 4GB | **5** (comfortable; 6-8 pushes it) |
| 4C / 8GB | 10-20 |
| 4C / 24GB ARM | 20+ |

Set `DEVICE_COUNT` in farm.env to match the host — don't assume 9/20 from the previous VPS.

## Permanent free (no expiry)

| Provider | Spec | Card? | Notes |
|---|---|---|---|
| **Oracle Cloud Always Free** | ARM Ampere A1 up to **4 OCPU / 24GB / 200GB** (+2x 1C/1G AMD) | ✅ (verification only) | 🏆 Best free farm host. Idle instances get reclaimed — keep load. Signup notoriously picky: "Forbidden — requests exceeded" = datacenter/VPN IP flagged → register from home ISP + clean browser + real debit card, wait 24-48h between retries. Toolkit `Timcuan/Oracle-create-script-` automates ARM provisioning (needs Tenancy OCID + Stack OCID + Telegram bot token — card+phone still user-side). |
| **Google Cloud** | e2-micro (0.25C/1GB), 30GB, US regions | ✅ | Small — 1-2 devices only |
| **IBM Cloud Lite** | 256MB | ✅ | Too small for farm |

## Trial credits (12 months / one-shot)

| Provider | Credit | Card? | Notes |
|---|---|---|---|
| **Azure for Students** | $100 / 12mo + 750h B1s | ❌ **No card** | Requires **verified ACTIVE university enrollment** (SheerID-style). A provisioned .edu portal account WITHOUT an enrolled course is rejected: "Unable to confirm your University ID". Domain-check-only .edu passes AWS Educate basics but NOT the paid-benefit vouchers. |
| **AWS** | t2.micro 750h/mo | ✅ | 12 months, then paid |
| **Alibaba Cloud** | $300 | ✅ | 1-3 months; region Asia (Singapore/Jakarta) low latency |
| **DigitalOcean** | $200 | ✅ | 60 days; VCC/prepaid cards often declined by anti-fraud — real debit card + matching billing address |
| **Vultr / Linode** | $100 | ✅ | 30-60 days |
| **Kamatera** | 30-day trial | ✅ | |
| **OVH** | **no real promo codes** | ✅ | OVH doesn't do stackable coupon codes (unlike RackNerd). Cheapest = VPS-1 $4.54/mo (2C/4G/40GB NVMe, unlimited traffic, daily backup). GitHub Student Pack OVH credit was REMOVED. "Free OVH" claims online = old promos / affiliate overclaim. |

## Card-free (no credit card at all)

| Provider | What | Notes |
|---|---|---|
| **Serv00** | Shared hosting, **3GB SSD, SSH + PM2**, 100 sites, 16 DBs, unlimited BW | Register with email only. NOT a real VPS (no root, no docker/incus) — good for light apps/bots, NOT for farm. |
| **GitHub Codespaces** | 120 core-hrs/mo Linux env + SSH | Card-free, monthly reset; per-session (not persistent 24/7) |
| **Koyeb** | Free nano instance (512MB/1vCPU), no sleep | Card-free |
| **Hax.co.id** | Free LXC VPS (small), register email | Indonesian; small spec |
| **Freestyle.sh** | Free tier: 100 vCPU-hrs + 200 GiB-hrs/mo, reset monthly | User's existing infra. 4C/8G VM = ~25h/mo; 2C/4G = ~50h/mo. Pause = $0. See skill `freestyle-vms`. |

## Verifier classification (which .edu unlocks what)

- **Domain-check** (email suffix only): AWS Educate basics, Google Workspace for Education, assorted small trials → passes with any `.edu`/`@student.*.edu` address.
- **SheerID / registrar DB check** (active enrollment): GitHub Student Pack, Notion, Figma, JetBrains, **Azure for Students**, AWS paid benefits → REJECTED without an enrolled paid course.

## Signup anti-fraud lessons (Oracle / DO / Azure)

1. "Forbidden — requests exceeded" on Oracle = IP fingerprint flagged (datacenter/VPN). Use home ISP / phone hotspot, fresh browser profile, real debit card. No script bypasses this — scripting makes it worse.
2. DO/Vultr decline VCC/prepaid virtual cards by design. Real physical debit card + billing address EXACTLY matching the bank record.
3. Azure Student needs the .edu to have an ACTIVE course enrollment — a fresh portal account won't pass; don't burn time re-submitting.
4. Cloud provider free tiers are one-account-per-person — a second account from the same IP/data = instant fraud flag.
