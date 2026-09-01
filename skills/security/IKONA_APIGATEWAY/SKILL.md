---
name: api-gateway-recon
category: security
trigger: 'API gateway reconnaissance — probe endpoints, auth, vectors'
description: 'Probe APIs: fingerprint stack, map endpoints, detect auth.'
---

# API Gateway Reconnaissance

Probing methodology for APIs and web apps.

## Commands

**Stack detection:**
```bash
curl -sI <target> | grep -i "server\|x-powered-by"
```

**Endpoint mapping:**
```bash
for p in /api/ /v1/ /robots.txt; do curl -sI "<target>$p"; done
```

**Auth testing:**
```bash
curl -s "<target>/v1/chat/completions" \
  -X POST -H "Authorization: Bearer sk-test" \
  -d '{"model":"test","messages":[{"role":"user","content":"x"}]}'
```

**Sensitive files:**
```bash
for f in .env config.json; do curl -sI "<target>/$f"|grep HTTP; done
```

## Output

```
TARGET: url
STACK: framework+server
AUTH: scheme
VECTORS: paths
```

## Pitfalls

- Escaped braces for JSON payloads
- Delays between probes (rate limit)