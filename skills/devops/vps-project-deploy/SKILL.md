---
name: vps-project-deploy
description: Deploy a new project on VPS with custom domain — automates Cloudflare DNS, SSL, nginx, and PM2 setup in one command.
---

# VPS Project Deploy

One-command deployment for new projects on the VPS with custom domain via Cloudflare.

## Prerequisites

1. **Cloudflare API Token** — create at dash.cloudflare.com/profile/api-tokens
   - Permissions: Zone DNS Edit, Zone SSL Edit
   - Zone Resources: Include All zones (or specific zone)
   - Save token to `~/.cloudflare-token` (single line, no newline)

2. **jq** installed: `apt install jq`

## Usage

```bash
bash deploy.sh <project-name> <port> <subdomain> [domain]
```

Examples:
```bash
bash deploy.sh chatbot 3001 bot reviewtechno.me
bash deploy.sh blog 3002 blog reviewtechno.me
```

## What it does

1. Creates Cloudflare DNS A record (proxied)
2. Generates Cloudflare Origin SSL certificate (10-year validity)
3. Saves cert + key to `/etc/nginx/ssl/<project>.crt` and `.key`
4. Creates nginx config at `/etc/nginx/sites-available/<project>`
5. Enables site + reloads nginx
6. Starts app with PM2 on specified port

## Pitfalls

- App code must be in `/root/<project-name>` before running deploy
- App must read `PORT` from env: `process.env.PORT || 3000`
- Cloudflare proxy (orange cloud) must be ON for SSL to work
- If deploying to brand new domain, add it to Cloudflare dashboard first (nameserver setup)