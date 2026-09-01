# Incus (LXC/LXD) on a Freestyle.sh VM — verified 2026-08-29

Goal: "1 VPS banyak Debian" — run many Debian containers on one Freestyle VM (4C/8G/32G Ubuntu 24.04, no snap, no apt `lxd`).

## Why Incus, not LXD

- Freestyle Ubuntu 24.04 images ship **without snap** (`command -v snap` empty) and `apt-get install lxd` has **no candidate** on noble. The LXD snap route dies with `cannot create temporary directory for the root file system` in environments without a working snap mount namespace — on Ubuntu 22.04 VPSes too.
- **Incus is available in Ubuntu noble universe as a real apt package** (`incus 6.0.0-1ubuntu0.3`, LTS) — daemon + client in one install, no build, no snap. Incus is the community fork of LXD, drop-in for system containers.

## Recipe (run inside the VM via `freestyle vm exec <id> -- sh -c '...'` or console)

```bash
# 1. Preflight (user namespaces are required for unprivileged containers)
unshare -U true && echo "userns OK" || echo "userns BLOCKED"

# 2. Install
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y incus   # gives /usr/bin/incus (client) + incusd daemon

# 3. Init (auto: creates dir-backed storage pool "default" + bridge "incusbr0")
sudo incus admin init --auto

# 4. Verify daemon + network
systemctl is-active incus            # active
sudo incus network list              # incusbr0 bridge, IPv4 10.10.3.1/24 + IPv6 fd42::/64
sudo incus storage list              # default, driver dir

# 5. Launch first Debian 12 container
sudo incus launch images:debian/12 debian-1

# 6. Verify internet from INSIDE the container
sudo incus exec debian-1 -- bash -c 'getent hosts deb.debian.org; timeout 20 apt-get update -qq && echo INTERNET-OK'
```

## Verified results (VM `rena`, 2026-08-29)

- `incus list` → `debian-1 RUNNING 10.10.3.7 (eth0) fd42:aeb3:b352:56b7:...`
- `apt-get update` inside container → **INTERNET-OK** (DNS + download work through incusbr0 NAT)

## Permission note

The daemon socket is `/var/lib/incus/unix.socket` and the default (non-root) user gets `You don't have the needed permissions`. Use **`sudo incus ...`** for every command (or add the user to the `incus-admin` group). Via `freestyle vm exec` you're not root, so `sudo` is required.

## Daily ops

```bash
sudo incus exec debian-1 bash                      # shell into container (no SSH needed)
sudo incus launch images:debian/12 debian-2        # more containers
sudo incus launch images:ubuntu/24.04 u1           # other distros
sudo incus list                                    # all containers + IPs
sudo incus stop debian-1 && sudo incus delete debian-1
```

## Networking caveats on Freestyle

- VM has no public IPv4 (`publicIpv4: None`) but **outbound IPv4 NAT works** (`curl -4 api.ipify.org` → `152.236.128.19`), so container installs are fine.
- Inbound from the internet is IPv6-only; to expose a container port publicly, use `freestyle tls create --domain x.style.dev --to vm=<slug>,port=N` (maps domain → container/host port) — don't rely on raw inbound ports.
- If the VM auto-pauses (idle), containers freeze with it — `freestyle vm start <id>` resumes.
