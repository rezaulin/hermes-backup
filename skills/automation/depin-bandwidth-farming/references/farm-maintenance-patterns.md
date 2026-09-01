# Farm Maintenance Patterns (verified 2026-08-30)

## Device abu-abu di dashboard + uptime BEKU (frozen) — stale tunnel-error marker

**Symptom:** device appears in the dashboard but grey; "Current online time" and
"Total online time" are stuck at the same N minutes (never increase); Balance $0.
Yet on the VM the SDK process runs (`pgrep -fc "earnapp run"` = 2), egress IP is a
good residential IP, and the marker check shows `perr_connected_1.651.510=YES` +
`perr_20_svc_connected_1.651.510=YES`. Looks healthy by marker-existence — but the
device stopped earning.

**Root cause:** a **stale `perr_tun_init_err_1.651.510.sent`** marker left over from an
earlier tunnel-init failure (e.g. created at 03:05 while the success markers are from
02:40). The SDK keeps the err state; merely restarting `earnapp run` does NOT clear it,
so the tunnel never comes back up → grey + frozen uptime. (Contrast: a fresh
`perr_tun_init_success` at a recent timestamp = healthy.)

**Diagnosis — trust TIMESTAMPS, not just YES/NO:**
```bash
# container time vs marker timestamps
sudo incus exec ea-N -- date -u +%Y-%m-%dT%H:%M:%SZ
sudo incus exec ea-N -- ls -la --time-style=+%H:%M:%S /etc/earnapp/*.sent | grep -E "tun_init|connected"
```
Healthy = `perr_tun_init_success_1.651.510.sent` timestamp is recent AND
`perr_tun_init_err` is absent. Stale = success is old + err marker present → repair below.
Also useful: `install_device?uuid=...` returning `Not found` = not registered on backend.

**Fix — clear stale state, then force a FRESH register:**
1. Delete the stale markers (use `rm -fv` so deletion is confirmed on screen):
   ```bash
   sudo incus exec ea-N -- sh -c 'rm -fv /etc/earnapp/perr_connected_1.651.510.sent /etc/earnapp/perr_20_svc_connected_1.651.510.sent /etc/earnapp/perr_tun_init_success_1.651.510.sent /etc/earnapp/perr_tun_init_err_1.651.510.sent'
   ```
2. Kill the SDK:
   ```bash
   sudo incus exec ea-N -- sh -c 'pkill -f "earnapp run" 2>/dev/null; pkill -f "earnapp autoupgrade" 2>/dev/null; sleep 2'
   ```
3. Re-run `finish_install` as its OWN exec step, full stdout, no grep filter (see gotcha):
   ```bash
   sudo incus exec ea-N -- bash -c 'export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt; echo yes | timeout 45 /usr/bin/earnapp finish_install 2>&1'
   # expect: ✔ Service refreshed → ✔ EarnApp is active (making money in the background)
   ```
4. Wait 60–120 s, then verify **fresh** markers (success timestamp is NOW, err is `no`):
   ```bash
   sudo incus exec ea-N -- sh -c 'for m in perr_connected_1.651.510 perr_20_svc_connected_1.651.510 perr_tun_init_success_1.651.510 perr_tun_init_err_1.651.510; do [ -f /etc/earnapp/$m.sent ] && echo "$m=YES" || echo "$m=no"; done'
   ```
   Success = `tun_init_success=YES` + `tun_init_err=no`, and `ls -la --time-style=+%H:%M:%S`
   shows the success marker freshly written. Then refresh the dashboard — uptime resumes.
5. If the device was never in `links.txt`, open `/r/<uuid>` in a Google-SSO-logged-in
   browser to bind it (device not found = never bound, separate from this repair).

**Gotcha — `finish_install` silently producing NO output inside a complex `bash -c`:**
wrapping kill+rm+finish_install in ONE heavily-nested `bash -c '...'` via exec-await can
silently do nothing (quoting), leaving markers stale and you none-the-wiser. Run
`finish_install` as its own exec call with `2>&1` and NO `grep` so you can SEE `✔ Registered`.

## Redsocks .conf files disappear mysteriously

All `.conf` files in `/opt/earnapp-farm/redsocks/` were deleted at some point (only `.log` files remained). The redsocks processes that started before the deletion survived (config loaded into memory at launch), but any process that died later could not restart because the `.conf` was missing. Root cause unknown (maybe a clean-up script, or the `recreate.sh`/`fix-all.sh` overwrites).

**Fix: bootstrap cron** — a script that runs every minute via root crontab:
- Checks each `.conf` file (dev0..dev19). If missing, regenerates from the template.
- Checks each redsocks process (`pgrep -f "redsocks -c dev$i.conf"`). If not running, starts it with `nohup`.
- Cron is the *only* process parent that survives the Freestyle `exec-await` session teardown (which kills `nohup`, `setsid`, and `systemd-run`).

