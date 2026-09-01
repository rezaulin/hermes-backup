# Cloud free-VM / free-VPS landscape (researched 2026-08-30, official pages)

Operator's recurring need: free compute for farm nodes, sandboxes, and trial-account automation, when paid VPS or Freestyle quota is exhausted. Prices/limits drift — re-verify before relying on them.

## Ranking (best → worst for "permanent free VM")

### 🥇 Oracle Cloud Always Free (PERMANENT, best specs)
- ARM Ampere A1: **up to 4 OCPU / 24 GB RAM** (usable as one VM or split into up to 2)
- Plus 2x AMD VMs (1/8 OCPU, 1 GB each)
- 200 GB block volume, 10 TB egress/month, 2 IPv4 free
- ⚠️ Credit card REQUIRED at signup (not charged within free limit)
- ⚠️ Instances reclaimed when idle — keep a heartbeat/activity
- ⚠️ Signup anti-fraud: datacenter/VPN IPs blocked with "Forbidden — requests exceeded". Signup from residential IP, incognito, wait 24-48h on rate-limit.
- Best permanent free VM big enough for a 20-device farm.

### 🥈 Google Cloud (PERMANENT, small)
- e2-micro (0.25 vCPU / 1 GB), 30 GB disk, permanent
- US regions only: us-west1 (Oregon), us-central1 (Iowa), us-east1 (SC)
- Credit card required. Small — 1-2 light devices.

### 🥉 12-month VM free (card required)
- **AWS**: t2.micro/t3.micro 1C/1G, 750 hr/mo, 12 mo
- **Azure**: B1s / B2pts v2 (ARM) / B2ats v2 (AMD), 750 hr/mo, 12 mo (new customers)
- **Azure for Students**: $100 credit + 750 hr/mo B1s, 12 mo — **NO credit card**, but requires ACTIVE .edu enrollment (SheerID). 12-mo expiry, education use only.

### Signup credit (card required, one-time)
- **DigitalOcean**: $200 / 60 days
- **Alibaba Cloud**: ~$300 / 1-3 mo
- **Vultr**: $100 / 30 days
- **Linode (Akamai)**: $100 / 60 days
- **Kamatera**: 30-day free trial
- **IONOS**: 30-day money-back
- **Hetzner**: no free tier (cheap, not free)

### 🆓 NO card at all
- **Hax.co.id** — free LXC VPS (root), email-only signup, small spec, unmetered. Indonesian.
- **GitHub Codespaces** — 120 core-hr/mo cloud dev env, SSH-able.
- **Koyeb** — 1 free instance (512MB/1vCPU).
- **Render** — free web service (512MB) + cron.
- **Fly.io** — small free allowance.
- **Google Cloud Shell** — Linux shell, 5GB disk, 60 hr/wk.
- **Cloudflare Workers** — 100k req/day edge compute.
- **Freestyle.sh** — 100 vCPU-hr + 200 GiB-hr/mo, resets monthly, API-key auth (operator already uses this).

## Signup failure modes (verified this session)

| Symptom | Root cause | Fix |
|:--|:--|:--|
| "Card declined" | VCC/virtual/prepaid card rejected; AVS mismatch; datacenter IP; no intl transaction | Use physical debit/credit card; exact billing address; residential network; enable intl/online |
| Oracle "Forbidden — requests exceeded" | IP rate-limit from datacenter/VPN or prior failures | Residential IP, incognito, wait 24-48h |
| Azure "Unable to confirm your University ID" | SheerID checks ACTIVE enrollment, not .edu possession | Enroll a real paid course, or use domain-check targets only |
| Provider 403 on page load | Datacenter IP blocked | Signup from home ISP / mobile tethering |

## Safety boundary
Never source BINs or fabricated card data to pass payment verification for free-credit claims — that is payment fraud. Legitimate paths: physical card + correct AVS + residential IP, or cardless options (Azure Student w/ real enrollment, Hax.co.id, GitHub Codespaces, Koyeb, Freestyle).
