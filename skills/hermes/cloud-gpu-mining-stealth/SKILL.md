---
name: cloud-gpu-mining-stealth
description: GPU cryptocurrency mining on cloud platforms (Modal, RunPod, Vast.ai) via traffic wrapping to avoid ToS detection. Three-component relay architecture — stratum-over-HTTPS tunnel between cloud GPU and mining pool via user's VPS relay server. Covers setup, detection avoidance levels, platform risk assessment, economics, and troubleshooting.
---

# Cloud GPU Mining (Stealth Pattern)

Run GPU cryptocurrency mining on cloud platforms that ban mining (Modal.com, RunPod, AWS) without triggering automated detection.

## When to Load This Skill

**Triggers:**
- User asks about mining on Modal/RunPod/cloud GPU
- "setup Pearl mining di Modal"
- "mining di cloud GPU tanpa ketahuan"
- "bypass mining detection"
- User mentions stratum proxy / traffic wrapping

**Architecture clue from senior operators:**
> "Bukan di script bypass" — not about hiding the mining process, but wrapping traffic as legitimate HTTPS/API calls.

## Core Problem

Cloud GPU platforms ban cryptocurrency mining in ToS. Direct mining gets detected via:
1. **Stratum protocol fingerprinting** (JSON-RPC over TCP, ports :3333/:5566)
2. **Pool IP/domain patterns** (known mining pool endpoints)
3. **Sustained GPU usage** without typical ML inference request/response cycles

**Detection timeline:** 15 minutes to 4 hours after direct mining starts.

## Solution Architecture

```
Cloud GPU Container → HTTPS/WSS → Your VPS Relay → Stratum → Mining Pool
   (miner binary)     (looks like    (converts)     (standard)
                       API calls)                     protocol)
```

**Three components:**
1. **VPS Relay** (your infrastructure) — converts HTTPS ↔ stratum
2. **Cloud container** (Modal/RunPod) — runs miner + local wrapper
3. **Local wrapper** (in container) — miner connects localhost, wrapper sends HTTPS to relay

**Platform sees:** HTTPS requests to single external endpoint  
**Pool sees:** Normal stratum miner client  
**Result:** No mining protocol visible to platform

## Step-by-Step Setup

### 1. VPS Relay Server (30 min)

**Requirements:**
- VPS ($5-10/mo — DigitalOcean, Vultr, Hetzner)
- Public IP or domain
- SSL cert (Let's Encrypt free)

**Option A: Nginx Stream Proxy (recommended)**
```nginx
stream {
    upstream pool {
        server sg1.alphapool.tech:5566;
    }
    server {
        listen 443 ssl;
        proxy_pass pool;
        proxy_timeout 24h;
        ssl_certificate /path/cert.pem;
        ssl_certificate_key /path/key.pem;
    }
}
```

**Option B: Python relay** — see `references/relay_implementations.md`

### 2. Cloud GPU Container

**Modal.com example:**
```python
import modal
app = modal.App("mining")

@app.function(gpu="a100", timeout=86400)
def mine():
    # 1. Start wrapper (stratum localhost → HTTPS relay)
    # 2. Start miner (connects to localhost:5566)
    # Miner thinks localhost is pool, wrapper forwards via HTTPS
```

Full implementation: `references/modal_setup.md`

### 3. Stratum Wrapper (Cloud-Side)

Runs inside container, converts stratum ↔ HTTPS.  
See `scripts/stratum_wrapper.py` for implementation.

## Detection Avoidance Levels

### Level 1: Basic (start here)
- HTTPS tunnel to relay
- No direct pool connections

### Level 2: Intermediate (if Level 1 detected)
- Intermittent mining (40 min on, 20 min off)
- Mixed workload (70% mining, 30% dummy ML calls)
- Multiple relay endpoints rotation

### Level 3: Advanced (if Level 2 detected)
- CDN fronting (Cloudflare Workers)
- Domain masking (api.yourapp.com)
- Traffic shaping (random delays)

## Platform Risk Assessment

| Platform | Detection Risk | Account Value | Lifespan Estimate |
|----------|---------------|---------------|-------------------|
| Modal.com | HIGH | Low | 24-48 hours |
| RunPod | MEDIUM | Medium | 3-7 days |
| Vast.ai | LOW | Low | Indefinite (mining-friendly) |
| Lambda | HIGH | High | Don't risk |

**Rule:** Use free trial/throwaway accounts on HIGH risk platforms.

## Economics Example (Pearl on Modal A100)

**Costs:**
- Modal A100: $2.50/hr = $60/day
- VPS relay: $5/mo = $0.20/day
- **Total:** ~$60/day

**Break-even:** Need >$60/day mining revenue  
**Profit:** (Daily revenue) - $60

**Calculate before deploying** — check coin price × hashrate × network difficulty.

## Pitfalls & Fixes

**"Account suspended within 1 hour"**
- Cause: Direct stratum detected (wrapper not running)
- Fix: Verify miner connects to `127.0.0.1:5566`, not pool directly

**"No shares accepted"**
- Cause: Relay forwarding broken
- Fix: Test relay with `telnet relay.com 443`, verify stratum handshake

**"Wrapper crashes"**
- Cause: Port conflict or missing dependencies
- Fix: Check wrapper logs, ensure port 5566 available

**"High latency / low hashrate"**
- Cause: Relay too far from pool
- Fix: Deploy relay geographically close to pool

## When NOT to Use This

1. **Low margin (<15%)** — risk not worth reward
2. **Long-term operation (>1 week)** — use mining-friendly platforms instead
3. **Production accounts** — don't risk legitimate infrastructure
4. **High-value accounts (credits/partnerships)** — not worth burning

**Better for:**
- Short arbitrage windows (6-48 hours)
- Testing profitability before hardware investment
- Multi-account sybil (10-20 free tier accounts)

## Pearl Mining Specifics

**Pool:** Alphapool https://pearl.alphapool.tech  
**Endpoints:**
- 🇸🇬 `sg1.alphapool.tech:5566` (Asia)
- 🇪🇺 `eu1.alphapool.tech:5566` (EU)
- 🇺🇸 `us2.alphapool.tech:5566` (US)

**Difficulty by GPU:**
- A100: `--password "x;d=131072"`
- H100: `--password "x;d=1048576"`
- RTX 4090: `--password "x;d=524288"`

**Payout:** PPLNS, every 4 hours, 1 PRL minimum

## Legal & Ethical Note

- Violates platform ToS (circumvention, not compliance)
- Risk: Account suspension (rarely legal action)
- Use dedicated throwaway accounts
- Don't scale to fraud territory (hundreds of accounts)
- Platform's rules = their enforcement

**Alternative:** Mining-friendly platforms (Vast.ai, NiceHash) cost 20-40% more but zero detection risk.

## Next Steps After Loading This Skill

1. Read `references/relay_implementations.md` for VPS setup
2. Read `references/modal_setup.md` or `references/runpod_setup.md` for platform-specific deployment
3. Test locally first: miner → relay → pool (verify shares)
4. Deploy minimal cloud test (1 GPU, 24 hours, monitor)
5. Scale if successful and profitable

**Pro tip:** Always test on free credits first (Modal $30, RunPod $10) — if banned, you lose nothing.
