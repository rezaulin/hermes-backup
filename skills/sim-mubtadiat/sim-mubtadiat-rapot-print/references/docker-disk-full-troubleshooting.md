# Docker Disk Full Troubleshooting - SIM Mubtadiat

## Root Cause Pattern
**Disk / at 100% → PostgreSQL can't write lock file → Database crashes in restart loop → Login fails**

## Symptoms
- Database container status: `Restarting (1)`
- Logs show: `FATAL: could not write lock file "postmaster.pid": No space left on device`
- Login returns 401 even with correct credentials
- App seems running but database queries fail

## Diagnosis Steps
```bash
# 1. Check disk space
df -h /

# 2. Check Docker volume usage
docker system df -v
du -sh /var/lib/docker/volumes/simmubtadiat_* 2>/dev/null

# 3. Check largest directories
du -sh /root/* | sort -hr | head -10
```

## Emergency Fix (Immediate Recovery)

### Step 1: Stop containers
```bash
cd /opt/simmubtadiat
docker compose down
```

### Step 2: Clean up unneeded Docker resources
```bash
# Remove unused images, build cache, networks
docker system prune -a -f
```

### Step 3: Remove large local files (if still full)
```bash
# Common culprits:
rm -rf /root/omni-pos              # 1.4G cloneable project
rm -rf /root/*.zip                  # Old backups
rm -rf /root/driver_research        # 1.3M temporary folder
```

### Step 4: Rebuild and start fresh
```bash
cd /opt/simmubtadiat
docker compose build --no-cache
docker compose up -d
```

### Step 5: Verify health
```bash
docker ps | grep simmu           # Both should be "Up"
docker logs simmubtadiat-db-1    # Should say "ready to accept connections"
curl http://127.0.0.1:8080/api/health  # Should return 200
```

## Prevention Strategies

### 1. Regular Disk Monitoring
Add to your workflow checklist:
- Before every deploy: `df -h /`
- Target: Keep >10% free space (minimum 3GB for this app)

### 2. Build Cache Management
After heavy development:
```bash
docker system prune -a -f --volumes  # Run weekly
```

### 3. File Hygiene
- Delete `.zip` files after extracting
- Clone projects from `/home/ubuntu` instead of `/root`
- Use bind mounts for large data instead of Docker volumes

### 4. Docker Compose Optimization
Use `.dockerignore` to exclude:
- Large build artifacts
- Development dependencies
- Unneeded test data

## Recovery Checklist Template

```bash
# Emergency recovery script
#!/bin/bash
set -e

echo "1. Stopping containers..."
docker compose down

echo "2. Cleaning Docker cache..."
docker system prune -a -f

echo "3. Checking disk space..."
df -h /

if [ $(df -h / | tail -1 | awk '{print $5}' | tr -d '%') -gt 95 ]; then
    echo "⚠️ Still full! Removing backup files..."
    rm -rf /root/*.zip /root/*.sql.bak 2>/dev/null || true
fi

echo "4. Rebuilding..."
cd /opt/simmubtadiat
docker compose build --no-cache

echo "5. Starting services..."
docker compose up -d

echo "6. Waiting for DB ready..."
for i in {1..30}; do
    docker exec simmubtadiat-db-1 pg_isready -U mubtadiaat 2>&1 && break
    sleep 2
done

echo "Done! Check with: docker ps | grep simmu"
```

## Session Notes
- **Date**: 2026-08-25
- **Total freed**: ~1.5G (deleted omni-pos 1.4G + build cache)
- **Final state**: 95% disk usage, all containers healthy
- **Lesson**: Always clean disk BEFORE rebuilding Docker images
