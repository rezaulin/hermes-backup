---
name: web-app-status-check
description: "Find and verify running web applications on a server — locate the project directory, identify the runtime (Docker/PM2/systemd/bare process), probe local + public endpoints, read logs, check DB health and backup freshness, then report status."
tags: [linux, webapp, health-check, docker, pm2, nginx, status, uptime, sysadmin]
triggers:
  - cek project
  - cek aplikasi
  - cek web
  - status aplikasi
  - aplikasi jalan
  - web down
  - situs down
  - is my app up
  - site down
  - health check
  - check my project
---

# Web App Status Check

Find a deployed web application on a server and verify it is actually healthy end-to-end, then report status clearly. Use whenever the user asks "cek project X yang lagi jalan", "aplikasinya masih hidup?", "web-nya down gak?", or similar.

## Workflow

### 1. Locate the project directory
Don't guess — search the whole filesystem shallowly, plus the usual homes:
```bash
find / -maxdepth 4 -iname '*<project-name>*' 2>/dev/null
find /opt /srv /var/www /home /root -maxdepth 3 -type d 2>/dev/null | head -50
```
Also check nginx configs — they often reveal project paths and domains:
```bash
ls /etc/nginx/sites-enabled/ && cat /etc/nginx/sites-enabled/<name>.conf
```

### 2. Identify the runtime — CHECK ALL FOUR, servers mix them
One server frequently runs several stacks at once (e.g. Docker for one app, PM2 for another, systemd for a third):
```bash
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
pm2 list
systemctl list-units --type=service --state=running | grep -iE 'node|php|gunicorn|uvicorn|<name>'
ss -tlnp | head -20        # who listens on which port
ps aux | grep -iE 'node|python|php|go|java' | grep -v grep
```
Map the chain: nginx vhost → proxy_pass port → owning process/container.

### 3. Health probes — local AND public
```bash
# Local (bypasses nginx/cert): expect 200 + fast time
curl -s -o /dev/null -w 'HTTP %{http_code} | %{time_total}s\n' http://127.0.0.1:<port>/
# Public (checks nginx + cert + app together)
curl -s -o /dev/null -w 'HTTPS %{http_code}\n' https://<domain>/ --max-time 10
```
Prefer verifying without `-k` (disabling TLS verification triggers security-approval prompts and hides cert problems). Only use `-k` deliberately and say so.

### 4. Recent logs
```bash
docker logs --tail 30 <container>            # docker
pm2 logs <name> --lines 30 --nostream        # pm2
journalctl -u <service> -n 30 --no-pager     # systemd
```

### 5. Database health
```bash
docker exec <db-ctr> pg_isready                       # postgres in docker
docker exec <db-ctr> psql -U postgres -lqt | cut -d'|' -f1   # list DBs
```

### 5b. Finding DB credentials without a .env file
Server processes often run without a readable `.env` (env passed inline by PM2/parent). Two recovery paths:
```bash
# (a) Read the running process's actual env — definitive proof of what it uses
tr '\0' '\n' < /proc/<PID>/environ | grep -E "DB_|DSN|PASSWORD|SECRET|PORT"
# (b) Read the source's DEFAULT DSN — processes with no env override fall back to it
grep -rn "dsn\|password=" backend/internal/config/*.go | head
```
If the process has no `DB_DSN` env, it is using the hardcoded fallback in source — that usually means the DB password is a known default in the codebase (a security finding worth reporting). Then probe directly:
```bash
PGPASSWORD='<pw>' psql -h 127.0.0.1 -U <user> -d <db> -Atc "SELECT count(*) FROM users;"
```
For a quick app census: `\dt`/`pg_tables` to list relations, then `count(*)` per core table (users by role, tenants/schools, students, exams). Report actual numbers — it grounds the status report in real usage.

### 5c. Service health beyond "process alive" — check real session state
A process can be UP while its function is dead. Probe functional endpoints, not just ports:
- WA/Baileys gateway: `curl -s localhost:<port>/status` → `{"connected":false}` means session died even though the process has 44-day uptime (phone logged out / socket closed). Reconnect path: `/qr` endpoint → scan again, or delete `auth/` dir.
- Backend with no `/health` route: any JSON 404 like `{"error":"Cannot GET /api/health"}` still proves the app answers; hit a real endpoint instead.
- PM2 restart counter > 0 or uptime delta vs other apps = silent restart, investigate.

### 6. Backup freshness — flag suspicious files
Look for recent backup files (`ls -la ~ /opt/<app> | grep -i backup`). Two signals:
- **Age**: last backup days/weeks old → mention it.
- **Size**: a suspiciously tiny SQL dump (e.g. 643 bytes) is almost certainly a FAILED or empty backup — call it out explicitly and point to the last known-good backup with a real size.

### 7. Report format
A compact table works well:

| Komponen | Status |
|---|---|
| App container | 🟢 Up X hours |
| Database | 🟢 healthy |
| Local HTTP | 🟢 200, <1ms |
| Public HTTPS | 🟢 200 |

Then: recent-log summary, warnings, and 2–3 concrete follow-up offers (fresh backup, DB inspection, investigate a restart).

## Pitfalls

### ⚠️ Container uptime deltas reveal silent restarts
`app Up 3 hours` vs `db Up 30 hours` means the app restarted recently. If the user didn't mention a deploy, flag it and offer to dig (`docker inspect --format '{{.State.StartedAt}}'`, `docker events`).

### ⚠️ Scanner/bot noise in logs is normal, not a breach
Public VPS logs constantly show automated probes hitting the raw IP: WordPress endpoints (`rest_route`, `/wp-admin`), `/register`, `/admin`, `/auth/callback`. The app answering them 404/405 is fine. Report it as background noise so the user doesn't panic — but DO flag actual successful (200) hits on sensitive paths.

### ⚠️ `git status` failing despite a `.git` dir
Projects on servers sometimes have an EMPTY `.git/` directory (an init that never completed). `git status` then says "not a git repository". Check `ls -la .git/` before concluding anything; an empty one is safe to re-init over.

### ⚠️ Never claim "healthy" from one signal
A green `docker ps` with a dead DB, or a 200 on port 8080 with a broken cert, still means the site is down for users. Minimum bar: container state + local probe + public probe + DB readiness.
