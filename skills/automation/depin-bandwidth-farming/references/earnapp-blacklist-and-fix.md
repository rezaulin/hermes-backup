# EarnApp IP Blacklist + Farm Self-Heal (verified 2026-08-30, ubuntu-2xl farm)

Covers three linked problems seen on the 20-device Incus EarnApp farm and their fixes:
1. A residential IP flagged **"Low quality IP (detected as VPN)"** by EarnApp → device stops earning.
2. The per-device **redsocks chain silently dying** (`.conf` files vanish) → device `ECONNREFUSED` walls.
3. A device that was connected but **never `finish_install`-registered** → `/r/<uuid>` says "device not found".

All three share one structural fact: **Freestyle `exec-await` kills every background daemon at session end** (nohup/setsid/systemd-run all die, cron survives). So any self-heal must be driven by a **root crontab bootstrap**, not by one-shot exec calls. See skill `freestyle-vms` for the exec-await quirk detail.

## 1. IP blacklist (VPN/low-quality IPs)

EarnApp flagged `99.160.186.234` (Wheaton, Illinois, AT&T / AS7018) as VPN even though it is residential. Symptom in dashboard: device shows `!`, "Device is not earning", "Low quality IP (detected as VPN)", with the detected IP shown. The device's `tun_init_success` marker may STILL be present — the marker only proves the tunnel came up, not that EarnApp rates the IP as earnable.

### Fix: blacklist file + watchdog check

`/opt/earnapp-farm/blacklist-ip.txt` (one IP per line, `#` comments allowed):
```
# EarnApp flagged these as VPN/low-quality even though residential:
99.160.186.234
```

Patch the watchdog so every probe checks the blacklist and swaps immediately:

```bash
# in earnapp-watchdog.sh — after the probe line:
#   out=$(probe_port "$p"); ip=${out%% *}; lat=${out##* }
# BLACKLIST: IP rusak/VPN — swap LANGSUNG, ga nunggu threshold
if [ "$ip" != "0" ] && grep -qxF "$ip" "$BLACKLIST" 2>/dev/null; then
  log "port $p IP $ip BLACKLISTED -> SWAP langsung"
  swap_port "$p"; fail=0; jelek=0
  echo "fail=$fail jelek=$jelek" > "$sf"
  continue
fi
```

Also make `swap_port` re-roll a new IP up to 5× so it doesn't land on another blacklisted IP:
```bash
swap_port(){
  local p=$1 idx=$((p-BASE_PORT)) c out ip lat tries=0
  c=$(printf "ea-%02d" "$idx")
  while [ "$tries" -lt 5 ]; do
    tries=$((tries+1))
    log "SWAP port $p (try $tries) -> forward US baru"
    if ! 9proxy proxy -c "$COUNTRY" -p "$p" >/dev/null 2>&1; then log "  !! forward_gagal $p"; return 1; fi
    sleep 3
    out=$(probe_port "$p"); ip=${out%% *}; lat=${out##* }
    [ "$ip" = "0" ] && { log "  !! swap masih mati $p (try $tries)"; continue; }
    grep -qxF "$ip" "$BLACKLIST" 2>/dev/null && { log "  !! IP baru $ip MASIH BLACKLIST -> forward ulang"; continue; }
    log "  new IP $p = $ip (${lat}ms)"
    pkill -f "redsocks -c $REDSOCKS_DIR/dev$idx.conf" 2>/dev/null
    nohup redsocks -c "$REDSOCKS_DIR/dev$idx.conf" >"$REDSOCKS_DIR/dev$idx.log" 2>&1 </dev/null &
    echo "$ip $(now)" > "$STATE_DIR/ip.$p"
    incus info "$c" >/dev/null 2>&1 && incus exec "$c" -- bash -c "pkill -f earnapp 2>/dev/null; nohup earnapp run >/tmp/earun.log 2>&1 &" 2>/dev/null
    log "  restarted $c"
    return 0
  done
  log "  !! swap gagal 5x utk port $p"; return 1
}
```

Manual one-off swap of a single port (e.g. 60006 = ea-06) when you don't want to wait for the watchdog tick:
```bash
9proxy proxy -c US -p 60006        # forward a fresh US IP to port 60006
sleep 4
curl -s -x http://127.0.0.1:60006 https://api.ipify.org   # confirm new IP (host-side OK for socks5)
# if that IP is blacklisted, run the forward again (loop) — watchdog handles this automatically
```

## 2. redsocks chain self-heal (conf vanished / daemon died)