Template (from `fix-all.sh`):
```
base { log_debug = off; log_info = on; log = "stderr"; daemon = off; redirector = iptables; }
redsocks { local_ip = 0.0.0.0; local_port = $rsport; ip = 127.0.0.1; port = $p; type = socks5; }
```
Where `rsport = 11080 + i` and `p = 60000 + i`.

## 9proxy Offline vs curl probe discrepancy

The watchdog probes each port via `curl -x http://127.0.0.1:$p https://api.ipify.org`. A port can **return an IP + low latency** (watchdog sees "OK") but **9proxy itself marks it "Offline"** in `9proxy port -s`. This happened on port 60001 (73.36.168.144, 1.5-5.2s latency, 9proxy-status=Offline). The dashboard then showed the device as "not earning/low quality" despite the SDK markers showing `connected` + `tun_init_success`.

**Fix: add 9proxy Offline check to the watchdog** — inside the main loop, after the curl probe, also check `9proxy port -s | grep ":$p " | grep -q Offline`. If yes, log and `swap_port` immediately (no latency threshold). This catches cases where the 9proxy-side binding is stale/erroring even though the port still responds to HTTP.

## IP quality auto-blacklist

Some IPs are flagged as "VPN" / "Low quality" by EarnApp even though they are residential (e.g. 99.160.186.234 — Wheaton IL, AT&T — EarnApp detected as VPN). The watchdog's original latency/offline probes don't catch this.

**Fix: add `is_low_quality()` to the watchdog** — after probing a new IP, query `ipinfo.io/$ip/json` for the `org` field. If the org contains a known datacenter/cloud keyword (AMAZON, DIGITALOCEAN, HETZNER, OVH, VULTR, GOOGLE, MICROSOFT, AZURE, ALIBABA, TENCENT, HUAWEI, DATACENTER, HOSTING, SERVER, CLOUD, COLO, RACKSPACE, LINODE, ORACLE, IBM, COGENT, HE.NET, LEVEL3, INTERNEXA), auto-add the IP to the blacklist file and `swap_port` immediately. The blacklist persists across watchdog runs.

Blacklist file: `/opt/earnapp-farm/blacklist-ip.txt` — one IP per line, comments allowed with `#`. The watchdog checks `is_blacklisted()` before every probe; if the current IP is blacklisted, swap immediately.

## finish_install vs earnapp run

`earnapp run` starts the SDK process and connects to the service (creates `perr_connected` markers). BUT it does NOT register the device UUID on the EarnApp backend. Without registration, the dashboard link returns "The device is not found".

**Registration requires `earnapp finish_install`** (a hidden subcommand, not shown in `--help`). This:
1. Accepts terms (pipe `echo yes |` to auto-accept)
2. Calls `https://client.earnapp.com/install_device?uuid=<uuid>&version=1.651.510&...`
3. Creates systemd services (`earnapp.service`, `earnapp_upgrader.service`)
4. Prints `✔ Registered` + the `/r/<uuid>` URL

**Critical env var:** `NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt` MUST be set in the process that runs `finish_install` — the SDK bundles its own CA store which lacks the SSL.com intermediate, causing `SELF_SIGNED_CERT_IN_CHAIN` → `Failed registration` → `perr_connected` markers without backend registration.

## iptables REDIRECT per device

Every container needs its own PREROUTING rule to redirect TCP through its per-device redsocks port. The convention:
- Container `ea-N` → iptables chain `EARN_N` → REDIRECT to port `11080 + N`
- The chain is created with `iptables -t nat -N EARN_N`
- The REDIRECT rule: `iptables -t nat -A EARN_N -p tcp -j REDIRECT --to-ports $((11080 + N))`
- The PREROUTING jump: `iptables -t nat -A PREROUTING -s <container_ip> -j EARN_N`

Missing REDIRECT rules cause the container's traffic to egress through the VM's datacenter IP (e.g. `152.236.128.19`), which EarnApp rejects with `tunnel_init_decline: ip_type.dch`.

The `fix-all.sh` script has a `wire_nat()` function that does this. When bringing up new devices, run `wire_nat` for each container after `incus launch` and before `setup_dev`.

## Watchdog v2 — detection summary

| Signal | Detection | Swap trigger | Added |
|:--|:--|:--|:--:|
| curl probe → no IP | `ip="0"` | fail ≥ 2 | original |
| latency ≥ LAT_BAD (6000ms) | `lat >= 6000` | jelek ≥ 3 | original |
| IP in blacklist file | `is_blacklisted()` | 1 hit → immediate | 2026-08-30 |
| 9proxy port shows Offline | `is_9proxy_offline()` | 1 hit → immediate | 2026-08-30 |
| IP org is datacenter/cloud | `is_low_quality()` | 1 hit → auto-blacklist + swap | 2026-08-30 |
