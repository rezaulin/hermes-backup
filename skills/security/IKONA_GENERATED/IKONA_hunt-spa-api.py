#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-spa-api

Skill: React/CRA:
Desc : Discover a single-page-app's hidden backend API from its public JS bundle, then test that API for broken access control / missing authentication. One of the highest-yield web plays in modern recon — SPAs ship their entire backend route map to the browser, and the API behind them is frequently missing the auth middleware the login page implies. Built from an authorized engagement where this play found an unauthenticated financial API that an ASM scan reporting hundreds of "Criticals" completely missed. Use whenever a target serves a JS-heavy SPA (React/Vue/Angular/Next), an "app"/"console"/"dashboard"/"portal" subdomain, or any `*api*` host shows up in recon. Leaked build artifacts (source maps / .env / .git / asset-manifest) are owned by hunt-source-leak; API version-inventory and behavioral diffing by hunt-shadow-api; this skill owns mapping a live SPA's backend routes from its JS bundle and testing them for broken access control / missing auth.

Run:  python claude-bughunter-hunt-spa-api.py --help
      python claude-bughunter-hunt-spa-api.py --list
      python claude-bughunter-hunt-spa-api.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-spa-api'
TITLE = 'React/CRA:'
DESCRIPTION = 'Discover a single-page-app\'s hidden backend API from its public JS bundle, then test that API for broken access control / missing authentication. One of the highest-yield web plays in modern recon — SPAs ship their entire backend route map to the browser, and the API behind them is frequently missing the auth middleware the login page implies. Built from an authorized engagement where this play found an unauthenticated financial API that an ASM scan reporting hundreds of "Criticals" completely missed. Use whenever a target serves a JS-heavy SPA (React/Vue/Angular/Next), an "app"/"console"/"dashboard"/"portal" subdomain, or any `*api*` host shows up in recon. Leaked build artifacts (source maps / .env / .git / asset-manifest) are owned by hunt-source-leak; API version-inventory and behavioral diffing by hunt-shadow-api; this skill owns mapping a live SPA\'s backend routes from its JS bundle and testing them for broken access control / missing auth.'

