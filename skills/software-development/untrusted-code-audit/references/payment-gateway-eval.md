# Unofficial Payment Gateway Evaluation Checklist

For "gateway" projects that ride on top of consumer/merchant portals (Saweria donation endpoint, ShopeePay Partner portal, etc) instead of official PG APIs. Applied after the code audit passes.

## Trust anchor question (the big one)
Where does the "paid" signal actually come from?
- Official PG webhook signed by provider → strong.
- Gateway's OWN polling producing the signal → the gateway is the trust anchor. Compromised/malicious gateway can forge `paid`. Server must dedupe by transactionId and, where possible, cross-check against the portal's own statement/reconciliation endpoint.
- HMAC-signed webhook only proves "came from our gateway", NOT "Shopee/Saweria saw the money".

## Dedup & replay
- Check `transactionId` unique-index in YOUR DB — never rely on the gateway's in-RAM dedupe map (wipe on restart → double-claim window).
- Webhook receivers: check timestamp freshness; reject replays.
- Amount-collision design: unique 1–99 digit suffix per invoice, or match by transactionId not amount.

## Cancel semantics
- Does "cancel" actually invalidate the QR? Usually NO (QR stays payable) → money can arrive after cancel with no webhook → orphan funds. Reconcile daily against portal statement (e.g. `/transactions/all` totalNetSales vs DB paid records).

## Operational
- Stateless gateways lose all pending-invoice state on restart — acceptable only if the store-side DB is source of truth.
- Rate-limit design: polling should scale with active checkouts only (0 requests when idle) to protect the session token from detection.

## ToS & account risk
- These are unofficial scrapers of internal endpoints (session token from DevTools). Account (merchant/creator) can be restricted. Advise dedicated account, not the main operational one.
- Funds path: confirm money lands in the USER's own balance (gateway read-only) — verify no write/transfer/withdraw endpoints exist in the code.

## Deployment hardening (if operator proceeds)
- Bind gateway to localhost/internal; expose only via authenticated internal proxy.
- Egress firewall: allowlist only the portal domain + notification API (e.g. Telegram). Blocks any exfil even if code turns out to have hidden calls.
- Deploy the deobfuscated source you audited, not the vendor's obfuscated blob.
- `.env` chmod 600; long random API key; secrets never in git.

## Case notes
- PG Saweria (Ikona Oni): donation-endpoint hack, `paid` detected by `qr_string==''` flip; clean code but fragile detection + no persistence + replay-able webhook.
- shoppepay-api-gateway (ahmadzakiyox): obfuscated but audited clean (only shopeepay.shopee.co.id + telegram + qrserver.com); QRIS EMVCo TLV inject + CRC16-CCITT; multi-token via `X-Shopee-Token` header enables shared multi-tenant hosting; `/check-payment` expects epoch SECONDS not ms.
