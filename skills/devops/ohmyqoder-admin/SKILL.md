---
name: ohmyqoder-admin
description: Manage and troubleshoot OhMyQoder deployment, authentication, tunnels, and model access
author: hermes-agent
version: 1.0.0
---

# OhMyQoder Administration

## Overview

OhMyQoder is a multi-model proxy service that routes requests through various LLM providers. Key concepts:

- **PAT tokens**: Provider auth credentials (format `pt-xxx`, NOT GitHub `ghp_xxx`)
- **Tunnels**: Cloudflared tunnels map external URLs → local port (e.g., `ral7eqz.abc-tunnel.us` → `localhost:20120`)
- **Model IDs**: Short codes like `dfmodel`, `dmodel`, `qmodel_38max` etc.
- **Vision support**: Most models have `is_vl: true` (vision-language capable)

## Quick Start

### 1. Enable Tunnel Access

```bash
TOKEN=$(curl -s http://localhost:20120/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"ohmyqoder-admin-2026"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -X POST http://localhost:20120/api/tunnel/enable \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Verify running:
```bash
curl -s http://localhost:20120/api/tunnel \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Expected output: `"running": true`, `"public_url": "https://rxxxxx.abc-tunnel.us"`

### 2. Add PAT Tokens

Two approaches:
- **Single add**: `/api/accounts/add` (async background job)
- **Bulk add**: `/api/accounts/bulk-add` (recommended for 50+ tokens)

Example bulk add with Python:
```python
import subprocess
import json

# Get fresh JWT token
login_resp = subprocess.run(['curl', '-s', 'http://localhost:20120/api/auth/login',
                            '-H', 'Content-Type: application/json',
                            '-d', '{"username":"admin","password":"ohmyqoder-admin-2026"}'],
                           capture_output=True, text=True)
token = json.loads(login_resp.stdout)['token']

# Read PATs from file
with open('pat_list.txt') as f:
    pats = [line.strip() for line in f if line.strip()]

bulk_payload = {'accounts': [{'pat': pat} for pat in pats]}

result = subprocess.run(['curl', '-X', 'POST', 'http://localhost:20120/api/accounts/bulk-add',
                        '-H', f'Authorization: Bearer {token}',
                        '-H', 'Content-Type: application/json',
                        '-d', json.dumps(bulk_payload)],
                       capture_output=True, text=True)

print(result.stdout)  # Response includes job ID for progress tracking
```

Track job status:
```bash
curl -s http://localhost:20120/api/op/status/<job-id> \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 3. Call Models via Tunnel

```bash
curl https://$PUBLIC_URL/v1/chat/completions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dfmodel",
    "messages": [{"role": "user", "content": [{"type": "text", "text": "Hello"}]}]
  }' | python3 -m json.tool
```

## Available Models

All models listed at `/api/models`. Key ones:

| Model ID | Name | Context | Vision | Reasoning | Best For |
|---|---|---|---|---|---|
| `ultimate` | Ultimate Tier | 1M | ✅ | ✅ | General flagship |
| `dmodel` | DeepSeek-V4-Pro | 1M | ✅ | ✅ | Complex tasks, OCR |
| `dfmodel` | DeepSeek-V4-Flash | 1M | ✅ | ✅ | Fast vision, cheap |
| `qmodel_38max` | Qwen3.8-Max | 180K | ✅ | ✅ | Document analysis |
| `kmodel_latest` | Kimi-K3 | 180K | ✅ | ❌ | Long context |
| `lite` | Lite | 180K | ❌ | ❌ | Text-only fast |
| `cmodel` | Cantus | 131K | ❌ | ✅ | Pure reasoning |

## Vision Capabilities

**Vision IS supported** — most models have `is_vl: true`.

Image upload methods:
1. **Public URL**: `{"type": "image_url", "image_url": {"url": "https://example.com/img.jpg"}}`
2. **Base64 data URL**: `{"url": "data:image/jpeg;base64,<encoded>"}` (may have compatibility issues)
3. **File upload**: Use external hosting → provide URL

Test vision:
```python
payload = {
    "model": "dfmodel",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "What color is this?"},
            {"type": "image_url", "image_url": {"url": "https://example.com/test.png"}}
        ]
    }]
}

result = subprocess.run(['curl', '-s', 'https://ral7eqz.abc-tunnel.us/v1/chat/completions',
                        '-H', f'Authorization: Bearer {token}',
                        '-H', 'Content-Type: application/json',
                        '-d', json.dumps(payload)],
                       capture_output=True, text=True)
print(json.loads(result.stdout)['choices'][0]['message']['content'])
```

## Authentication Notes

⚠️ **Critical pitfall**: Do NOT use `ADMIN_KEY` from `.env` for API calls!
- Admin key is for frontend/dashboard only
- All API endpoints require **JWT token from `/api/auth/login`**
- Login payload: `{"username": "admin", "password": "ohmyqoder-admin-2026"}`
- Token expires after 24 hours (refresh by re-calling login)

## Tunnel Management

Check current tunnel status:
```bash
curl http://localhost:20120/api/tunnel \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Disable tunnel:
```bash
curl -X POST http://localhost:20120/api/tunnel/disable \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Restart cloudflared manually (if needed):
```bash
pkill -9 cloudflared
sleep 1
nohup /root/.9router/bin/cloudflared --no-autoupdate tunnel --url http://localhost:20120 >/tmp/cloudflared.log 2>&1 &
tail -f /tmp/cloudflared.log | grep -iE "https?://"
```

## References

See `references/` for session-specific details:
- `tunnel-setup.md` — Detailed tunnel debugging path
- `pat-bulk-loading.md` — Batch PAT addition recipes
- `vision-compatibility.md` — Image upload format testing
