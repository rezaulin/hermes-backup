---
name: linux-server-diagnostics
description: "Diagnose and fix Linux server resource issues — disk full, CPU overload, RAM pressure, runaway processes. Standard triage workflow plus targeted cleanup strategies for Ubuntu/Debian servers."
tags: [linux, server, diagnostics, disk, cpu, ram, cleanup, ubuntu, sysadmin]
triggers:
  - server overload
  - disk full
  - cpu tinggi
  - ram penuh
  - server lambat
  - space server
  - resource check
  - server health
---

# Linux Server Diagnostics & Cleanup

## When to Load
User reports or asks about server performance, disk space, CPU usage, RAM, or general server health. Also load when any command reveals resource exhaustion.

## Triage Workflow (Run These First)

Run all three in parallel:

```bash
# Disk
df -h

# RAM
free -h

# CPU + load
uptime && echo "---" && nproc && echo "---" && top -bn1 | head -20
```

### Interpretation Guide

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Disk usage | <80% | 80-95% | >95% (immediate action) |
| RAM available | >50% free | 20-50% | <20% or heavy swap |
| Load average | ≤ nproc | 1-2x nproc | >2x nproc sustained |
| CPU idle | >20% | 5-20% | 0% (fully saturated) |

## Disk Cleanup — Common Targets (Ubuntu/Debian)

### Safe to clean (no user confirmation needed for caches):
```bash
# Package manager caches (auto-rebuild on demand)
npm cache clean --force
rm -rf ~/.cache/pip ~/.cache/uv ~/.cache/go-build ~/.cache/node-gyp

# Electron + Playwright caches (large, ~1-2GB)
rm -rf ~/.cache/electron ~/.cache/ms-playwright

# System journal logs — set BOTH a time AND size cap
journalctl --vacuum-time=3d
journalctl --vacuum-size=150M   # critical! vacuum-time alone FREES 0B when
                                # archived journals predate retention; only the
                                # size cap actually shrank 696M→120M on one 30G VPS

# Old rotated logs + the live failed-login log (btmp)
rm -f /var/log/btmp.1 /var/log/auth.log.{1,2,3,4}*
truncate -s 0 /var/log/btmp   # btmp (failed SSH logins) grows to 90M+ — truncate, safe

# snapd cache (huge, ~800M) + apt package index (auto-re-download)
rm -rf /var/lib/snapd/cache/*
apt-get clean && rm -rf /var/lib/apt/lists/*   # apt index rebuilds on next update

# Go module cache — ~1.2G, re-downloads on demand. Verify GOPATH not mid-build first.
# GOFLAGS=-mod=mod; go clean -modcache   # or rm -rf /root/go/pkg/mod if no active Go dev

# Temp files
find /tmp -type f \( -name "*.deb" -o -name "*.tar.gz" \) -delete
find /tmp -type d -name "go-build*" -exec rm -rf {} +
find /tmp -type d -name "electron-download*" -exec rm -rf {} +
```

### Requires user confirmation:
- Project directories (always verify with user before deleting)
- Docker images/containers (`docker system prune`) — see orphan-verification below
- Snap cache (`/var/lib/snapd/cache/`)
- Old kernel images in `/boot/`

## Docker / Container Cleanup — verify ORPHANED before deleting

The hard part is not deciding what to delete — it's **proving a container/DB/volume is truly unused** so you don't destroy a live service. Always separate "safe caches" from "perlu konfirmasi" and, for anything running, trace its connections BEFORE removal.

### Critical distinction: "running" ≠ "in use"
A postgres container that's been `Up 2 weeks` can still be a **live backend for a running systemd service or another app**, not an orphan. A docker container in `Created` state (never started) is a leftover. Both need verification.

