# Freestyle VM SSH + RDP access — verified 2026-08-29 (VM rena)

Two access paths proven on a Freestyle VM: (1) SSH via the official proxy with a
scoped identity token — from the CLI or an external client (Termius/PuTTY);
(2) a real RDP GUI (XFCE4 + xrdp) reachable over the VM's public IPv6.

## SSH via proxy — scoped identity token (no permanent key in the VM)

Freestyle VMs do NOT run a normal SSH daemon on a public port. You connect through
`beta-ssh.freestyle.sh` and the proxy authorizes a THROWAWAY keypair inside the VM for a
couple of minutes per connection. No SSH key is ever installed in the guest, and the
token stays OUTSIDE the VM (checked by the proxy).

```bash
ssh <vm-id-or-slug>@beta-ssh.freestyle.sh                       # prompts, token as password
ssh <vm-id-or-slug>:<token>@beta-ssh.freestyle.sh               # token in username
ssh <vm-id-or-slug>+<linux-user>:<token>@beta-ssh.freestyle.sh  # as a specific Linux user
```

- No `+user` = default user (uid 1000, `ubuntu` on Ubuntu snapshots) or `root` on images
  without a uid-1000 user. **`+root` gives a root session on ANY image.**
- If a grant carries `allowedLinuxUsers`, the connection MUST name a user
  (`+<user>`) — the bare `<slug>:<token>` form is refused.

Mint identity + grant + token (node SDK; reads `FREESTYLE_API_KEY` from env):
```ts
const f = new Freestyle();
const { identity } = await f.identities.create();
await identity.permissions.vm.grant({ vmId, allowedLinuxUsers: ["root"] }); // optional
const { token } = await identity.tokens.create();
console.log(`ssh ${slug}+root:${token}@beta-ssh.freestyle.sh`);
```
Verify: `ssh -o StrictHostKeyChecking=no '<slug>+root:<TOKEN>@beta-ssh.freestyle.sh' 'id; hostname'`
→ `uid=0(root) ... freestyle-vm`.

### External clients (Termius / PuTTY) — token goes in the USERNAME, not password

The token is part of the user string. Field-by-field:

| Field | Value |
|---|---|
| Host | `beta-ssh.freestyle.sh` |
| Port | `22` |
| Username | `<slug>+<linux-user>:<token>` e.g. `rena+root:ABcDEF...` (keep colon+token attached) |
| Password | empty |

Termius: New Host → address/port → username verbatim → blank password → connect.
PuTTY: host/port → Connection → Data → Auto-login username `rena+root:<TOKEN>` → Open
(blank password if prompted).

## RDP GUI — XFCE4 + xrdp (needs IPv6 from the client)

Freestyle VMs are **IPv6-only for inbound** (no public IPv4). RDP works ONLY from a
device with an IPv6 route to the VM's public IPv6. IPv4-only clients cannot reach it —
fall back to a browser-GUI path (see README/repo notes: x11vnc+noVNC over a
`freestyle tls ... .style.dev` domain) instead.

```bash
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y --no-install-recommends xfce4 xfce4-terminal xrdp
systemctl enable xrdp && systemctl restart xrdp

# Point the session at XFCE (after the ~/.profile block in /etc/xrdp/startwm.sh):
#   startxfce4 &
#   exit 0

# Root has no password by default on Ubuntu — xrdp needs one to log in:
echo 'root:<PASSWORD>' | chpasswd
```

- `PermitRootLogin prohibit-password` in sshd only affects SSH; xrdp logs in with a
  password fine (separate path).
- Freestyle default firewall is OUTBOUND-only → you MUST add an inbound rule or the
  port is unreachable:
  ```bash
  freestyle firewall create --from public --to "vm=<vmId>,port=3389,proto=tcp" \
    --description "RDP inbound 3389"
  ```
- Verify: `ss -tlnp | grep 3389` (xrdp LISTEN), `systemctl is-active xrdp`, and a
  localhost RDP banner check `timeout 4 bash -c 'exec 3<>/dev/tcp/127.0.0.1/3389 && head -c16 <&3 | xxd'`.
- Connect with host = VM's public IPv6 (e.g. `2602:f470:...:412`), port 3389, user
  `root`.
- Client IPv6 check (Windows): `ipconfig` (look for "IPv6 Address"), `ping -6 <vm6>`,
  `tracert -6 <vm6>`.
- ⚠️ Self-connect to the VM's OWN public IPv6 from inside fails (hairpin NAT) — that is
  normal, not a services problem. Test the daemon via localhost, test inbound from the
  client.

## Gotchas hit live
- `ss -tlnp` shows xrdp listening on `*:3389` — good.
- The doc's editor-connection (vscode/cursor) URLs and cmux URL are for IDE use; plain
  terminal SSH works on ANY image, even `freestyle/busybox`.
- Keep `PubkeyAuthentication` enabled for custom images (the proxy path needs it).
