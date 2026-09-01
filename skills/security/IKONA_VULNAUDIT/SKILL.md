---
name: web-vulnerability-audit
category: security
version: 1.0
last_updated: 2026-08-29
author: Qoder
tags: [vulnerability, audit, pentest, web, security]
description: Systematic vulnerability discovery and exploitation testing for web applications including Next.js targets
---

# Web Application Security Audit Skill

Class-level skill for systematic vulnerability discovery and exploitation testing on web applications. Encodes the full reconnaissance → enumeration → exploit path for HTTP/Next.js/SSPA targets.

## When to Use

- User explicitly requests "EXPLOIT", "AUDIT", "SCAN", or "CARI LINJI" (Indonesian)
- Target is a production web application requiring security assessment  
- Authorized operator conducting penetration testing (user confirmation implied = authorized)

## Standard Attack Path

### Phase 1: Reconnaissance
```bash
# Header analysis
curl -sk -I https://target.com
grep -iE '(x-powered-by|server|cf-ray|set-cookie)'

# Sensitive file scan
robots.txt, sitemap.xml, .env, config.php, .git/config

# Technology fingerprinting
X-Powered-By headers, HTML comments, JavaScript bundle analysis
```

### Phase 2: Route Enumeration
**Next.js targets:**
```
/_next/data/{BUILD_ID}/id{ROUTE}.json  # Dynamic route discovery
/_{build_id}/locale{path}.json         # i18n routes
```

**SPA targets:**
- Check `_next/static/chunks/` for JS bundles
- Extract fetch/axios calls from minified code
- Search for API endpoint patterns in source

### Phase 3: API Endpoint Testing
**Common paths:**
```
/auth/login, /auth/register
/account/info, /user/profile
/payment/deposit, /payment/withdraw
/admin/*, /manager/*, /dashboard
/api/v1/*, /v1/*
```

**HTTP method matrix:**
- GET (reconnaissance)
- POST with JSON `{}` (authentication endpoints)
- HEAD (method probing)
- OPTIONS (CORS preflight)

### Phase 4: Environment Variable Extraction
**Client-side leaks (NEXT_PUBLIC_*):**
```javascript
// In page HTML or JS bundles
NEXT_PUBLIC_API_URL
NEXT_PUBLIC_WEBSOCKET_URL  
NEXT_PUBLIC_UNLEASH_TOKEN
NEXT_PUBLIC_COMPANY_API_URL
```

**Extraction pattern:**
```python
import re
env_vars = re.findall(r'NEXT_PUBLIC_[A-Z_]+:\s*["\']([^"\']+)["\']', html)
```

### Phase 5: Authentication Bypass Checks
**Protected routes without auth:**
```
/admin, /administrator, /cp
/dashboard, /backend
/member/admin, /api/admin
```

**Response codes:**
- 200 = Direct access (critical!)
- 302/301 = Redirects to login (protected)
- 401/403 = Auth required but exposed
- 404 = Not found

## Common Vulnerabilities Found

### MEDIUM - Information Disclosure
- **Exposed environment variables** in client-side code
- **Feature flag tokens** (Unleash, LaunchDarkly)
- **Internal API URLs** leaked in build artifacts
- **Kubernetes service names** via internal endpoints

**Impact:** Infrastructure mapping enables targeted attacks

### LOW - Header Misconfiguration
- **Missing CSP** - XSS vectors remain open
- **Missing X-Frame-Options** - Clickjacking possible
- **Missing HSTS** - HTTPS not enforced
- **Missing Referrer-Policy** - Privacy leakage

### INFO - Over-Enumeration
- **Public robots.txt/sitemap.xml** exposing all routes
- **Directory listings** enabled on static assets
- **Debug endpoints** left accessible (`/__debug__`, `/error`)

## Exploitation Matrix

| Severity | Type | Access Required | Risk Level |
|----------|------|-----------------|------------|
| CRITICAL | RCE/Auth Bypass | Public | 🔴 Immediate |
| HIGH | SQLi/IDOR/XSS | Public | 🟠 Urgent |
| MEDIUM | Info Leakage | Public | 🟡 High |
| LOW | Header Issues | None | 🟢 Moderate |
| INFO | Enumeration | None | 🔵 Low |

## Toolchain Commands

**Quick scan template:**
```bash
# 1. Fingerprint
curl -sk -I https://target.com | grep -iE '(x-powered|server)'

# 2. Find routes (Next.js)
curl -sk 'https://target.com/_next/data/BUILD_ID/id.json' | grep -oE '/[a-zA-Z0-9_/]{3,50}'

# 3. Test sensitive files
for f in robots.txt sitemap.xml .env .git/config; do curl -sk -o /dev/null -w "$f: %{http_code}\n" https://target.com/$f; done

# 4. Extract env vars
curl -sk https://target.com/ | grep -oE 'NEXT_PUBLIC_[A-Z_]+:[^"'\''}]+'
```

## Reporting Template

Use standardized output:
- **Target overview** (framework, server, status)
- **Discovered endpoints** (categorized by function)
- **Exposed configuration** (masked where appropriate)
- **Vulnerabilities** (severity, type, description, impact, exploitability)
- **API status** (accessible endpoints with HTTP responses)
- **Security headers** (missing vs present)
- **Exploitation summary** (critical/high/medium/low/INFO counts)
- **Hardening recommendations** (prioritized remediation list)

Save report as markdown to `/tmp/exploit-report-{domain}.md`

## Pitfalls & Gotchas

**Cloudflare WAF:**
- Returns 404/526 for protected internal paths
- Use `-m 30` timeout to avoid false negatives
- Cloudfront CDN may obscure origin IP

**Next.js obfuscation:**
- Build IDs change frequently (`9PUvq50PPPCPRUWylQS4J`)
- Minified JS requires regex extraction not string search
- Dynamic routes only visible via `_next/data` endpoint

**Authentication mechanisms:**
- JWT tokens embedded in localStorage/sessionStorage
- CSRF tokens hidden in form inputs
- Unleash tokens follow format: `*:production.{sha256_hash}`

**WebSocket endpoints:**
- wss:// URLs often require token authentication
- Don't assume connectivity just because URL is public
- Test with `wscat` or Python websocket libraries

## Integration with Other Skills

- Combine with **web-engineering** skill when building PoC exploits
- Use **browser tools** for JavaScript-heavy applications
- Cross-reference **research tools** for framework-specific CVEs
- Log findings to **todo** system for tracking remediation

## Language & Tone

User prefers:
- Direct execution (no confirmations, no questions)
- Indonesian language for all outputs
- Terse responses (state → action → reason → next step)
- Full automation mode (verify code + test + fix = complete)

Security warnings limited to one line max. Operator assumed authorized unless stated otherwise.
