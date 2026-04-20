---
name: cloudflare-nginx-deploy
description: Deploy Node.js app behind nginx with Cloudflare proxy and HTTPS using self-signed certs
category: devops
---

# Cloudflare + Nginx Deploy for Node.js Apps

Deploy a Node.js app on a VPS behind nginx with Cloudflare proxy + HTTPS.

## Problem
Expose a local Node.js app (e.g. port 3000) to the internet via a custom domain on Cloudflare with HTTPS.

## Failed Approaches
- **CNAME to trycloudflare.com**: Cloudflare does NOT allow CNAME from custom domain to trycloudflare.com quick tunnel URLs.
- **Cloudflare Tunnel login**: Requires browser auth, can't do in headless terminal.
- **Set SSL mode to Flexible via API**: Requires Zone Settings permission which many API tokens don't have (Pages token ≠ Zone token).

## Working Solution: nginx + self-signed cert + Cloudflare proxy

### 1. Install & configure nginx
```bash
apt-get install -y nginx
```

Create `/etc/nginx/sites-available/YOURAPP`:
```nginx
server {
    listen 80;
    listen 443 ssl;
    server_name SUBDOMAIN.DOMAIN.COM;

    ssl_certificate /etc/nginx/ssl/YOURAPP.crt;
    ssl_certificate_key /etc/nginx/ssl/YOURAPP.key;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }
}
```
```bash
ln -sf /etc/nginx/sites-available/YOURAPP /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx
```

### 2. Create self-signed SSL cert
```bash
mkdir -p /etc/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/YOURAPP.key \
  -out /etc/nginx/ssl/YOURAPP.crt \
  -subj "/CN=SUBDOMAIN.DOMAIN.COM"
```
Cloudflare accepts self-signed certs when proxied=true (Full SSL mode).

### 3. Create DNS A record via Cloudflare API
```bash
CF_TOKEN="YOUR_TOKEN"
ZONE="YOUR_ZONE_ID"

curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE/dns_records" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"type":"A","name":"SUBDOMAIN","content":"VPS_IP","proxied":true}'
```

### 4. Verify
```bash
# Direct test
curl -sk https://VPS_IP -H "Host: SUBDOMAIN.DOMAIN.COM"
# Via Cloudflare
curl -sk -o /dev/null -w "%{http_code}" https://SUBDOMAIN.DOMAIN.COM
```

## Key Insight
When `proxied: true`, Cloudflare connects to origin on port 443 using HTTPS. Even with a self-signed cert on origin, Cloudflare accepts it in "Full" SSL mode (not "Strict"). This avoids needing Let's Encrypt or paid certs.

**521 Error**: If you get HTTP 521 via Cloudflare but direct IP works, it means origin lacks SSL on port 443. Cloudflare with `proxied: true` tries HTTPS to origin. Fix: add self-signed cert + listen 443.

## ⚠️ CRITICAL: Sub-Subdomain SSL Limitation

Cloudflare's Universal SSL wildcard cert covers `*.domain.com` (1 level only).

**`sub1.sub2.domain.com` (3-level / sub-subdomain) will NEVER get SSL from Cloudflare.**

Example:
- ✅ `absen.reviewtechno.me` — covered by `*.reviewtechno.me`
- ❌ `v2.absen.reviewtechno.me` — NOT covered (sub-subdomain)
- ✅ `v2.reviewtechno.me` — covered by `*.reviewtechno.me`

**Symptoms**: HTTPS returns SSL handshake failure (`sslv3 alert handshake failure`), but HTTP works fine. curl returns HTTP 000 on HTTPS. Chrome auto-upgrades HTTP→HTTPS and shows error page.

**Fix**: Always use single-level subdomains for Cloudflare-proxied sites. If you need a "v2" of an existing app, use `v2.domain.com` NOT `v2.absen.domain.com`.
## Debugging: HTTPS Serves Wrong Content

**Symptom**: `curl http://localhost:PORT/file` shows correct content, but `curl https://domain.com/file` shows completely different content (different file size, different HTML). Browser shows old/stale version despite file on disk being updated.

**Root Cause**: nginx only listens on port 80 for the subdomain. When Cloudflare (in Full/Strict SSL mode) connects to origin on port 443, the request falls through to the **default vhost** or another server block that happens to listen on 443 — serving a completely different app.

**Debug Steps**:
```bash
# 1. Compare file sizes — if different, it's serving the wrong file
curl -s http://localhost:PORT/ | wc -c
curl -s https://DOMAIN.COM/ | wc -c

# 2. Check what's actually different
curl -s http://localhost:PORT/ | grep "UNIQUE_MARKER"
curl -s https://DOMAIN.COM/ | grep "UNIQUE_MARKER"

# 3. Check nginx vhosts listening on 443
grep -r "listen.*443" /etc/nginx/sites-enabled/

# 4. Check which server block handles the request
curl -sk -H "Host: SUBDOMAIN.DOMAIN.COM" https://VPS_IP/
```

**Fix**: Add `listen 443 ssl` to the correct nginx server block:
```nginx
server {
    listen 80;
    listen 443 ssl;  # ← THIS was missing!
    server_name v2.domain.com;
    ssl_certificate /etc/nginx/ssl/YOURAPP.crt;
    ssl_certificate_key /etc/nginx/ssl/YOURAPP.key;
    # ... proxy config
}
```

## Nginx config when Cloudflare is proxied

Depends on Cloudflare SSL mode:

- **Flexible**: Cloudflare connects to origin via HTTP. Only `listen 80` needed.
- **Full/Full Strict**: Cloudflare connects to origin via HTTPS. **Must have `listen 443 ssl`** with a cert (self-signed works with Full, not Strict).

Rule of thumb: always add both `listen 80` AND `listen 443 ssl` to be safe.

## Cloudflare API Workflow

### Get Zone ID
```bash
curl -s "https://api.cloudflare.com/client/v4/zones?name=DOMAIN.COM" \
  -H "Authorization: Bearer TOKEN" | grep '"id"'
```

### List DNS Records
```bash
curl -s "https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records" \
  -H "Authorization: Bearer TOKEN"
```

### Create A Record
```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"type":"A","name":"SUBDOMAIN","content":"VPS_IP","proxied":true}'
```

### Update DNS Record
```bash
curl -X PUT "https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records/RECORD_ID" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"type":"CNAME","name":"SUBDOMAIN","content":"TARGET","proxied":false}'
```

### Delete DNS Record
```bash
curl -X DELETE "https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records/RECORD_ID" \
  -H "Authorization: Bearer TOKEN"
```

## API Token Requirements
- **DNS**: Zone > DNS > Edit (for creating A records)
- **Zone Settings**: Zone > Zone Settings > Edit (for changing SSL mode — not always needed)
- Pages tokens do NOT have zone/DNS permissions.
- Token from `wrangler` or Pages dashboard won't work for DNS operations.
