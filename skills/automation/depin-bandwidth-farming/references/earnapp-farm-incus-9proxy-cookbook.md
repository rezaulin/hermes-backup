# EarnApp farm on Incus + 9Proxy By-IPs — end-to-end verified recipe (2026-08-30)

Full pipeline that got devices online & linked on a 32C/64G Freestyle VM (Ubuntu 24.04, Incus 6.0, Docker 29). Every step below was executed and verified this session.

## Architecture
```
9proxyd (By-IPs, US residential)          ── 20 forwarded ports 127.0.0.1:60000-60019
   │ each port = one SOCKS5/HTTP proxy (US, ~1.2-3s latency)
redsocks (host, one per device :11080-11099)── upstream = 127.0.0.1:6000N, type=socks5
   │
iptables REDIRECT (PREROUTING -s <containerIP> -j EARNx → --to-ports 11080+N)
   │
20 Incus Debian containers ea-00..ea-19 ── each `earnapp run` (SDK 1.651.510)
```

EarnApp SDK ignores HTTP_PROXY env, so the proxy must be applied at the network layer (redsocks+iptables). This is the same principle as the Docker redsocks path, but with Incus container IPs on the bridge instead of Docker bridge IPs.

## 9Proxy By-IPs CLI — verified gotchas
- **Login = account username+password, NOT api-key.** `9proxy auth -u <email> -p <pass>`. The api-key is only for the By-GB extract API; By-IPs uses the App login. Confirm plan/budget: `9proxy proxy -b` shows `Remaining IPs`.
- **Default `Num ports` = 10.** Forwarding >10 fails with `✗ Forwarding failed: no port available`. Fix: `9proxy setting --start 60000 --limit 20` then re-forward. Check current: `9proxy setting --display`.
- **Ranged forward is rejected** (`9proxy proxy -c US -p 60000-60019` → `Params validation failed`). Must loop per-port: `for p in $(seq 60000 60019); do 9proxy proxy -c US -p $p; done`.
- **Forwarded ports are BOTH SOCKS5 and HTTP.** Test: `curl -x http://127.0.0.1:60000 https://api.ipify.org` and `curl -x socks5://...` both work.
- **Refresh same port = new IP.** A dead/slow IP is replaced by `9proxy proxy -c US -p <same port>` (no need to kill port first, though `9proxy port -k <port>` works too). Always verify the new exit: `curl -x http://127.0.0.1:<port> https://api.ipify.org`.
- Install .deb (`https://static.9proxy-cdn.net/download/latest/linux/9proxy-linux-debian-amd64.deb`) → `systemctl start 9proxyd`. Full CLI help: `9proxy -h`, `9proxy proxy -h`, `9proxy port -h` (`-s` status table, `-k` kill, `-t` test).

## EarnApp linking — SDK 1.651.510 + NODE_EXTRA_CA_CERTS (critical)
Symptom: device turns on but `earnapp.com/r/<uuid>` says "The device is not found" → device was never registered in backend.

- **Old image SDK 1.294.218 (e.g. `fazalfarhan01/earnapp`) is DEAD.** Its hardcoded proxy-IP allowlist is expired → log `restricted_domain: proxyjs.luminatinet.com failed 15.197.193.114` → never connects → link always "device not found". Do not use it.
- **Use official SDK 1.651.510**: `wget https://cdn-earnapp.b-cdn.net/static/earnapp-ssl3-x64-1.651.510`. Filename pattern from `install.sh`: `${PRODUCT:-earnapp}${SSL_SUFFIX:-ssl3}-x64-${VERSION}`, VERSION=1.651.510, ARCH=x64. Ubuntu 24.04 → `-ssl3`.
- **MUST set `NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt`** before `finish_install`. SDK is Node-packaged with its own trust store that LACKS the SSL.com root → `SELF_SIGNED_CERT_IN_CHAIN` on `client.earnapp.com/install_device` → `Failed registration`. curl to that endpoint works (cert is healthy); only Node's bundled store fails. Persist via `/etc/environment`.
- **Run `earnapp finish_install`**, not just `start`+`run`. It does install→`Registering Device...`→`✔ Registered`→prints `https://earnapp.com/r/sdk-node-<uuid>`. `start`+`run` alone never registers.
- **Link in browser:** login `earnapp.com` first (dashboard may use **Google SSO** — SSO is only for dashboard, not the device), then open the printed `/r/<uuid>` in the same logged-in tab. The account must have capacity (older accounts with existing devices are fine).
- Other subcommands: `register` (prints link), `showid` (prints uuid), `status`.

