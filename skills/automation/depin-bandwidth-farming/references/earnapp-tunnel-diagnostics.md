# EarnApp Tunnel Diagnostics — Per-Device Verification

## Marker Matrix (SDK 1.651.510)

| Marker File | Meaning | Decisive? |
|---|---|---|
| `perr_connected_1.651.510.sent` | SDK connected to EarnApp service | ❌ **Not alone** — many devices have this but earn $0 |
| `perr_20_svc_connected_1.651.510.sent` | Service connection established | ❌ Same as above |
| `perr_tun_init_success_1.651.510.sent` | Tunnel initialised — **actually earning** | ✅ **YES** — this is the real signal |
| `perr_tun_init_err_1.651.510.sent` | Tunnel init failed | Diagnostic — why device isn't earning |
| `perr_restricted_domain_1.294.218.sent` | Stale old-SDK failure (1.294.218) | Ignore if 1.651.510 markers exist |
| `perr_ipv6_102_test_fail_1.651.510.sent` | IPv6 test failed (IPv6-only VM) | Harmless — does not block earning |

**Rule:** Device is earning only when `perr_tun_init_success_1.651.510.sent` is present. The `perr_connected` + `perr_20_svc_connected` pair alone means "SDK reached the service" — not earning.

## Verification: Raw-REST Exec Loop (from control host)

Use this when the npm SDK returns 401/wrong-team. Works on any Freestyle API key.

```bash
# 1. Define helpers
KEY="<your-key>"
VM="<vm-id>"
BASE="https://beta-api.freestyle.sh/v5"

exec_cmd() {
  curl -s -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
    -d "{\"command\":\"$1\",\"timeoutMs\":60000}" \
    "$BASE/vms/$VM/exec-await" | python3 -m json.tool
}

# 2. Quick per-container marker check
exec_cmd '
for c in $(sudo incus list -c n --format csv 2>/dev/null | grep ^ea- | cut -d, -f1 | sort -V); do
  uuid=$(sudo incus exec "$c" -- cat /etc/earnapp/uuid 2>/dev/null)
  conn=$(sudo incus exec "$c" -- sh -c "test -f /etc/earnapp/perr_connected_1.651.510.sent && echo 1 || echo 0" 2>/dev/null)
  svc=$(sudo incus exec "$c" -- sh -c "test -f /etc/earnapp/perr_20_svc_connected_1.651.510.sent && echo 1 || echo 0" 2>/dev/null)
  tun=$(sudo incus exec "$c" -- sh -c "test -f /etc/earnapp/perr_tun_init_success_1.651.510.sent && echo 1 || echo 0" 2>/dev/null)
  echo "$c | ${uuid: -8} | conn=$conn svc=$svc tun=$tun"
done
'
```

## Egress check — the #1 reason a whole batch is "connected but not earning"

`perr_connected` + `perr_20_svc_connected` can be present while the tunnel never comes up (`tun=0`) because **the container's traffic egresses via the VM's own datacenter IP, not the per-device residential proxy**. EarnApp declines the tunnel (`ip_type.dch`), device stays grey in the dashboard. Seen 2026-08-30 on the 20-device farm: ea-10..ea-19 all conn=1/svc=1/tun=0 with egress `152.236.128.19` = the VM's Megaport datacenter egress.

Root cause: **the per-container iptables `PREROUTING` REDIRECT rule is missing** — the `EARN<n>` chain exists but has **`0 references`** (nothing jumps into it from PREROUTING). Rules were only present for ea-00..ea-09; ea-10..ea-19 were never wired, so their traffic bypassed redsocks entirely.

Diagnose (add to the exec loop above):
```bash
# per container: egress must be US residential, NOT the VM's datacenter IP
sudo incus exec "$c" -- curl -s --max-time 8 https://api.ipify.org
# on the host: which containers have a PREROUTING jump?
sudo iptables -t nat -S PREROUTING | grep '10.64.158'        # ea-00..ea-09 present, ea-10..ea-19 absent = unwired
# chain exists but unused?
sudo iptables -t nat -L EARN10 -n | head -3                   # "0 references" = no PREROUTING jump
```

Fix — wire the missing container (this is the `wire_nat()` function in `fix-all.sh`):
```bash
CH="EARN$i"; IP="<container-eth0-ip>"
sudo iptables -t nat -N "$CH" 2>/dev/null
sudo iptables -t nat -A "$CH" -p tcp -j REDIRECT --to-ports "1108$i"     # rsport = 11080+idx
sudo iptables -t nat -C PREROUTING -s "$IP" -j "$CH" 2>/dev/null || sudo iptables -t nat -A PREROUTING -s "$IP" -j "$CH"
sudo incus exec "$c" -- bash -c "pkill -f earnapp 2>/dev/null; nohup earnapp run >/tmp/earun.log 2>&1 &"
```
Then verify egress flips to the residential IP and `perr_tun_init_success` appears after 60–90s.

**Fast farm-wide triage:** sweep all containers in one exec — print device | uuid | conn | svc | tun | egress. Any row with `tun=0` + egress equal to the VM datacenter IP = unwired container (fix with wire_nat), not an SDK/proxy problem. Don't waste time swapping proxies for these — the proxy was never in the path.

## Latency probe — predicting which "earning" devices are about to go grey

A `tun_init_success` marker can be stale: the tunnel came up earlier, but the current proxy IP is dying. Probe per port and cross-check the dashboard:
```bash
for p in 60000 60001 60002 60003 60004 60005 60006 60007 60008; do
  t0=$(date +%s%3N)
  ip=$(curl -s --max-time 8 -x "http://127.0.0.1:$p" https://api.ipify.org 2>/dev/null)
  t1=$(date +%s%3N); echo "$p | ${ip:---} | $((t1-t0))ms"
done
9proxy port -s | grep -E "600[0-9]{2}"     # Online/Offline per port
```
Signals a device is headed grey: `9proxy port -s` shows **Offline** for its port, and/or latency ≥ ~6000 ms (the watchdog's `LAT_BAD`). Swap preemptively rather than waiting for the watchdog's 2–3 consecutive bad ticks.

## Pitfalls

- **Exec runs as uid 1000 (ubuntu) by default.** `incus`, `docker`, `iptables` commands need `sudo -n`. The Freestyle `ubuntu` user has sudo NOPASSWD on the base images.
- **`incus list` output format** — use `-c n --format csv` for scriptable names; the default table format is hard to parse.
- **Earning ≠ connected to service.** Conn+svc markers are misleading — always check `tun_init_success`.
- **Farm files (`links.txt`, `uuids.txt`) are not ground truth.** After `recreate.sh` or `setup-earnapp-dev.sh`, container UUIDs may differ from what the txt files say. Always read `/etc/earnapp/uuid` from inside the container.