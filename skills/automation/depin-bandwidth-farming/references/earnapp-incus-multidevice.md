# EarnApp multi-device on Incus (LXC) containers — verified 2026-08-30

Docker-free farm on ONE Freestyle VM (Ubuntu 24.04, 32C/62G). 20 Debian containers
`ea-00..ea-19`, each wired through its OWN 9Proxy US residential port via transparent
iptables REDIRECT → host redsocks → local 9Proxy port. Scale target 20 devices.

## Why Incus instead of docker (operator asked for "1 VPS banyak Debian")

- `apt-get install incus` → command `incus`, daemon `incusd`, works without snap.
- `incus admin init --auto` → bridge `incusbr0` (10.64.158.1/24) + `dir` storage pool.
- Launch base: `incus launch images:debian/12 ea-00` (alias list: `incus image list images:`).
  Image caches after first pull, so subsequent launches are fast.

## Gotcha 1 — incusbr0 has NO NAT out of the box (docker iptables conflict)

`incus network show incusbr0` reports `ipv4.nat: true` but there is NO MASQUERADE for
10.64.158.0/24 (only docker's 172.17.0.0/16 gets one), and the container `curl -4` hangs.
Container can ping host gw but not the internet. Fix (as root):
```bash
iptables -t nat -A POSTROUTING -s 10.64.158.0/24 ! -o incusbr0 -j MASQUERADE
iptables -A FORWARD -i incusbr0 -j ACCEPT
iptables -A FORWARD -o incusbr0 -j ACCEPT
```
(incus uses nftables but iptables rules here worked; don't assume the incus-built NAT firewalls traffic.)

## Gotcha 2 — launching many containers one-after-another corrupts the stragglers

Launching 20 with `incus launch` in a tight loop (2s apart) left ea-10..19 permanently
`STOPPED` with `incusd: Failed to retrieve PID of executing child process` and no log —
they could never `start` again (clean `incus start` stuck STOPPED). Fix:
- **Delete & recreate the corrupted ones**, never trust a start that returns no error but
  stays STOPPED. `incus delete <c> -f` then re-launch.
- Add a small sleep between launches; check `incus list --format csv | cut -d, -f2`.
- Containers that come up with only IPv6 (no IPv4) → need a lease refresh or static IP.

## Gotcha 3 — cast IPv4 via DHCP is flaky here; pin static per container

`incus list --format csv | cut -d, -f3` (IPv4) can be empty for some containers (IPv6 in f3).
Force determinism for the NAT map — pin IPv4 per instance using **device override**:
```bash
incus stop <c> -f
incus config device override <c> eth0 ipv4.address="10.64.158.2xx"   # NOT `device set` (profile error)
incus start <c>
```
`incus config device set` fails with `Device from profile(s) cannot be modified for
individual instance. Override device or modify profile instead` — must be `device override`.
Use .2xx (outside DHCP range) to avoid collisions.

## Deploy shape (per device i)

```
container ea-ii (fixed IP 10.64.158.x)
   │ outbound TCP
   ▼
iptables -t nat chain EARNii : REDIRECT -p tcp --to-ports <11080+i>   (PREROUTING -s <containerIP> -j EARNii)
   ▼
redsocks dev ii.conf : local_ip 0.0.0.0, local_port 11080+i, upstream 127.0.0.1:60000+i, type socks5     (host, nohup)
   ▼
9Proxy port 60000+i  →  US residential exit
```
- Copy the EarnApp binary into each container: `incus file push /opt/.../earnapp ea-ii/usr/bin/earnapp`, then
  `printf '<uuid>' > /etc/earnapp/uuid && touch /etc/earnapp/status`, `chmod a+rw` the dir, `earnapp start &`,
  `earnapp run &`.
- **Apply the cert-store fix for registration** — the SDK's bundled CA lacks SSL.com intermediate, so `finish_install`
  dies with `SELF_SIGNED_CERT_IN_CHAIN` + `Failed registration` and the `/r/` link stays "device not found" even when
  the node is connected. Every process that runs `earnapp` must set:
  ```bash
  export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt   # then earnapp finish_install → '✔ Registered'
  ```
  Full detail in the top-level SKILL.md + `references/earnapp-current-sdk-and-linking.md`.
- redsocks on host runs as a `nohup … &` inside an SSH session — plain `& disown` inline via SSH returns 255/
  exits; wrap the `redsocks` launch in a small script file and run that script. Set `local_ip = 0.0.0.0`
  (127.0.0.1 won't accept the REDIRECTed packets coming from the bridge direction → `curl from container`
  returns `connection refused` while the iptables counter is still incrementing).

## Verification per device (prove the chain end-to-end)

```bash
incus exec ea-00 -- bash -c "curl -s --max-time 10 https://api.ipify.org"
# (empty earlier = NAT broken, see Gotcha 1; must eventually show the residential US exit, not VM egress)
```
redsocks log: `[10.64.158.21:47000->104.26.12.205:443]: accepted` = packet redirected then relayed.
`/etc/earnapp/perr_connected_<ver>.sent` present + `status` = `enabled` = node connected to backend.

## Resource footprint
20 containers + 20 redsocks on 32C/62G is light (each ~1-2MB RSS for earnapp). Do NOT forward
>10 9Proxy ports without `9proxy setting --start 60000 --limit 20` first (default limit is 10).
