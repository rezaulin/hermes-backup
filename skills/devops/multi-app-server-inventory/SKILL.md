---
name: multi-app-server-inventory
description: Systematic discovery and inventory of all running applications on a shared server. Build a map of processes, ports, configs, and relationships for shared infrastructure management.
---

# Multi-App Server Inventory

**Purpose**: When managing a shared VPS/server with multiple apps, systematically discover, document, and maintain an inventory of all services, their locations, configurations, and interdependencies.

## Discovery Workflow

### Phase 1: Process Mapping
```bash
# Step 1: All user processes
ps aux --sort=-%cpu | head -30

# Step 2: Filter by technology
ps aux | grep -E 'node|go|python|php|ruby' | grep -v grep
ps aux | grep postgres | grep -v grep

# Step 3: Get working directories
for pid in $(pgrep -f 'app_name'); do
    ls -la /proc/$pid/cwd 2>/dev/null
done
```

### Phase 2: Port & Network Map
```bash
# Listening ports with PIDs
netstat -tlnp | sort -k4

# Alternative with more details
ss -tlnp | sort -k4

# External facing connections
netstat -anp | grep ESTABLISHED | sort -k6

# Reverse proxy configuration
cat /etc/nginx/sites-enabled/* | grep -E 'upstream|proxy_pass|listen'
```

### Phase 3: Container Inventory
```bash
# Docker containers
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}"

# Container networks
docker network ls
docker network inspect <network_name>

# Container environment variables
docker exec <container_id> env | sort

# Container volumes
docker inspect <container_id> --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}'
```

### Phase 4: Configuration Aggregation
```bash
# Find all .env files in common locations
find /opt /home /root -name '.env' -type f 2>/dev/null | head -50

# Check PM2 processes
pm2 list
pm2 describe <app_name>

# Systemd services
systemctl list-units --type=service --all | grep -v loaded

# Cron jobs (if applicable)
crontab -l
ls -la /etc/cron.d/
```

### Phase 5: Database Survey
```bash
# Postgres databases
docker exec db_container psql -U user -d dbname -c "\l"

# MySQL/MariaDB
docker exec mysql_container mysql -u root -e "SHOW DATABASES;"

# Connection counts
docker exec db_container psql -U user -d dbname -c "SELECT count(*) FROM pg_stat_activity;"
```

## Documentation Template

Create `/var/admin/server_inventory.md` with this structure:

```markdown
# Server Inventory - [hostname]

Last updated: YYYY-MM-DD

## Web Applications

| App Name | URL | Port | Backend | Tech Stack | Location | Status |
|----------|-----|------|---------|------------|----------|--------|
| OhMyQoder | internal | 20120 | Go | chi + golang | ~/ohmyqoder | ✅ Running |
| SIM Mubtadiat | reviewtechno.me | 80/443 | Next.js + Go | Vite + chi | /opt/simmubtadiat | ✅ Running |

## Database Services

| Service | Type | Port | Main DB | User | Notes |
|---------|------|------|---------|------|-------|
| mubtadiaat-db | PostgreSQL | 5432 | mubtadiaat_db | mubtadiaat | Docker container |
| smart-lms-db | PostgreSQL | 5432 | lms_db | lms_admin | PM2 managed |

## External Dependencies

| Service | Provider | Purpose | Auth Method |
|---------|----------|---------|-------------|
| Cloudflare DNS | Cloudflare | DNS + SSL | API token |
| GitHub | GitHub | Code repo | SSH key |

## Resource Usage

- CPU: X% (top process: NAME)
- Memory: X GB / Y GB total
- Disk: X GB / Y GB used (largest dirs: /path1, /path2)
- Network: X Mbps up / Y Mbps down

## Maintenance Schedule

| Task | Frequency | Last Run | Next Due | Owner |
|------|-----------|----------|----------|-------|
| Log rotation | Weekly | YYYY-MM-DD | YYYY-MM-DD | auto |
| DB backup | Daily | YYYY-MM-DD | YYYY-MM-DD | cron |
| Security updates | Monthly | YYYY-MM-DD | YYYY-MM-DD | admin |

## Emergency Contacts

- Main Admin: [contact info]
- DB Admin: [contact info]  
- DevOps Support: [contact info]
- Provider Support: [provider contact]
```

## Real Server Examples

### Example 1: jarvis's VPS (Aug 2026)
```
Apps Found:
1. OhMyQoder (Go tooling assistant) @ ~/ohmyqoder
   - Port: 20120
   - Config: ~/ohmyqoder/.env
   - Tunnel: cloudflared via ~/.9router
   
2. SIM Mubtadiat (Pesantren LMS) @ /opt/simmubtadiat  
   - Port: 80/443 (nginx) → 20128 (next.js)
   - DB: simmubtadiat-db-1 (PostgreSQL)
   - Access: https://reviewtechno.me
   
3. Digital Sekolah (Smart LMS) @ /home/ubuntu/smart-lms
   - PM2 managed
   - Port: 8085
   - Domain: rezaulin.tech
   
Databases:
- mubtadiaat_db (SIM Mubtadiat)
- smart_lms (Digital Sekolah) 
- Other: lms_admin, various test dbs
```

## Automation Scripts

### Quick Inventory Script
Save as `/usr/local/bin/server-inventory.sh`:
```bash
#!/bin/bash
echo "=== PROCESS MAP ==="
ps aux --sort=-%cpu | head -20

echo -e "\n=== PORT MAP ==="
netstat -tlnp | grep LISTEN

echo -e "\n=== DOCKER CONTAINERS ==="
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n=== TOP DIRECTORIES ==="
du -sh /opt /home /root 2>/dev/null | sort -h

echo -e "\n=== ENV FILES ==="
find /opt /home -maxdepth 3 -name '.env' 2>/dev/null | wc -l
echo "Found $(find /opt /home -maxdepth 3 -name '.env' 2>/dev/null | wc -l) .env files"
```

Usage: `server-inventory.sh > /tmp/inventory-$(date +%Y%m%d).log`

## Maintenance Best Practices

1. **Weekly updates**: Run discovery script every Monday morning
2. **Document changes immediately**: When deploying new apps or removing old ones
3. **Tag obsolete entries**: Mark retired apps with `[DEPRECATED]` rather than deleting
4. **Cross-reference URLs**: Ensure all public-facing endpoints have documented owners
5. **Security audit quarterly**: Review who has access to each app's credentials

## Related Skills
- See references/server-credential-discovery for finding specific app credentials
- See references/docker-troubleshooting for container-specific debugging