#!/bin/bash
# launch-rdp-gui.sh — Launcher xfreerdp ke display Xvfb + fire xdotool control.
# Usage: launch-rdp-gui.sh <user> <pass> [server=127.0.0.1:13389] [win 1280x700]
# Set DISPLAY & XAUTHORITY sesuai Xvfb host sebelum run (lihat SKILL.md).
set -u
USER="${1:?usage: launch-rdp-gui.sh <user> <pass> [server] [size]}"
PASS="$2"
SERVER="${3:-127.0.0.1:13389}"
SIZE="${4:-1280x700}"
# ambil Xauthority Xvfb yang aktif
export DISPLAY="${DISPLAY:-:99}"
export XAUTHORITY="${XAUTHORITY:-$(ls /tmp/xvfb-run.*/Xauthority 2>/dev/null | head -1)}"
[ -n "$XAUTHORITY" ] && [ -f "$XAUTHORITY" ] || { echo "ERR: XAUTHORITY gak ketemu ($XAUTHORITY)"; exit 1; }
echo "[launch] xfreerdp $SERVER ($SIZE) display=$DISPLAY auth=$XAUTHORITY"
xfreerdp /v:"$SERVER" /u:"$USER" /p:"$PASS" /size:"$SIZE" \
    +clipboard /cert-ignore /log-level:INFO
