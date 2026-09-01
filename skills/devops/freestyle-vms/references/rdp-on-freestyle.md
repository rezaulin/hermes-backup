# RDP (xrdp) on a Freestyle VM — verified runbook 2026-08-29 (VM rena)

Goal: give the owner a desktop GUI (not CLI) on `rena`, reachable from a real
RDP client (mstsc / Remmina / Termius). Because Freestyle VMs are IPv6-only
inbound, real RDP requires the client device to have IPv6. For anything else,
use the browser noVNC route instead.

## 1. Install desktop + xrdp (inside VM, as root)

```bash
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq --no-install-recommends xfce4 xfce4-terminal xrdp
```

`--no-install-recommends` keeps it light. XFCE4 chosen over GNOME for RAM/CPU
(VM is 4C/8G but this is fine).

## 2. Point xrdp's startwm at XFCE

Default `/etc/xrdp/startwm.sh` execs `/etc/X11/Xsession`, which may not start
the desktop you want. Replace the tail:

```bash
cp /etc/xrdp/startwm.sh /etc/xrdp/startwm.sh.bak
# replace the Xsession lines with:
#   startxfce4 &
#   exit 0
```

Verified final tail:
```bash
if test -r ~/.profile; then
	. ~/.profile
fi

startxfce4 &
exit 0
```

## 3. Enable/start + confirm listening

```bash
systemctl enable xrdp
systemctl restart xrdp
systemctl is-active xrdp          # -> active
ss -tlnp | grep 3389              # -> LISTEN ... *:3389  (xrdp)
```

## 4. Set root password (xrdp login)

Ubuntu 24.04 root normally has no password (SSH uses the proxy key). xrdp
needs a real password:

```bash
echo 'root:<STRONG_PASSWORD>' | chpasswd
```

Note: `PermitRootLogin prohibit-password` in sshd is IRRELEVANT to xrdp — it
only governs SSH. xrdp uses PAM auth, so the password works even though direct
root SSH-by-password is disabled.

## 5. Open inbound 3389 (REQUIRED)

Freestyle firewall is **outbound-only by default** — no inbound rule exists
until you create one. From the control host:

```bash
freestyle firewall create \
  --from "public" \
  --to "vm=<VM_ID>,port=3389,proto=tcp" \
  --description "RDP inbound to rena" \
  --output json
```

Keep the returned rule id (`fw-...`) — that's what you delete to close it.

## 6. Verify server actually serves RDP — use LOCALHOST, not public IPv6

**Don't test by self-connecting to the public IPv6** — hairpin NAT makes that
fail even though the port is correctly open to the outside. Verify locally:

```bash
# banner over localhost = RDP handshake works
timeout 4 bash -c 'exec 3<>/dev/tcp/127.0.0.1/3389 && echo BANNER_OK && head -c16 <&3 | xxd && exec 3<&-'
```

Expect `BANNER_OK` + a hex dump (RDP protocol greeting). Also confirm the
public IPv6 itself is routable (different concern from the port):
`ip -6 route show default` and `ping6 -c2 2602:...` from inside.

## 7. Owner connection details

| Field | Value |
|---|---|
| Host | `2602:f470:...:412` (the VM's `publicIpv6`) |
| Port | `3389` |
| User | `root` |
| Password | (the one set in step 4) |

Client device MUST have IPv6 — test `test-ipv6.com` on the device first.

## Gotchas / pitfalls

- **Hairpin NAT false negative:** self-connecting to the public IPv6 from
  inside the VM fails (`Network is unreachable` on IPv4-only control host, or
  timeout on hairpin) even when the port is genuinely open. Always verify via
  `127.0.0.1` banner.
- **Control host may be IPv4-only:** the host this was debugged from could not
  reach the IPv6 at all (`connect: Network is unreachable`) — that's why local
  banner verification matters; don't conclude the VM is broken from an
  IPv4-only probe.
- **startwm.sh backup:** keep `.bak` so you can revert if XFCE swap breaks
  something.
- **Auto-pause:** VM pauses on idle; an idle RDP session may drop. Keep the
  RDP session connected when leaving the desktop.
