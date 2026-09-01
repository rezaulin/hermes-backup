# EarnApp on cloud/datacenter IP — deep dive (2026-08-29, Freestyle.sh VM `rena`)

Full evidence trail for the "EarnApp rejects datacenter IPs" conclusion. Target host: Freestyle.sh VM, 4 vCPU / 8 GiB / Ubuntu 24.04, egress IP `152.236.128.19` (AS49915 Megaport, Emeryville CA, hostname `s906369.megaport.com`).

## Setup verified as WORKING on the VM
- Docker 29.1.3 present; both images pull fine:
  - `fazalfarhan01/earnapp:lite` — `ENTRY=[] CMD=[install]`, no privileged needed.
  - `madereddy/earnapp:latest` — `ENTRY=[/entrypoint.sh] CMD=[run]`, `CONFIG_DIR=/etc/earnapp`, `INSTALLER_URL=https://brightdata.com/static/earnapp/install.sh`.
- Container runs non-privileged, docker healthcheck → `healthy`.
- `-e EARNAPP_UUID=sdk-node-aaaaabbbbbcccc01` → file `/etc/earnapp/uuid` contains exactly that value. UUID format `sdk-node-` + 14 hex chars.
- Fresh container (no env) also starts; /etc/earnapp gets `brd_sdk2.log`, `uuid`, `status`, `consent` etc.

## The two blockers (raw evidence)

### Blocker 1 — datacenter IP decline (DECISIVE)
```
NOTICE: tunnel_init resp: {"arch":"x64",...,"uuid":"sdk-node-verbosetest01","ifname":"eth0","ifs":[{"name":"eth0","addr":"172.17.0.2"}]}
NOTICE: tunnel_init_decline: ip_type.dch
NOTICE: eth0 connect decline cooldown 86400000
```
- `ip_type.dch` = datacenter host classification. Cooldown 86 400 000 ms = 24 h per IP.
- Happens whether or not `EARNAPP_UUID` is set — it's the IP, not the device.

### Blocker 2 — restricted_domain allowlist
```
ERR: restricted_domain: proxyjs.luminatinet.com failed 15.197.193.114
ERR: perr restricted_domain {"host":"proxyjs.luminatinet.com","details":"failed 15.197.193.114","allowed":["54.243.132.124","54.197.238.153","23.23.115.110", ... ~30 us-east-1 AWS IPs]}
ERR: conn_open_single failed resolve proxyjs.lum-sdk.io
```
- SDK dials only hardcoded AWS us-east-1 IPs. DNS round-robin answering CloudFront/Global-Accelerator IPs (`15.197.193.114`, `3.33.193.183`) = refused, logs `proxyjs_dns_failed`.

## What does NOT indicate eligibility
- `curl "https://client.earnapp.com/is_ip_blocked?uuid=...&version=1.294.218&arch=x64&appid=node_earnapp.com"` → `{"ip_blocked":false}` for the Megaport IP. The dch classification is applied later at `tunnel_init` and beats the blocklist check.

## Working single-node success signals (for a residential host)
- Logs: `perr lum_sdk_node_connected ... res 200`, `perr lum_sdk_node_20_svc_connected ... res 200`.
- Note the telemetry calls include `uuid=...` — backend tracks per-UUID per-IP, consistent with per-device dashboard.

## Installer endpoint history
- `https://earnapp.com/i/install` → SPA dashboard shell now (window.APP_ID = "earnapp", no installer script served to curl).
- `https://brightdata.com/static/earnapp/install.sh` is the current installer URL used by community images.
- Community source repos: `fazalfarhan01/EarnApp-Docker`, `TrakkDev/earnapp_docker` (image embeds `wget -qO- https://brightdata.com/static/earnapp/install.sh`).
