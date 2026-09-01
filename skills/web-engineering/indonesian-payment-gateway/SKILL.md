---
name: indonesian-payment-gateway
description: "Integrate & audit Indonesian payment channels (QRIS/GoPay/OVO/DANA/ShopeePay/e-wallets) into apps — official PGs and unofficial/scraping gateways. Covers security-auditing obfuscated gateway code, EMVCo QRIS dynamic generation, anti-collision payment matching, and native-in-backend vs self-hosted gateway architecture."
tags: [qris, payment-gateway, shopeepay, ewallet, indonesia, security-audit]
triggers:
  - qris
  - payment gateway
  - shopeepay
  - gopay / ovo / dana integration
  - audit script payment
  - verifikasi pembayaran otomatis
---

# Indonesian Payment Gateway Integration

Class-level playbook for wiring QRIS/e-wallet payments into apps for user jarvis (selling digital goods, school billing, etc.). Full working example of the native pattern: `digital-sekolah` project (`internal/shopeepay/` + `internal/handlers/payment_gateway.go`). Session-detail (ShopeePay Partner API spec, TLV recipe): `references/shopeepay-native-integration.md`.

## Core facts (Indonesian QRIS)

- QRIS = EMVCo merchant-presented QR standard. ANY QRIS static/dynamic accepts GoPay/OVO/DANA/ShopeePay/LinkAja/m-banking — the acquirer is encoded in TLV tag 26/51; the receiving account is the MERCHANT's.
- Funds flow directly to the merchant account behind the QRIS — a "gateway" app that only reads transaction lists can never move money (verify this claim during audit: no withdrawal/transfer API calls).
- Dynamic QRIS = static QRIS string + injected amount (tag 54) + recomputed CRC16 (tag 63). Pure string manipulation — no provider needed.
- Amount collisions: two customers paying identical amounts in the same window → ambiguous match. Countermeasures (use BOTH): (1) unique-code suffix Rp 1–99 added to the requested amount (buyer must pay the EXACT final number), (2) dedupe by provider `transactionId` — in-memory map AND a persistent DB unique index (memory alone dies on restart → double-claim window).

## Auditing an unofficial/obfuscated gateway (mandatory before trusting)

1. **Deobfuscate**: `npm i -g webcrack && webcrack server.js -o deobf` (handles javascript-obfuscator control-flow-flattening + RC4 string arrays). If the repo ships only the obfuscated build, that's itself a red flag to surface.
2. **Static scan** the deobfuscated source: `eval|Function(|child_process|exec|spawn|fs.|writeFile|atob|base64` — all should be absent for a read-only gateway. Enumerate every URL: `grep -oE "https?://[a-zA-Z0-9._/-]+"`.
3. **Trace secret flows**: where do token/credentials go? Acceptable = only the provider's official domain (+ Telegram for alerts). A QR-render third party (e.g. api.qrserver.com) leaks QR content — flag it, prefer local rendering (`qrcode` / `go-qrcode` libs).
4. **Run it sandboxed**: dummy `.env`, start it, probe every endpoint with/without API key, confirm behaviors match README claims. A dummy token SHOULD produce "invalid token" from the real provider API — that proves live integration.
5. Verdict template: exfiltration (none/found), hidden ops, third-party leaks, ToS exposure (always true for unofficial scraping — tenant account risk is the real bet).

## Architecture choice: native-in-backend vs tenant-self-hosted gateway

- **Tenant self-hosted gateway** (token never leaves tenant infra): more trust, worse UX — tenant must deploy, open ports, manage uptime.
- **Native in backend** (tenant pastes provider token + static QRIS into admin UI; backend stores AES-GCM-encrypted, calls provider API directly): far better tenant onboarding; central DB becomes the trust anchor. For jarvis's multi-tenant apps he chose NATIVE ("mereka harus bisa atur sendiri-sendiri" = per-tenant config, not per-tenant servers). Read-only provider tokens make the trust tradeoff acceptable.
- Either way expose to tenants: config form, "Test connection" button (hits provider with stored creds), status badge, and a step-by-step token-extraction guide.

## Universal integration flow (client-polled, anti-rate-limit)

```
buyer opens checkout → app creates invoice (amount + unique code)
  → generate dynamic QRIS → show QR + countdown (15 min)
  → frontend polls backend every ~5s ONLY while checkout page open
  → backend queries provider transaction list [invoice_time, now]
  → match: status=success AND amount==final AND txId not claimed
  → mark paid → persist payment record (method=qris, provider txId) → receipt + notification
```
Polling only while a checkout is active keeps provider API traffic proportional to real buyers — the standard anti-detection design for unofficial APIs.

## Pitfalls

- Provider internal tokens EXPIRE silently (session logout/rotation). Admin UI must show last-check status + re-paste flow; alert on invalid (Telegram/WA).
- `startTime` epoch units vary by provider (seconds vs ms) — a 58609-year date in logs = unit bug.
- Verify generated QRIS by decoding the PNG (pyzbar/PIL) and asserting the amount tag equals the final amount — end-to-end proof, not just "200 OK".
- Provider `amount` strings may carry thousand separators ("50.000") — strip `.` and `,` before int-parsing.
- Official PGs (Midtrans/Xendit) remain the recommendation for real merchant volume; unofficial scraping gateways risk merchant-account restriction. State this once, then execute the operator's choice without re-preaching.
