#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/waf-bypass-techniques

Skill: SKILL: WAF Bypass Techniques — Evasion Playbook
Desc : >-

Run:  python hack-skills-waf-bypass-techniques.py --help
      python hack-skills-waf-bypass-techniques.py --list
      python hack-skills-waf-bypass-techniques.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/waf-bypass-techniques'
TITLE = 'SKILL: WAF Bypass Techniques — Evasion Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: waf-bypass-techniques", "description: >-", "WAF bypass methodology and generic evasion techniques. Use when a web application", "firewall blocks injection payloads (SQLi, XSS, RCE) and you need to craft", "bypasses using encoding, protocol-level tricks, or WAF-specific weaknesses."],
    'skill-waf-bypass-techniques-evasion-playbook': [],
    '0-related-routing': ["- [sqli-sql-injection](../sqli-sql-injection/SKILL.md) for payloads to deliver after bypassing WAF", "- [xss-cross-site-scripting](../xss-cross-site-scripting/SKILL.md) for XSS payloads that need WAF evasion", "- [request-smuggling](../request-smuggling/SKILL.md) when smuggling can route requests around WAF entirely", "- [http-parameter-pollution](../http-parameter-pollution/SKILL.md) HPP is itself a WAF bypass primitive", "- [csp-bypass-advanced](../csp-bypass-advanced/SKILL.md) when WAF blocks inline scripts but CSP bypass is available", "- [ghost-bits-cast-attack](../ghost-bits-cast-attack/SKILL.md) **Java backends only** \u2014 when every encoding trick above is blocked, use Ghost Bits: Java's 16-bit `char` to 8-bit `byte` narrowing produces 255 Unicode bypass variants per dangerous ASCII byte; re-enables WAF-patched CVEs in Tomcat, Spring, Jetty, Jackson, Fastjson, BCEL, and more"],
    'product-specific-reference': ["Load [WAF_PRODUCT_MATRIX.md](./WAF_PRODUCT_MATRIX.md) when you need per-product bypass techniques for Cloudflare, AWS WAF, ModSecurity CRS, Akamai, Imperva, F5 BIG-IP, or Sucuri."],
    '1-phase-0-identify-the-waf': ["Before bypassing, know what you're fighting."],
    '1-1-tools': [],
    '1-2-behavioral-fingerprinting': ["1. Send benign request \u2192 record baseline response (status, headers, body size)", "2. Send obvious attack: /?q=<script>alert(1)</script>", "3. Compare: 403? Custom block page? Redirect? Connection reset?", "4. Block page content reveals WAF: \"Cloudflare\", \"Access Denied (Imperva)\", \"ModSecurity\"", "5. If transparent proxy: check response time difference (WAF adds latency)"],
    '2-generic-bypass-categories': [],
    '2-1-encoding-bypasses': [],
    '2-2-chunked-transfer-encoding': ["Split the payload across HTTP chunks so no single chunk contains the blocked pattern:", "```http", "POST /search HTTP/1.1", "Transfer-Encoding: chunked", "WAFs that inspect the full body may not reassemble chunks before matching."],
    '2-3-http-2-binary-format-bypasses': ["HTTP/2 transmits headers as binary HPACK-encoded frames. Some WAFs only inspect after downgrading to HTTP/1.1:", "- Header names can contain characters illegal in HTTP/1.1", "- Pseudo-headers (`:method`, `:path`) bypass header-based WAF rules", "- H2 \u2192 H1 downgrade may introduce request smuggling (see [request-smuggling](../request-smuggling/SKILL.md))"],
    '2-4-http-parameter-pollution-hpp': ["Different servers handle duplicate parameters differently:", "WAF checks `a=1` (benign), app uses `a=2` (malicious). Or combine: `a=sel&a=ect` \u2192 ASP.NET sees `a=sel,ect`."],
    '2-5-ip-source-spoofing-bypass-ip-based-rules': ["Headers trusted by some WAFs/apps for client IP:", "X-Forwarded-For: 127.0.0.1", "X-Real-IP: 127.0.0.1", "X-Originating-IP: 127.0.0.1", "True-Client-IP: 127.0.0.1", "CF-Connecting-IP: 127.0.0.1", "X-Client-IP: 127.0.0.1", "Forwarded: for=127.0.0.1", "Use case: WAF whitelists internal IPs or has different rule sets per source."],
    '2-6-path-normalization-tricks': [],
    '2-7-content-type-manipulation': ["WAFs often have format-specific parsers. Switching Content-Type can bypass rules:", "Default:  Content-Type: application/x-www-form-urlencoded  \u2192 WAF parses params", "Switch:   Content-Type: application/json  \u2192 WAF may not parse JSON body", "Switch:   Content-Type: multipart/form-data  \u2192 WAF may not inspect all parts", "Switch:   Content-Type: text/xml  \u2192 WAF expects XML, payload in different format", "**Trick**: If app accepts both JSON and form-urlencoded, use JSON \u2014 WAFs often have weaker JSON inspection rules."],
    '2-8-multipart-boundary-abuse': ["```http", "Content-Type: multipart/form-data; boundary=----WAFBypass", "Content-Disposition: form-data; name=\"q\"", "<script>alert(1)</script>", "Variations: long boundary strings, boundary with special characters, missing final boundary, nested multipart."],
    '2-9-newline-whitespace-injection': ["```sql", "-- SQL keyword splitting", "ECT * FROM users", "-- SQL comment insertion", "SEL/**/ECT * FR/**/OM users", "UN/**/ION SEL/**/ECT 1,2,3", "-- Tab/vertical tab as separator", "SELECT\\t*\\tFROM\\tusers"],
    '2-10-keyword-splitting-alternative-syntax': [],
    '3-protocol-level-bypass-techniques': [],
    '3-1-request-line-abuse': ["```http", "GET /path?q=attack HTTP/1.1    \u2190 WAF inspects", "```http", "GET http://target.com/path?q=attack HTTP/1.1   \u2190 Absolute URI: some WAFs miss the path"],
    '3-2-header-injection-via-crlf': ["If WAF inspects original headers but app processes injected ones:", "X-Custom: value\\r\\nX-Forwarded-For: 127.0.0.1"],
    '3-3-connection-state-bypass': ["1. Establish connection through WAF (normal request)", "2. On same keep-alive connection, send attack request", "3. Some WAFs reduce inspection on subsequent requests in same connection"],
    '4-waf-bypass-decision-tree': ["Payload blocked by WAF?", "\u251c\u2500\u2500 Identify WAF (wafw00f, response headers, block page)", "\u251c\u2500\u2500 Try encoding bypasses", "\u2502   \u251c\u2500\u2500 URL encode payload \u2192 still blocked?", "\u2502   \u251c\u2500\u2500 Double URL encode \u2192 still blocked?", "\u2502   \u251c\u2500\u2500 Unicode/overlong UTF-8 \u2192 still blocked?", "\u2502   \u251c\u2500\u2500 Mixed case keywords \u2192 still blocked?", "\u2502   \u2514\u2500\u2500 HTML entities (for XSS) \u2192 still blocked?", "\u251c\u2500\u2500 Try protocol-level bypasses", "\u2502   \u251c\u2500\u2500 Switch Content-Type (JSON, multipart, XML)", "\u2502   \u2502   \u2514\u2500\u2500 App accepts alternate format? \u2192 re-send payload", "\u2502   \u251c\u2500\u2500 HTTP Parameter Pollution (duplicate params)", "\u2502   \u251c\u2500\u2500 Chunked Transfer-Encoding to split payload", "\u2502   \u251c\u2500\u2500 HTTP/2 direct if available (binary framing bypass)", "\u2502   \u2514\u2500\u2500 Request line: absolute URI format", "\u251c\u2500\u2500 Try path-based bypasses", "\u2502   \u251c\u2500\u2500 Path normalization (/./path, //path, ;param)", "\u2502   \u251c\u2500\u2500 Different HTTP method (POST vs PUT vs PATCH)", "\u2502   \u2514\u2500\u2500 Alternate endpoint serving same function", "\u251c\u2500\u2500 Try payload mutation", "\u2502   \u251c\u2500\u2500 SQL: comments (/**/), alternative functions, hex literals", "\u2502   \u251c\u2500\u2500 XSS: alternative tags/events, JS template literals", "\u2502   \u251c\u2500\u2500 RCE: wildcard abuse, string concatenation, variable expansion", "\u2502   \u2514\u2500\u2500 Check WAF_PRODUCT_MATRIX.md for vendor-specific mutations", "\u251c\u2500\u2500 Try IP-source bypass", "\u2502   \u251c\u2500\u2500 X-Forwarded-For / True-Client-IP spoofing", "\u2502   \u251c\u2500\u2500 Access origin server directly (bypass CDN)", "\u2502   \u2514\u2500\u2500 Find origin IP (Shodan, historical DNS, email headers)", "\u2514\u2500\u2500 Try request smuggling to skip WAF entirely", "\u2514\u2500\u2500 See ../request-smuggling/SKILL.md"],
    '5-common-mistakes-trick-notes': ["1. **Test bypass with actual exploitation, not just 200 OK**: WAF may return 200 but strip the payload silently.", "2. **WAFs often have size limits**: Very large request bodies (>8KB\u2013128KB depending on WAF) may bypass inspection entirely.", "3. **Rate limiting \u2260 WAF**: Getting 429s is rate limiting, not payload blocking. Different bypass needed.", "4. **CDN caching**: If the WAF is at CDN level, cached responses bypass WAF on subsequent requests. Poison cache with clean request, exploit cache.", "5. **Origin server direct access**: If you find the origin IP behind CDN/WAF, connect directly \u2014 WAF is bypassed completely.", "6. **Multipart file upload fields**: WAFs often skip inspection of file content in multipart uploads \u2014 embed payload in filename or file content if reflected."],
    '6-defense-perspective': [],
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