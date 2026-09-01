#!/usr/bin/env bash
# earnapp-farm.sh — deploy N EarnApp "devices" on one host, each behind its own residential proxy
# Usage: sudo bash earnapp-farm.sh <count>   (count = number of devices, default 10)
# Requires: docker, sudo NOPASSWD, redsocks via apt, /opt/earnapp-farm/proxies.txt (one ip:port per line)
set -uo pipefail

COUNT="${1:-10}"
BASE_RS_PORT=11080          # redsocks instance port base (per device)
WORKDIR=/opt/earnapp-farm
IMG=fazalfarhan01/earnapp:lite
NET=earnapp-net
STATES=/var/lib/earnapp-farm

echo "==> [1/9] Preflight"
if ! id -nG | grep -qw docker && ! groups | grep -qw docker; then echo "  ! user not in docker group"; fi
if ! sudo -n true 2>/dev/null; then echo "  FATAL: need sudo NOPASSWD"; exit 1; fi
docker network create -d bridge "$NET" 2>/dev/null || echo "  net $NET exists"
sudo mkdir -p "$WORKDIR" "$STATES"
echo "  ok"

echo "==> [2/9] Install redsocks if missing"
if ! command -v redsocks >/dev/null 2>&1; then
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -q redsocks >/dev/null 2>&1 || sudo apt-get update -qq && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -q redsocks >/dev/null 2>&1
fi
command -v redsocks >/dev/null 2>&1 && echo "  redsocks $(redsocks --version 2>&1 | head -1) ok" || { echo "  FATAL: redsocks missing"; exit 1; }

echo "==> [3/9] Pull image"
docker pull -q "$IMG" >/dev/null 2>&1 || docker pull "$IMG"

echo "==> [4/9] Cleanup stale (idempotent)"
for c in $(docker ps -aq --filter "label=earnapp.farm=1"); do
  docker rm -f "$c" >/dev/null 2>&1
done
sudo pkill -f 'redsocks.*earnapp' 2>/dev/null && sleep 1
sudo iptables -t nat -F EARN_FARM 2>/dev/null

echo "==> [5/9] Create redsocks configs + start instances"
PROXY_FILE="$WORKDIR/proxies.txt"
if [ ! -s "$PROXY_FILE" ]; then
  echo "  FATAL: $PROXY_FILE empty — put one 'ip:port' 9proxy per line first"
  exit 1
fi
COUNT_AVAIL=$(wc -l < "$PROXY_FILE")
if [ "$COUNT" -gt "$COUNT_AVAIL" ]; then
  echo "  WARN: only $COUNT_AVAIL proxies, limiting to $COUNT_AVAIL"
  COUNT="$COUNT_AVAIL"
fi

rm -f "$STATES"/*.proxy 2>/dev/null
i=0
while IFS= read -r proxy; do
  [ -z "$proxy" ] && continue
  [ "$i" -ge "$COUNT" ] && break
  i=$((i+1))
  dev="ea-dev$i"
  rs_port=$((BASE_RS_PORT + i))
  sudo tee "$WORKDIR/redsocks-$dev.conf" >/dev/null <<EOF
base { log_debug = off; log_info = on; daemon = on; redirector = iptables; }
redsocks {
  local_ip = 0.0.0.0;
  local_port = $rs_port;
  ip = ${proxy%%:*};
  port = ${proxy##*:};
  type = http-connect;
  autoproxy = 0;
  timeout = 15;
}
EOF
  sudo -b env RS_CONF="$WORKDIR/redsocks-$dev.conf" redsocks -c "$WORKDIR/redsocks-$dev.conf" >/dev/null 2>&1
  echo "$rs_port" > "$STATES/$dev.proxy"
  echo "  $dev -> proxy $proxy (redsocks :$rs_port)"
done < "$PROXY_FILE"

echo "==> [6/9] Ensure iptables chain"
sudo iptables -t nat -N EARN_FARM 2>/dev/null || sudo iptables -t nat -F EARN_FARM
sudo iptables -t nat -C PREROUTING -j EARN_FARM 2>/dev/null || sudo iptables -t nat -I PREROUTING 1 -j EARN_FARM
sudo iptables -t nat -C OUTPUT -j EARN_FARM 2>/dev/null || sudo iptables -t nat -I OUTPUT 1 -j EARN_FARM

echo "==> [7/9] Launch containers, each with its own redsocks redirect"
i=0
while IFS= read -r proxy; do
  [ -z "$proxy" ] && continue
  [ "$i" -ge "$COUNT" ] && break
  i=$((i+1))
  dev="ea-dev$i"
  rs_port=$((BASE_RS_PORT + i))
  uuid="sdk-node-$(printf '%08x%06x' $RANDOM $RANDOM)"
  docker run -d --name "$dev" \
    --label earnapp.farm=1 \
    --network "$NET" \
    --memory 256m --cpus 0.5 \
    --restart unless-stopped \
    -e EARNAPP_UUID="$uuid" \
    "$IMG" >/dev/null 2>&1 || { echo "  ! $dev failed"; continue; }
  cip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$dev")
  sudo iptables -t nat -A EARN_FARM -s "$cip" -p tcp -j REDIRECT --to-ports "$rs_port" >/dev/null 2>&1 || \
    sudo iptables -t nat -A EARN_FARM -s "$cip" -p tcp --dport 80 -j REDIRECT --to-ports "$rs_port"
  echo "$uuid" > "$STATES/$dev.uuid"
  echo "$cip" > "$STATES/$dev.ip"
  echo "  $dev: $cip -> redsocks :$rs_port uuid=$uuid"
done < "$PROXY_FILE"

echo "==> [8/9] Verifikasi"
sleep 12
bad=0
for d in $(docker ps --format '{{.Names}}' | grep '^ea-dev'); do
  st=$(docker inspect -f '{{.State.Health.Status}}' "$d" 2>/dev/null || docker inspect -f '{{.State.Status}}' "$d")
  conn=$(docker logs "$d" 2>&1 | grep -cE 'lum_sdk_node_connected|tunnel_init|proxyjs_client_conn' || true)
  echo "  $d: state=$st conn_signals=$conn"
  [ "$(docker inspect -f '{{.State.Running}}' "$d")" != "true" ] && bad=$((bad+1))
done
echo "==> [9/9] Ringkasan"
echo "  devices=$i  (total di daftar: $(wc -l < "$PROXY_FILE"))"
echo "  config dir: $WORKDIR"
echo "  states: $STATES"
[ "$bad" -eq 0 ] && echo "  STATUS: ALL RUNNING" || echo "  STATUS: $bad down"
