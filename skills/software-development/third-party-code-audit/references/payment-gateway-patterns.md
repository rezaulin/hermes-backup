# Payment-Gateway Drops — Analyzed Patterns & Checklist

Reusable notes from audited unofficial Indonesian payment-gateway drops. New drops: compare against these patterns, don't re-derive from scratch.

## PG Saweria + Webhook (Ikona Oni, 2026) — Node
- Rides Saweria's public DONATION endpoint; only needs a Saweria username (no API key).
- User-ID scrape: regex `"id":"([0-9a-fA-F-]+)"` from `saweria.co/<username>` HTML. Paid detection = `qr_string` becomes `''`. Both fragile to upstream changes.
- 3-digit unique-amount suffix (15.000 → 15.483) — display finalAmount only.
- Webhook layer: HMAC-SHA256 raw body, `sha256=` prefix, constant-time compare — but timestamp header sent and NEVER checked (no replay protection), trust anchor is the gateway process itself (can forge paid events), state in-memory only (restart loses tracking), cancel() doesn't void the QR (orphan payments).
- Default example secret `rahasia1234567890abc` hardcoded — common lazy pattern to flag.

## ShopeePay Partner API Gateway (ahmadzakiyox) — Node/Express
- Rides ShopeePay Partner Portal internal session token (`B:...` from DevTools `get-transaction-list` → metadata.token).
- Dynamic QRIS: parse EMVCo TLV of a static QRIS, inject amount into Tag 54, recompute CRC16-CCITT in-memory. Solid technique.
- Anti-rate-limit by design: zero Shopee API calls when no active checkout (client-polled).
- server.js is javascript-obfuscator output; `server-raw.js` absent → README "zero third-party / creds never leave" claims UNAUDITABLE. Recover surface by regex-extracting string literals from the bundle.
- startTime param = epoch SECONDS (not ms) — check units when probing.
- Dedup transactionId in-memory Map only (24h) — restart opens double-claim window; authors recommend DB-side dedup too.
- Endpoints: /api/health (public), /token-status, /update-token, /create-qris, /qr/:id (302), /check-payment, /transactions, /transactions/all, /api/logs — all X-API-Key except health & /qr.

## Standing verdict template
Severity table 🔴🟡🟢 covering: secrets in source/examples, trust anchor of "paid" events, webhook replay/dedupe, in-memory-only state, cancel semantics, unofficial-endpoint fragility + ToS/ban risk, license restrictions. End with verdict + hardening list + next-step offer.
