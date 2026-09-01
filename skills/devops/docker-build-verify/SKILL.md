---
name: docker-build-verify
description: Multi-stage Docker build verification pattern — always rebuild image + verify timestamp before reporting deploy complete
version: 1.0
tags: [docker, deployment, build-verification]
---

# DOCKER BUILD & VERIFY PATTERN FOR MULTI-STAGE APPS

> For multi-stage Docker builds (Vite frontend + Go backend), `docker compose up -d` **does not rebuild** — it only starts containers from cached images. Must explicitly run `docker compose build --no-cache` then verify file timestamps before deploying.

## Why This Happens

Docker Compose behavior:
- `docker compose up -d` → checks if image is newer than last build → uses cached image if unchanged
- Source code changes in `/opt/simmubtadiat/frontend/rapot.html` do NOT trigger rebuild automatically
- Container runs old `/app/public/dist/rapot.html` even after `npm run build` on host

## Correct Workflow

```bash
# 1. Edit source files
patch /path/to/rapot.html

# 2. Build frontend (generates /opt/simmubtadiat/public/dist/)
cd /opt/simmubtadiat/frontend && npm run build

# 3. REBUILD IMAGE (critical step!)
cd /opt/simmubtadiat && docker compose build --no-cache app

# 4. Start/restart containers
docker compose up -d

# 5. VERIFY BUILD OUTPUT inside container
docker exec simmubtadiat-app-1 sh -c 'stat /app/public/dist/rapot.html'

# 6. VERIFY LIVE SERVER
curl -sL http://reviewtechno.me/rapot.html | grep "class=\"student-data\""

# Only then report: ✅ Deploy complete!
```

## Verification Commands

### Check timestamp inside container
```bash
docker exec simmubtadiat-app-1 sh -c 'stat /app/public/dist/rapot.html'
# Modify: 2026-08-26 02:29:27.000000000 +0000
```

If timestamp matches current time, file was rebuilt. If old, skip to Step 3.

### Verify live server content
```bash
curl -sL http://domain.com/rapot.html | grep ".st-label" | head -3
```

Look for updated CSS values (e.g., `.st-label { width: 95px; }`).

## Pitfalls

❌ **Wrong:** Assuming `docker compose up -d` picks up latest build  
✅ **Right:** Always run `build --no-cache` after CSS/JS changes

❌ **Wrong:** Claiming "deploy done" after container restart  
✅ **Right:** Verify `stat` timestamp + live curl response

❌ **Wrong:** Running `npm run build` only on host  
✅ **Right:** Rebuild Docker image to copy `/app/public/dist/` into container layer

## When to Force Rebuild

- Any CSS/HTML/JS change (`rapot.html`, `style.css`, `*.js`)
- New static assets added
- Service Worker version update
- Cache-clearing deployments

## Related Skills

- `fullstack-web-engineering` (Deployment section #64)
- `print-layout-fix` (verification requirements)