## Incus per-container transparent proxy — verified setup
1. **Incus containers had NO outbound IPv4 NAT by default** (Incus `dir` storage; the MASQUERADE that exists is only for the Docker bridge). Symptom: container `curl` times out / `exit 28`. Fix:
   ```bash
   iptables -t nat -A POSTROUTING -s 10.64.158.0/24 ! -o incusbr0 -j MASQUERADE
   iptables -A FORWARD -i incusbr0 -j ACCEPT; iptables -A FORWARD -o incusbr0 -j ACCEPT
   ```
   (didn't persist an Incus nat rule itself; this manual rule restored outbound).
2. **redsocks 0.5 must listen on `0.0.0.0`**, not `127.0.0.1` — packets arriving via iptables REDIRECT from the bridge come from container IPs and get dropped on 127.0.0.1. Config: `local_ip = 0.0.0.0; local_port = 11080+N; ip = 127.0.0.1; port = 6000N; type = socks5;`. Start detached: `nohup redsocks -c conf >log 2>&1 </dev/null &` (in-ssh `& disown` failed; a wrapper script with nohup works).
3. **iptables per device**: `-t nat -N EARN<N>` then `-A EARN<N> -p tcp -j REDIRECT --to-ports <11080+N>`, then `-A PREROUTING -s <containerIP> -j EARN<N>`.
4. **Launching 20 containers serially too fast corrupts some** → they stay `STOPPED` with log `Failed to retrieve PID of executing child process` and won't start. Recreate corrupt ones one-at-a-time (`incus delete -f` + `incus launch`), with 2s pauses.
5. **Static IP per container**: NIC comes from the `default` profile, so `incus config device set` fails ("Device from profile ... cannot be modified"). Use `incus config device override <c> eth0 ipv4.address=10.64.158.2xx`. DHCP can also lag; static is more deterministic for NAT mapping.

## Watchdog — 3-state, US-only, swap-only-on-confirmed-dead (thrifty)
System: probe all ports ~every 5 min via cron; classify 3 states; swap ONLY jelek/mati. Free keep-alive = 0 IP burn.

- **Probe per port** = `curl -s --max-time 8 -x http://127.0.0.1:<port> https://api.ipify.org` → returns exit IP + elapsed ms.
- **States:**
  - OK: latency < 2500ms → leave alone, reset counters (thrifty: no IP consumed).
  - LAMBAT/west: latency 2500-6000ms (residential proxies legitimately run 1-3s; don't call 1-3s "offline"). Swap after **3 consecutive** weak results.
  - OFFLINE: `curl` empty. Swap after **2 consecutive** failures (anti-false-positive — a single timeout is often a blip; verified a port that "failed" once was actually fine next probe).
- **Swap**: `9proxy proxy -c US -p <port>` (always `-c US` → next IP is US residential); verify new exit; `pkill -f redsocks -c dev<N>.conf` + relaunch; restart container's `earnapp run`. Two-layer US guarantee: forward with `-c US` AND verify exit org is a US home ISP (Comcast/AT&T) via `ipinfo.io/<exit>/json`.
- **Durability CSV** `port,ip,start_utc,changed_utc,status,lat_ms` — collects which IPs live long vs die in ~1h, so you keep durable IPs and only churn bad ones (the user's stated goal; a fresh IP dying within the hour is common).
- **Idempotent, cron-safe**: `*/5 * * * * bash /opt/earnapp-farm/earnapp-watchdog.sh 20 >> cron.log`. cron wasn't installed/running on the fresh VM → `apt-get install -y cron && systemctl enable --now cron`.

Scripts referenced (on the farm VM under `/opt/earnapp-farm/`, also reproducible from this skill): `earnapp-watchdog.sh`, `live-status.sh` (table: port/exit-IP/state/latency/uptime), `setup-earnapp-dev.sh <container>` (push SDK 1.651.510 → set NODE_EXTRA_CA_CERTS → finish_install → print link).
