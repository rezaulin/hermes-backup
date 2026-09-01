# SIM Mubtadiat — Security posture (audited 2026-08-31)

Result of an authorized web-security audit of `reviewtechno.me` (SIM Mubtadiat) and the host server. **Verdict: no exploitable weakness found — this app is properly hardened.**

## What's GOOD (verified, don't re-test)

| Check | Result |
|---|---|
| Backend bind | `127.0.0.1:8080` (Docker `simmubtadiat-app-1`) — **correct**, not `0.0.0.0`. Internet can only reach it via nginx :80/:443. |
| Login rate-limit | 429 `Too Many Requests` ("Tunggu 1 menit") after ~4-10 rapid attempts, `retry-after` header present. |
| User enumeration | Error `NIP atau password salah` — same message for missing NIP vs wrong password → no oracle. |
| TLS | TLSv1.3, valid cert (~70d at scan). |
| Route protection | `/dashboard`, `/superadmin`, `/dashboard/wali` → server-side 307 → `/login` (RSC payload check), NOT client-side-only. Protected APIs return 401. |
| DB | postgres only on 127.0.0.1:5432. |

## What's MISSING (recommendations)

- **Security headers** — no HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy → clickjacking + MIME-sniffing + protocol-downgrade exposure. Fix: nginx `add_header` block on the 443 server.
- **Rate-limit threshold** slightly loose (4-10 tries before 429) — acceptable, could tighten to 3-5.

## ⚠️ Scanner false-positive trap (IMPORTANT)

Both SIM Mubtadiat and Digital Sekolah are **Go SPA / catch-all apps behind Cloudflare**: EVERY unknown path (`/.env`, `/.git/config`, `/backup.sql`, `/.ssh/id_rsa`, `/admin`, `/wp-login.php`, ...) returns **HTTP 200 with the SPA index HTML** (soft-404). A naive scanner (`webtest.py --modules exposed` etc.) will report dozens of fake "exposed file" hits.

**Rule: when scanning Go/Next.js SPAs, verify by checking the response BODY — if it's the app's HTML shell, it's a catch-all soft-404, not a real file. Never conclude from status-code alone.** Real leak = body contains actual `.env`/SQL/rsa content.

## Host server note (both apps)

The host runs SIM Mubtadiat (Docker, 127.0.0.1:8080) + Digital Sekolah (PM2, **0.0.0.0:8085** + WA gateway **0.0.0.0:3001** — see `digital-sekolah` skill's security section; those two ARE exposed and need binding to 127.0.0.1). SIM Mubtadiat itself is the well-bound one.
