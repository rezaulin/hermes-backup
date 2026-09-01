# 9Proxy By-IPs: App + port-forwarding (NOT the extract API) — verified 2026-08-29

Operator's account is **Residential by IPs**. This is the correct way to feed proxies for a node farm — the `/api/proxy` extract API is for By-GB accounts only.

## Why the API is useless here

- Every `https://api.9proxy.com/...` request from BOTH the farm VM and the operator's home browser 308-redirect-loops to itself (`ERR_TOO_MANY_REDIRECTS` / `location: <same URL>`).
- Doc statement (overview): API is "Public API (API Key)" with query-param auth `?api-key=<key>` — BUT that is the By-GB / account-management surface. A By-IPs package has no extract endpoint that works.
- The legacy OpenAPI doc at `docs.9proxy.com/api-references/proxy-api.md` is misleading (still describes `/api/proxy?num=&country=` — By-GB behavior).

## The official flow for By-IPs (docs: getting-started/residential-proxy-by-ips/for-linux/*)

> "Residential Proxy by IPs gives you access to real residential IPs through a local port-forwarding system inside the 9Proxy App... An IP is only deducted when you forward it to a local port... use it via `localhost:port`."

1. **Install** — Debian/Ubuntu:
   ```bash
   wget https://static.9proxy-cdn.net/download/latest/linux/9proxy-linux-debian-amd64.deb
   sudo apt install ./9proxy-linux-debian-amd64.deb     # debconf OK prompt
   sudo systemctl start 9proxyd.service
   ```
2. **Login** (two ways):
   ```bash
   9proxy auth -s                                  # interactive UI (username + password)
   9proxy auth -u <username> -p <password>         # direct CLI
   9proxy auth -l                                  # sign out
   ```
3. **Set port range** (before forwarding):
   ```bash
   9proxy setting -s <start_port>                  # e.g. 60000
   9proxy setting -l <num_ports>                   # e.g. 20
   ```
4. **Forward US IPs to ports** (CLI automation, headless-friendly):
   ```bash
   9proxy proxy -c US -p 60000                     # forward a US residential proxy to port 60000
   # -c <country> · -p <port> · -n <use Today-List proxy (used in last 24h)>
   9proxy proxy -u                                 # interactive: list proxies, F to filter (country/state/city/zip/ISP), Enter to forward ("to all ports" or "to a port")
   ```
5. **Verify each port** from the VM:
   ```bash
   curl -s -x http://127.0.0.1:60000 https://api.ipify.org      # must be the US residential exit
   curl -s https://ipinfo.io/<exit>/json                        # ISP (Comcast/AT&T/T-Mobile/...), NOT datacenter
   ```
6. **Feed the farm** — each `proxies.txt` line in engageub/InternetIncome:
   ```
   socks5://127.0.0.1:60000
   socks5://user:pass@127.0.0.1:60001        # only if Proxy Authentication enabled
   ```
7. **Watchdog note:** port went dead (proxy IP expired ~24h) → `9proxy proxy -c US -p <same port>` re-forwards a fresh IP to the same port, then restart the TUN + app containers for that device.

## Commands cheat-sheet (command-references.md)

`9proxy -h` (list), `9proxy api` (enable API — for the local 9Proxy app API), `9proxy auth`, `9proxy port`, `9proxy proxy` (the money command), `9proxy setting`.
Optional auth format for forwarded ports: `username:password:localhost:port` (Proxy Authentication feature).

## Gotchas (this session)

- The .deb URL in the docs is STALE (404 on `static.9proxy-cdn.net` from multiple boxes). The download page (`9proxy.com/download/linux`) still links the same dead URL. Workaround: operator clicks the button from their browser (may be served from a different edge/session) OR contact `support@9proxy.com` for the current build.
- Freestyle VM runs Ubuntu 22.04 x86_64 w/ sudo NOPASSWD + systemd (verified) — `9proxyd.service` fits fine.
- 9Proxy App is an Electron/CLI client; needs credentials that stay valid (2FA may be required for dashboard API key generation, NOT for app login).
