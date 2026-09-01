# ShopeePay Partner API Gateway — audit verdict & API notes

Repo: `ahmadzakiyox/shoppepay-api-gateway` (audited + deobfuscated 2026-08; deobfuscated copy was at /tmp/deobf/deobfuscated.js).

## Audit verdict (full source read, 596 lines)

**CLEAN — no backdoor/exfiltration.** Obfuscation was IP protection, not malware.
- Outbound hosts: `shopeepay.shopee.co.id` (mutasi read), `api.telegram.org` (optional alerts), `api.qrserver.com` (QR image render — third party sees QRIS string; not secret but flag it).
- No eval/Function/child_process/fs anywhere → can't touch disk or spawn processes.
- SHOPEE_TOKEN flows ONLY to shopeepay.shopee.co.id request bodies.
- Read-only by design: filter `serviceList:[1,3]`, only get-transaction-list/detail. Cannot move funds even if token leaks.
- CORS `origin:*` on the gateway itself — its only real protection is X-API-Key.
- Bug: `/check-payment` `startTime` expects **epoch SECONDS** (ms → year-58609 log entries).

## How it works (for integration)

- Merchant session token from DevTools: partner.shopee.co.id → Network → `get-transaction-list` → payload.data.metadata.token (starts with `B:`). Token check every 5min; dead token → Telegram alert + suggest `POST /update-token`.
- Dynamic QRIS: parse static QRIS TLV, inject amount into Tag 54 (after Tag 53 if absent), recompute CRC16-CCITT, expiry 15min.
- Verification is CLIENT-POLLED: store polls `/check-payment {amount, startTime}` only while a checkout page is open → anti rate-limit by design (zero calls when store quiet).
- Dedupe: in-memory Map of claimed transactionIds, TTL 24h — **lost on restart**; integrators MUST also dedupe in their own DB.
- Multi-tenant: per-request token override via header `X-Shopee-Token`.

## Endpoints (all except / and /api/health need X-API-Key)

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | liveness (public) |
| `GET /token-status` | `{data:{token_status:"valid"\|"invalid"}}` |
| `POST /update-token` `{token}` | hot-swap Shopee token |
| `POST /create-qris` `{amount}` | → `{data:{qris_url, amount, expires_at:"2006-01-02 15:04:05", expires_in}}` |
| `GET /qr/:id` | 302 → api.qrserver.com PNG |
| `POST /check-payment` `{amount, startTime}` | → `{paid, transaction:{transactionId, amount, status, time, issuer}}` |
| `GET /transactions` / `/transactions/all` | list / full month (paged, 500ms delay) |
| `GET /api/logs` | circular 100-entry RAM log |

## Merchant requirements (for tenants)

1. ShopeePay Partner merchant account (KTP + usaha, free) — personal ShopeePay CANNOT do this (no QRIS static, no mutasi API).
2. QRIS statis issued to that merchant → `.env QRIS_STATIC`.
3. Token from DevTools (above) → `.env SHOPEE_TOKEN`.
4. Funds land 100% in the merchant's own ShopeePay balance; gateway never touches money.

## Hardening when deploying for a tenant

- Run DEOBFUSCATED source (webcrack output) so tenant can audit what runs.
- Bind localhost or firewall; egress allow only shopeepay.shopee.co.id + api.telegram.org (+ api.qrserver.com unless QR render swapped for local `qrcode` lib).
- Strong random API_KEY; .env chmod 600; dedicated merchant account separate from main ops.
- Reconcile daily: paid invoices vs `/transactions/all` totalNetSales.

## Sandbox test recipe

Dummy `.env` (token `B:dummy`, API_KEY testkey123, PORT 4455), `node server.js` via background=true, then curl every endpoint — boot banner lists routes; `invalid token` errors confirm the request path without real data.
