# EarnApp Dead-Node Repair — missing redsocks → ECONNREFUSED → fix

Session-verified recipe (2026-08-30, Freestyle ubuntu-2xl farm, device `ea-05`). Use when a
device shows `conn=0/svc=0/tun=0` (no SDK markers) even though the earnapp process runs.

## Diagnosis ladder

1. **Snapshot the farm state per device** (which containers are earning vs dead):
   ```bash
   for i in $(seq 0 19); do
     c=$(printf "ea-%02d" $i)
     conn=$(sudo incus exec "$c" -- sh -c 'test -f /etc/earnapp/perr_connected_1.651.510.sent && echo 1 || echo 0')
     svc=$(sudo incus exec "$c" -- sh -c 'test -f /etc/earnapp/perr_20_svc_connected_1.651.510.sent && echo 1 || echo 0')
     tun=$(sudo incus exec "$c" -- sh -c 'test -f /etc/earnapp/perr_tun_init_success_1.651.510.sent && echo 1 || echo 0')
     echo "$c|conn=$conn|svc=$svc|tun=$tun"
   done
   ```
   EARNING = `conn+svc+tun` all 1. **conn+svc without tun = connected but NOT earning** (tunnel init failed).

2. **Check the per-device redsocks + iptables wiring**:
   ```bash
   ps aux | grep redsocks | grep -v grep            # which devN.conf are actually running
   sudo ss -tlnp | grep 1108[0-9]                    # which redsocks ports are listening
   sudo iptables -t nat -S PREROUTING | grep <contIP>   # is the REDIRECT rule present?
   sudo iptables -t nat -S EARN5                       # chain exists? points to which rs port?
   ```
   Common failure: **the device's redsocks conf is missing AND the redsocks process isn't running**,
   but the iptables REDIRECT rule (e.g. `-A PREROUTING -s <contIP> -j EARN5` → `REDIRECT --to-ports 11085`)
   still exists. Result: container traffic to 11085 hits nothing → SDK logs a wall of
   `perr send failed ... ECONNREFUSED` and never registers. **This is the #1 dead-node cause.**

## Fix (redsocks conf missing / process not running)

1. **Confirm the base template** from `fix-all.sh` (it regenerates devN.conf for the whole farm):
   ```bash
   cat > /opt/earnapp-farm/redsocks/devN.conf <<EOF
   base { log_debug = off; log_info = on; log = "stderr"; daemon = off; redirector = iptables; }
   redsocks { local_ip = 0.0.0.0; local_port = 1108N; ip = 127.0.0.1; port = 6000N; type = socks5; }
   EOF
   ```
   (N = device index; `1108N` = redsocks listen, `6000N` = 9proxy upstream port. Match what
   `iptables -t nat -S EARN<N>` shows for `--to-ports`.)

2. **Start it** — see the cron-survival rule below.

3. **Restart earnapp inside the container** and clear stale markers:
   ```bash
   sudo incus exec ea-N -- bash -c "pkill -f earnapp; sleep 2; \
     rm -f /etc/earnapp/perr_connected_1.651.510.sent /etc/earnapp/perr_20_svc_connected_1.651.510.sent \
           /etc/earnapp/perr_tun_init_success_1.651.510.sent; \
     export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt; \
     nohup earnapp run >/tmp/earun.log 2>&1 &"
   ```

4. **Wait 60–90s** — SDK boots in phases; markers appear progressively:
   `svc_init → show_dialog → choose_peer → connected → tun_init_success`.
   The device is EARNING only once `perr_tun_init_success_1.651.510.sent` exists.
   Re-check with the ladder in step 1.

5. **Verify egress end-to-end** (the decisive proof the chain works):
   ```bash
   sudo incus exec ea-N -- curl -s --max-time 8 https://api.ipify.org
   ```
   Must return the **residential proxy IP** (e.g. `64.57.177.95`), NOT the VM's datacenter egress.
   NOTE: `curl -x http://127.0.0.1:11085 ...` from the HOST will FAIL even when everything is
   correct — redsocks is a transparent redirector for iptables, NOT an HTTP proxy. Test from
   INSIDE the container, not with `-x` on the host.

6. **Linking:** device is `perr_connected`, so opening `https://earnapp.com/r/<uuid>` in a browser
   logged into the EarnApp account binds it. Read the real UUID from inside the container
   (`sudo incus exec ea-N -- cat /etc/earnapp/uuid`), NOT from `uuids.txt` (stale after recreates).

## ⚠ Cron-survival rule (Freestyle exec-await)

Background daemons started inside a Freestyle **`exec-await`** command are SIGTERM'd at session
end — `nohup ... &`, `setsid nohup ... &`, and even `systemd-run`/`systemctl start` all die within
seconds (`Terminated`, status 143). **Only processes parented by the cron daemon survive.**
To keep redsocks (or any farm daemon) alive when driving the VM through exec-await, use a
cron bootstrap:

```bash
# /opt/earnapp-farm/bootstrap-redsocks.sh  (start-if-not-running)
CONF=/opt/earnapp-farm/redsocks/devN.conf
pgrep -f "redsocks -c $CONF" >/dev/null || nohup redsocks -c "$CONF" >/opt/earnapp-farm/redsocks/devN.log 2>&1 &
# register in root crontab:
# * * * * * /bin/bash /opt/earnapp-farm/bootstrap-redsocks.sh >> /opt/earnapp-farm/cron.log 2>&1
```
Same trick applies to any always-on daemon the agent must start on a Freestyle VM.
