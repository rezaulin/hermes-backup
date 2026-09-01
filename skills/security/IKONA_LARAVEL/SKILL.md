---
name: laravel-pentest
description: Pentest Laravel apps — debug leaks, WAF, webhooks.
---

# LARAVEL PENTEST — Recon → Exploit Pipeline

## When to Use
- Pentest webapp yang kelihatan Laravel: cookie `{app}-session` (custom name, e.g. `akundigitalid-session`), `XSRF-TOKEN` cookie, Blade + Vite assets (`/build/assets/app-*.js`)
- Marketplace/e-commerce dengan payment gateway QRIS (klikqris, midtrans, xendit, tripay)
- Uji payment flow: cart → checkout → order → pay page → webhook callback
- Target authorized only (web sendiri / teman yang minta dites)

## Phase 1 — Fingerprint & Recon

1. **Headers + cookies**: `Set-Cookie` name = app id; `X-Frame-Options`, CSP, HSTS ada/gak.
2. **Debug mode leak (HIGH finding)**: request route yang gak ada dengan header `Accept: application/json`:
   ```bash
   curl -H "Accept: application/json" https://target/api/nonexistent
   ```
   Debug ON → JSON full stack trace: `"exception"`, `"file": "/home/user/laravel/vendor/..."`, line numbers, absolute server path. Ini langsung finding info disclosure.
3. **Route enum via method-not-allowed**: `PUT`/`DELETE` ke route yang ada → `"The PUT method is not supported for route X. Supported methods: GET, HEAD, POST."` → daftar method tiap route.
4. **Model enumeration**: path dengan slug/ID → error beda:
   ```
   /kategori/abc   → "No query results for model [App\Models\Category] abc"
   /produk/abc     → "No query results for model [App\Models\Product] abc"
   /toko/abc       → "No query results for model [App\Models\SellerProfile] abc"
   /blog/abc       → "No query results for model [App\Models\Post] abc"
   ```
   Route yang gak ada → `"The route X could not be found."` — bedain dua-duanya buat petakan route table + model list.
5. **Laravel anti-bot honeypot**: form login/register punya hidden field `website`, `company` (harus kosong) + `form_started_at` timestamp. Kalo keisi → ditolak.
6. **419 CSRF**: `419` = token/session mismatch (curl cookie jar gak sinkron sama token page). Selalu pakai session yang sama buat ambil token & submit.
7. **429 rate limit**: `ThrottleRequestsException` stack trace ikut bocor di JSON — konfirmasi throttle config.

## Phase 2 — WAF Bypass (Imunify360 / Cloudflare)

Gejala: curl dapat `"Access denied by Imunify360 bot-protection"` (422/403) di endpoint tertentu, atau halaman `<title>One moment, please...</title>` (JS challenge) di path admin. Sementara endpoint lain jalan normal.

- Curl kena block, **real browser (browser_exec) gak** — JS challenge resolve sendiri.
- Pola kerja: **curl buat recon ringan, browser buat exploit/post-auth**.
- Di browser, pakai fetch dengan header yang bener:
  ```js
  const xsrf = document.cookie.split(';').map(c=>c.trim()).find(c=>c.startsWith('XSRF-TOKEN='));
  const xToken = xsrf ? decodeURIComponent(xsrf.split('=')[1]) : '';
  await fetch('/endpoint', {
    method: 'POST',
    headers: { 'X-XSRF-TOKEN': xToken, 'X-Requested-With': 'fetch', 'Accept': 'application/json' },
    body: formData, credentials: 'include'
  });
  ```
- WAF bisa block per-endpoint (voucher preview) tapi allow yang lain — jangan asumsi seluruh site block.

## Phase 3 — Auth & Account Access

- **Register + verifikasi email**: pakai domain temp yang ada IMAP-nya (mis. user@temp-mail.example → Gmail). Ambil link verifikasi dari email: `/verify-email/{user_id}/{hash}?expires=...&signature=...` → auto-login + dashboard. URL verify-nya bocorin user ID numerik.
- **User enum via login**: email belum daftar → `"These credentials do not match our records."`; user daftar tapi belum verified → pesan beda ("verifikasi dulu"). Beda message = enum.
- Rate limiter "Aktivitas terlalu cepat" muncul di register/login — space request-nya.

## Phase 4 — Order/Checkout Business Logic

- **Cart qty mass assignment**: `items[{id}][qty]=99999` → total ikut gede (Rp 35.000 → Rp 3.499.965.000). Negatif qty → item kehapus (bukan total negatif). Cek batas validasi.
- **Direct checkout tanpa cart flow**: `POST /checkout/{product_id}` cuma butuh `additional_info` → langsung create order, redirect `Location: /pay/{invoice}`. Gak perlu lewat cart.
- **Order state machine**: UNPAID → EXPIRED ±30 menit. Payment page `/pay/{invoice}` nampilin invoice, total, kode unik, QRIS, countdown.
- **Route probe `/pay/{x}/{action}`**:
  - invoice valid → `"Data Transaksi tidak ditemukan."` = route ada, data gak match
  - numeric → `"The route pay/465/status could not be found."` = route gak ada
  - `405` + "Supported methods: POST" = endpoint ada, tinggal cari parameternya

## Phase 5 — Payment Webhook Forging

1. **Discovery**: probe `POST /webhook/{provider}` — `404 route could not be found` = gak ada; `4xx + message` = ADA, gagal validasi.
2. **Validation-order leak**: tiap payload beda → error beda, urutan cek kebaca:
   ```
   tanpa merchant_id  → "Merchant ID tidak valid."          (cek merchant dulu)
   + signature        → "Metode pembayaran order (X) tidak sesuai dengan webhook endpoint (Y)"
   status salah       → "Status pembayaran tidak valid."    (enum check)
   payload salah      → "Payload tidak valid."              (schema check)
   ```
   Urutan error = urutan validasi server. Ini peta buat forge.
3. **Provider docs = sumber truth**: gateway QRIS kayak klikqris.com punya `/dokumentasi-api` publik — webhook payload format, signature scheme, sandbox, idempotency requirement. Baca itu buat tau apa yang target harus implement.
4. **Signature**: docs bilang "compare signature callback dengan signature response create awal". Kalau implementasi bener, forge gak mungkin tanpa signature asli. Coba bypass: signature kosong, duplicate param, JSON pollution (`data[signature]` vs `signature`), missing field — kadang cek-nya cuma "field ada" bukan "nilai valid".
5. **QRIS image URL bocorin metadata**: `https://gateway/storage/qris_mypg/qris_{invoice}_{unix_ts}.png` → nama provider, tipe payment, invoice, timestamp ref.

## Pitfalls
1. **Jangan nembak checkout terus** — rate limit 429 cepet kena, order juga expired 30 menit. Bikin order baru hemat.
2. **WAF cache**: endpoint yang tadinya 422 bisa balik 404 sesaat (browser session beda) — refresh halaman dulu, jangan langsung simpulkan route ilang.
3. **200 ≠ vulnerable** — cek body/efek, bukan status doang (Laravel SPA balas 200 buat semua).
4. **Session browser ilang** pas `window.location` navigasi di tengah exec — pisah navigasi & fetch ke call terpisah.
5. Jangan test web orang tanpa izin. Skill ini buat authorized scope.

## References
- `references/akundigital-klikqris-session.md` — contoh nyata: endpoint, payload, error messages dari pentest akundigital.id (Laravel + klikqris MY PG)
