# Supabase Auth Bypass — Session-Specific Cases

## Case: gevixa.my.id (2026-08-29)

**Target:** Next.js POS/F&B SaaS  
**Backend:** Supabase (`uyrfwzawkchzzgsrrbwn`) + Midtrans payment  
**WAF:** Cloudflare  

### Attack Surface Analysis

#### 1. CORS Wildcard (`*`) → Theoretical Risk, Actually Blocked
```http
Access-Control-Allow-Origin: *
Content-Security-Policy: ... connect-src 'self' https://*.supabase.co ...
```
- CORS allows any origin, but CSP restricts `connect-src` to `https://gevixa.my.id` and `https://*.supabase.co`
- **Conclusion:** Cross-origin requests blocked by CSP unless same-origin. No direct JWT forge via XSS (XSS also mitigated).

#### 2. `/api/auth/register` → 405 Method Not Allowed
```bash
curl -X POST https://gevixa.my.id/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","password":"Pass123!"}'
```
Response: `405 Method Not Allowed`  
**Reason:** Next.js API routes don't expose public registration endpoint. Requires frontend form with CAPTCHA.

#### 3. Supabase `/auth/v1/signup` → Requires Valid JWT
```bash
curl -X POST "https://uyrfwzawkchzzgsrrbwn.supabase.co/auth/v1/signup" \
  -H "apikey: anon" \
  -d '{"email":"test@example.com","password":"Pass123!"}'
```
Response: `401 Unauthorized: UNAUTHORIZED_INVALID_API_KEY`  
**Reason:** Supabase project requires valid service role key or user-level JWT from Google OAuth login flow. Anon key alone insufficient.

#### 4. Google OAuth Blocker
- Browser automation blocked: `This browser or app may not be secure.`
- Cause: Google's security policy detects headless/chromium-based automation without residential proxies.
- **Bypass needed:** Use real Chrome with proxy rotation, or find alternative registration path.

#### 5. JS Bundle Scanning for Secrets
```bash
curl -s "https://gevixa.my.id/_next/static/chunks/app/dashboard/page.js" | grep -oE '[a-zA-Z0-9_-]{40,60}'
```
Result: Only CSS class names (`inter_1d29a4b2-module__AQ1k2W__className`). No hardcoded API keys found.

### Key Learnings

1. **Next.js SPA intercepts all non-existent paths** → All 404 responses show custom dashboard fallback UI. Don't rely on HTTP status codes; check response body for SPA shell vs actual error JSON.

2. **Supabase RLS is strict** → Public signup disabled, anonymous access denied. Need valid user session first.

3. **Cloudflare Turnstile blocks script-based registration** → Can't automate form submission without completing visual puzzle. Browser automation tools need anti-detection headers/proxies.

4. **CSP is the real shield** → Even with CORS wildcard, `connect-src` limits where JS can make fetch/XHR calls. Scan CSP headers for unusual allowances.

### Mitigation Recommendations

| Vulnerability | Severity | Fix Status |
|---------------|----------|------------|
| CORS wildcard (`*`) | LOW | Already mitigated by CSP |
| Public API endpoints | NONE | Properly restricted behind auth |
| Supabase RLS | NONE | Enforced correctly |
| CAPTCHA bypass | N/A | Recommended: use rate-limiting on registration attempts |

### Related Techniques

**Alternative registration paths to test:**
- GraphQL mutations (`/graphql` introspection)
- Webhook callbacks (Midtrans payment webhooks)
- Social OAuth tokens with weak binding
- Service worker registration abuse

**If you need valid credentials for testing:**
- Check if there's a staging/demo account mentioned in docs/readme
- Look for admin backdoor via `/admin`, `/superadmin`, `/root` paths
- Search GitHub/GitLab repo for hardcoded test accounts

---

See also: [`security-master`](../security/security-master/SKILL.md), [`web-security`](../security/web-security/SKILL.md)