# Farm scale-up, dead-node start, and the quota-pause "all dead" trap (2026-08-30)

Session-tested on the PMJ ubuntu-2xl farm (9 → 20 device attempt, then reverted to 9).

## ⚠️ WORKFLOW RULE — "gimana caranya?" = explain the PLAN, do NOT execute

User asked "jika aku pengen 20 device gimana?" (how would I scale to 20?) → agent
immediately executed: forwarded 11 new ports, wiring, finish_install — burning
**11 paid 9Proxy IPs permanently** (pool 52→41) without confirmation. User was
upset ("loh kamu udah forward ip lagi? hangus lagi berarti ip nya?", "entahlah aku
capek", "rugi"). Rules that prevent this:

1. **A "how do I…?" question is a request for the plan/steps, not permission to act.**
   Answer with the numbered steps + the cost of each step (IPs consumed, VM quota),
   then let the user say "gas".
2. **Never consume paid/non-refundable resources without explicit go-ahead.** 9Proxy
   By-IPs forwards are permanent (see main SKILL.md). Forwarding "to try it" wastes
   money. Same for creating VMs, buying proxy packages, scaling container counts.
3. If the user sounds tired/frustrated ("capek", "entahlah", "rugi") — STOP, own the
   mistake, present recovery options, don't push more actions.

## Scale 9 → 20 (procedure that actually worked)

All 20 containers (ea-00..ea-19) usually ALREADY exist from initial `deploy.sh`
(binary + UUID present); only 3 things were needed:

```bash
# 1. Forward the missing ports (CONSUMES IPs — confirm first!)
for p in $(seq 60009 60019); do 9proxy proxy -c US -p "$p"; done

# 2. Wire iptables REDIRECT for ea-10..ea-19 (EARN10..EARN19 chains, rs ports 11090..11099)
#    ea-09 was already wired (EARN9) but not earning — needed re-register.
#    Verify: iptables -t nat -S PREROUTING | grep -c "10.64.158"  → 20

# 3. Register + START earnapp per container — use systemd, NOT nohup!
sudo incus exec ea-10 -- bash -c 'export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt; echo yes | timeout 45 /usr/bin/earnapp finish_install'
sudo incus exec ea-10 -- systemctl start earnapp earnapp_upgrader   # ← key step
```

- **`finish_install` may print NOTHING if the service already exists** (grep for
  "Registered" comes back empty, exit 143 from exec-await timeout) — don't panic;
  the device may still register. Verify with markers afterwards, not the grep.
- **Dead container fix = `systemctl start earnapp` INSIDE the container, NOT
  `nohup earnapp run &`.** The systemd unit (`earnapp.service`/`earnapp_upgrader.service`)
  is enabled in the container image and **survives the Freestyle exec-await teardown**
  (it's parented by the container's PID-1 systemd, outside the exec session's process
  group). `nohup ... &` from exec-await dies with status 143 every time. Diagnose:
  `sudo incus exec ea-N -- systemctl is-active earnapp` → `inactive (dead)` = that's
  the fix target. A healthy device shows `active` (compare against an earning one).
- After start, wait 60–90 s; markers appear in phase order
  `svc_init → show_dialog → choose_peer → connected → tun_init_success`.
- Scale-up result observed: 18/20 reached `tun_init_success` within minutes
  (ea-09, ea-18 lagged; ea-09 fixed by `systemctl start`).

## ⚠️ "Semua device mati sekaligus" = VM PAUSED (quota), not the farm

If the whole dashboard goes grey / every device dead at once, check the VM first:
`GET /v5/vms` → if `state: paused` and a start probe returns
`429 {"code":"LIMIT_EXCEEDED", "message":"... allowance for memory_time, vcpu_time
has been used..."}` — the Freestyle **free-tier monthly allowance burned out** and
the VM auto-paused. NOT a device/farm problem:
- All 20 containers + 9proxy are offline because the VM is off.
- Paid IPs already forwarded stay "used" (9Proxy model) — no refund either way.
- Options: wait for monthly reset, or upgrade to Hobby (paid) to resume immediately.
- Diagnose BEFORE debugging devices: `python3 scripts/freestyle-key-status.py` or a
  raw GET /vms state check. Saves hours chasing per-device ghosts.

## VPS sizing for the farm — don't oversize

Real usage of a 20-device farm: ~3.5 GiB RAM, light CPU, ~17 GB disk.
- **`freestyle/ubuntu` (4C/8G/32G) is the right size** for 10–20 devices (same spec
  as the old `rena` VM which ran a farm fine).
- **Oversizing (32C/64G ubuntu-2xl) burns the free-tier `vcpu_time`/`memory_time`
  allowance much faster** — allowance is sized × uptime, not × actual usage, so a
  big idle VM still consumes quota. The quota-pause above was partly self-inflicted
  by running the farm on the biggest snapshot.
- Scale target: ~20 devices max on one 4C/8G box; don't pre-allocate ports for
  containers that aren't earning.