PAYLOADS = {
    'main': ["name: hunt-spa-api", "description: Discover a single-page-app's hidden backend API from its public JS bundle, then test that API for broken access control / missing authentication. One of the highest-yield web plays in modern recon \u2014 SPAs ship their entire backend route map to the browser, and the API behind them is frequently missing the auth middleware the login page implies. Built from an authorized engagement where this play found an unauthenticated financial API that an ASM scan reporting hundreds of \"Criticals\" completely missed. Use whenever a target serves a JS-heavy SPA (React/Vue/Angular/Next), an \"app\"/\"console\"/\"dashboard\"/\"portal\" subdomain, or any `*api*` host shows up in recon. Leaked build artifacts (source maps / .env / .git / asset-manifest) are owned by hunt-source-leak; API version-inventory and behavioral diffing by hunt-shadow-api; this skill owns mapping a live SPA's backend routes from its JS bundle and testing them for broken access control / missing auth.", "sources: authorized-engagement", "report_count: 1"],
    'when-to-use-this-skill': ["Trigger when:", "- A target host returns a tiny HTML shell + big `/static/js/*.js` or `/_next/static/*` bundles (React/Vue/Angular/Next/Svelte SPA)", "- You see a subdomain named `console`, `app`, `dashboard`, `portal`, `admin`, `panel`, `manage`, `internal`", "- Recon surfaces any `*api*`, `*-api*`, `api.*` host", "- A login page is OAuth/SSO-gated (the *frontend* auth tells you nothing about whether the *API* enforces auth)", "The core insight: **a SPA is a client to a backend API, and it ships the full map of that API \u2014 hosts, routes, sometimes keys \u2014 to anyone who views source.** The login page being protected says nothing about whether the API behind it checks tokens. Auth is frequently enforced on the *gateway/login* and missing on a *route group* of the API.", "DO NOT skip this because \"the app needs login\" \u2014 that's exactly when this pays off."],
    'the-play-5-steps': [],
    '1-pull-the-shell-enumerate-the-bundles': ["```bash", "curl -s https://console.target.com/ -o index.html"],
    'react-cra': ["grep -oE '/static/js/[^\"]+\\.js' index.html"],
    'next-js': ["grep -oE '/_next/static/[^\"]+\\.js' index.html"],
    'generic': ["grep -oiE 'src=\"[^\"]+\\.js[^\"]*\"' index.html", "Download every bundle (they can be multi-MB \u2014 that's fine, it's all route data):", "```bash", "mkdir bundles", "for j in $(grep -oE '/static/js/[^\"]+\\.js' index.html | sort -u); do", "curl -s \"https://console.target.com$j\" -o \"bundles/$(echo \"$j\"|tr '/' '_')\""],
    '2-harvest-api-hosts-routes-and-secrets-from-the-bundles': ["```bash", "B=bundles/*.js"],
    'backend-api-hosts-incl-dev-beta-staging-variants-often-weaker-auth': ["grep -ohiE 'https://[a-z0-9.-]*(api|console|backend|service)[a-z0-9.-]*\\.target\\.com[a-z0-9/_-]*' $B | sort -u"],
    'versioned-api-base-paths': ["grep -ohiE '/api/v[0-9]+/?' $B | sort -u"],
    'route-literals-minified-bundles-store-routes-as-string-segments-not-full-urls': [],
    'grep-for-quoted-resource-action-strings': ["grep -ohiE '\"[a-z0-9_-]+/[a-z0-9_/-]+\"' $B | tr -d '\"' \\"],
    'secrets-validate-before-trusting-most-aiza-keys-are-maps-analytics-not-auth': ["grep -ohiE '(AIza[0-9A-Za-z_-]{35}|AKIA[0-9A-Z]{16}|sk_live_[0-9A-Za-z]+|eyJ[A-Za-z0-9_-]{10,}\\.[A-Za-z0-9_-]{10,}|apiKey[\"'\"'\"']?\\s*[:=]\\s*[\"'\"'\"'][^\"'\"'\"']+)' $B | sort -u", "**Note:** minifiers store routes as concatenated string segments (e.g. `\"account/payment/list\"`), NOT full `/api/v2/...` URLs \u2014 so a naive `/api/v*` grep returns nothing. Grep for the **resource-word route strings** and prepend the base yourself."],
    '3-establish-a-control-find-an-endpoint-that-is-gated': ["Before declaring anything vulnerable, send an unauthenticated request to an endpoint you expect to be protected, and capture what *correct* rejection looks like:", "```bash", "curl -s -X POST https://api.target.com/api/users -H 'Content-Type: application/json' -d '{}'"],
    'secure-error-missing-or-invalid-authorization-header-or-http-401': ["This is your differential. A sibling API (e.g. a second API host, or a different route group on the same host) is the ideal control \u2014 same stack, so a different response = real authz gap, not a quirk."],
    '4-test-each-route-family-unauthenticated-both-methods': ["For every discovered route, send it with **no `Authorization` header** and compare to the control:", "```bash", "for r in <routes>; do", "curl -s -o /tmp/r -w \"[%{http_code}] $r\\n\" -X POST -H 'Content-Type: application/json' -d '{}' \"https://api.target.com/api/v2/$r\"", "Interpret:", "- **`401`/`\"Missing authorization\"`** \u2192 gated (correct). Move on.", "- **`200` with data** \u2192 unauthenticated data exposure. **Finding.**", "- **`400 \"field X is mandatory\"`** \u2192 the route processed your request and reached *business-logic validation* without an auth check \u2192 **auth bypass; supply the field minimally to confirm.**", "- **`200` + verbose DB/stack error** (e.g. `PROCEDURE db_x.sp_y does not exist`) \u2192 reached the data layer unauthenticated; also a SQLi-surface signal.", "- **Mandatory fields named like `is_admin` / `is_internal` / `requested_by` / `role_id` / `account_type`** \u2192 **authorization derived from client-supplied parameters** \u2014 set the privilege flag and you self-elevate. Critical-class."],
    '5-pivot-prove-minimally': ["- IDs returned by one endpoint (`account_id`, `order_id`, `deal_id`) are the keys the *other* endpoints consume \u2014 they prove the whole router is reachable, not just one route.", "- Test `dev-`/`beta-`/`staging-` API variants \u2014 they frequently have weaker/disabled auth.", "- Check the response headers: `Access-Control-Allow-Origin: *` compounds the issue (any web origin reads it from a victim's browser).", "- **STOP at minimum-necessary proof.** A handful of records (or a `totalCount`) confirms the missing check. Do NOT enumerate the table \u2014 see `redteam-mindset` data-minimization boundary. The finding is the absent auth, not the data volume."],
    'what-the-api-behind-the-sso-login-really-means': ["A common, dangerous architecture:", "- `console.target.com` (the SPA) \u2192 login is **Entra/Okta/Google OAuth** (looks airtight).", "- `api.target.com` (the backend) \u2192 some route groups enforce the bearer token, **some route groups forgot the middleware.**", "The frontend login is theatre if the API doesn't independently validate the token on every route. Always test the API directly, bare, regardless of how locked-down the login UI is."],
    'anti-patterns': ["- **\"The app requires login, so the API must be protected.\"** No \u2014 test the API directly, unauthenticated. The whole point.", "- **\"Minified bundle, can't read it.\"** You don't need to read it \u2014 grep it for hosts/routes/secrets. 5 minutes.", "- **\"`/api/v1/foo` returned 404, so no API here.\"** Wrong base or wrong method. Try `/api/`, `/api/v2/`, POST not GET, and the exact route strings from the bundle (Express's 404 echoes the path \u2014 use it to calibrate).", "- **\"AIza key found \u2192 critical secret.\"** Validate first \u2014 most are Maps/analytics keys (`CONFIGURATION_NOT_FOUND` on identitytoolkit = not Auth-enabled). Don't over-claim.", "- **Dumping the whole dataset once you get a 200.** Stop at PoC. (`redteam-mindset`.)", "- **Account-creation / write endpoints as \"proof\".** Read endpoints prove the auth gap without creating state. Never POST a `create`/`signup`/`upload` to \"demonstrate\" \u2014 that's a destructive write needing explicit per-action authorization."],
    'related-skills-chains': ["- **`hunt-api-misconfig`** \u2014 once the API is mapped, run the broader misconfig matrix (method tampering, mass assignment, JWT alg confusion) per route.", "- **`hunt-idor`** \u2014 the `account_id`/`order_id` pivots feed straight into IDOR testing across discovered routes.", "- **`hunt-source-leak`** \u2014 sourcemaps (`*.js.map`) reconstruct original source for deeper route/secret extraction; same harvesting muscle.", "- **`hunt-nextjs`** \u2014 for Next.js targets, layer the middleware-bypass (`x-middleware-subrequest`) and `/_next/data` route tests on top of this.", "- **`redteam-mindset`** \u2014 the data-minimization boundary governs step 5: prove the missing check, don't exfiltrate the table.", "- **`recon-scope-triage`** \u2014 verify the API host actually belongs to the target before testing (don't pop a same-named third party's API)."],
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