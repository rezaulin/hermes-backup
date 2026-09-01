---
name: docker-deployment-verification
description: Verify Docker container deployments before confirming success
---

# Docker Deployment Verification Pattern

## Purpose
Always verify files actually updated in containers BEFORE reporting "deploy complete". Common pitfall: `docker compose up -d` only restarts existing containers — it DOES NOT re-build images or copy new source files.

## When to Use
After ANY code change needing reflection in running web services.

## Critical Workflow

### 1. Build Frontend Assets
```bash
cd /opt/simmubtadiat/frontend && npm run build
```

### 2. Rebuild Docker Image (MANDATORY!)
```bash
cd /opt/simmubtadiat
docker compose build --no-cache app
```
**NEVER skip this** — `up -d` alone won't copy new files.

### 3. Start Containers
```bash
docker compose up -d
```

### 4. VERIFY IN CONTAINER
```bash
docker exec simmubtadiat-app-1 sh -c 'stat /app/public/dist/rapot.html | grep Modify'
```
Check timestamp is **newer** than your source file modification time.

### 5. VERIFY LIVE SERVER
```bash
curl -sL http://reviewtechno.me/rapot.html | grep -A3 ".st-label"
```
Confirm CSS/content matches expected changes. For Service Workers:
```bash
curl -sL http://reviewtechno.me/sw.js | head -1
```

## User Frustration Signal
User gets frustrated when told "deploy complete" but browser still shows old cached version. Always:
- Check file timestamps match post-build time
- Bump Service Worker `CACHE_NAME` version (v29 → v30, etc.)
- Give hard reload instruction: Ctrl+Shift+R or incognito mode

## Verification Checklist
- [ ] `npm run build` completed successfully
- [ ] `docker compose build --no-cache` completed  
- [ ] Container file timestamp newer than source modification
- [ ] Live URL `curl` returns expected content/CSS
- [ ] Service Worker version bumped (if applicable)
- [ ] Hard reload instruction given to user

## Pattern Summary
```
Source Change → npm build → docker build → docker up → 
docker exec stat → curl live → confirm all match → report done
```

If any verification fails, do NOT report success — debug until match!