### Orphan-verification sequence (in the right order)
```bash
# 1. Map the compose project → source dir (this alone resolves many dupes)
docker inspect <ctr> --format '{{json .Config.Labels}}'
# look for com.docker.compose.project, .project.working_dir, .project.config_files
find /opt /root /home /srv -maxdepth 3 -name "docker-compose*" 2>/dev/null

# 2. Is anything ACTUALLY connected to this port? (host-side proof)
lsof -i :<port>          # or ss -tlnp | grep <port>
# ESTABLISHED TCP from another process = LIVE consumer. Do NOT touch.

# 3. Is the "app" that should use this DB even running?
docker ps -a                            # Created vs Up state
pm2 list / systemctl list-units --all   # host apps (pm2 apps & systemd services)

# 4. Is it on a docker network ALONE (no peers = orphan) vs shared with consumers?
docker network ls
docker inspect <ctr> --format '{{json .NetworkSettings.Networks}}'
for c in $(docker ps --format '{{.Names}}'); do
  echo "$c: $(docker inspect $c --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')"
done
# Orphan pattern: the DB sits alone on its own compose network (e.g. ubuntu_default),
# no app container shares it, no host process connects → safe to remove.

# 5. Map the LIVE web path so you never kill it:
nginx -T | grep -E 'server_name|listen|proxy_pass'   # which vhost → which port
```

### Trimming the network cuts reconnect loops
When presenting a container to the user, say which **live service + port + domain** you verified it (or its sibling) is serving, so it's unambiguous which copy is the real one.

### Real session lesson: duplicate projects by name
Two compose dirs (`/opt/simmubtadiat` and `/home/ubuntu`) both built a `mubtadiaat` app. Only `/opt/simmubtadiat` was proxied by nginx to `reviewtechno.me` on port 8080; the `/home/ubuntu` copy's app was `Created` (never started). The `/home/ubuntu` DB was the orphan. **Always resolve "which copy is live" via nginx vhosts + ports before targeting a container by project name.**

### Hard confirmation gate on DB volumes
Deleting a postgres container's **named volume** destroys data irreversibly. Before `docker volume rm`, list the DB's contents if you can:
```bash
docker exec <ctr> psql -U <user> -l   # show databases → judge if it's test/live
```
A `Created`-state app with a running sibling DB and no peer network → orphan, safe: `docker rm` container, `docker image rm`, `docker volume prune -f`.

## CPU Investigation

### Step 1: Identify top consumers
```bash
ps aux --sort=-%cpu | head -15
```

### Step 2: Understand process relationships
```bash
pstree -p -a -s <PID>
```

### Step 3: Check for orphaned processes
```bash
# Deleted PTY = parent SSH session died but process still running
ls -la /proc/<PID>/fd/
# Look for "(deleted)" on /dev/pts/* entries

# Check process state
cat /proc/<PID>/status | grep -E "State|Threads"
cat /proc/<PID>/wchan
```

### Step 4: Kill runaway processes
```bash
kill <PID>          # graceful first
kill -9 <PID>       # if graceful fails
```

## Pitfalls

### ⚠️ Recursive shell scripts = infinite CPU loop
A script that `exec`s itself (or calls itself) creates an infinite loop at 100% CPU:
```bash
# BUG: this script calls itself forever
cd /root/myapp && exec ./src/notify.sh
```
**Detection**: `pstree` shows the script spawning itself. `cat` the script to confirm the recursive call.
**Fix**: Kill the process, then fix the script content before re-running.

### ⚠️ Full-disk `du -x /` times out on busy servers — use per-directory instead
A recursive `du -x -h --max-depth=2 /` over the whole filesystem often exceeds the 60s tool timeout on boxes with big `/usr`, docker volumes, or many small files. Don't leave it hanging.

**Correct sizing approach — hit known big dirs individually:**
```bash
for d in /var/log /var/cache /var/tmp /tmp /root/.cache /root/.npm /root/.local \
         /var/lib/docker /usr /home /opt; do
  echo "=== $d ==="; du -x -h -s "$d" 2>/dev/null
done
```
Then drill into whichever is large with `du -x -h --max-depth=2 <dir>`. Targets order: journal logs (`journalctl --disk-usage`), caches, docker, rotated logs (`find /var/log -type f -size +50M`).

### ⚠️ NEVER list active projects as "safe to delete" — separate caches from projects
When presenting cleanup candidates, NEVER include project directories in the "safe to delete" batch. A project that looks unused (e.g., `/root/omni-pos`) may be the one the user is actively building right now.

