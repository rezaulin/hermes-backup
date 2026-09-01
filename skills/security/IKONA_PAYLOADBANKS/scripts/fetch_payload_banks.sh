#!/bin/bash
# fetch_payload_banks.sh — bulk-download security payload banks (VERIFIED Aug 2026)
# Run: bash fetch_payload_banks.sh <destination-references-dir>
# Requires: curl, bash. No other deps.
set -e
DEST="${1:?usage: bash fetch_payload_banks.sh /path/to/skill/references}"
mkdir -p "$DEST/payloadsallthethings" "$DEST/hacktricks" "$DEST/misc"

enc() { printf '%s' "$1" | sed 's/ /%20/g'; }

ok=0; fail=0
grab() { # url dst
  if curl -sfL -m 60 "$1" -o "$2"; then
    ok=$((ok+1)); printf "OK   %-36s %7s\n" "$2" "$(wc -c < "$2")"
  else
    fail=$((fail+1)); printf "FAIL %s\n" "$1"; rm -f "$2"
  fi
}

# --- PayloadsAllTheThings (swisskyrepo, branch master, spaces -> %20) ---
PATT_BASE="https://raw.githubusercontent.com/swisskyrepo/PayloadsAllTheThings/master"
declare -A PATT=(
  ["XSS Injection/README.md"]="payloadsallthethings/xss.md"
  ["SQL Injection/README.md"]="payloadsallthethings/sqli.md"
  ["Server Side Request Forgery/README.md"]="payloadsallthethings/ssrf.md"
  ["Server Side Template Injection/README.md"]="payloadsallthethings/ssti.md"
  ["JSON Web Token/README.md"]="payloadsallthethings/jwt.md"
  ["Race Condition/README.md"]="payloadsallthethings/race.md"
  ["Upload Insecure Files/README.md"]="payloadsallthethings/upload.md"
  ["Insecure Direct Object References/README.md"]="payloadsallthethings/idor.md"
  ["Open Redirect/README.md"]="payloadsallthethings/open-redirect.md"
  ["CRLF Injection/README.md"]="payloadsallthethings/crlf.md"
  ["Command Injection/README.md"]="payloadsallthethings/cmd-injection.md"
  ["CORS Misconfiguration/README.md"]="payloadsallthethings/cors.md"
  ["Prototype Pollution/README.md"]="payloadsallthethings/proto-pollution.md"
  ["Web Sockets/README.md"]="payloadsallthethings/websockets.md"
  ["XXE Injection/README.md"]="payloadsallthethings/xxe.md"
)
for src in "${!PATT[@]}"; do
  grab "$PATT_BASE/$(enc "$src")" "$DEST/${PATT[$src]}"
done

# --- HackTricks (carlospolop, branch master, content di src/pentesting-web/) ---
HT="https://raw.githubusercontent.com/carlospolop/hacktricks/master/src/pentesting-web"
declare -A HTF=(
  ["bypass-payment-process.md"]="hacktricks/bypass-payment.md"
  ["race-condition.md"]="hacktricks/race-condition.md"
  ["hacking-jwt-json-web-tokens.md"]="hacktricks/jwt.md"
  ["cors-bypass.md"]="hacktricks/cors-bypass.md"
  ["csrf-cross-site-request-forgery.md"]="hacktricks/csrf.md"
  ["oauth-to-account-takeover.md"]="hacktricks/oauth-takeover.md"
  ["proxy-waf-protections-bypass.md"]="hacktricks/waf-bypass.md"
  ["content-security-policy-csp-bypass/README.md"]="hacktricks/csp-bypass.md"
  ["mass-assignment-cwe-915.md"]="hacktricks/mass-assignment.md"
  ["nosql-injection.md"]="hacktricks/nosql-injection.md"
  ["orm-injection.md"]="hacktricks/orm-injection.md"
  ["ldap-injection.md"]="hacktricks/ldap-injection.md"
  ["login-bypass/README.md"]="hacktricks/login-bypass.md"
  ["deserialization/README.md"]="hacktricks/deserialization.md"
  ["file-upload/README.md"]="hacktricks/file-upload.md"
  ["file-inclusion/README.md"]="hacktricks/file-inclusion.md"
  ["idor.md"]="hacktricks/idor.md"
  ["account-takeover.md"]="hacktricks/account-takeover.md"
  ["2fa-bypass.md"]="hacktricks/2fa-bypass.md"
  ["rate-limit-bypass.md"]="hacktricks/rate-limit-bypass.md"
  ["open-redirect.md"]="hacktricks/open-redirect.md"
  ["clickjacking.md"]="hacktricks/clickjacking.md"
  ["parameter-pollution.md"]="hacktricks/parameter-pollution.md"
  ["crlf-0d-0a.md"]="hacktricks/crlf.md"
  ["command-injection.md"]="hacktricks/command-injection.md"
)
for src in "${!HTF[@]}"; do
  grab "$HT/$src" "$DEST/${HTF[$src]}"
done

# --- Misc bug-bounty (pengganti payloadbox yang DEAD) ---
grab "https://raw.githubusercontent.com/Mehdi0x90/Web_Hacking/main/README.md" "$DEST/misc/web_hacking_mehdi0x90.md"
grab "https://raw.githubusercontent.com/EdOverflow/bugbounty-cheatsheet/master/cheatsheets/xss.md" "$DEST/misc/bb-xss.md"
grab "https://raw.githubusercontent.com/EdOverflow/bugbounty-cheatsheet/master/cheatsheets/sqli.md" "$DEST/misc/bb-sqli.md"
grab "https://raw.githubusercontent.com/EdOverflow/bugbounty-cheatsheet/master/cheatsheets/ssrf.md" "$DEST/misc/bb-ssrf.md"

echo "---"
echo "downloaded=$ok failed=$fail total=$(du -sh "$DEST" | cut -f1)"
