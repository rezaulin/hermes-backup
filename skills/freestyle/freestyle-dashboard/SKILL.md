---
name: freestyle-dashboard
description: Freestyle.sh VM management and EarnApp multi-device farm deployment
category: devops
---

# Freestyle VM Management & EarnApp Farm

**Overview:** Guide for managing multi-device EarnApp farm on Freestyle.sh Pro plan VMs, including SSH access, device deployment, cleanup procedures, and residential proxy integration.

## Quick Reference: SSH Access

VM ID format: `vm-<id>` (no slug), accessed via proxy SSH:
```bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  "vm-<ID>+root:<token>@beta-ssh.freestyle.sh"
```

**Example:**
```bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  "vm-e3066474c40140bb9993cfb9611bdcab+root:6DNs9MDXyLDuXtcZ.HFhpNXpcHMEcKFx5@beta-ssh.freestyle.sh"
```

Token extracted from `/v5/identities/{id}/permissions/vm` grant response.

## Pro Plan VM Specs

Plan: **Pro** ($500/month)
- Max concurrent VMs: 400
- Max saved VMs: 4,000
- Max per VM: 32 vCPU / 64 GiB RAM / 256 GB disk

---

## Clean Up Failed EarnApp Devices

### Remove Docker containers
```bash
docker ps -a --filter name="earnapp|ea-" --format "{{.Names}}" | xargs -r docker stop && docker rm
```

### Flush redsocks & iptables
```bash
systemctl stop redsocks-* 2>/dev/null || true
iptables -t nat -X EARN_FARM 2>/dev/null || true
rm -rf /etc/redsocks.d/earnapp* /opt/earnapp-farm/redsocks/*
```

### Cleanup temp scripts
```bash
rm -f /opt/earnapp-farm/finish-*.sh
rm -rf /opt/earnapp-farm/ea-*
```

---

## Deployment Checklist

1. ✅ Verify IP eligibility before deploying (EarnApp rejects datacenter IPs)
2. ✅ Generate UUIDs: `head -c 1024 /dev/urandom | md5sum | tr -d ' -'`
3. ✅ Deploy containers with `EARNAPP_UUID=sdk-node-XXXX` env var
4. ✅ Link devices via `https://earnapp.com/r/<uuid>` in browser logged into Google SSO
5. ✅ Monitor logs for `lum_sdk_node_connected ... res 200`

---

## Residential Proxy Integration

### 9Proxy By-IPs CLI (preferred for farm)
```bash
# Install .deb package
dpkg -i 9proxy_*.deb

# Auth
9proxy auth -u <user> -p <pass>

# Set port range (default=10, bump to more)
9proxy setting -s 10001 -l 20

# Forward US residential IPs to local ports
9proxy proxy -c US -p 10001
9proxy proxy -c US -p 10002
...
```

### Redsocks configuration template
```conf
redsocks {
    local_addr = 127.0.0.1:11080;
    local_port = 11080;
    type = socks5;
    relay = "user:pass@9proxy.host:port";
    autoproxy = 0;
}
```

### Verify exit IP
```bash
curl -s -x socks5h://127.0.0.1:11080 https://api.ipify.org
# Should return residential IP, NOT VM egress IP
```

---

## Common Issues

### IP rejected (datacenter classification)
**Log signature:** `tunnel_init_decline: ip_type.dch`
**Fix:** Use residential proxy (9Proxy/IPRoyal)

### DNS resolution failed
**Log signature:** `ERR: restricted_domain` + `proxyjs_dns_failed`
**Fix:** Don't use DNS hack; implement transparent TUN proxy instead

### Empty reply from server
**Log signature:** `curl: (52) Empty reply from server`
**Fix:** Ensure redsocks uses `type = socks5` not `http-connect`