**Correct workflow:**
1. List caches, logs, and temp files as "safe to delete" (these are always safe)
2. List project directories SEPARATELY under a "❓ Perlu Konfirmasi" section
3. For each project, briefly describe what it appears to be (check README, package.json)
4. Wait for explicit user confirmation before deleting ANY project directory

**User correction from real session:** User was frustrated that their active project was listed alongside disposable cache. This is a trust-eroding mistake. Always separate caches from projects in your cleanup report.

### ⚠️ `hermes setup` / `hermes gateway` processes
These may be the agent handling the current conversation. Do NOT kill them — check with the user first. Restart via `hermes gateway restart` if needed.

**Distinguish the runaway `hermes setup` from the live `gateway` (real session, 98% CPU for 12 DAYS):** A stuck `hermes setup` process (`.../venv/bin/hermes setup`) can spin at ~98% CPU for weeks after the install it was meant to run already finished — it's a zombie setup, NOT the agent. The live agent is `python -m hermes_cli.main gateway run` (CPU ~0.1%). Before killing anything, verify by PID which is which:
```bash
ps -o pid,ppid,etime,pcpu,cmd -p <PID>
# live gateway: cmd ends "...gateway run", CPU ~0.1%
# runaway:      cmd ends "...hermes setup", CPU ~98%
# If the runaway's parent is a stale `bash` chain (PPID → bash), kill the whole chain.
```
Kill only the runaway. Re-verify the gateway PID is still alive AFTER the kill (`ps -p <gwpid>`).

### ⚠️ Orphaned processes from dead SSH sessions
Processes started via SSH with no `nohup`/`tmux`/`screen` keep running after disconnect. Their PTY file descriptors show as `(deleted)`. These can consume CPU indefinitely. Safe to kill if confirmed unused.

### ⚠️ PostgreSQL systemd "active (exited)" is MISLEADING — meta-service, not the actual cluster
`systemctl status postgresql` shows `Active: active (exited)` even when the actual database is DOWN, because `postgresql.service` is a **meta-service** (`ExecStart=/bin/true`) that just triggers cluster services and exits. The real PostgreSQL runs under `postgresql@14-main.service` (or similar version-specific unit).

**Real session error:** User reported login failure on smart-lms. `systemctl status postgresql` showed "active (exited)" — looks healthy. But `/var/run/postgresql/.s.PGSQL.5432` socket didn't exist, and all app connections were refused. The actual cluster had died due to disk pressure (89% full).

**Correct diagnosis workflow:**
```bash
# 1. Check if socket exists (most reliable signal)
ls -la /var/run/postgresql/.s.PGSQL.*

# 2. Try connecting (MUST cd /tmp first — postgres user can't access /root)
cd /tmp && sudo -u postgres psql -c "SELECT 1"

# 3. Check actual cluster service
systemctl status postgresql@*-main 2>/dev/null
```

**Fix when PostgreSQL cluster is dead:**
```bash
sudo systemctl restart postgresql
ls -la /var/run/postgresql/.s.PGSQL.5432   # verify socket appeared
pm2 restart <app-name>                       # restart dependent app
```

**Root cause pattern:** Disk >85% → PostgreSQL can't write WAL → cluster dies silently → meta-service still shows "active". Always check `df -h /` when PostgreSQL connections fail.

### ⚠️ PM2-managed apps — logs and restart pattern
Apps managed by PM2 store logs at `/root/.pm2/logs/<name>-{out,error}.log`:
```bash
pm2 list                          # all apps + status + uptime
pm2 logs <name> --lines 50 --nostream  # recent logs without tailing
```
After fixing a dependency (e.g., restarting PostgreSQL), always `pm2 restart <name>` — the app won't auto-reconnect if it's been erroring for hours.

## Cleanup Priority Order
1. **Caches** (npm, pip, go-build, electron, playwright) — always safe, auto-rebuild
2. **Journal logs** — `journalctl --vacuum-time=3d` is safe
3. **Old rotated logs** — `.log.1`, `.log.2.gz`, `btmp.1`
4. **Temp files** — `/tmp` cleanup
5. **Unused projects** — ONLY with explicit user confirmation
6. **Docker cleanup** — `docker system prune` with confirmation
