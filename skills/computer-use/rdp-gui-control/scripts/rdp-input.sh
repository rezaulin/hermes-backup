#!/bin/bash
# rdp-input.sh — Kirim input keyboard/mouse ke window FreeRDP.
# Usage: rdp-input.sh <action> [args]
#   action: key '<combo>'  |  type '<text>'  |  enter  |  click <x> <y> [btn]  |  move <x> <y>  |  scrshot <out.png>
set -u
WID=$(xdotool search --name "FreeRDP" 2>/dev/null | head -1)
[ -n "$WID" ] || { echo "ERR: window FreeRDP gak ketemu"; exit 1; }
export DISPLAY="${DISPLAY:-:99}"
export XAUTHORITY="${XAUTHORITY:-$(ls /tmp/xvfb-run.*/Xauthority 2>/dev/null | head -1)}"
ACT="${1:?usage: rdp-input.sh <action> [args]}"
case "$ACT" in
  key)   xdotool key --window "$WID" "$2";;
  type)  xdotool type --window "$WID" --delay 40 "$2";;
  enter) xdotool key --window "$WID" Return;;
  click) x=${2:-0}; y=${3:-0}; btn=${4:-1}
         xdotool mousemove --window "$WID" "$x" "$y"; sleep 0.3; xdotool click --window "$WID" "$btn";;
  move)  xdotool mousemove --window "$WID" "$2" "$3";;
  scrshot) out="${2:-/tmp/rdp.png}"
         xwd -root -display "$DISPLAY" -silent -out /tmp/_rdp.xwd 2>/dev/null
         convert /tmp/_rdp.xwd "$out" 2>/dev/null
         echo "screenshot -> $out ($(stat -c%s "$out") bytes)";;
  *) echo "action tak dikenal: $ACT"; exit 2;;
esac