Observed: ALL 20 `devN.conf` files were gone from `/opt/earnapp-farm/redsocks/` (only `.log` files remained) yet old redsocks processes kept running — they had loaded config into memory at start. Any process that died could NOT restart (no conf). The iptables `EARN_<N>` REDIRECT rules persisted (e.g. ea-05 → `EARN5` → port 11085), so traffic hit a dead listener → `ECONNREFUSED`.

### Fix: crontab bootstrap that regenerates conf + restarts dead redsocks every minute

`/opt/earnapp-farm/bootstrap-redsocks.sh`:
```bash
#!/bin/bash
# regenerate missing .conf + start dead redsocks. cron-safe, idempotent.
DIR=/opt/earnapp-farm
REDSOX=$DIR/redsocks
RS_BASE=11080
BASE_PORT=60000
mkdir -p "$REDSOX"
for i in $(seq 0 19); do
  p=$((BASE_PORT+i)); rsport=$((RS_BASE+i)); CONF="$REDSOX/dev$i.conf"
  if [ ! -f "$CONF" ]; then
    cat > "$CONF" <<EOF
base {
  log_debug = off;
  log_info = on;
  log = "stderr";
  daemon = off;
  redirector = iptables;
}
redsocks {
  local_ip = 0.0.0.0;
  local_port = $rsport;
  ip = 127.0.0.1;
  port = $p;
  type = socks5;
}
EOF
    echo "[$(date -u +%H:%M:%S)] regenerated $CONF" >> $DIR/cron.log
  fi
  if ! pgrep -f "redsocks -c $CONF" >/dev/null 2>&1; then
    nohup redsocks -c "$CONF" >"$REDSOX/dev$i.log" 2>&1 </dev/null &
    echo "[$(date -u +%H:%M:%S)] bootstrap started redsocks dev$i pid $!" >> $DIR/cron.log
  fi
done
```

Register in root crontab (survives exec-await):
```bash
(crontab -l 2>/dev/null | grep -v bootstrap-redsocks; echo "* * * * * /bin/bash /opt/earnapp-farm/bootstrap-redsocks.sh >> /opt/earnapp-farm/cron.log 2>&1") | crontab -
```
The existing watchdog cron line (`*/5 * * * * /bin/bash /opt/earnapp-farm/earnapp-watchdog.sh 20 >> ...`) stays. Bootstrap every minute catches a dead redsocks within 60s; the watchdog handles IP-quality swaps every 5 min.

## 3. Device connected but "The device is not found" on link

`earnapp run` makes the SDK connect (`perr_connected` marker) but does **NOT register the device on EarnApp's backend**. Registration happens in `earnapp finish_install` (run by the official `install.sh`). If the device was DEAD at install time (redsocks down → finish_install's `install_device` request failed ECONNREFUSED), the node is never registered → `/r/<uuid>` returns "The device is not found" even after you later fix connectivity.

### Fix: after the proxy chain is healthy, re-run finish_install inside the container

```bash
sudo incus exec ea-N -- bash -c '
export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt
echo yes | timeout 45 /usr/bin/earnapp finish_install 2>&1
'
```
Success looks like:
```
✔ Service already exists: earnapp
✔ EarnApp is installed and running.
- Registering Device...
✔ Registered
✔ EarnApp is active (making money in the background)
⚠ Open the following URL in the browser:
  https://earnapp.com/r/<uuid>
```
Then open the URL in a browser logged into earnapp.com (Google SSO) — device binds immediately (no more "device not found"). The UUID does NOT change across finish_install — same `/r/<uuid>` as before.

## Verify end-to-end after a fix

- **Egress (decisive):** `sudo incus exec ea-N -- curl -s https://api.ipify.org` → must be a US residential IP, NOT the VM egress. (Host-side `curl -x http://127.0.0.1:<rs-port>` only works for socks5 redsocks.)
- **Markers:** wait 60–90s after `earnapp run` restart; expect phase order `perr_05_svc_init → perr_10_show_dialog → perr_15_choose_peer → perr_connected → perr_20_svc_connected → perr_tun_init_success`.
- **Registration:** `finish_install` must print `✔ Registered` (not just "Open the following URL") — that is the only proof the node is bound to the account.

## Files on the farm VM (ubuntu-2xl, /opt/earnapp-farm/)
- `blacklist-ip.txt` — IPs to never re-forward (VPN/low-quality).
- `bootstrap-redsocks.sh` — 1-min crontab self-heal for redsocks conf+daemon.
- `earnapp-watchdog.sh` — 5-min crontab quality watchdog (now blacklist-aware).
- `state/ip.<port>`, `state/wd.<port>` — per-port current IP + fail/jelek counters.
- `durability.csv` — telemetry history.
