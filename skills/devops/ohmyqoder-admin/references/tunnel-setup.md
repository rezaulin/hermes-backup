# OhMyQoder Tunnel Setup & Debugging Path

## Environment Detection Pattern

When OhMyQoder won't accept requests or models appear unavailable:

1. **Check if tunnel is running:**
```bash
curl -s http://localhost:20120/api/tunnel \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Expected fields to check:
- `"enabled": true/false` (should be true)
- `"running": true/false` (should be true)
- `"public_url"` — the external URL to hit
- `"bin_found": true/false` (cloudflared binary exists?)

2. **If `running: false`, enable it:**
```bash
curl -X POST http://localhost:20120/api/tunnel/enable \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

3. **Verify cloudflared process:**
```bash
ps aux | grep cloudflared | grep -v grep
# Should show: /root/.9router/bin/cloudflared tunnel --url http://localhost:20120 ...
```

4. **Check logs for domain registration:**
```bash
tail -f /tmp/cloudflared.log 2>/dev/null | grep -iE "http|https|tunnel|domain|url"
# OR read pipe output via /proc/<pid>/fd/1 (advanced)
```

5. **Manual restart procedure** (if automatic enable fails):
```bash
pkill -9 cloudflared
sleep 1
nohup /root/.9router/bin/cloudflared --no-autoupdate tunnel --url http://localhost:20120 >/tmp/cloudflared.log 2>&1 &
sleep 3
cat /tmp/cloudflared.log | grep -iE "https?://"
```

## Session-Specific Instance Info

This session's tunnel configuration:
- **Worker URL**: `https://abc-tunnel.us` (from `.env`)
- **Cloudflared binary**: `/root/.9router/bin/cloudflared`
- **Local port**: `20120`
- **Generated short ID**: `al7eqz`
- **Public URL**: `https://ral7eqz.abc-tunnel.us` (9router domain)
- **Backup URL**: `https://varieties-theoretical-mayor-regulated.trycloudflare.com` (free cloudflared auto-fallback)

### Troubleshooting: Cloudflared Output Not Visible

Cloudflared writes stdout to pipe when started as background service, making direct access difficult. Workaround:
1. Kill existing process: `pkill -9 cloudflared`
2. Restart with explicit log file: `nohup <binary> tunnel --url http://localhost:20120 >/tmp/cloudflared.log 2>&1 &`
3. Wait 3 seconds, then grep logs: `cat /tmp/cloudflared.log | grep https`

The URL appears in logs as a line like:
```
INF Requesting new quick Tunnel on trycloudflare.com...
INF Registered tunnel connection id=<uuid> url=https://xxx.trycloudflare.com
```

## Authentication Flow Pitfalls

### ❌ WRONG: Using ADMIN_KEY directly
```bash
# This does NOT work for API endpoints
curl http://localhost:20120/api/accounts/add \
  -H "Authorization: Bearer ohmyqoder-admin-2026" \
  -d '{"pat": "pt-xxx"}'
# Returns: {"error": {"message": "Invalid API key"}}
```

### ✅ CORRECT: JWT token from login endpoint
```bash
# Step 1: Login to get token
RESPONSE=$(curl -s http://localhost:20120/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"ohmyqoder-admin-2026"}')
TOKEN=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Step 2: Use token for all API calls
curl http://localhost:20120/api/accounts/bulk-add \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '<json_payload>'
```

Token expires after 86400 seconds (24 hours). Always get fresh token before large operations.

## Model Availability Checks

After enabling tunnel, verify models are accessible:

```bash
curl https://$PUBLIC_URL/api/models \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Response format:
```json
{
  "models": [
    {
      "id": "dfmodel",
      "name": "DeepSeek-V4-Flash",
      "context_length": 1000000,
      "is_vl": true,
      "is_reasoning": true
    },
    ...
  ]
}
```

Key insight: If tunnel is enabled but `/api/models` returns empty list or error, cloudflared hasn't finished registering yet. Wait 10-15 seconds after enable command.
