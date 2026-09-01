#!/usr/bin/env bash
# earnapp-watchdog.sh — poll device health, replace dead proxies, restart affected redsocks, verify earnapp connection
# Usage: sudo bash earnapp-watchdog.sh   (run every ~5 min via cron/systemd timer)
# Config: token/order via env EARNAPP_9PROXY_TOKEN / EARNAPP_9PROXY_ORDER or /opt/earnapp-farm/9proxy.env
set -uo pipefail

WORKDIR=/opt/earnapp-farm
STATES=/var/lib/earnapp-farm
PROXY_FILE="$WORKDIR/proxies.txt"
API_BASE="https://api.9proxy.com/api/proxy"
API_T="1"
COUNTRY="US"
LOG="$WORKDIR/watchdog.log"

ts() { date +%Y-%m-%dT%H:%M:%S; }
log() { echo "$(ts) $*" >> "$LOG"; }

API_TOKEN="${EARNAPP_9PROXY_TOKEN:-}"
API_ORDER="${EARNAPP_9PROXY_ORDER:-}"
if [ -f "$WORKDIR/9proxy.env" ]; then
  . "$WORKDIR/9proxy.env"
fi
[ -z "$API_TOKEN" ] && { log "ERROR: no 9proxy token"; exit 1; }

found_log() {
  docker logs "$1" 2>&1 | grep -qE 'lum_sdk_node_connected|tunnel_init resp|proxyjs_client_conn' && return 0 || return 1
}

mapfile -t devs < <(docker ps --filter "label=earnapp.farm=1" --format '{{.Names}}' | sort)
[ "${#devs[@]}" -lt 1 ] && { log "ERROR: no farm containers"; exit 1; }

changed=0
for dev in "${devs[@]}"; do
  rs_port=$(cat "$STATES/$dev.proxy" 2>/dev/null || echo "")
  [ -z "$rs_port" ] && continue
  cur_proxy=$(grep '^  ip = ' "$WORKDIR/redsocks-$dev.conf" 2>/dev/null | sed 's/.*ip = //;s/;//')
  cur_port=$(grep '^  port = ' "$WORKDIR/redsocks-$dev.conf" 2>/dev/null | sed 's/.*port = //;s/;//')
  proxy="${cur_proxy}:${cur_port}"

  # real egress IP through THIS device's redsocks (proves chain end-to-end)
  exit_ip=$(curl -s --max-time 12 -x "http://127.0.0.1:$rs_port" https://api.ipify.org 2>/dev/null | head -1)

  earn_ok=0
  found_log "$dev" && earn_ok=1

  dead=0
  [ -z "$exit_ip" ] && dead=1
  if [ -n "$exit_ip" ] && ! echo "$exit_ip" | grep -qE '^[0-9.]+$'; then dead=1; fi

  if [ "$dead" -eq 1 ] || [ "$earn_ok" -eq 0 ]; then
    log "DEVICE $dev: proxy=$proxy exit='$exit_ip' earn_ok=$earn_ok -> DEAD, replacing"
    resp=$(curl -s --max-time 20 "${API_BASE}?num=1&country=${COUNTRY}&t=${API_T}" \
           -H "Authorization: Token ${API_TOKEN}" 2>/dev/null | head -20)
    newline=$(echo "$resp" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+' | head -1)
    if [ -z "$newline" ]; then
      log "  failed to fetch new proxy; resp=$resp"
      continue
    fi
    nip="${newline%%:*}"; nport="${newline##*:}"
    sudo sed -i "s/^  ip = .*/  ip = ${nip};/" "$WORKDIR/redsocks-$dev.conf"
    sudo sed -i "s/^  port = .*/  port = ${nport};/" "$WORKDIR/redsocks-$dev.conf"
    sudo pkill -f "redsocks-$dev" 2>/dev/null
    sleep 1
    sudo -b env RS_CONF="$WORKDIR/redsocks-$dev.conf" redsocks -c "$WORKDIR/redsocks-$dev.conf" >/dev/null 2>&1
    docker restart "$dev" >/dev/null 2>&1
    log "  replaced -> ${nip}:${nport}, restarted $dev"
    changed=$((changed+1))
  else
    log "DEVICE $dev: OK (exit=$exit_ip earn_ok=$earn_ok)"
  fi
done
log "watchdog done, replaced=$changed"
