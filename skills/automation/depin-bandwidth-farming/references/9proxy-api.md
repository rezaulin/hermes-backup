# 9Proxy API — quick reference (from official docs, 2026-08-29)

Source: `https://docs.9proxy.com/api-references/proxy-api` (GitBook). Raw markdown: append `.md` to any docs URL. OpenAPI JSON: embedded in the page as `{% openapi %}` pointing at a gitbook file-storage URL.

## GET /api/proxy (extract proxies)

Query params:
| Param | Type | Meaning |
|---|---|---|
| `num` | string | number of proxies to retrieve |
| `country` | string | country code (e.g. `US`, `VN`) |
| `state` / `city` / `zip` / `isp` | string | geo/ISP targeting |
| `port` | string | specific port; `ports` = comma list |
| `plan` | string | `premium`, `free`, … |
| `today` | boolean | only proxies updated today |
| `t` | string | response type: `1`=txt (ip:port per line), `2`=json |

Responses (JSON mode): `{"error":false,"message":"...","data":[{...,"ip","port","city","country_code","is_online"} ]}`
Errors: 400 invalid params · 402 insufficient balance · 404 no proxy found · 406 too many extractions.

## Definitions worth knowing

- `ProxyInfo`: id, city, ip, country_code, `is_online`, binding, …
- `ResponseTodayList` / `ResponseBase`: same envelope.
- `PortStats` (`port`, `online`), `PortInfo` (`address`, `public_ip`, `online`) — used by proxy-status/check endpoints.

## Auth & access modes (docs: getting-started/residential-proxy-by-gb/…)

- Two families: **Residential by IPs** (this extract API — one `ip:port` per proxy, ~24h life) and **Residential by GB** (fixed `host:port` gateway + user-pass — most VM-friendly, no source-IP lock).
- **User-pass username carries targeting/session** (making-requests.md):
  `subuser-country-<cc>-st-<state>-city-<city>-isp-<isp>-sst-<min>-ssid-<id>` → e.g. `subaccount-country-us-sst-15-ssid-device1`; password = sub-user password. `sst` = sticky (keep IP for N min), rotating otherwise.
- **Whitelist-IP mode** exists (auth by source IP, no creds) — fine for fixed-IP servers but has source-IP-lock caveat (see gateway notes); prefer user-pass for farms.
- Full doc index: `docs.9proxy.com/llms.txt` (GitBook; append `.md` to any page for raw markdown).

## AUTH MECHANISM (updated 2026-08-29 — the header form below this note is WRONG)

The proxy-extract endpoints authenticate with the API key as a **query parameter `api-key`**, NOT an HTTP auth header:

```
curl "https://api.9proxy.com/client/v1/proxy-connection/get-list?api-key=YOUR_KEY&limit=3&page=1"
```

- Docs (GitBook "Public API overview", `docs.9proxy.com/developers/public-api/overview.md`): production `api.9proxy.com`, sandbox `sandbox.9proxy.com`; the security scheme is defined as `api-key` query param; **no IP-whitelist / region restriction documented** for API calls (whitelisting in their docs means auth of your proxy *connection* by source IP, unrelated to API access).
- `Authorization: Token <key>` is NOT accepted by the public API — auth is query-param based. **`/api/proxy` listed under api-references is the legacy/OpenAPI-doc surface; the current path family is `/client/v1/...`** (get-list, whitelist CRUD, user-pass mgmt, account, billing…).

### Observed gotcha: Cloudflare 308 redirect-loop on some source IPs (2026-08-29)

From one box, EVERY request to `api.9proxy.com` (any path, any auth form, `-L` or not) came back as an infinite `HTTP/2 308` redirect to ITSELF (`location: <same URL>`) — i.e. the API was unreachable from that egress regardless of key validity. Docs state no API IP allowlist, so treat this as a Cloudflare/edge-region quirk rather than a key problem. **Debug path if the operator reports the same:**
1. Copy the exact request into their browser (home IP): `https://api.9proxy.com/api/proxy?num=1&country=US&t=2&api-key=<key>` — JSON `{"error":false,...}` = key valid & reachable; 308/loop = account/region issue.
2. Verify key exists & active: Dashboard → Account Settings → API Key (2FA required to (re)generate; key shown once at creation).
3. Ask which package is active (**By IPs vs By GB**) — determines which endpoint family & username format is correct; wrong family can itself cause edge weirdness.
4. If browser works but the VM still loops: route the API call through a residential proxy, or query from a different egress.

## Watchdog integration notes

- 9Proxy residential IPs live **~24h**, sometimes less → poll frequently, swap dead ones.
- Auth for extract: **`?api-key=<key>` query param** on `/client/v1/proxy-connection/get-list` (see above) — verify against current docs; formats drift.
- Fishing raw proxies from the txt (`t=1`) response is the simplest watchdog path: grep `ip:port` lines.
- The dashboard is a Next.js SPA (`9proxy.com`) — scrape-resistant i18n JSON; use `docs.9proxy.com` (GitBook) for docs, not the marketing site.
