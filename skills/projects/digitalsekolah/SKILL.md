---
name: digitalsekolah
description: "Operate & develop Digital Sekolah (Smart LMS) — Go/Fiber + Postgres multi-tenant school system at /home/ubuntu/smart-lms, domain rezaulin.tech, repo rezaulin/digitalsekolah. Load for ALL work on smart-lms/digitalsekolah (stack map, billing model, PM2 ops, security gotchas)."
tags: [digitalsekolah, smart-lms, project, lms]
triggers:
  - smart lms
  - smart-lms
  - digitalsekolah
  - digital sekolah
  - rezaulin.tech
---

# Digital Sekolah (Smart LMS)

Multi-tenant school management system (LMS + billing + PPDB + parent portal). Branding in-app is "Digital Sekolah". Load this skill for any work on it.

## Stack & Runtime Map

| Component | Details |
|---|---|
| Backend | Go (Fiber v2 / GORM), `/home/ubuntu/smart-lms/backend/smart-lms`, port **8085**, PM2 name `smart-lms-backend` |
| WA Gateway | Baileys + Express, `/home/ubuntu/smart-lms/wa-gateway/index.js`, port **3001**, PM2 name `smart-lms-wa-gateway`. Health: `curl localhost:3001/status` — `connected:false` means WA session died (not logged out); re-scan via `/qr` |
| DB | PostgreSQL 15 @ 127.0.0.1:5432, db `smart_lms`, user `smart_lms_admin`. Backend process runs WITHOUT `DB_DSN` env → falls back to hardcoded default DSN in `internal/config/config.go` (default password `smart123` — rotation still pending) |
| Frontend | React/TS/Vite, nginx serves `frontend/dist` directly |
| Domain | `rezaulin.tech`, config `/etc/nginx/sites-enabled/smart-lms`, Let's Encrypt SSL |
| Repo | `github.com/rezaulin/digitalsekolah` (private, SSH push works from this server). Published Aug 2026 as fresh **orphan commit** — old history with binaries stays at `ahzani12/smart-lms` |
| Roles | superadmin, admin_pusat, admin_cabang, bendahara, guru (NIP), siswa (6-digit ID), orang_tua (kode akses) |

## Ops

- `pm2 status`, `pm2 logs smart-lms-backend`, `pm2 restart smart-lms-backend`
- Build: `cd backend && go build -o smart-lms .` (one-off scripts `add_bendahara.go` / `check_bendahara.go` / `seed_soal.go` are tagged `//go:build ignore`; run via `go run <file>`)
- Rate limits baked in: 200 req/min global, 5 login attempts/min per IP
- Notification worker polls queue every 30s; channels: baileys (own gateway), fonnte, wablas, telegram

## Billing Model (integration point for payment gateways)

```
JenisTagihan (master per school: SPP/Seragam/etc; nominal_default;
  periode bulanan|sekali|tahunan; apply_potongan)
  → GenerateTagihan (bulk)
Tagihan (per student per period; nominal − keringanan = total;
  terbayar; status belum_bayar|sebagian|lunas|batal)
  → POST /api/billing/bayar (manual by bendahara, financeOnly)
Pembayaran (cicilan/lunas; metode cash|transfer|qris|va — "qris" slot
  exists but was unused; nomor_kuitansi auto; void requires PIN)
  → recalcTagihan → notifyTagihanLunas (WA/Telegram queue)
```

Routes: `/api/billing/*` in `internal/routes/routes.go` (jenis, generate, tagihan, bayar, void, kuitansi, potongan, pengeluaran, dashboard, report). Parent portal: `/api/parent*`. Models: `internal/models/billing.go`.

## Planned: ShopeePay QRIS self-service (audit done Aug 2026)

- Source of `ahmadzakiyox/shoppepay-api-gateway` deobfuscated (webcrack) and audited — **clean**: calls only `shopeepay.shopee.co.id`, `api.telegram.org`, `api.qrserver.com` (QR image render). See skill `untrusted-code-audit`.
- Plan: `SchoolPaymentConfig` per tenant (token AES-encrypted), `QRISPayment` table with unique `transaction_id` index (dedupe beyond gateway RAM), endpoints `/billing/qris/create` + `/billing/qris/:id/status` reusing the CreatePembayaran path, parent-portal QR modal with countdown, shared gateway hosted by us using `X-Shopee-Token` multi-store routing. Deploy the **deobfuscated** source, bind internal, egress-firewall to ShopeePay+Telegram only.
- Tenant onboarding needs: ShopeePay Partner merchant account + their static QRIS + token from DevTools. Funds land in the tenant's own ShopeePay balance; gateway is read-only.
- Open decisions when session left off: shared vs self-hosted gateway mode, partial-payment (cicilan) via QRIS or full-amount only, fee display.

## Gotchas

- `ecosystem.config.js` contains VAPID private key — never commit it; repo has `ecosystem.config.js.example` template instead
- `wa-gateway/auth/` = WhatsApp session creds — gitignored, never commit
- backend dir accumulates junk: `.exe`, `.db`, tarballs — all gitignored in digitalsekolah repo; don't re-commit
- Default superadmin `super@lms.id/super123` — verify it was changed before any public exposure
- DB password hardcoded default in source (config.go) — rotate to env-provided DSN when touching config
