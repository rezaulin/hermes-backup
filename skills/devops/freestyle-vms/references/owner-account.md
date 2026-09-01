# Owner's Freestyle.sh account (as of 2026-08-29)

| Item | Value |
|---|---|
| Account ID | `acct-f5ff51a5c73f442888b08cbdf225291f` |
| Dashboard URL | https://dash.freestyle.sh/accounts/acct-f5ff51a5c73f442888b08cbdf225291f |
| VM ID | `vm-fcce26f45bfa4a9983183e2044cda00c` |
| VM slug | `reza-vm` |
| Spec | 4 vCPU / 8192 MiB RAM / 32768 MiB storage |
| Base image | freestyle/ubuntu (snapshot `sh-e8d6e4b8830c4480baf223048a1cfb1e`) |
| Persistence | persistent — files + memory survive pause/resume |
| Public IPv6 | `2602:f470:40:1:cb1:9dd1:94d5:c265` (dualStack — NO public IPv4 observed) |
| idleTimeoutSeconds | **86400** (bumped 2026-08-24 from default 300) |
| Created | 2026-08-23 08:10 UTC |
| State at capture | **paused** (free while paused) |
| Plan/quota | Free tier — monthly `memory_time`/`vcpu_time` allowance EXHAUSTED as of 2026-08-29 → `vm start` fails with `LIMIT_EXCEEDED` until reset or Hobby upgrade |
| Firewall | 1 rule only: `allow vm → public Internet` (outbound). **No inbound rules** — port 22 not publicly reachable |
| Snapshots | None (only the root base-image snapshot) |

- **API key IS stored** at `/root/freestyle/.env` (600, `FREESTYLE_API_KEY=...`) — copied from chat 2026-08-29. Check there first; fall back to `/root/freestyle-check/.env*`, shell history, `session_search "freestyle apikey"`, else ask owner (dashboard → API keys).
- SDK workspace + npm CLI: `freestyle` package installed globally (`freestyle --version` → 0.2.7); older SDK workspace at `/root/freestyle-check/` (has `list.mjs`).
- The dashboard SPA shows nothing to logged-out browsers (login wall) — always operate via SDK/CLI instead.
- **Owner plan (2026-08-29):** wants LXC/LXD on this VM — 1 VPS running multiple Debian containers. Setup script staged at `/root/freestyle/lxd-setup.sh` (installs LXD via apt — NOT snap; enables `lxdbr0` with `ipv6.address auto` + `ipv6.nat true` for IPv6-only host; launches `images:debian/12 debian-1`; includes a user-namespace guard `unshare -U` that aborts if unprivileged containers are unsupported). Blocked until quota resets / Hobby upgrade.
