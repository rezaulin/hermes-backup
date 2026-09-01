#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-http-smuggling

Skill: Cybermes Skill
Desc : Hunt HTTP request smuggling (CL.TE, TE.CL, H2.CL, H2.TE). Cause: front-end proxy and back-end server disagree on where one request ends and the next begins (Content-Length vs Transfer-Encoding header parsing inconsistency). CL.TE: front-end uses CL, back uses TE → smuggle by sending TE: chunked but with body that fits CL count. TE.CL: opposite. H2.CL: HTTP/2 downgrade, smuggle CL into HTTP/1.1 back-end. Detection tools: Burp HTTP Request Smuggler extension, smuggler.py, h2csmuggler. Confirm: time-delay technique (smuggled GET with 30s timeout) — if front-end returns slow on next victim request, smuggling works. Validate: cache poisoning chain (smuggle request that gets cached for victim), credential theft (smuggle X-Forwarded-For override that captures next user's cookies), bypass auth (smuggled internal-path request). Real paid examples from major CDN deployments. Use when hunting H1 paid programs running CDN+origin stacks, when targeting load balancer / WAF bypass.

Run:  python claude-bughunter-hunt-http-smuggling.py --help
      python claude-bughunter-hunt-http-smuggling.py --list
      python claude-bughunter-hunt-http-smuggling.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-http-smuggling'
TITLE = 'Cybermes Skill'
DESCRIPTION = "Hunt HTTP request smuggling (CL.TE, TE.CL, H2.CL, H2.TE). Cause: front-end proxy and back-end server disagree on where one request ends and the next begins (Content-Length vs Transfer-Encoding header parsing inconsistency). CL.TE: front-end uses CL, back uses TE → smuggle by sending TE: chunked but with body that fits CL count. TE.CL: opposite. H2.CL: HTTP/2 downgrade, smuggle CL into HTTP/1.1 back-end. Detection tools: Burp HTTP Request Smuggler extension, smuggler.py, h2csmuggler. Confirm: time-delay technique (smuggled GET with 30s timeout) — if front-end returns slow on next victim request, smuggling works. Validate: cache poisoning chain (smuggle request that gets cached for victim), credential theft (smuggle X-Forwarded-For override that captures next user's cookies), bypass auth (smuggled internal-path request). Real paid examples from major CDN deployments. Use when hunting H1 paid programs running CDN+origin stacks, when targeting load balancer / WAF bypass."

PAYLOADS = {
    'main': ["name: hunt-http-smuggling", "description: \"Hunt HTTP request smuggling (CL.TE, TE.CL, H2.CL, H2.TE). Cause: front-end proxy and back-end server disagree on where one request ends and the next begins (Content-Length vs Transfer-Encoding header parsing inconsistency). CL.TE: front-end uses CL, back uses TE \u2192 smuggle by sending TE: chunked but with body that fits CL count. TE.CL: opposite. H2.CL: HTTP/2 downgrade, smuggle CL into HTTP/1.1 back-end. Detection tools: Burp HTTP Request Smuggler extension, smuggler.py, h2csmuggler. Confirm: time-delay technique (smuggled GET with 30s timeout) \u2014 if front-end returns slow on next victim request, smuggling works. Validate: cache poisoning chain (smuggle request that gets cached for victim), credential theft (smuggle X-Forwarded-For override that captures next user's cookies), bypass auth (smuggled internal-path request). Real paid examples from major CDN deployments. Use when hunting H1 paid programs running CDN+origin stacks, when targeting load balancer / WAF bypass.\""],
    '17-http-request-smuggling': [],
    'cl-te-content-length-front-transfer-encoding-back': ["```http", "POST / HTTP/1.1", "Content-Length: 13", "Transfer-Encoding: chunked", "SMUGGLED"],
    'detection': ["1. Burp extension: HTTP Request Smuggler", "2. Right-click request \u2192 Extensions \u2192 HTTP Request Smuggler \u2192 Smuggle probe", "3. Manual timing: CL.TE probe + ~10s delay = backend waiting for rest of body"],
    'impact-chain': ["Poison next request \u2192 access admin as victim", "Steal credentials \u2192 capture victim's session", "Cache poisoning \u2192 stored XSS at scale"],
    'target-suitability-matrix-2026-reality-check': ["The classic CL.TE / TE.CL payloads are NOT universally exploitable in 2026. Modern proxies are RFC 9112 strict by default. Fingerprint the front-end BEFORE investing time."],
    'operator-fingerprint-quick-check': ["```bash", "curl -sI https://target/ | grep -i \"Server:\"", "- `nginx/1.21+`, `Caddy`, `envoy` \u2192 CL/TE classic is dead \u2014 pivot to H2.CL/H2.TE if the front-end speaks HTTP/2, or look for legacy proxies upstream", "- `HAProxy`, header points to AWS/CDN \u2192 run the full payload matrix", "- No Server header \u2192 assume hardened, but run a single quick `space-before-colon` probe; if it doesn't 400, dig deeper"],
    'h2-cl-h2-te-the-modern-dominant-vector': ["H2-downgrade smuggling attacks rely on the front-end speaking HTTP/2 to the client and HTTP/1.1 to origin. The downgrade introduces CL/TE confusion because HTTP/2's frame-length headers don't survive the conversion cleanly. Most CDN+origin chains in 2024-2026 use this exact topology.", "Tools that send HTTP/2 raw frames (Burp Pro's HTTP Request Smuggler extension, `h2csmuggler`, `smuggler.py`) are the right starting point against CDN-fronted targets. Avoid HTTP/1.1-only test clients (curl, raw sockets) against H2-front-ended targets \u2014 you'll send the wrong protocol entirely."],
    'related-skills-chains': ["- **`hunt-cache-poison`** \u2014 Smuggling + cache is the canonical critical chain; one smuggled request becomes the cached response for every subsequent victim. Chain primitive: CL.TE smuggle a request whose response body contains attacker HTML/JS \u2192 front-end cache stores it under a popular URL (`/`, `/login`) \u2192 de-sync poisoning where the smuggled request becomes the cached response for the next N victims, persisting for the cache TTL.", "- **`hunt-auth-bypass`** \u2014 Smuggling reaches internal-only routes that the front-end WAF/auth-proxy filters out. Chain primitive: smuggle `GET /admin/users HTTP/1.1` past the front-end ACL that blocks external `/admin/*` \u2192 backend processes the smuggled request as if from a trusted internal source \u2192 bypass front-end auth by smuggling internal-routed request \u2192 admin data in the response queue.", "- **`hunt-idor`** \u2014 Smuggling attaches the NEXT user's session cookies to an attacker-controlled request path. Chain primitive: smuggle `GET /api/me HTTP/1.1` with no cookies \u2192 backend pairs it with the next legitimate user's incoming connection cookies \u2192 victim's session cookie attached to attacker's smuggled request \u2192 attacker reads the response containing victim's PII/tokens.", "- **`hunt-xss`** \u2014 Smuggling injects XSS payloads into the response stream of the next victim without ever appearing in a URL parameter. Chain primitive: smuggled request body contains reflected payload that the backend renders into the next response in the queue \u2192 next visitor to `/` receives attacker HTML inline \u2192 reflected XSS at every visitor without any URL parameter visible to them or to logs.", "- **`security-arsenal`** \u2014 Reach for the smuggling payload bank (CL.TE / TE.CL / TE.TE obfuscations, H2.CL downgrade probes, h2csmuggler one-liners, Burp HTTP Request Smuggler extension config) and the time-delay confirmation template before manual hex-editing.", "- **`triage-validation`** \u2014 Run the Pre-Severity Gate before claiming Critical: the smuggled-request effect MUST land on a request issued by a different client/session, not your own follow-up. A timing delta in your own browser alone is parser disagreement, not exploitable smuggling."],
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