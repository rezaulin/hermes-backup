#!/bin/bash
# tunnel-rdp.sh — Buka SSH tunnel ke port RDP VM remote (bypass IPv6-only).
# Usage: bash tunnel-rdp.sh <ssh-target> [local-port] [remote-port]
#   ssh-target: e.g. "rena+root:TOKEN@beta-ssh.freestyle.sh" (token di username)
#   default port: local 13389 -> remote 3389 (xrdp)
set -u
TARGET="${1:?usage: tunnel-rdp.sh <ssh-target> [local-port] [remote-port]}"
LP="${2:-13389}"
RP="${3:-3389}"
echo "[tunnel] $LP -> $TARGET:$RP  (pass: ${LP}:127.0.0.1:${RP})"
while true; do
  echo "[tunnel] connecting... $(date -Is)"
  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
      -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
      -o ExitOnForwardFailure=yes \
      -N -L "$LP:127.0.0.1:$RP" "$TARGET"
  echo "[tunnel] dropped, reconnect 3s..."; sleep 3
done
