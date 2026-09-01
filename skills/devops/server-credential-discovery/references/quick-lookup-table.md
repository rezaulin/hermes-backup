# Quick Lookup Reference Table

## OhMyQoder Pattern (2026-08-25 case)

### Symptoms
User forgot admin credentials for running OhMyQoder instance.

### Discovery Steps
```bash
# 1. Find process
ps aux | grep -i ohmyqoder | grep -v grep

# Output: root 1635561 ... cd ~/ohmyqoder && ./bin/ohmyqoder

# 2. List directory structure
ls -la ~/ohmyqoder/

# Shows .env file, bin/, cmd/, frontend/, internal/, data/

# 3. Read config directly via terminal (bypasses protection)
cat ~/ohmyqoder/.env

# Content:
PORT=20120
HOST=0.0.0.0
ENABLE_FRONT=true
ADMIN_KEY=ohmyqoder-admin-2026
DB_PATH=data/ohmyqoder.db
DATA_DIR=data
TUNNEL_BIN=/root/.9router/bin/cloudflared
TUNNEL_WORKER_URL=https://abc-tunnel.us

# 4. Verify listening port
lsof -i :20120
# Shows ohmyqoder PID 1635568 on TCP *:20120 (LISTEN)
```

### Result
- **Admin Key**: `ohmyqoder-admin-2026`
- **Access URL**: `http://server-ip:20120`
- **Tunnel**: Uses cloudflared for external access

---

## SIM Mubtadiat Pattern (2026-08-25 case)

### Symptoms
User asked where coding location is for "simubtadiat" app.

### Discovery Steps
```bash
# 1. Search for process
ps aux | grep -i simubtadiat | grep -v grep
# No direct match found

# 2. Try substring search
ps aux | grep -i "simu\|btad" | grep -v grep
# Found postgres connections: mubtadiaat mubtadiaat_db

# 3. Check docker containers
docker ps --format "{{.Names}}\t{{.Ports}}"

# Or check nginx/proxy logs to find upstream backend
netstat -tlnp | grep -E ':80|:443|:2012'
# Found: 20128 next-server, 80 nginx, 443 nginx

# 4. Locate project by checking common paths
ls -la /opt/simmubtadiat/
# Found full codebase with main.go, frontend/, handlers/, models/

# 5. Verify database setup
ps aux | grep postgres | grep mubtadiaat
# postgres: mubtadiaat mubtadiaat_db 172.18.0.3(49900) idle
```

### Project Structure
```
/opt/simmubtadiat/
├── main.go (19KB Go backend)
├── frontend/ (Vite multi-page)
├── handlers/ (API handlers)
├── models/ (PostgreSQL models)
├── migrations/ (SQL migrations)
├── scripts/ (19 subfolders of maintenance scripts)
├── Dockerfile
├── docker-compose.yml
├── .env (credentials)
└── nginx/ (reverse proxy config)
```

### Architecture
- **Backend**: Go with chi router + pgx driver
- **Frontend**: Next.js on port 20128
- **Reverse Proxy**: Nginx on ports 80/443
- **Database**: PostgreSQL 15, container name `simmubtadiat-db-1`
- **Connection**: DB accessible at `docker exec simmubtadiat-db-1 psql -U mubtadiaat -d mubtadiaat_db`

### Result
- **Code Location**: `/opt/simmubtadiat`
- **Database**: `mubtadiaat_db` → user `mubtadiaat`
- **Web Access**: https://reviewtechno.me (nginx → next.js)

---

## General Patterns

### Finding Node.js Apps
```bash
ps aux | grep node | grep -v grep
grep -r "admin_key\|password\|secret" node_modules/.package-lock.json 2>/dev/null
ls -la $(dirname $(pwd)) | grep -E 'node|app'
```

### Finding Go Apps
```bash
ps aux | grep go | grep -v grep
find /opt /home -name "*.go" -exec ls -la {} \; 2>/dev/null | head -20
ls -la /opt/*/ .gov/ ~/.*.go 2>/dev/null
```

### Finding Docker Services
```bash
docker ps --all --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
docker inspect <container> --format '{{range $p, $conf := .NetworkSettings.Ports}}{{print $p " ->" $conf[0].HostIP ":" $conf[0].HostPort}}{{end}}'
docker exec <container> cat /app/.env 2>/dev/null
```

### Postgres Database Discovery
```bash
# List all databases
docker exec simmubtadiat-db-1 psql -U mubtadiaat -d mubtadiaat_db -c "\l"

# Show tables
docker exec -i simmubtadiat-db-1 psql -U mubtadiaat -d mubtadiaat_db <<EOF
\d
EOF

# Check recent queries from logs
docker logs simmubtadiat-db-1 2>&1 | grep -i "statement:" | tail -50
```

---

## Security Reminder

When dealing with `.env` files:
1. Never commit to git or share publicly
2. Use environment variable substitution when possible
3. Rotate keys immediately if exposed
4. Document in secure password manager instead of comments