# Docker Rebuild Deployment Reference (SIM Mubtadiat)

**Created**: 2026-08-25  
**Purpose**: Fast deployment guide for frontend changes to the Simubtadiat app.

---

## Quick Deploy Checklist ✅

When you edit HTML/JS files and want to push changes live:

```bash
cd /opt/simmubtadiat

# Step 1: Check what changed
git status --short frontend/

# Step 2: Stop container
docker compose down app

# Step 3: Rebuild image (critical — copies frontend/ into image)
docker compose build app

# Step 4: Start with new image
docker compose up -d app

# Step 5: Wait for migration + health check
sleep 15

# Step 6: Verify content served (grep a pattern you just added)
curl -s https://reviewtechno.me/raport.html | grep "your-pattern"

# Step 7: If verification fails, debug
docker logs simmubtadiat-app-1 --tail 30
curl -I https://reviewtechno.me/raport.html | grep -i cache
```

---

## Why `--build` is Mandatory

**Vite builds static assets during Docker multi-stage build**, not at runtime:

```dockerfile
# FROM Dockerfile line 6-8:
COPY frontend/ ./
RUN npm install
RUN npm run build    # <-- This runs every time you BUILD the image
```

Without `--build`, Docker reuses the cached layer from the LAST BUILD, so your edits are ignored.

---

## Common Pitfalls & Solutions

### Issue 1: Changes still don't show after rebuild

**Cause**: Cloudflare static asset cache serving old bytes

**Fix**: Add version suffix to filename, force browser reload
```bash
mv raport.html raport-v29.html
# Update all references
sed -i 's|href="/raport\.html"|href="/raport-v29.html"|g' *.html
docker cp raport-v29.html simmubtadiat-app-1:/app/public/dist/
```

**Diagnostic**: 
```bash
docker exec simmubtadiat-app-1 md5sum /app/public/dist/raport.html
curl -s https://reviewtechno.me/raport.html | md5sum
# Compare — if different, CF cache hit
```

### Issue 2: Build fails with "npm run build" error

**Common cause**: Syntax error in Vite config or missing dependency

**Debug**:
```bash
cd /opt/simmubtadiat/frontend
cat package.json | grep '"scripts"' -A 5
npm run build  # local test first before docker
```

### Issue 3: Container won't start after rebuild

**Check migration errors**:
```bash
docker logs simmubtadiat-app-1 --since 5m
docker inspect simmubtadiat-app-1 --format '{{json .State}}'
```

**Revert to previous image**:
```bash
docker compose stop app
docker tag simmubtadiat-app:old simmubtadiat-app:latest
docker compose start app
```

---

## Local Testing Before Full Deploy

For rapid iteration without full rebuild:

```bash
# Edit file locally
vim /opt/simmubtadiat/frontend/raport.html

# Copy directly to container (no rebuild needed for HTML only)
docker cp /opt/simmubtadiat/frontend/raport.html simmubtadiat-app-1:/app/public/dist/raport.html

# Force browser cache bust by appending timestamp query param
echo "<script>window.location.search = '?v=' + Date.now();</script>" >> /tmp/header.js
docker cp /tmp/header.js simmubtadiat-app-1:/app/public/dist/header.js

# Refresh browser with Ctrl+F5 or clear cache
```

**WARNING**: Only works for standalone HTML files. JS bundles require rebuild due to hashed filenames (`assets/raport-B3OhYkrC.js`).

---

## Verification Scripts (Optional)

### Pattern match verify
```bash
#!/bin/bash
# /opt/simmubtadiat/scripts/verify-deploy.sh

PATTERN="$1"
URL="https://reviewtechno.me/raport.html"

curl -sL "$URL" | grep -q "$PATTERN" && echo "✅ Pattern found: $PATTERN" || echo "❌ MISSING: $PATTERN"
```

Usage: `./scripts/verify-deploy.sh "your-html-class-name"`

### Cloudflare cache check
```bash
#!/bin/bash
# /opt/simmubtadiat/scripts/check-cf-cache.sh

URL="$1"
curl -Is "$URL" | grep -E "^cf-cache-status|^etag|^last-modified"
```

Returns `HIT` means stale content being served even after rebuild.

---

## Session Example: Rapport Layout Fix (2026-08-25)

**Context**: Owner requested header restructuring and table alignment fixes.

**Workflow used**:
1. Patched `/opt/simmubtadiat/frontend/rapot.html`
2. Patched `/opt/simmubtadiat/frontend/src/js/rapot.js`
3. Stopped: `docker compose down app`
4. Built: `docker compose build app` (took ~90 seconds total)
5. Started: `docker compose up -d app`
6. Verified: `curl -s https://reviewtechno.me/rapot.html | grep "كشف الدرجات"`

**Result**: All changes deployed live, verified via HTTP fetch before asking owner to test.

---

## Related Skills

See main `sim-mubtadiat` skill:
- Print layout debugging techniques
- Arabic text rendering rules
- Reference photo matching workflow
- HTML template reconstruction methods

---

## Notes for Future Sessions

- Docker pull size varies based on builder layers (expect ~50MB for alpine base + Go binary)
- First build always slowest; subsequent builds faster due to caching
- Use `docker buildx` parallel build if working with multiple services
- Monitor disk space: `df -h /var/lib/docker` before large rebuilds
- **NEVER** skip the `curl verify` step — assume nothing until proven it served correctly
