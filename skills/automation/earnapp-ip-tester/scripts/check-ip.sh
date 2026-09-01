#!/bin/bash
# check-ip.sh — pre-test IP quality buat EarnApp farm
# Usage: bash check-ip.sh <IP>
# Exit: 0 = LOLOS (bagus), 1 = GAGAL (jelek)

set -euo pipefail

IP="${1:-}"
[ -z "$IP" ] && { echo "Usage: $0 <IP>"; exit 2; }

echo "=== IP: $IP ==="

# 1. Cek org/region
INFO=$(curl -s --max-time 6 "https://ipinfo.io/$IP/json" 2>/dev/null || echo '{}')
ORG=$(echo "$INFO" | grep -oE '"org": *"[^"]*"' | head -1 | sed 's/.*: *"//;s/"//')
CITY=$(echo "$INFO" | grep -oE '"city": *"[^"]*"' | head -1 | sed 's/.*: *"//;s/"//')
REGION=$(echo "$INFO" | grep -oE '"region": *"[^"]*"' | head -1 | sed 's/.*: *"//;s/"//')
echo "  City/Region: $CITY, $REGION"
echo "  Org: $ORG"

# 2. Reject datacenter ASN
DC_ASN="AMAZON|DIGITALOCEAN|HETZNER|OVH|VULTR|GOOGLE|AZURE|ALIBABA|TENCENT|HUAWEI|HOSTING|SERVER|CLOUD|COLO|RACKSPACE|LINODE|ORACLE|IBM|COGENT|HE.NET|LEVEL3|INTERNEXA|TIER.NET|TIER-NET"
if echo "$ORG" | grep -qiE "$DC_ASN"; then
    echo "  ❌ REJECT: Datacenter ASN ($ORG)"
    exit 1
fi

# 3. Reject California
if echo "$REGION" | grep -qi "california"; then
    echo "  ❌ REJECT: California flagged region"
    exit 1
fi

# 4. Cek latency
LAT=$(curl -s --max-time 8 -o /dev/null -w "%{time_total}" "https://ipinfo.io/$IP/json" 2>/dev/null || echo "999")
echo "  Latency: ${LAT}s"
if (( $(echo "$LAT >= 1.5" | bc -l 2>/dev/null) )); then
    echo "  ❌ REJECT: Latency > 1.5s"
    exit 1
fi

# 5. LOLOS
echo "  ✅ LOLOS — IP layak dipasang"
exit 0