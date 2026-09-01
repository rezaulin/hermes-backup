# engageub/InternetIncome repo — prebuilt multi-proxy DePIN farm (analyzed 2026-08-29)

GitHub: `engageub/InternetIncome` (255★ / 74 forks, Shell, last updated 2026-08-27).
Runs 30+ bandwidth-sharing apps inside Docker, each app container wired through its OWN proxy via TUN containers. README claims ~$50+/mo per IP with all apps enabled.

## Why it matters for this skill
Same goal as the hand-rolled redsocks+iptables architecture in the parent SKILL.md, but packaged and maintained: instead of host redsocks per device, it creates one **TUN container per proxy** and attaches each app container via `--network=container:tun$UNIQUE_ID$i`. Because the forcing happens at the network layer, it works for EarnApp (whose SDK ignores HTTP_PROXY/HTTPS_PROXY env vars).

## proxies.txt format (validated by `validate_proxies()`)
One line per proxy, protocol REQUIRED:
```
socks5://user:pass@host:port
socks5h://user:pass@host:port
http://user:pass@host:port
https://user:pass@host:port
socks4://user:pass@host:port
ss://method:pass@host:port        # shadowsocks
host:port                          # bare → falls through to tun2socks
```
Parsing detail: split on the LAST `@` so passwords containing `@` still work. Any invalid line → `exit 1` (hard fail, fix the file).

## TUN container matrix (one per proxy)
| Condition | Image | Notes |
|---|---|---|
| `USE_SOCKS5_DNS=true` + socks5:// | `ghcr.io/heiher/hev-socks5-tunnel:2.17.1` | env `SOCKS5_ADDR/PORT/USERNAME/PASSWORD`, `LOG_LEVEL`, `ICMP=reply`; socks5 DNS routing |
| `USE_DNS_OVER_HTTPS=true` + http/socks | `ghcr.io/tun2proxy/tun2proxy:v0.8.3` | `--proxy <url> --dns over-tcp` (DoT/DoH — no DNS leak) |
| default http/https/socks4 | `tun2proxy:v0.8.3` | `--dns virtual` |
| anything else (bare/ss) | `xjasonlyu/tun2socks:v2.7.0` | env `PROXY=<url>` |

All TUN containers: `--cap-add=NET_ADMIN`, bind-mount `/dev/net/tun`, `--restart=always`, ipv6 disabled via sysctl. A custom `resolv.conf` is bind-mounted readonly into app containers (`USE_DNS_OVER_HTTPS` + DNS caching reduce leaks/latency — recommended for EarnApp so DNS queries don't reveal the VM origin).

## Config (properties.conf)
- `USE_PROXIES=true/false` — master switch for the whole proxy layer.
- `USE_SOCKS5_DNS=true` / `USE_DNS_OVER_HTTPS=true` — pick TUN backend (matrix above).
- Per-app credential fields (email/token/UUID) — only apps with non-empty creds get started; set creds in single quotes.
- Apps & DC-IP tolerance (from README comparison table): DC-tolerant → AntGain, WizardGain, URnetwork, Titan Network, Adnade, EarnFM, Peer2Profit, ProxyBase, ProxyRack, Repocket, TraffMonetizer, ProxyLite, BitPing, Mysterium, Bytelixir, Salad. Residential/ISP-only → EarnApp, PacketStream, Honeygain, IPRoyal Pawns, Ebesucher, Grass, Wipter, Uprock, PassiveApp, Bytebenefit.
- Browser-extension-style apps (Ebesucher, Adnade) run docker-in-docker (`docker:cli` mounting `/var/run/docker.sock` + the repo dir) with a chrome/firefox container and a `restart.sh` loop.

## ⚠️ NO BUILT-IN DEAD-PROXY WATCHDOG (verified by grep of the script)
- Flags are only `--start` / `--stop` / `--restartChrome` / `--restartFirefox` / `--restartAdnade` etc. There is **no healthcheck / monitor / is_alive / replace logic**.
- `--restart=always` restarts a crashed app container but with the **SAME proxy** — a dead proxy just keeps failing.
- The dind loops (`while true; do sleep 3600/7200/86400; restart.sh --restartApp; done`) only restart browser sessions; they do **not** swap proxies.
- → The operator requirement "auto-ganti proxy yang mati sebelum 24 jam" REQUIRES an external watchdog (cron ~5min): detect dead TUN container (curl an exit-IP endpoint THROUGH the container's network), pull a fresh proxy from the provider API, rewrite that line in `proxies.txt`, then restart the TUN container + its app containers.

## Running
```bash
wget -O main.zip https://github.com/engageub/InternetIncome/archive/refs/heads/main.zip
unzip -o main.zip && cd InternetIncome-main
sudo apt-get install -y docker.io unzip   # if needed; ARM needs binfmt+qemu for amd64 images
vi properties.conf                         # creds in single quotes
sudo bash internetIncome.sh --start        # first run pulls ~30 images — heavy! check disk/bandwidth
sudo bash internetIncome.sh --stop         # removes containers; node IDs persisted in ./ folders
```
First `--start` is a big pull (test VM had 24GB free — enough but slow). Repo ships `proxies.txt`, `restart.sh`, chrome/firefox profile zips.

## Trust / notes
- 255★, active Aug-2026, no LICENSE — use at own risk (README disclaims liability).
- README is full of the author's affiliate/referral links (obvious monetization) — replace with operator's own creds; the script itself just `docker run`s the apps and is not hostile.
- README wiki promotes "100+ SOCKS5 proxies → passive income" and "static residential proxies from $1" — useful pointers for sourcing.
