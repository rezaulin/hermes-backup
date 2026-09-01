# Residential proxy gateway auth modes & VM-fit pitfalls (tested 2026-08-29, Freestyle.sh VM egress `152.236.128.19` / AS49915 Megaport)

Different residential providers authenticate differently — and that decides whether they work from a datacenter/cloud VM at all. **Test from the target VM before building any automation.**

## The three auth modes (know which one your provider uses)

| Mode | How it works | VM-hostile? | Example |
|---|---|---|---|
| **Source-IP whitelist** | Gateway only accepts connections from IPs added in dashboard | **YES — datacenter/cloud IP often banned or requires whitelisting** | IPRoyal gateway (`geo.iproyal.com:12321`) |
| **Quota gating** | TCP connects, proxy responds but refuses once monthly GB exhausted | Not source-hostile, but quota dies fast on farms | Webshare free tier (10 proxies / 1GB/mo) |
| **User-pass auth (structured username)** | Fixed host:port gateway + username embeds region/session (`subuser-country-us-sst-15-ssid-x`) | **Most VM-friendly** — auth is in the credential, not the source IP | 9Proxy Residential by GB, Smartproxy, Oxylabs |

## IPRoyal specifics (paid residential, sticky 30-min sessions)

- Credential format: `geo.iproyal.com:12321:user:pass_category-country-us_session-XXXX_lifetime-30m` — sticky session = same exit IP for 30 min per session.
- Sessions tested from a **home/residential box: all alive**, 10/10 distinct **true residential ISPs** (T-Mobile, Charter, Verizon, AT&T, Cablevision, Cox) — perfect earnapp-grade exits.
- From the **Freestyle VM**, direct `curl -x http://user:pass@geo.iproyal.com:12321 https://api.ipify.org` **WORKS and returns the residential exit IP** (95.135.207.164 / Cox). So TCP + auth to the gateway is fine.
- BUT through **redsocks `type=socks5`**, gateway answers `Socks5 server status: connection not allowed by ruleset (2)` — IPRoyal's ruleset rejects the source (the VM). Diagnosis: it's **policy on the source IP**, not a config or quota problem. Fix options: whitelist the VM's egress IP in the IPRoyal dashboard, or use a provider with user-pass/no-source-lock (9Proxy).
- `geo.iproyal.com` may not resolve in the VM's default resolver — `getent hosts` from the VM; use a public resolver (`nslookup … 1.1.1.1`) to confirm.

## Webshare specifics (the `ip:port:user:pass` list format — catch this early!)

- The operator's first list (`31.59.20.176:6754:viirzqjm:8zzxubcotb8e`, … 10 entries) was **Webshare**, not 9Proxy — format `ip:port:user:pass`, provider identified by response header `X-Webshare-Error` / `X-Webshare-Reason`.
- All 10 had **exhausted monthly bandwidth**: TCP connect OK, HTTP CONNECT → `HTTP/1.1 402 Payment Required` + `X-Webshare-Reason: bandwidthlimit` (+ plain-text body "Bandwidth limit reached. Please upgrade…"). So the free tier was already consumed — **not dead proxies, just quota**.
- Also note the IP geos were **random (US/UK/ES/PT/JP)** — a provider list is only useful for EarnApp if it's US-targeted; check region per proxy, not just liveness.
- Webshare platform: `webshare.io` (docs 404 at `/proxy-api-documentation`), free tier = 10 proxies, paid rotating residential from ~$1.4/GB. Good dry-run provider only if quota is fresh.

## 9Proxy specifics

- Two product families: **Residential by IPs** (extract `ip:port` proxies, ~24h lifetime — the API in `9proxy-api.md`) and **Residential by GB** (fixed host:port gateway + **user-pass with structured username** — most VM-friendly, no source-IP lock).
- User-pass username anatomy (docs `getting-started/residential-proxy-by-gb/making-requests.md`):
  `subuser-country-us-st-<state>-city-<city>-isp-<isp>-sst-<session_min>-ssid-<session_id>`
  → e.g. `subaccount-country-us-sst-15-ssid-device1`. Password = the sub-user password. Session-type: `sst` sticky / rotating.
- **Whitelist-IP mode also exists** (auth by source IP, no user/pass) — fits fixed-IP servers but has the same VM-source caveat as IPRoyal; prefer user-pass for farms.
- Docs live on GitBook (`docs.9proxy.com`, append `.md` for raw markdown; `llms.txt` = full index). The marketing site is a scrape-resistant Next.js SPA; `proxy.9proxy.com` / `geo.9proxy.com` may not resolve everywhere — `api.9proxy.com` resolves via Cloudflare public DNS.
- Extract API: `GET /api/proxy?num=N&country=US&t=1` → text `ip:port` lines. **Auth = query param `?api-key=<key>`** (an `Authorization: Token` header is NOT accepted by the current public API — see `9proxy-api.md` — and the API itself may 308-loop from some egresses).
